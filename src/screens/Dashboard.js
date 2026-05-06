import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

let HealthConnect = null;
let isHCSupported = false;

// Only try to import on Android
if (Platform.OS === 'android') {
  try {
    HealthConnect = require('react-native-health-connect');
    isHCSupported = true;
  } catch (e) {
    console.log('Health Connect not available:', e.message);
  }
}

const mockData = {
  weightKg: 81.8, // ~180 lbs
  caloriesBurned: 2147,
  steps: 8432,
};

function CircularProgress({ value, max, size = 90, strokeWidth = 8, color = '#6366F1', label }) {
  const pct = Math.min(value / max, 1);
  return (
    <View style={{ alignItems: 'center' }}>
      <View style={{ width: size, height: size, position: 'relative' }}>
        <View style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, borderRadius: size/2, border: `${strokeWidth}px solid #374151` }} />
        <View style={{
          width: size, height: size, borderRadius: size/2,
          border: `${strokeWidth}px solid transparent`,
          borderTopColor: pct >= 0.125 ? color : 'transparent',
          borderRightColor: pct >= 0.25 ? color : 'transparent',
          borderBottomColor: pct >= 0.5 ? color : 'transparent',
          borderLeftColor: pct >= 0.75 ? color : 'transparent',
          position: 'absolute',
          transform: [{ rotate: '-90deg' }],
        }} />
        <View style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, justifyContent: 'center', alignItems: 'center' }}>
          <Text style={styles.circleValue}>{typeof value === 'number' && value > 999 ? Math.round(value).toLocaleString() : Math.round(value * 10) / 10}</Text>
          <Text style={styles.circleLabel}>{label}</Text>
        </View>
      </View>
    </View>
  );
}

function MetricCard({ icon, label, value, unit, color = '#6366F1' }) {
  return (
    <View style={styles.metricCard}>
      <View style={[styles.metricIcon, { backgroundColor: color + '20' }]}>
        <Ionicons name={icon} size={20} color={color} />
      </View>
      <View style={styles.metricInfo}>
        <Text style={styles.metricValue}>{value}{unit && <Text style={styles.metricUnit}> {unit}</Text>}</Text>
        <Text style={styles.metricLabel}>{label}</Text>
      </View>
    </View>
  );
}

export default function Dashboard({ navigation }) {
  const [hcData, setHcData] = useState(mockData);
  const [isLoading, setIsLoading] = useState(true);
  const [hcStatus, setHcStatus] = useState('checking'); // checking | connected | available | unavailable
  const [greeting, setGreeting] = useState('');

  useEffect(() => {
    const hr = new Date().getHours();
    if (hr < 12) setGreeting('Good morning');
    else if (hr < 17) setGreeting('Good afternoon');
    else setGreeting('Good evening');

    if (Platform.OS === 'android' && HealthConnect) {
      initHealthConnect();
    } else {
      setHcStatus('unavailable');
      setIsLoading(false);
    }
  }, []);

  const initHealthConnect = async () => {
    try {
      const isAvailable = await HealthConnect.initialize();
      if (!isAvailable) {
        setHcStatus('unavailable');
        setIsLoading(false);
        return;
      }

      setHcStatus('available');

      // Request permissions
      const granted = await HealthConnect.requestPermission([
        { accessType: 'read', recordType: 'Weight' },
        { accessType: 'read', recordType: 'ActiveCaloriesBurned' },
        { accessType: 'read', recordType: 'Steps' },
      ]);

      if (granted && granted.length > 0) {
        setHcStatus('connected');
        await readHealthData();
      } else {
        setHcStatus('available');
        setIsLoading(false);
      }
    } catch (e) {
      console.log('Health Connect init error:', e.message);
      setHcStatus('unavailable');
      setIsLoading(false);
    }
  };

  const readHealthData = async () => {
    try {
      const now = new Date();
      const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
      const endTime = now.toISOString();
      const startTime = startOfDay.toISOString();

      const timeRangeFilter = {
        startTime,
        endTime,
      };

      // Read weight
      let weightKg = mockData.weightKg;
      try {
        const weightResult = await HealthConnect.readRecords('Weight', { timeRangeFilter });
        if (weightResult.records && weightResult.records.length > 0) {
          // Get most recent weight
          const sorted = [...weightResult.records].sort((a, b) =>
            new Date(b.startTime).getTime() - new Date(a.startTime).getTime()
          );
          weightKg = sorted[0].weight?.inKilograms || weightKg;
        }
      } catch (e) {
        console.log('Weight error:', e.message);
      }

      // Read active calories
      let caloriesBurned = mockData.caloriesBurned;
      try {
        const calResult = await HealthConnect.readRecords('ActiveCaloriesBurned', { timeRangeFilter });
        if (calResult.records && calResult.records.length > 0) {
          caloriesBurned = calResult.records.reduce((sum, r) =>
            sum + (r.energy?.inKilocalories || 0), 0
          );
        }
      } catch (e) {
        console.log('Calories error:', e.message);
      }

      // Read steps
      let steps = mockData.steps;
      try {
        const stepsResult = await HealthConnect.readRecords('Steps', { timeRangeFilter });
        if (stepsResult.records && stepsResult.records.length > 0) {
          steps = stepsResult.records.reduce((sum, r) => sum + (r.count || 0), 0);
        }
      } catch (e) {
        console.log('Steps error:', e.message);
      }

      setHcData({
        weightKg: Math.round(weightKg * 10) / 10,
        caloriesBurned: Math.round(caloriesBurned),
        steps: steps,
      });
    } catch (e) {
      console.log('Read health data error:', e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshData = async () => {
    if (hcStatus === 'connected') {
      setIsLoading(true);
      await readHealthData();
    } else {
      await initHealthConnect();
    }
  };

  if (isLoading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color="#6366F1" />
        <Text style={styles.loadingText}>Loading health data...</Text>
      </View>
    );
  }

  const getStatusInfo = () => {
    switch (hcStatus) {
      case 'connected':
        return { color: '#10B981', text: 'Health Connect connected', icon: 'checkmark-circle' };
      case 'available':
        return { color: '#F59E0B', text: 'Health Connect available — tap refresh to enable', icon: 'warning' };
      case 'checking':
        return { color: '#6366F1', text: 'Checking Health Connect...', icon: 'hourglass' };
      default:
        return { color: '#6B7280', text: 'Health Connect not available', icon: 'cloud-offline' };
    }
  };

  const status = getStatusInfo();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>{greeting}</Text>
          <Text style={styles.title}>FitSync</Text>
        </View>
        <TouchableOpacity style={styles.refreshBtn} onPress={refreshData}>
          <Ionicons name="refresh" size={22} color="#6366F1" />
        </TouchableOpacity>
      </View>

      {/* Status */}
      <TouchableOpacity style={styles.statusBar} onPress={hcStatus === 'available' ? refreshData : undefined}>
        <Ionicons name={status.icon} size={16} color={status.color} />
        <Text style={[styles.statusText, { color: status.color }]}>{status.text}</Text>
      </TouchableOpacity>

      {/* Rings */}
      <View style={styles.ringsCard}>
        <View style={styles.ringsRow}>
          <CircularProgress value={hcData.steps} max={10000} color="#10B981" label="Steps" size={90} strokeWidth={8} />
          <CircularProgress value={hcData.caloriesBurned} max={2500} color="#EC4899" label="kcal" size={90} strokeWidth={8} />
          <View style={styles.weightRing}>
            <Text style={styles.weightValue}>{hcData.weightKg}</Text>
            <Text style={styles.weightUnit}>kg</Text>
            <Text style={styles.weightLabel}>Weight</Text>
          </View>
        </View>
      </View>

      {/* Today's Summary */}
      <View style={styles.summaryCard}>
        <View style={styles.summaryRow}>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryValue}>{hcData.steps.toLocaleString()}</Text>
            <Text style={styles.summaryLabel}>Steps</Text>
          </View>
          <View style={styles.summaryDivider} />
          <View style={styles.summaryItem}>
            <Text style={styles.summaryValue}>{hcData.caloriesBurned.toLocaleString()}</Text>
            <Text style={styles.summaryLabel}>Calories Burned</Text>
          </View>
          <View style={styles.summaryDivider} />
          <View style={styles.summaryItem}>
            <Text style={styles.summaryValue}>{hcData.weightKg}</Text>
            <Text style={styles.summaryLabel}>Weight (kg)</Text>
          </View>
        </View>
      </View>

      {/* Quick Actions */}
      <Text style={styles.sectionTitle}>Quick Actions</Text>
      <View style={styles.quickActions}>
        <TouchableOpacity style={styles.quickAction} onPress={() => navigation.navigate('Food')}>
          <View style={[styles.quickActionIcon, { backgroundColor: '#6366F120' }]}>
            <Ionicons name="restaurant" size={24} color="#6366F1" />
          </View>
          <Text style={styles.quickActionText}>Log Food</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickAction} onPress={() => navigation.navigate('Workout')}>
          <View style={[styles.quickActionIcon, { backgroundColor: '#10B98120' }]}>
            <Ionicons name="fitness" size={24} color="#10B981" />
          </View>
          <Text style={styles.quickActionText}>Workout</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickAction} onPress={() => navigation.navigate('Progress')}>
          <View style={[styles.quickActionIcon, { backgroundColor: '#F59E0B20' }]}>
            <Ionicons name="trending-up" size={24} color="#F59E0B" />
          </View>
          <Text style={styles.quickActionText}>Progress</Text>
        </TouchableOpacity>
      </View>

      {/* Today's Workout */}
      <Text style={styles.sectionTitle}>Today's Workout</Text>
      <TouchableOpacity style={styles.workoutCard} onPress={() => navigation.navigate('Workout')}>
        <View style={styles.workoutIcon}>
          <Ionicons name="football" size={28} color="#10B981" />
        </View>
        <View style={styles.workoutInfo}>
          <Text style={styles.workoutName}>Volleyball Day</Text>
          <Text style={styles.workoutFocus}>Dynamic Warm-Up + Power</Text>
        </View>
        <Ionicons name="chevron-forward" size={22} color="#6B7280" />
      </TouchableOpacity>

      {/* Spacer for tab bar */}
      <View style={{ height: 100 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  centered: { justifyContent: 'center', alignItems: 'center' },
  loadingText: { color: '#9CA3AF', fontSize: 16, marginTop: 16 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingTop: 16, paddingBottom: 8 },
  greeting: { fontSize: 14, color: '#9CA3AF' },
  title: { fontSize: 32, fontWeight: '800', color: '#F9FAFB' },
  refreshBtn: { width: 44, height: 44, borderRadius: 22, backgroundColor: '#1F2937', justifyContent: 'center', alignItems: 'center' },
  statusBar: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, marginBottom: 12, gap: 8 },
  statusText: { fontSize: 13 },
  ringsCard: { backgroundColor: '#1F2937', borderRadius: 20, padding: 20, marginHorizontal: 16, marginBottom: 16 },
  ringsRow: { flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center' },
  circleValue: { fontSize: 18, fontWeight: '800', color: '#F9FAFB' },
  circleLabel: { fontSize: 11, color: '#9CA3AF', marginTop: 2 },
  weightRing: { width: 90, height: 90, borderRadius: 45, border: '8px solid #374151', justifyContent: 'center', alignItems: 'center' },
  weightValue: { fontSize: 22, fontWeight: '800', color: '#F9FAFB' },
  weightUnit: { fontSize: 12, color: '#6B7280' },
  weightLabel: { fontSize: 10, color: '#9CA3AF', marginTop: 2 },
  summaryCard: { backgroundColor: '#1F2937', borderRadius: 20, padding: 20, marginHorizontal: 16, marginBottom: 20 },
  summaryRow: { flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center' },
  summaryItem: { alignItems: 'center' },
  summaryValue: { fontSize: 24, fontWeight: '800', color: '#F9FAFB' },
  summaryLabel: { fontSize: 12, color: '#9CA3AF', marginTop: 4 },
  summaryDivider: { width: 1, height: 50, backgroundColor: '#374151' },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#F9FAFB', marginHorizontal: 16, marginBottom: 12, marginTop: 8 },
  quickActions: { flexDirection: 'row', paddingHorizontal: 16, gap: 12, marginBottom: 16 },
  quickAction: { flex: 1, backgroundColor: '#1F2937', borderRadius: 16, padding: 16, alignItems: 'center', gap: 8 },
  quickActionIcon: { width: 48, height: 48, borderRadius: 14, justifyContent: 'center', alignItems: 'center' },
  quickActionText: { fontSize: 13, fontWeight: '600', color: '#F9FAFB' },
  workoutCard: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1F2937', marginHorizontal: 16, borderRadius: 16, padding: 16, gap: 14 },
  workoutIcon: { width: 52, height: 52, borderRadius: 14, backgroundColor: '#10B98120', justifyContent: 'center', alignItems: 'center' },
  workoutInfo: { flex: 1 },
  workoutName: { fontSize: 16, fontWeight: '700', color: '#F9FAFB' },
  workoutFocus: { fontSize: 13, color: '#9CA3AF', marginTop: 2 },
  metricCard: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1F2937', borderRadius: 14, padding: 14, gap: 12 },
  metricIcon: { width: 40, height: 40, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  metricInfo: {},
  metricValue: { fontSize: 18, fontWeight: '700', color: '#F9FAFB' },
  metricUnit: { fontSize: 13, color: '#6B7280' },
  metricLabel: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
});