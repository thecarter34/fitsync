import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  Modal, TextInput, Alert, FlatList
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { getExercises, saveExercises, INITIAL_WORKOUTS } from '../utils/exercises';

const DAY_ORDER = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

const DAY_LABELS = {
  monday: 'Monday — Power Day',
  tuesday: 'Tuesday — Active Recovery',
  wednesday: 'Wednesday — Golf',
  thursday: 'Thursday — Rest',
  friday: 'Friday — Pump Day',
  saturday: 'Saturday — Metabolic',
  sunday: 'Sunday — Rest',
};

const MUSCLE_GROUPS = [
  'Shoulders', 'Chest', 'Back', 'Lats', 'Biceps', 'Triceps',
  'Posterior Chain', 'Quads/Glutes', 'Glutes/Hams', 'Core',
  'Full Body', 'Calves', 'Forearms', 'Rear Delts', 'Side Delts', 'Upper Chest',
];

const COMMON_EXERCISES = [
  { name: 'Strict Barbell OHP', muscle: 'Shoulders' },
  { name: 'RDLs', muscle: 'Posterior Chain' },
  { name: 'DB Bulgarian Split Squats', muscle: 'Quads/Glutes' },
  { name: 'SA DB Bent-Over Rows', muscle: 'Back' },
  { name: 'KB Swings', muscle: 'Glutes/Hams' },
  { name: 'Pallof Press', muscle: 'Core' },
  { name: 'Lat Pull-Downs', muscle: 'Lats' },
  { name: 'Smith Machine Bent-Over Rows', muscle: 'Back' },
  { name: 'Incline DB Bench', muscle: 'Upper Chest' },
  { name: 'DB Lateral Raises', muscle: 'Side Delts' },
  { name: 'Cable Flies', muscle: 'Chest' },
  { name: 'Incline DB Press', muscle: 'Upper Chest' },
  { name: 'Lean-Away Lateral Raises', muscle: 'Side Delts' },
  { name: 'Strict OHP', muscle: 'Shoulders' },
  { name: 'High Cable Flyes', muscle: 'Upper Chest' },
  { name: 'Face Pulls', muscle: 'Rear Delts' },
  { name: 'Air Bike Tabata', muscle: 'Full Body' },
  { name: 'Box Jumps / Step-Ups', muscle: 'Quads/Glutes' },
  { name: 'Wall Balls', muscle: 'Full Body' },
  { name: 'Jump Rope Intervals', muscle: 'Calves' },
  { name: 'Shrugs', muscle: 'Shoulders' },
  { name: 'Rope Crush Curls', muscle: 'Biceps' },
  { name: 'Reverse Flyes', muscle: 'Rear Delts' },
];

function AddExerciseModal({ visible, onClose, onAdd }) {
  const [name, setName] = useState('');
  const [muscle, setMuscle] = useState('');
  const [sets, setSets] = useState('3');
  const [reps, setReps] = useState('8');
  const [weight, setWeight] = useState('');
  const [rest, setRest] = useState('60 sec');

  const handleAdd = () => {
    if (!name.trim() || !muscle) {
      Alert.alert('Missing Info', 'Please enter exercise name and muscle group.');
      return;
    }
    onAdd({
      name: name.trim(),
      muscle,
      sets: parseInt(sets) || 3,
      reps: reps,
      weight: parseInt(weight) || 0,
      rest: rest || '60 sec',
    });
    setName('');
    setMuscle('');
    setSets('3');
    setReps('8');
    setWeight('');
    setRest('60 sec');
    onClose();
  };

  return (
    <Modal animationType="slide" transparent={true} visible={visible} onRequestClose={onClose}>
      <View style={styles.modalOverlay}>
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Add Exercise</Text>
            <TouchableOpacity onPress={onClose}>
              <Ionicons name="close" size={24} color="#9CA3AF" />
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalScroll}>
            <Text style={styles.inputLabel}>Exercise Name</Text>
            <TextInput
              style={styles.textInput}
              value={name}
              onChangeText={setName}
              placeholder="e.g. Incline DB Press"
              placeholderTextColor="#6B7280"
            />

            <Text style={styles.inputLabel}>Muscle Group</Text>
            <View style={styles.muscleSelector}>
              {MUSCLE_GROUPS.map(m => (
                <TouchableOpacity
                  key={m}
                  style={[styles.muscleChip, muscle === m && styles.muscleChipSelected]}
                  onPress={() => setMuscle(m)}
                >
                  <Text style={[styles.muscleChipText, muscle === m && styles.muscleChipTextSelected]}>{m}</Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.rowInputs}>
              <View style={styles.halfInput}>
                <Text style={styles.inputLabel}>Sets</Text>
                <TextInput
                  style={styles.textInput}
                  value={sets}
                  onChangeText={setSets}
                  keyboardType="numeric"
                  placeholder="3"
                  placeholderTextColor="#6B7280"
                />
              </View>
              <View style={styles.halfInput}>
                <Text style={styles.inputLabel}>Reps</Text>
                <TextInput
                  style={styles.textInput}
                  value={reps}
                  onChangeText={setReps}
                  placeholder="8"
                  placeholderTextColor="#6B7280"
                />
              </View>
            </View>

            <View style={styles.rowInputs}>
              <View style={styles.halfInput}>
                <Text style={styles.inputLabel}>Weight (lb)</Text>
                <TextInput
                  style={styles.textInput}
                  value={weight}
                  onChangeText={setWeight}
                  keyboardType="numeric"
                  placeholder="135"
                  placeholderTextColor="#6B7280"
                />
              </View>
              <View style={styles.halfInput}>
                <Text style={styles.inputLabel}>Rest</Text>
                <TextInput
                  style={styles.textInput}
                  value={rest}
                  onChangeText={setRest}
                  placeholder="60 sec"
                  placeholderTextColor="#6B7280"
                />
              </View>
            </View>

            <Text style={styles.inputLabel}>Quick Add Common Exercises</Text>
            <View style={styles.quickAddGrid}>
              {COMMON_EXERCISES.slice(0, 10).map((ex, i) => (
                <TouchableOpacity
                  key={i}
                  style={styles.quickAddBtn}
                  onPress={() => {
                    setName(ex.name);
                    setMuscle(ex.muscle);
                  }}
                >
                  <Text style={styles.quickAddText}>{ex.name}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </ScrollView>

          <TouchableOpacity style={styles.addBtn} onPress={handleAdd}>
            <Ionicons name="add" size={20} color="#fff" />
            <Text style={styles.addBtnText}>Add Exercise</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

function EditExerciseModal({ visible, exercise, onClose, onSave }) {
  const [name, setName] = useState(exercise?.name || '');
  const [muscle, setMuscle] = useState(exercise?.muscle || '');
  const [sets, setSets] = useState(exercise?.sets?.toString() || '3');
  const [reps, setReps] = useState(exercise?.reps?.toString() || '8');
  const [weight, setWeight] = useState(exercise?.weight?.toString() || '');
  const [rest, setRest] = useState(exercise?.rest || '60 sec');

  useEffect(() => {
    if (exercise) {
      setName(exercise.name || '');
      setMuscle(exercise.muscle || '');
      setSets(exercise.sets?.toString() || '3');
      setReps(exercise.reps?.toString() || '8');
      setWeight(exercise.weight?.toString() || '');
      setRest(exercise.rest || '60 sec');
    }
  }, [exercise]);

  const handleSave = () => {
    if (!name.trim() || !muscle) {
      Alert.alert('Missing Info', 'Please enter exercise name and muscle group.');
      return;
    }
    onSave({
      ...exercise,
      name: name.trim(),
      muscle,
      sets: parseInt(sets) || 3,
      reps: reps,
      weight: parseInt(weight) || 0,
      rest: rest || '60 sec',
    });
    onClose();
  };

  return (
    <Modal animationType="slide" transparent={true} visible={visible} onRequestClose={onClose}>
      <View style={styles.modalOverlay}>
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Edit Exercise</Text>
            <TouchableOpacity onPress={onClose}>
              <Ionicons name="close" size={24} color="#9CA3AF" />
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalScroll}>
            <Text style={styles.inputLabel}>Exercise Name</Text>
            <TextInput
              style={styles.textInput}
              value={name}
              onChangeText={setName}
              placeholder="e.g. Incline DB Press"
              placeholderTextColor="#6B7280"
            />

            <Text style={styles.inputLabel}>Muscle Group</Text>
            <View style={styles.muscleSelector}>
              {MUSCLE_GROUPS.map(m => (
                <TouchableOpacity
                  key={m}
                  style={[styles.muscleChip, muscle === m && styles.muscleChipSelected]}
                  onPress={() => setMuscle(m)}
                >
                  <Text style={[styles.muscleChipText, muscle === m && styles.muscleChipTextSelected]}>{m}</Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.rowInputs}>
              <View style={styles.halfInput}>
                <Text style={styles.inputLabel}>Sets</Text>
                <TextInput
                  style={styles.textInput}
                  value={sets}
                  onChangeText={setSets}
                  keyboardType="numeric"
                  placeholder="3"
                  placeholderTextColor="#6B7280"
                />
              </View>
              <View style={styles.halfInput}>
                <Text style={styles.inputLabel}>Reps</Text>
                <TextInput
                  style={styles.textInput}
                  value={reps}
                  onChangeText={setReps}
                  placeholder="8"
                  placeholderTextColor="#6B7280"
                />
              </View>
            </View>

            <View style={styles.rowInputs}>
              <View style={styles.halfInput}>
                <Text style={styles.inputLabel}>Weight (lb)</Text>
                <TextInput
                  style={styles.textInput}
                  value={weight}
                  onChangeText={setWeight}
                  keyboardType="numeric"
                  placeholder="135"
                  placeholderTextColor="#6B7280"
                />
              </View>
              <View style={styles.halfInput}>
                <Text style={styles.inputLabel}>Rest</Text>
                <TextInput
                  style={styles.textInput}
                  value={rest}
                  onChangeText={setRest}
                  placeholder="60 sec"
                  placeholderTextColor="#6B7280"
                />
              </View>
            </View>
          </ScrollView>

          <TouchableOpacity style={styles.saveBtn} onPress={handleSave}>
            <Ionicons name="checkmark" size={20} color="#fff" />
            <Text style={styles.saveBtnText}>Save Changes</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

export default function ProgramManager({ navigation }) {
  const [workouts, setWorkouts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [addModalDay, setAddModalDay] = useState(null);
  const [editExercise, setEditExercise] = useState(null);
  const [editingDay, setEditingDay] = useState(null);

  useEffect(() => {
    loadWorkouts();
  }, []);

  const loadWorkouts = async () => {
    let stored = await getExercises();
    if (!stored) {
      // Seed initial workouts on first load (Workout screen handles this on mobile,
      // but web may load Program first)
      await saveExercises(INITIAL_WORKOUTS);
      stored = INITIAL_WORKOUTS;
    }
    setWorkouts(stored);
    setLoading(false);
  };

  const handleAddExercise = (day, exercise) => {
    const updated = { ...workouts };
    if (!updated[day].exercises) updated[day].exercises = [];
    updated[day].exercises.push(exercise);
    setWorkouts(updated);
    saveExercises(updated);
  };

  const handleSaveExercise = (updatedExercise) => {
    const day = editingDay;
    const updated = { ...workouts };
    const exIndex = updated[day].exercises.findIndex(e => e.name === editExercise.name);
    if (exIndex >= 0) {
      updated[day].exercises[exIndex] = updatedExercise;
    }
    setWorkouts(updated);
    saveExercises(updated);
    setEditExercise(null);
    setEditingDay(null);
  };

  const handleDeleteExercise = (day, exerciseName) => {
    Alert.alert(
      'Delete Exercise',
      `Remove "${exerciseName}" from this day?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            const updated = { ...workouts };
            updated[day].exercises = updated[day].exercises.filter(e => e.name !== exerciseName);
            setWorkouts(updated);
            saveExercises(updated);
          },
        },
      ]
    );
  };

  const moveExercise = (day, index, direction) => {
    const newIndex = index + direction;
    const updated = { ...workouts };
    const exercises = [...updated[day].exercises];
    if (newIndex < 0 || newIndex >= exercises.length) return;
    const [moved] = exercises.splice(index, 1);
    exercises.splice(newIndex, 0, moved);
    updated[day].exercises = exercises;
    setWorkouts(updated);
    saveExercises(updated);
  };

  const getMuscleColor = (muscle) => {
    const map = {
      'Shoulders': '#F59E0B', 'Chest': '#EF4444', 'Back': '#3B82F6',
      'Lats': '#8B5CF6', 'Biceps': '#EC4899', 'Triceps': '#F97316',
      'Posterior Chain': '#10B981', 'Quads/Glutes': '#06B6D4', 'Glutes/Hams': '#14B8A6',
      'Core': '#6366F1', 'Full Body': '#EF4444', 'Calves': '#84CC16',
      'Forearms': '#F59E0B', 'Rear Delts': '#8B5CF6', 'Side Delts': '#EC4899',
      'Upper Chest': '#EF4444',
    };
    return map[muscle] || '#6366F1';
  };

  if (loading || !workouts) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading program...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.headerRow}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
            <Ionicons name="chevron-back" size={24} color="#6366F1" />
            <Text style={styles.backBtnText}>Back</Text>
          </TouchableOpacity>
          <Text style={styles.screenTitle}>Program Manager</Text>
          <View style={{ width: 60 }} />
        </View>

        <Text style={styles.subtitle}>Tap an exercise to edit · Swipe or tap X to remove</Text>

        {DAY_ORDER.map(dayKey => {
          const day = workouts ? workouts[dayKey] : null;
          if (!day || !day.exercises || day.exercises.length === 0) return null;

          return (
            <View key={dayKey} style={styles.daySection}>
              <View style={styles.dayHeader}>
                <View>
                  <Text style={styles.dayTitle}>{DAY_LABELS[dayKey]}</Text>
                  <Text style={styles.dayFocus}>{day.focus}</Text>
                </View>
                <TouchableOpacity
                  style={styles.addDayBtn}
                  onPress={() => setAddModalDay(dayKey)}
                >
                  <Ionicons name="add" size={20} color="#6366F1" />
                </TouchableOpacity>
              </View>

              {day.exercises.map((exercise, index) => (
                <TouchableOpacity
                  key={`${exercise.name}-${index}`}
                  style={styles.exerciseRow}
                  onPress={() => {
                    setEditExercise(exercise);
                    setEditingDay(dayKey);
                  }}
                >
                  <View style={[styles.exerciseMuscleBar, { backgroundColor: getMuscleColor(exercise.muscle) }]} />
                  <View style={styles.exerciseInfo}>
                    <Text style={styles.exerciseName}>{exercise.name}</Text>
                    <Text style={styles.exerciseMeta}>{exercise.muscle} · {exercise.sets}x{exercise.reps} · {exercise.weight}lb</Text>
                  </View>
                  <View style={styles.reorderControls}>
                    <TouchableOpacity
                      style={[styles.reorderBtn, index === 0 && styles.reorderBtnDisabled]}
                      onPress={() => moveExercise(dayKey, index, -1)}
                      disabled={index === 0}
                    >
                      <Ionicons name="chevron-up" size={18} color={index === 0 ? '#374151' : '#6366F1'} />
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[styles.reorderBtn, index === (day.exercises?.length || 0) - 1 && styles.reorderBtnDisabled]}
                      onPress={() => moveExercise(dayKey, index, 1)}
                      disabled={index === (day.exercises?.length || 0) - 1}
                    >
                      <Ionicons name="chevron-down" size={18} color={index === (day.exercises?.length || 0) - 1 ? '#374151' : '#6366F1'} />
                    </TouchableOpacity>
                  </View>
                  <TouchableOpacity
                    style={styles.deleteBtn}
                    onPress={() => handleDeleteExercise(dayKey, exercise.name)}
                  >
                    <Ionicons name="trash-outline" size={18} color="#EF4444" />
                  </TouchableOpacity>
                </TouchableOpacity>
              ))}

              {day.notes && (
                <View style={styles.dayNotes}>
                  <Ionicons name="information-circle" size={14} color="#F59E0B" />
                  <Text style={styles.dayNotesText}>{day.notes}</Text>
                </View>
              )}
            </View>
          );
        })}

        <View style={styles.emptyDays}>
          <Text style={styles.emptyDaysTitle}>Days with no exercises</Text>
          <View style={styles.emptyDaysList}>
            {DAY_ORDER.filter(d => !workouts[d]?.exercises?.length).map(d => (
              <TouchableOpacity
                key={d}
                style={styles.emptyDayPill}
                onPress={() => setAddModalDay(d)}
              >
                <Text style={styles.emptyDayPillText}>{d}</Text>
                <Ionicons name="add" size={16} color="#6366F1" />
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </ScrollView>

      {/* Add Exercise Modal */}
      <AddExerciseModal
        visible={addModalDay !== null}
        onClose={() => setAddModalDay(null)}
        onAdd={(exercise) => handleAddExercise(addModalDay, exercise)}
      />

      {/* Edit Exercise Modal */}
      <EditExerciseModal
        visible={editExercise !== null}
        exercise={editExercise}
        onClose={() => { setEditExercise(null); setEditingDay(null); }}
        onSave={handleSaveExercise}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  content: { padding: 16, paddingBottom: 40 },
  loadingText: { color: '#9CA3AF', textAlign: 'center', marginTop: 60, fontSize: 16 },
  headerRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 },
  backBtn: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  backBtnText: { color: '#6366F1', fontSize: 16, fontWeight: '600' },
  screenTitle: { fontSize: 20, fontWeight: '800', color: '#F9FAFB' },
  subtitle: { fontSize: 13, color: '#6B7280', marginBottom: 20 },
  daySection: { marginBottom: 28 },
  dayHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  dayTitle: { fontSize: 17, fontWeight: '700', color: '#F9FAFB' },
  dayFocus: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
  addDayBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: '#1F2937', justifyContent: 'center', alignItems: 'center' },
  exerciseRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1F2937', borderRadius: 14, marginBottom: 8, overflow: 'hidden' },
  exerciseMuscleBar: { width: 5, alignSelf: 'stretch' },
  exerciseInfo: { flex: 1, paddingVertical: 14, paddingHorizontal: 14 },
  exerciseName: { fontSize: 15, fontWeight: '600', color: '#F9FAFB' },
  exerciseMeta: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
  reorderControls: { flexDirection: 'row', alignItems: 'center', gap: 2 },
  reorderBtn: { padding: 6, justifyContent: 'center' },
  reorderBtnDisabled: { opacity: 0.4 },
  deleteBtn: { padding: 16, justifyContent: 'center' },
  dayNotes: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 14, paddingBottom: 8 },
  dayNotesText: { fontSize: 12, color: '#F59E0B', fontStyle: 'italic' },
  emptyDays: { marginTop: 8 },
  emptyDaysTitle: { fontSize: 14, fontWeight: '600', color: '#6B7280', marginBottom: 10 },
  emptyDaysList: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  emptyDayPill: { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: '#1F2937', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 12 },
  emptyDayPillText: { color: '#9CA3AF', fontSize: 13, fontWeight: '600', textTransform: 'capitalize' },
  // Modal styles
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.7)', justifyContent: 'flex-end' },
  modalContainer: { backgroundColor: '#1F2937', borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, maxHeight: '85%' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  modalTitle: { fontSize: 20, fontWeight: '800', color: '#F9FAFB' },
  modalScroll: { maxHeight: 400 },
  inputLabel: { fontSize: 13, fontWeight: '600', color: '#9CA3AF', marginBottom: 6, marginTop: 16 },
  textInput: { backgroundColor: '#111827', borderRadius: 12, paddingHorizontal: 16, paddingVertical: 12, fontSize: 16, color: '#F9FAFB', borderWidth: 1, borderColor: '#374151' },
  muscleSelector: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  muscleChip: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16, backgroundColor: '#111827', borderWidth: 1, borderColor: '#374151' },
  muscleChipSelected: { backgroundColor: '#6366F1', borderColor: '#6366F1' },
  muscleChipText: { fontSize: 12, color: '#9CA3AF' },
  muscleChipTextSelected: { color: '#fff', fontWeight: '600' },
  rowInputs: { flexDirection: 'row', gap: 12 },
  halfInput: { flex: 1 },
  quickAddGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 8 },
  quickAddBtn: { backgroundColor: '#111827', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 10, borderWidth: 1, borderColor: '#374151' },
  quickAddText: { fontSize: 11, color: '#9CA3AF' },
  addBtn: { backgroundColor: '#6366F1', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 16, borderRadius: 16, marginTop: 20 },
  addBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  saveBtn: { backgroundColor: '#10B981', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 16, borderRadius: 16, marginTop: 20 },
  saveBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
});