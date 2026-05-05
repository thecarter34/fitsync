import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, Alert, FlatList, Modal } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { getExercises, getAllLastSessions, getSuggestedWeight, INITIAL_WORKOUTS } from '../utils/exercises';

const MUSCLE_GROUPS = [
  'Shoulders', 'Chest', 'Back', 'Lats', 'Biceps', 'Triceps',
  'Posterior Chain', 'Quads/Glutes', 'Glutes/Hams', 'Core',
  'Full Body', 'Calves', 'Forearms', 'Rear Delts', 'Side Delts', 'Upper Chest',
];

export default function QuickStartWorkout({ navigation, route }) {
  const [allExercises, setAllExercises] = useState([]);
  const [selectedExercises, setSelectedExercises] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [lastSessionData, setLastSessionData] = useState({});
  const [showAddCustomModal, setShowAddCustomModal] = useState(false);
  const [newExerciseName, setNewExerciseName] = useState('');
  const [newExerciseMuscle, setNewExerciseMuscle] = useState('');
  const [newExerciseSets, setNewExerciseSets] = useState('3');
  const [newExerciseReps, setNewExerciseReps] = useState('8');
  const [newExerciseWeight, setNewExerciseWeight] = useState('');

  useEffect(() => {
    loadAllExercisesAndLastSessions();
  }, []);

  const loadAllExercisesAndLastSessions = async () => {
    const storedWorkouts = await getExercises();
    const masterExerciseList = new Map();

    if (storedWorkouts) {
      Object.values(storedWorkouts).forEach(day => {
        day.exercises?.forEach(ex => {
          masterExerciseList.set(ex.name, ex);
        });
      });
    }

    // Also add exercises from INITIAL_WORKOUTS if not already in master list
    Object.values(INITIAL_WORKOUTS).forEach(day => {
      day.exercises?.forEach(ex => {
        if (!masterExerciseList.has(ex.name)) {
          masterExerciseList.set(ex.name, ex);
        }
      });
    });

    setAllExercises(Array.from(masterExerciseList.values()));

    const allLastSessions = await getAllLastSessions();
    setLastSessionData(allLastSessions);
  };

  const filteredExercises = allExercises.filter(ex =>
    ex.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleExerciseSelection = (exercise) => {
    setSelectedExercises(prev => {
      const exists = prev.find(e => e.name === exercise.name);
      if (exists) {
        return prev.filter(e => e.name !== exercise.name);
      } else {
        const lastSession = lastSessionData[exercise.name];
        const suggestedWeight = lastSession ? getSuggestedWeight(lastSession.weight, lastSession.setsCompleted, exercise.sets) : exercise.weight;
        return [...prev, { ...exercise, loggedWeight: suggestedWeight }];
      }
    });
  };

  const updateSelectedExercise = (name, field, value) => {
    setSelectedExercises(prev =>
      prev.map(ex =>
        ex.name === name
          ? { ...ex, [field]: value }
          : ex
      )
    );
  };

  const handleAddCustomExercise = () => {
    if (!newExerciseName.trim() || !newExerciseMuscle.trim()) {
      Alert.alert('Missing Info', 'Please enter exercise name and muscle group.');
      return;
    }
    const newExercise = {
      name: newExerciseName.trim(),
      muscle: newExerciseMuscle.trim(),
      sets: parseInt(newExerciseSets) || 3,
      reps: newExerciseReps,
      weight: parseInt(newExerciseWeight) || 0,
      rest: '60 sec',
    };
    setSelectedExercises(prev => [...prev, { ...newExercise, loggedWeight: newExercise.weight }]);
    setAllExercises(prev => {
      if (!prev.find(e => e.name === newExercise.name)) {
        return [...prev, newExercise];
      }
      return prev;
    });
    setShowAddCustomModal(false);
    setNewExerciseName('');
    setNewExerciseMuscle('');
    setNewExerciseSets('3');
    setNewExerciseReps('8');
    setNewExerciseWeight('');
  };

  const startCustomWorkout = () => {
    if (selectedExercises.length === 0) {
      Alert.alert('No Exercises', 'Please select at least one exercise to start a workout.');
      return;
    }
    
    const exercisesWithUnit = selectedExercises.map(ex => ({ ...ex, unit: 'lb' }));
    const newData = {
      label: 'Custom Workout',
      type: 'custom',
      color: '#6366F1',
      icon: 'fitness',
      focus: 'Mixed',
      exercises: exercisesWithUnit,
    };
    
    route.params.setWorkoutStackData({ customWorkoutData: newData, addToExisting: false });
    navigation.goBack();
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color="#6366F1" />
          <Text style={styles.backBtnText}>Back</Text>
        </TouchableOpacity>
        <Text style={styles.screenTitle}>Quick Start Workout</Text>
        <View style={{ width: 60 }} />
      </View>

      <TextInput
        style={styles.searchInput}
        placeholder="Search exercises..."
        placeholderTextColor="#6B7280"
        value={searchTerm}
        onChangeText={setSearchTerm}
      />

      <TouchableOpacity style={styles.addCustomBtn} onPress={() => setShowAddCustomModal(true)}>
        <Ionicons name="add-circle-outline" size={20} color="#F9FAFB" />
        <Text style={styles.addCustomBtnText}>Add Custom Exercise</Text>
      </TouchableOpacity>

      <ScrollView style={styles.exerciseListContainer}>
        {filteredExercises.map((exercise, index) => {
          const isSelected = selectedExercises.some(e => e.name === exercise.name);
          const lastSession = lastSessionData[exercise.name];
          const suggestedWeight = lastSession ? getSuggestedWeight(lastSession.weight, lastSession.setsCompleted, exercise.sets) : exercise.weight;
          const currentSelected = selectedExercises.find(e => e.name === exercise.name);

          return (
            <TouchableOpacity
              key={exercise.name}
              style={[styles.exerciseItem, isSelected && styles.exerciseItemSelected]}
              onPress={() => toggleExerciseSelection(exercise)}
            >
              <View style={styles.exerciseItemLeft}>
                <Ionicons
                  name={isSelected ? "checkmark-circle" : "ellipse-outline"}
                  size={20}
                  color={isSelected ? "#10B981" : "#9CA3AF"}
                />
                <View>
                  <Text style={styles.exerciseName}>{exercise.name}</Text>
                  <Text style={styles.exerciseMuscle}>{exercise.muscle}</Text>
                </View>
              </View>
              <View style={styles.exerciseItemRight}>
                {isSelected && (
                  <View style={styles.selectedExerciseDetails}>
                    <TextInput
                      style={styles.detailInput}
                      value={currentSelected.sets?.toString() || ''}
                      onChangeText={(val) => updateSelectedExercise(exercise.name, 'sets', parseInt(val) || 0)}
                      keyboardType="numeric"
                      placeholder="Sets"
                      placeholderTextColor="#6B7280"
                    />
                    <TextInput
                      style={styles.detailInput}
                      value={currentSelected.reps?.toString() || ''}
                      onChangeText={(val) => updateSelectedExercise(exercise.name, 'reps', val)}
                      placeholder="Reps"
                      placeholderTextColor="#6B7280"
                    />
                    <TextInput
                      style={styles.detailInput}
                      value={currentSelected.loggedWeight?.toString() || ''}
                      onChangeText={(val) => updateSelectedExercise(exercise.name, 'loggedWeight', parseInt(val) || 0)}
                      keyboardType="numeric"
                      placeholder="Weight"
                      placeholderTextColor="#6B7280"
                    />
                  </View>
                )}
                {!isSelected && (lastSession || suggestedWeight !== exercise.weight) && (
                  <View>
                    {lastSession && <Text style={styles.lastWeightText}>Last: {lastSession.weight} lb</Text>}
                    {suggestedWeight !== exercise.weight && <Text style={styles.suggestedText}>Try: {suggestedWeight} lb</Text>}
                  </View>
                )}
              </View>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      <TouchableOpacity
        style={[styles.startButton, selectedExercises.length === 0 && styles.startButtonDisabled]}
        onPress={startCustomWorkout}
        disabled={selectedExercises.length === 0}
      >
        <Ionicons name="play" size={20} color="#fff" />
        <Text style={styles.startButtonText}>Start Custom Workout ({selectedExercises.length})</Text>
      </TouchableOpacity>

      {/* Add Custom Exercise Modal */}
      <Modal
        animationType="slide"
        transparent={true}
        visible={showAddCustomModal}
        onRequestClose={() => setShowAddCustomModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Add New Exercise</Text>
              <TouchableOpacity onPress={() => setShowAddCustomModal(false)}>
                <Ionicons name="close" size={24} color="#9CA3AF" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalScroll}>
              <Text style={styles.inputLabel}>Exercise Name</Text>
              <TextInput
                style={styles.textInput}
                value={newExerciseName}
                onChangeText={setNewExerciseName}
                placeholder="e.g. Barbell Rows"
                placeholderTextColor="#6B7280"
              />

              <Text style={styles.inputLabel}>Muscle Group</Text>
              <View style={styles.muscleSelector}>
                {MUSCLE_GROUPS.map(m => (
                  <TouchableOpacity
                    key={m}
                    style={[styles.muscleChip, newExerciseMuscle === m && styles.muscleChipSelected]}
                    onPress={() => setNewExerciseMuscle(m)}
                  >
                    <Text style={[styles.muscleChipText, newExerciseMuscle === m && styles.muscleChipTextSelected]}>{m}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              <View style={styles.rowInputs}>
                <View style={styles.halfInput}>
                  <Text style={styles.inputLabel}>Sets</Text>
                  <TextInput
                    style={styles.textInput}
                    value={newExerciseSets}
                    onChangeText={setNewExerciseSets}
                    keyboardType="numeric"
                    placeholder="3"
                    placeholderTextColor="#6B7280"
                  />
                </View>
                <View style={styles.halfInput}>
                  <Text style={styles.inputLabel}>Reps</Text>
                  <TextInput
                    style={styles.textInput}
                    value={newExerciseReps}
                    onChangeText={setNewExerciseReps}
                    placeholder="8"
                    placeholderTextColor="#6B7280"
                  />
                </View>
              </View>

              <Text style={styles.inputLabel}>Starting Weight (lb)</Text>
              <TextInput
                style={styles.textInput}
                value={newExerciseWeight}
                onChangeText={setNewExerciseWeight}
                keyboardType="numeric"
                placeholder="135"
                placeholderTextColor="#6B7280"
              />
            </ScrollView>

            <TouchableOpacity style={styles.addBtn} onPress={handleAddCustomExercise}>
              <Ionicons name="add" size={20} color="#fff" />
              <Text style={styles.addBtnText}>Add to Custom Workout</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A', paddingBottom: 0 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: '#1F2937' },
  backBtn: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  backBtnText: { color: '#6366F1', fontSize: 16, fontWeight: '600' },
  screenTitle: { fontSize: 20, fontWeight: '800', color: '#F9FAFB' },
  searchInput: { backgroundColor: '#1F2937', borderRadius: 12, paddingHorizontal: 16, paddingVertical: 12, fontSize: 16, color: '#F9FAFB', margin: 16, borderWidth: 1, borderColor: '#374151' },
  addCustomBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, backgroundColor: '#374151', padding: 14, borderRadius: 14, marginHorizontal: 16, marginBottom: 16 },
  addCustomBtnText: { color: '#F9FAFB', fontSize: 15, fontWeight: '600' },
  exerciseListContainer: { flex: 1, paddingHorizontal: 16 },
  exerciseItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1F2937',
    borderRadius: 14,
    marginBottom: 8,
    padding: 16,
  },
  exerciseItemSelected: { borderColor: '#6366F1', borderWidth: 1 },
  exerciseItemLeft: { flexDirection: 'row', alignItems: 'center', gap: 12, flex: 1 },
  exerciseName: { fontSize: 16, fontWeight: '700', color: '#F9FAFB' },
  exerciseMuscle: { fontSize: 13, color: '#9CA3AF', marginTop: 2 },
  exerciseItemRight: { alignItems: 'flex-end', flexDirection: 'row', gap: 10 },
  lastWeightText: { fontSize: 12, color: '#9CA3AF' },
  suggestedText: { fontSize: 12, color: '#10B981', fontWeight: '600' },
  selectedExerciseDetails: { flexDirection: 'row', gap: 8 },
  detailInput: {
    backgroundColor: '#111827',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
    fontSize: 14,
    color: '#F9FAFB',
    width: 60,
    textAlign: 'center',
  },
  startButton: {
    backgroundColor: '#6366F1',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    padding: 18,
    borderRadius: 16,
    margin: 16,
  },
  startButtonDisabled: {
    backgroundColor: '#374151',
  },
  startButtonText: { color: '#fff', fontSize: 18, fontWeight: '700' },

  // Modal styles (similar to ProgramManager)
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
  addBtn: { backgroundColor: '#6366F1', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 16, borderRadius: 16, marginTop: 20 },
  addBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
});
