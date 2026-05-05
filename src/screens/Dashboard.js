import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Dimensions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

// Mock Garmin data - in production this comes from Garmin Connect API
const mockGarminData = {
  caloriesBurned: 2147,
  steps: 8432,
  activeMinutes: 47,
  weight: 180.4,
  bmi: 25.8,
  heartRate: { resting: 58, avg: 72, max: 145 },
};

const mockNutrition = {
  consumed: 1450,
  target: 2200,
  protein: { current: 98, target: 180 },
  carbs: { current: 145, target: 220 },
  fat: { current: 52, target: 73 },
  fiber: { current: 18, target: 35 },
  water: { current: 4, target: 8 },
};

function CircularProgress({ value, max, size = 120, strokeWidth = 12, color = '#6366F1', label, sublabel }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.min(value / max, 1);
  const dashOffset = circumference * (1 - progress);

  return (
    <View style={{ alignItems: 'center' }}>
      <View style={{ width: size, height: size, position: 'relative' }}>
        <View style={{
          width: size, height: size, borderRadius: size / 2,
          border: `${strokeWidth}px solid #374151`, position: 'absolute',
        }} />
        <View style={{
          width: size, height: size, borderRadius: size / 2,
          border: `${strokeWidth}px solid transparent`,
          borderTopColor: color, borderRightColor: progress > 0.25 ? color : 'transparent',
          borderBottomColor: progress > 0.5 ? color : 'transparent',
          borderLeftColor: progress > 0.75 ? color : 'transparent',
          position: 'absolute', transform: [{ rotate: '-90deg' }],
        }} />
        <View style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, justifyContent: 'center', alignItems: 'center' }}>
          <Text style={styles.circleValue}>{value}</Text>
          <Text style={styles.circleLabel}>{label}</Text>
        </View>
      </View>
      {sublabel && <Text style={styles.circleSublabel}>{sublabel}</Text>}
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

function MacroBar({ label, current, target, color }) {
  const pct = Math.min((current / target) * 100, 100);
  return (
    <View style={styles.macroRow}>
      <Text style={styles.macroLabel}>{label}</Text>
      <View style={styles.macroBarBg}>
        <View style={[styles.macroBarFill, { width: `${pct}%`, backgroundColor: color }]} />
      </View>
      <Text style={styles.macroValues}>{current}g / {target}g</Text>
    </View>
  );
}

export default function Dashboard({ navigation }) {
  const [garminData] = useState(mockGarminData);
  const [nutrition] = useState(mockNutrition);
  const [greeting, setGreeting] = useState('');

  useEffect(() => {
    const hr = new Date().getHours();
    if (hr < 12) setGreeting('Good morning');
    else if (hr < 17) setGreeting('Good afternoon');
    else setGreeting('Good evening');
  }, []);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>{greeting}</Text>
          <Text style={styles.date}>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</Text>
        </View>
        <TouchableOpacity style={styles.syncBadge} onPress={() => navigation.navigate('Settings')}>
          <Ionicons name="bluetooth" size={16} color="#6366F1" />
          <Text style={styles.syncText}>Garmin</Text>
        </TouchableOpacity>
      </View>

      {/* Calorie Ring */}
      <View style={styles.calorieCard}>
        <View style={styles.calorieHeader}>
          <Text style={styles.cardTitle}>Today's Fuel</Text>
          <Text style={styles.calorieTarget}>Target: {nutrition.target} kcal</Text>
        </View>
        <View style={styles.calorieRing}>
          <CircularProgress
            value={nutrition.consumed}
            max={nutrition.target}
            size={160}
            strokeWidth={14}
            color="#6366F1"
            label="kcal"
          />
          <View style={styles.calorieStats}>
            <View style={styles.calorieStat}>
              <Text style={styles.calorieStatValue}>{nutrition.consumed}</Text>
              <Text style={styles.calorieStatLabel}>eaten</Text>
            </View>
            <View style={styles.calorieDivider} />
            <View style={styles.calorieStat}>
              <Text style={[styles.calorieStatValue, { color: '#10B981' }]}>{nutrition.consumed < nutrition.target ? nutrition.target - nutrition.consumed : 0}</Text>
              <Text style={styles.calorieStatLabel}>remaining</Text>
            </View>
            <View style={styles.calorieDivider} />
            <View style={styles.calorieStat}>
              <Text style={[styles.calorieStatValue, { color: '#F59E0B' }]}>{garminData.caloriesBurned}</Text>
              <Text style={styles.calorieStatLabel}>burned</Text>
            </View>
          </View>
        </View>
      </View>

      {/* Macros */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Macros</Text>
        <MacroBar label="Protein" current={nutrition.protein.current} target={nutrition.protein.target} color="#EF4444" />
        <MacroBar label="Carbs" current={nutrition.carbs.current} target={nutrition.carbs.target} color="#3B82F6" />
        <MacroBar label="Fat" current={nutrition.fat.current} target={nutrition.fat.target} color="#F59E0B" />
        <MacroBar label="Fiber" current={nutrition.fiber.current} target={nutrition.fiber.target} color="#10B981" />
      </View>

      {/* Garmin Stats */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>Garmin Data</Text>
          <Ionicons name="watch" size={20} color="#6366F1" />
        </View>
        <View style={styles.metricsGrid}>
          <MetricCard icon="flame" label="Burned" value={garminData.caloriesBurned} unit="kcal" color="#EF4444" />
          <MetricCard icon="footsteps" label="Steps" value={garminData.steps.toLocaleString()} color="#3B82F6" />
          <MetricCard icon="timer" label="Active" value={garminData.activeMinutes} unit="min" color="#10B981" />
          <MetricCard icon="heart" label="Resting HR" value={garminData.heartRate.resting} unit="bpm" color="#EC4899" />
        </View>
      </View>

      {/* Water */}
      <TouchableOpacity style={styles.waterCard} onPress={() => {}}>
        <View style={styles.waterLeft}>
          <Ionicons name="water" size={28} color="#06B6D4" />
          <View style={styles.waterInfo}>
            <Text style={styles.waterTitle}>Water</Text>
            <Text style={styles.waterSubtitle}>{nutrition.water.current} of {nutrition.water.target} glasses</Text>
          </View>
        </View>
        <View style={styles.waterButtons}>
          <TouchableOpacity style={styles.waterBtn}>
            <Ionicons name="remove" size={20} color="#9CA3AF" />
          </TouchableOpacity>
          <Text style={styles.waterCount}>{nutrition.water.current}</Text>
          <TouchableOpacity style={styles.waterBtn}>
            <Ionicons name="add" size={20} color="#06B6D4" />
          </TouchableOpacity>
        </View>
      </TouchableOpacity>

      {/* Quick Add */}
      <TouchableOpacity style={styles.quickAddBtn} onPress={() => navigation.navigate('Food')}>
        <Ionicons name="add-circle" size={22} color="#fff" />
        <Text style={styles.quickAddText}>Log Food</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  content: { padding: 16, paddingBottom: 100 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
  greeting: { fontSize: 28, fontWeight: '700', color: '#F9FAFB' },
  date: { fontSize: 14, color: '#9CA3AF', marginTop: 2 },
  syncBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1F2937', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, gap: 6 },
  syncText: { color: '#6366F1', fontSize: 13, fontWeight: '600' },
  calorieCard: { backgroundColor: '#1F2937', borderRadius: 20, padding: 20, marginBottom: 16 },
  calorieHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 16 },
  calorieTarget: { color: '#9CA3AF', fontSize: 13 },
  cardTitle: { fontSize: 17, fontWeight: '700', color: '#F9FAFB', marginBottom: 4 },
  calorieRing: { alignItems: 'center', gap: 20 },
  circleValue: { fontSize: 32, fontWeight: '800', color: '#F9FAFB' },
  circleLabel: { fontSize: 13, color: '#9CA3AF', marginTop: 2 },
  circleSublabel: { fontSize: 12, color: '#6B7280', marginTop: 4 },
  calorieStats: { flexDirection: 'row', gap: 16 },
  calorieStat: { alignItems: 'center' },
  calorieStatValue: { fontSize: 20, fontWeight: '700', color: '#F9FAFB' },
  calorieStatLabel: { fontSize: 11, color: '#9CA3AF', marginTop: 2 },
  calorieDivider: { width: 1, height: 36, backgroundColor: '#374151' },
  card: { backgroundColor: '#1F2937', borderRadius: 20, padding: 20, marginBottom: 16 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  metricsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  metricCard: { backgroundColor: '#111827', borderRadius: 14, padding: 14, flexDirection: 'row', alignItems: 'center', gap: 12, width: (width - 64) / 2 },
  metricIcon: { width: 40, height: 40, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  metricInfo: {},
  metricValue: { fontSize: 17, fontWeight: '700', color: '#F9FAFB' },
  metricUnit: { fontSize: 13, color: '#9CA3AF' },
  metricLabel: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  macroRow: { marginBottom: 14 },
  macroLabel: { fontSize: 13, fontWeight: '600', color: '#D1D5DB', marginBottom: 6 },
  macroBarBg: { height: 8, backgroundColor: '#374151', borderRadius: 4, overflow: 'hidden' },
  macroBarFill: { height: '100%', borderRadius: 4 },
  macroValues: { fontSize: 11, color: '#6B7280', marginTop: 4 },
  waterCard: { backgroundColor: '#1F2937', borderRadius: 20, padding: 18, marginBottom: 16, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  waterLeft: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  waterInfo: {},
  waterTitle: { fontSize: 16, fontWeight: '700', color: '#F9FAFB' },
  waterSubtitle: { fontSize: 13, color: '#9CA3AF', marginTop: 2 },
  waterButtons: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  waterBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: '#374151', justifyContent: 'center', alignItems: 'center' },
  waterCount: { fontSize: 24, fontWeight: '800', color: '#06B6D4', minWidth: 30, textAlign: 'center' },
  quickAddBtn: { backgroundColor: '#6366F1', borderRadius: 16, padding: 16, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 10, marginBottom: 16 },
  quickAddText: { color: '#fff', fontSize: 16, fontWeight: '700' },
});