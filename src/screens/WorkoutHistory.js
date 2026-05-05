import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { getWorkoutHistory, deleteWorkoutSession } from '../utils/storage';

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

export default function WorkoutHistory({ navigation }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    const data = await getWorkoutHistory();
    setHistory(data);
    setLoading(false);
  };

  const handleDelete = (session) => {
    Alert.alert(
      'Delete Workout',
      `Delete "${session.label}" from ${new Date(session.completedAt).toLocaleDateString()}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            await deleteWorkoutSession(session.id);
            setHistory(prev => prev.filter(s => s.id !== session.id));
          },
        },
      ]
    );
  };

  const getDayName = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { weekday: 'short' });
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color="#6366F1" />
          <Text style={styles.backBtnText}>Back</Text>
        </TouchableOpacity>
        <Text style={styles.screenTitle}>Workout History</Text>
        <View style={{ width: 60 }} />
      </View>

      {loading ? (
        <Text style={styles.emptyText}>Loading...</Text>
      ) : history.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="barbell-outline" size={48} color="#374151" />
          <Text style={styles.emptyTitle}>No workouts yet</Text>
          <Text style={styles.emptySubtitle}>Complete a workout to see it here</Text>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.listContainer}>
          {history.map((session, index) => (
            <View key={session.id} style={styles.sessionCard}>
              <View style={styles.sessionHeader}>
                <View>
                  <Text style={styles.sessionLabel}>{session.label}</Text>
                  <Text style={styles.sessionDate}>
                    {new Date(session.completedAt).toLocaleDateString('en-US', { 
                      weekday: 'long', month: 'short', day: 'numeric' 
                    })}
                  </Text>
                </View>
                <TouchableOpacity
                  style={styles.deleteBtn}
                  onPress={() => handleDelete(session)}
                >
                  <Ionicons name="trash-outline" size={18} color="#EF4444" />
                </TouchableOpacity>
              </View>

              <View style={styles.sessionStats}>
                <View style={styles.statItem}>
                  <Ionicons name="time-outline" size={16} color="#6366F1" />
                  <Text style={styles.statValue}>{formatTime(session.durationSeconds)}</Text>
                  <Text style={styles.statLabel}>duration</Text>
                </View>
                <View style={styles.statItem}>
                  <Ionicons name="fitness-outline" size={16} color="#6366F1" />
                  <Text style={styles.statValue}>{session.exercises?.length || 0}</Text>
                  <Text style={styles.statLabel}>exercises</Text>
                </View>
                <View style={styles.statItem}>
                  <Ionicons name="checkmark-circle-outline" size={16} color="#6366F1" />
                  <Text style={styles.statValue}>
                    {session.exercises?.reduce((sum, ex) => sum + (ex.setsCompleted || 0), 0) || 0}
                  </Text>
                  <Text style={styles.statLabel}>sets</Text>
                </View>
              </View>

              {session.exercises?.length > 0 && (
                <View style={styles.exerciseSummary}>
                  {session.exercises.slice(0, 3).map((ex, i) => (
                    <Text key={i} style={styles.exerciseSummaryText}>
                      {ex.name} {ex.setsCompleted ? `(${ex.setsCompleted} sets)` : ''}
                    </Text>
                  ))}
                  {session.exercises.length > 3 && (
                    <Text style={styles.moreExercises}>+ {session.exercises.length - 3} more</Text>
                  )}
                </View>
              )}
            </View>
          ))}
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: '#1F2937' },
  backBtn: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  backBtnText: { color: '#6366F1', fontSize: 16, fontWeight: '600' },
  screenTitle: { fontSize: 20, fontWeight: '800', color: '#F9FAFB' },
  listContainer: { padding: 16, paddingBottom: 40 },
  sessionCard: { backgroundColor: '#1F2937', borderRadius: 16, padding: 16, marginBottom: 12 },
  sessionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 },
  sessionLabel: { fontSize: 18, fontWeight: '700', color: '#F9FAFB' },
  sessionDate: { fontSize: 13, color: '#9CA3AF', marginTop: 2 },
  deleteBtn: { padding: 4 },
  sessionStats: { flexDirection: 'row', gap: 20, marginBottom: 12 },
  statItem: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  statValue: { fontSize: 15, fontWeight: '700', color: '#F9FAFB' },
  statLabel: { fontSize: 12, color: '#6B7280' },
  exerciseSummary: { borderTopWidth: 1, borderTopColor: '#111827', paddingTop: 10 },
  exerciseSummaryText: { fontSize: 12, color: '#9CA3AF', marginBottom: 2 },
  moreExercises: { fontSize: 12, color: '#6366F1', marginTop: 2 },
  emptyContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingBottom: 80 },
  emptyTitle: { fontSize: 20, fontWeight: '700', color: '#F9FAFB', marginTop: 16 },
  emptySubtitle: { fontSize: 14, color: '#6B7280', marginTop: 8 },
  emptyText: { color: '#9CA3AF', textAlign: 'center', marginTop: 60 },
});