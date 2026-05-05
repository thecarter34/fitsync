import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Dimensions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

// Mock weight history - in production from Garmin API
const weightHistory = [
  { date: '2026-04-19', weight: 183.2 },
  { date: '2026-04-20', weight: 182.8 },
  { date: '2026-04-21', weight: 183.5 },
  { date: '2026-04-22', weight: 182.1 },
  { date: '2026-04-23', weight: 181.4 },
  { date: '2026-04-24', weight: 180.9 },
  { date: '2026-04-25', weight: 180.4 },
];

const mockBodyStats = {
  currentWeight: 180.4,
  goalWeight: 175,
  startingWeight: 188,
  bmi: 25.8,
  bodyFat: 18.5,
  muscleMass: 146.8,
  water: 55,
};

const weeklyStats = {
  avgCalories: 2147,
  avgSteps: 8234,
  avgSleep: 7.2,
  workouts: 4,
};

function MiniChart({ data, color = '#6366F1' }) {
  const max = Math.max(...data.map(d => d.weight));
  const min = Math.min(...data.map(d => d.weight));
  const range = max - min || 1;
  const chartWidth = width - 80;
  const chartHeight = 100;

  return (
    <View style={styles.miniChart}>
      {data.map((d, i) => {
        const h = ((d.weight - min) / range) * chartHeight;
        const x = (i / (data.length - 1)) * chartWidth;
        return (
          <View key={i} style={{
            position: 'absolute',
            bottom: 0,
            left: x - 16,
          }}>
            <View style={{
              width: 32,
              height: Math.max(h, 4),
              backgroundColor: i === data.length - 1 ? color : color + '60',
              borderTopLeftRadius: 4,
              borderTopRightRadius: 4,
            }} />
          </View>
        );
      })}
    </View>
  );
}

function StatBox({ label, value, unit, icon, color }) {
  return (
    <View style={styles.statBox}>
      <View style={[styles.statIcon, { backgroundColor: color + '20' }]}>
        <Ionicons name={icon} size={18} color={color} />
      </View>
      <Text style={styles.statValue}>{value}{unit && <Text style={styles.statUnit}> {unit}</Text>}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

export default function Progress({ navigation }) {
  const [period, setPeriod] = useState('7d');

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Progress</Text>
        <View style={styles.periodToggle}>
          {['7d', '30d', '90d'].map(p => (
            <TouchableOpacity
              key={p}
              style={[styles.periodBtn, period === p && styles.periodBtnActive]}
              onPress={() => setPeriod(p)}
            >
              <Text style={[styles.periodText, period === p && styles.periodTextActive]}>{p}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Weight Card */}
      <View style={styles.weightCard}>
        <View style={styles.weightHeader}>
          <View>
            <Text style={styles.currentWeight}>{mockBodyStats.currentWeight}</Text>
            <Text style={styles.weightUnit}>lbs current</Text>
          </View>
          <View style={styles.weightGoal}>
            <Text style={styles.goalLabel}>Goal</Text>
            <Text style={styles.goalValue}>{mockBodyStats.goalWeight} lbs</Text>
          </View>
        </View>

        <MiniChart data={weightHistory} color="#6366F1" />

        <View style={styles.weightMeta}>
          <View style={styles.metaItem}>
            <Ionicons name="trending-down" size={16} color="#10B981" />
            <Text style={styles.metaText}>-{weightHistory[0].weight - weightHistory[weightHistory.length - 1].weight} lbs</Text>
          </View>
          <Text style={styles.metaDate}>from {weightHistory[0].date}</Text>
        </View>
      </View>

      {/* Body Composition */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Body Composition</Text>
        <Text style={styles.cardSubtitle}>Synced from Garmin</Text>
        <View style={styles.statsGrid}>
          <StatBox label="BMI" value={mockBodyStats.bmi} icon="body" color="#6366F1" />
          <StatBox label="Body Fat" value={mockBodyStats.bodyFat} unit="%" icon="water" color="#F59E0B" />
          <StatBox label="Muscle" value={mockBodyStats.muscleMass} unit="lbs" icon="barbell" color="#EF4444" />
          <StatBox label="Water" value={mockBodyStats.water} unit="%" icon="drop" color="#06B6D4" />
        </View>
      </View>

      {/* Weekly Summary */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>This Week</Text>
        <View style={styles.weeklyGrid}>
          <View style={styles.weeklyItem}>
            <Ionicons name="flame" size={24} color="#EF4444" />
            <Text style={styles.weeklyValue}>{weeklyStats.avgCalories.toLocaleString()}</Text>
            <Text style={styles.weeklyLabel}>avg kcal burned</Text>
          </View>
          <View style={styles.weeklyItem}>
            <Ionicons name="footsteps" size={24} color="#3B82F6" />
            <Text style={styles.weeklyValue}>{weeklyStats.avgSteps.toLocaleString()}</Text>
            <Text style={styles.weeklyLabel}>avg steps/day</Text>
          </View>
          <View style={styles.weeklyItem}>
            <Ionicons name="moon" size={24} color="#8B5CF6" />
            <Text style={styles.weeklyValue}>{weeklyStats.avgSleep}h</Text>
            <Text style={styles.weeklyLabel}>avg sleep</Text>
          </View>
          <View style={styles.weeklyItem}>
            <Ionicons name="barbell" size={24} color="#10B981" />
            <Text style={styles.weeklyValue}>{weeklyStats.workouts}</Text>
            <Text style={styles.weeklyLabel}>workouts</Text>
          </View>
        </View>
      </View>

      {/* Starting Point */}
      <View style={styles.startingCard}>
        <View style={styles.startingInfo}>
          <Text style={styles.startingLabel}>From starting weight</Text>
          <Text style={styles.startingValue}>{mockBodyStats.startingWeight} lbs</Text>
        </View>
        <View style={styles.startingArrow}>
          <Ionicons name="arrow-forward" size={20} color="#6366F1" />
        </View>
        <View style={styles.startingInfo}>
          <Text style={styles.startingLabel}>Total lost</Text>
          <Text style={[styles.startingValue, { color: '#10B981' }]}>{mockBodyStats.startingWeight - mockBodyStats.currentWeight} lbs</Text>
        </View>
      </View>
    </ScrollView>
  );
}

import { TouchableOpacity } from 'react-native';

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  content: { padding: 16, paddingBottom: 100 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  title: { fontSize: 28, fontWeight: '700', color: '#F9FAFB' },
  periodToggle: { flexDirection: 'row', backgroundColor: '#1F2937', borderRadius: 12, padding: 4 },
  periodBtn: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 8 },
  periodBtnActive: { backgroundColor: '#6366F1' },
  periodText: { fontSize: 13, fontWeight: '600', color: '#9CA3AF' },
  periodTextActive: { color: '#fff' },
  weightCard: { backgroundColor: '#1F2937', borderRadius: 20, padding: 20, marginBottom: 16 },
  weightHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20 },
  currentWeight: { fontSize: 48, fontWeight: '800', color: '#F9FAFB' },
  weightUnit: { fontSize: 14, color: '#9CA3AF' },
  weightGoal: { alignItems: 'flex-end' },
  goalLabel: { fontSize: 12, color: '#6B7280' },
  goalValue: { fontSize: 18, fontWeight: '700', color: '#6366F1' },
  miniChart: { height: 100, backgroundColor: '#111827', borderRadius: 12, marginBottom: 12, position: 'relative', overflow: 'hidden' },
  weightMeta: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  metaItem: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  metaText: { fontSize: 14, fontWeight: '600', color: '#10B981' },
  metaDate: { fontSize: 13, color: '#6B7280' },
  card: { backgroundColor: '#1F2937', borderRadius: 20, padding: 20, marginBottom: 16 },
  cardTitle: { fontSize: 18, fontWeight: '700', color: '#F9FAFB', marginBottom: 4 },
  cardSubtitle: { fontSize: 13, color: '#6B7280', marginBottom: 16 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  statBox: { backgroundColor: '#111827', borderRadius: 14, padding: 14, width: (width - 72) / 2, alignItems: 'center' },
  statIcon: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center', marginBottom: 8 },
  statValue: { fontSize: 20, fontWeight: '800', color: '#F9FAFB' },
  statUnit: { fontSize: 13, color: '#9CA3AF' },
  statLabel: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  weeklyGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 16, marginTop: 8 },
  weeklyItem: { alignItems: 'center', width: (width - 72) / 2 },
  weeklyValue: { fontSize: 22, fontWeight: '800', color: '#F9FAFB', marginTop: 8 },
  weeklyLabel: { fontSize: 12, color: '#9CA3AF', marginTop: 4 },
  startingCard: { backgroundColor: '#1F2937', borderRadius: 16, padding: 16, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 },
  startingInfo: { alignItems: 'center' },
  startingLabel: { fontSize: 12, color: '#6B7280', marginBottom: 4 },
  startingValue: { fontSize: 20, fontWeight: '800', color: '#F9FAFB' },
  startingArrow: { paddingHorizontal: 16 },
});