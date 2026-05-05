import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  Modal, Pressable, TextInput, Alert
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { saveWorkoutSession, getWorkoutHistory } from '../utils/storage';
import { getExercises, saveExercises, getAllLastSessions, saveSessionResult, getSuggestedWeight, INITIAL_WORKOUTS } from '../utils/exercises';

const DAY_MAP = {
  0: 'sunday', 1: 'monday', 2: 'tuesday', 3: 'wednesday',
  4: 'thursday', 5: 'friday', 6: 'saturday',
};

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function ExerciseCard({ exercise, index, lastSession, suggestedWeight }) {
  return (
    <View style={styles.exerciseCard}>
      <View style={styles.exerciseLeft}>
        <View style={styles.exerciseIndex}>
          <Text style={styles.exerciseIndexText}>{index + 1}</Text>
        </View>
        <View style={styles.exerciseInfo}>
          <Text style={styles.exerciseName}>{exercise.name}</Text>
          <Text style={styles.exerciseMuscle}>{exercise.muscle}</Text>
        </View>
      </View>
      <View style={styles.exerciseRight}>
        {lastSession && (
          <Text style={styles.lastWeightText}>Last: {lastSession.weight} lb</Text>
        )}
        {suggestedWeight && suggestedWeight > exercise.weight && (
          <Text style={styles.suggestedText}>Try: {suggestedWeight} lb</Text>
        )}
        <Text style={styles.exerciseSetsReps}>{exercise.sets} x {exercise.reps}</Text>
        <Text style={styles.exerciseWeight}>{exercise.weight} lb</Text>
        <Text style={styles.exerciseRest}>rest {exercise.rest}</Text>
      </View>
    </View>
  );
}

function DaySelector({ selected, onSelect }) {
  const dayKeys = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
  const dayAbbrev = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
  const today = new Date().getDay();
  const [workouts, setWorkouts] = React.useState(null);

  useEffect(() => {
    getExercises().then(setWorkouts);
  }, []);

  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.daySelector}>
      {dayKeys.map((key, i) => {
        const isSelected = selected === key;
        const isToday = today === i;
        const workout = workouts ? workouts[key] : null;
        const dayWorkout = workout || null;
        return (
          <TouchableOpacity
            key={key}
            style={[styles.dayPill, isSelected && styles.dayPillSelected, isToday && !isSelected && styles.dayPillToday]}
            onPress={() => onSelect(key)}
          >
            <Text style={[styles.dayPillText, isSelected && styles.dayPillTextSelected]}>
              {workout ? workout.label?.split(' ')[0] : dayAbbrev[i]}
            </Text>
            <Text style={[styles.dayPillSub, isSelected && styles.dayPillTextSelected]}>{dayAbbrev[i]}</Text>
          </TouchableOpacity>
        );
      })}
    </ScrollView>
  );
}

export default function WorkoutScreen({ navigation, route }) {
  const [inProgress, setInProgress] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [completedSets, setCompletedSets] = useState({}); // {exerciseIndex: [{weight: number, completed: bool}]}
  const [workoutHistory, setWorkoutHistory] = useState([]);
  const [workouts, setWorkouts] = React.useState(null);
  const [lastSessionData, setLastSessionData] = useState({});
  const [showSummary, setShowSummary] = useState(false);
  const [summaryData, setSummaryData] = useState(null);
  const [activeExerciseModal, setActiveExerciseModal] = useState(null);

  // Handle custom workout from Quick Start
  useEffect(() => {
    const wsState = route?.params?.workoutStackState;
    if (!wsState?.customWorkoutData) return;
    const data = wsState.customWorkoutData;
    
    if (inProgress && currentSession && wsState.addToExisting) {
      // Add to existing session
      setCurrentSession(prev => ({
        ...prev,
        exercises: [...prev.exercises, ...(data.exercises || []).map(ex => ({ ...ex, unit: ex.unit || 'lb' }))]
      }));
      route.params.setWorkoutStackData({ customWorkoutData: null, addToExisting: false });
    } else if (data.exercises?.length) {
      // Start new session
      setCurrentSession({ ...data, unit: 'lb' });
      setInProgress(true);
      setElapsedTime(0);
      setCompletedSets({});
      route.params.setWorkoutStackData({ customWorkoutData: null, addToExisting: false });
    }
  }, [route?.params?.workoutStackState]);

  // Reload workouts whenever this screen comes into focus
  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', async () => {
      const stored = await getExercises();
      if (stored) setWorkouts(stored);
    });
    return unsubscribe;
  }, [navigation]);

  useEffect(() => {
    const load = async () => {
      let stored = await getExercises();
      // Seed default workouts if nothing stored yet
      if (!stored) {
        await saveExercises(INITIAL_WORKOUTS);
        stored = INITIAL_WORKOUTS;
      }
      setWorkouts(stored);
      const history = await getWorkoutHistory();
      setWorkoutHistory(history);
      const sessions = await getAllLastSessions();
      setLastSessionData(sessions);
    };
    load();
  }, []);

  useEffect(() => {
    let interval;
    if (inProgress) {
      interval = setInterval(() => setElapsedTime(prev => prev + 1), 1000);
    }
    return () => clearInterval(interval);
  }, [inProgress]);

  const startWorkout = async () => {
    const plan = workouts?.[selectedDay];

    if (plan && plan.exercises?.length > 0) {
      setInProgress(true);
      setCurrentSession({
        type: selectedDay,
        label: plan.label,
        color: plan.color,
        icon: plan.icon,
        focus: plan.focus,
        startTime: new Date().toISOString(),
        exercises: plan.exercises.map(ex => ({ ...ex, setsCompleted: 0 })),
      });
      setElapsedTime(0);
      setCompletedSets({});
      setCurrentSession(prev => ({ ...prev, unit: 'lb' }));
    } else {
      alert('No workout scheduled for this day. Use Quick Start to build a custom workout!');
    }
  };

  const finishWorkout = async () => {
    if (!currentSession) return;

    const prs = [];
    for (const ex of currentSession.exercises) {
      const exIdx = currentSession.exercises.indexOf(ex);
      const setLog = completedSets[exIdx] || [];
      const completedCount = setLog.filter(s => s.completed).length;
      // Use the last completed set's weight for tracking
      const lastCompletedSet = setLog.filter(s => s.completed).slice(-1)[0];
      const weightUsed = lastCompletedSet?.weight || ex.weight || 0;
      
      await saveSessionResult(ex.name, weightUsed, completedCount, ex.reps);
      
      const last = lastSessionData[ex.name];
      if (last && weightUsed > last.weight && completedCount >= last.sets) {
        prs.push(ex.name);
      }
    }

    const sessionToSave = {
      ...currentSession,
      endTime: new Date().toISOString(),
      durationSeconds: elapsedTime,
      exercises: currentSession.exercises.map((ex, i) => ({
        ...ex,
        setLog: completedSets[i] || [],
        setsCompleted: (completedSets[i] || []).filter(s => s.completed).length,
      })),
    };

    await saveWorkoutSession(sessionToSave);

    const totalSets = sessionToSave.exercises.reduce((sum, ex) => sum + ex.setsCompleted, 0);
    setSummaryData({ duration: elapsedTime, totalSets, prs });
    setShowSummary(true);

    const updatedHistory = await getWorkoutHistory();
    setWorkoutHistory(updatedHistory);
    const sessions = await getAllLastSessions();
    setLastSessionData(sessions);

    setInProgress(false);
    setCurrentSession(null);
    setElapsedTime(0);
    setCompletedSets({});
  };

  const completeSet = (index) => {
    // Show modal to record weight before completing set
    setActiveExerciseModal(index);
  };

  const logSetForExercise = (index) => {
    // Mark the first incomplete set as completed, with current weight
    setCompletedSets(prev => {
      const prevSets = prev[index] || [];
      const exercise = currentSession.exercises[index];
      const defaultWeight = exercise?.weight || 0;
      // Find first incomplete set and mark it done
      const updated = prevSets.map((s, i) =>
        !s.completed && i === prevSets.findIndex(s2 => !s2.completed) ? { ...s, completed: true } : s
      );
      // If we don't have enough set slots, add one
      if (updated.filter(s => s.completed).length < (exercise?.sets || 0)) {
        const nextSetIdx = updated.filter(s => s.completed).length;
        updated[nextSetIdx] = { weight: defaultWeight, completed: true };
      }
      return { ...prev, [index]: updated };
    });
  };

  const updateActiveExerciseWeight = (index, newWeight) => {
    setCurrentSession(prev => {
      const updated = { ...prev };
      updated.exercises = prev.exercises.map((ex, i) =>
        i === index ? { ...ex, loggedWeight: newWeight } : ex
      );
      return updated;
    });
  };

  const moveExerciseInSession = (index, direction) => {
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= currentSession.exercises.length) return;
    setCurrentSession(prev => {
      const exercises = [...prev.exercises];
      const [moved] = exercises.splice(index, 1);
      exercises.splice(newIndex, 0, moved);
      return { ...prev, exercises };
    });
    setCompletedSets(prev => {
      const updated = { ...prev };
      const keys = Object.keys(prev);
      const vals = [...(prev[index] || []), ...(prev[newIndex] || [])];
      return updated;
    });
    // Also reorder completedSets
    setCompletedSets(prev => {
      const updated = { ...prev };
      const fromKey = index.toString();
      const toKey = newIndex.toString();
      const fromSets = updated[fromKey];
      const toSets = updated[toKey];
      const temp = {};
      // Build new keys based on reordered exercise positions
      const newKeys = {};
      Object.keys(updated).forEach(k => {
        const ki = parseInt(k);
        if (ki === index) newKeys[newIndex] = fromSets;
        else if (ki === newIndex) newKeys[index] = toSets;
        else newKeys[ki] = updated[ki];
      });
      return newKeys;
    });
  };

  const getExerciseDisplay = useCallback((exercise) => {
    const last = lastSessionData[exercise.name];
    const suggested = last ? getSuggestedWeight(last.weight, last.setsCompleted, exercise.sets) : null;
    return { lastSession: last, suggestedWeight: suggested };
  }, [lastSessionData]);

  const today = new Date().getDay();
  const todayKey = DAY_MAP[today];
  const [selectedDay, setSelectedDay] = useState(todayKey);
  const selectedWorkout = workouts ? workouts[selectedDay] : null;

  if (inProgress && currentSession) {
    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Active Workout</Text>
            <Text style={styles.date}>{currentSession.label}</Text>
          </View>
          <View style={styles.headerRight}>
            <View style={styles.timerBadge}>
              <Ionicons name="timer-outline" size={18} color="#fff" />
              <Text style={styles.timerText}>{formatTime(elapsedTime)}</Text>
            </View>
          </View>
        </View>

        <View style={[styles.workoutCard, { borderColor: (currentSession.color || '#6366F1') + '40' }]}>
          <View style={[styles.workoutHeader, { backgroundColor: (currentSession.color || '#6366F1') + '20' }]}>
            <View style={[styles.workoutIcon, { backgroundColor: currentSession.color || '#6366F1' }]}>
              <Ionicons name={currentSession.icon || 'fitness'} size={20} color="#fff" />
            </View>
            <View style={styles.workoutHeaderInfo}>
              <Text style={[styles.workoutLabel, { color: currentSession.color || '#6366F1' }]}>{currentSession.label}</Text>
              <Text style={styles.workoutFocus}>{currentSession.focus}</Text>
            </View>
          </View>

          <View style={styles.exerciseList}>
            {currentSession.exercises.map((exercise, index) => {
              const setData = completedSets[index] || Array(exercise.sets).fill(null).map(() => ({ weight: exercise.weight || 0, reps: exercise.reps || 8, completed: false }));
              const lastSession = lastSessionData[exercise.name];
              const prevDisplay = lastSession ? `${lastSession.weight} × ${lastSession.reps}` : null;
              return (
                <View key={`act-${exercise.name}-${index}`} style={styles.exerciseBlock}>
                  <View style={[styles.exerciseColorBar, { backgroundColor: currentSession.color || '#6366F1' }]} />
                  <View style={styles.exerciseBlockContent}>
                    <View style={styles.exerciseBlockHeader}>
                      <View style={styles.exerciseBlockTitleRow}>
                        <View style={styles.exerciseNameRow}>
                          <TouchableOpacity
                            style={styles.sessionReorderBtn}
                            onPress={() => moveExerciseInSession(index, -1)}
                            disabled={index === 0}
                          >
                            <Ionicons name="chevron-up" size={16} color={index === 0 ? '#374151' : '#6366F1'} />
                          </TouchableOpacity>
                          <TouchableOpacity
                            style={styles.sessionReorderBtn}
                            onPress={() => moveExerciseInSession(index, 1)}
                            disabled={index === currentSession.exercises.length - 1}
                          >
                            <Ionicons name="chevron-down" size={16} color={index === currentSession.exercises.length - 1 ? '#374151' : '#6366F1'} />
                          </TouchableOpacity>
                          <Text style={[styles.exerciseBlockName, { color: currentSession.color || '#6366F1' }]}>{exercise.name}</Text>
                        </View>
                        <TouchableOpacity
                          style={styles.exerciseUnitToggle}
                          onPress={() => {
                            const newUnit = exercise.unit === 'kg' ? 'lb' : 'kg';
                            setCurrentSession(prev => ({
                              ...prev,
                              exercises: prev.exercises.map((ex, i) =>
                                i === index ? { ...ex, unit: newUnit } : ex
                              )
                            }));
                          }}
                        >
                          <Text style={styles.exerciseUnitToggleText}>{exercise.unit === 'kg' ? 'KG' : 'LB'}</Text>
                        </TouchableOpacity>
                      </View>
                      <Text style={styles.exerciseBlockMuscle}>{exercise.muscle}</Text>
                    </View>

                    {/* Column Headers */}
                    <View style={styles.setTableHeader}>
                      <Text style={[styles.setTableHeaderText, { width: 36 }]}>SET</Text>
                      <Text style={[styles.setTableHeaderText, { flex: 1 }]}>PREVIOUS</Text>
                      <Text style={[styles.setTableHeaderText, { width: 70, textAlign: 'center' }]}>{exercise.unit === 'kg' ? 'KG' : 'LB'}</Text>
                      <Text style={[styles.setTableHeaderText, { width: 60, textAlign: 'center' }]}>REPS</Text>
                      <View style={{ width: 36 }} />
                    </View>

                    {/* Set Rows */}
                    {Array.from({ length: exercise.sets }, (_, setIdx) => {
                      const thisSet = setData[setIdx] || { weight: exercise.weight || 0, reps: exercise.reps || 8, completed: false };
                      return (
                        <View key={setIdx} style={styles.setTableRow}>
                          <View style={styles.setNumLabelContainer}>
                            <Text style={styles.setNumLabel}>{setIdx + 1}</Text>
                            {exercise.sets > 1 && (
                              <TouchableOpacity
                                style={styles.deleteSetBtn}
                                onPress={() => {
                                  // Remove this specific set
                                  setCurrentSession(prev => {
                                    const updated = { ...prev };
                                    updated.exercises = prev.exercises.map((ex, i) =>
                                      i === index ? { ...ex, sets: ex.sets - 1 } : ex
                                    );
                                    return updated;
                                  });
                                  setCompletedSets(prev => {
                                    const prevSets = prev[index] || [];
                                    const updated = prevSets.filter((_, si) => si !== setIdx);
                                    return { ...prev, [index]: updated };
                                  });
                                }}
                              >
                                <Ionicons name="close" size={12} color="#EF4444" />
                              </TouchableOpacity>
                            )}
                          </View>
                          <Text style={styles.prevText}>{prevDisplay || '—'}</Text>
                          <TextInput
                            style={[styles.setInput, thisSet.completed && styles.setInputDone]}
                            value={thisSet.weight?.toString() || ''}
                            onChangeText={(val) => {
                              const num = parseInt(val) || 0;
                              setCompletedSets(prev => {
                                const prevSets = prev[index] || Array(exercise.sets).fill(null).map(() => ({ weight: exercise.weight || 0, reps: exercise.reps || 8, completed: false }));
                                const updated = [...prevSets];
                                updated[setIdx] = { ...updated[setIdx], weight: num };
                                return { ...prev, [index]: updated };
                              });
                            }}
                            keyboardType="numeric"
                            placeholder={exercise.weight?.toString() || '0'}
                            placeholderTextColor="#6B7280"
                          />
                          <TextInput
                            style={[styles.setInput, styles.setInputReps, thisSet.completed && styles.setInputDone]}
                            value={thisSet.reps?.toString() || ''}
                            onChangeText={(val) => {
                              const num = parseInt(val) || 0;
                              setCompletedSets(prev => {
                                const prevSets = prev[index] || Array(exercise.sets).fill(null).map(() => ({ weight: exercise.weight || 0, reps: exercise.reps || 8, completed: false }));
                                const updated = [...prevSets];
                                updated[setIdx] = { ...updated[setIdx], reps: num };
                                return { ...prev, [index]: updated };
                              });
                            }}
                            keyboardType="numeric"
                            placeholder={String(exercise.reps || 8)}
                            placeholderTextColor="#6B7280"
                          />
                          <TouchableOpacity
                            style={[styles.setCheckCircle, thisSet.completed && styles.setCheckCircleDone]}
                            onPress={() => {
                              setCompletedSets(prev => {
                                const prevSets = prev[index] || Array(exercise.sets).fill(null).map(() => ({ weight: exercise.weight || 0, reps: exercise.reps || 8, completed: false }));
                                const updated = [...prevSets];
                                updated[setIdx] = { ...updated[setIdx], completed: !thisSet.completed };
                                return { ...prev, [index]: updated };
                              });
                            }}
                          >
                            <Ionicons
                              name={thisSet.completed ? 'checkmark' : 'ellipse-outline'}
                              size={16}
                              color={thisSet.completed ? '#fff' : '#6B7280'}
                            />
                          </TouchableOpacity>
                        </View>
                      );
                    })}

                    {/* Add Set */}
                    <TouchableOpacity
                      style={styles.addSetBtn}
                      onPress={() => {
                        // Add a new set to the exercise
                        setCurrentSession(prev => {
                          const updated = { ...prev };
                          updated.exercises = prev.exercises.map((ex, i) =>
                            i === index ? { ...ex, sets: (ex.sets || 3) + 1 } : ex
                          );
                          return updated;
                        });
                        // Also add to completedSets tracking
                        setCompletedSets(prev => {
                          const prevSets = prev[index] || [];
                          return { ...prev, [index]: [...prevSets, { weight: exercise.weight || 0, reps: exercise.reps || 8, completed: false, unit: exercise.unit || 'lb' }] };
                        });
                      }}
                    >
                      <Text style={styles.addSetBtnText}>+ ADD SET</Text>
                    </TouchableOpacity>

                    {/* Exercise Actions */}
                    <View style={styles.exerciseActions}>
                      <TouchableOpacity
                        style={styles.exerciseActionBtn}
                        onPress={() => {
                          setCurrentSession(prev => ({
                            ...prev,
                            exercises: prev.exercises.filter((_, i) => i !== index)
                          }));
                        }}
                      >
                        <Ionicons name="trash-outline" size={14} color="#EF4444" />
                        <Text style={styles.exerciseActionBtnText}>Remove</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                </View>
              );
            })}

            {/* + Add Exercise Button */}
            <TouchableOpacity
              style={styles.addExerciseBtn}
              onPress={() => {
                route.params.setWorkoutStackData({
                  customWorkoutData: {
                    exercises: [],
                    label: 'Add Exercise',
                    color: currentSession.color || '#6366F1',
                    icon: currentSession.icon || 'fitness',
                    focus: 'Add to Workout',
                    unit: 'lb'
                  },
                  addToExisting: true
                });
                navigation.navigate('QuickStart');
              }}
            >
              <Ionicons name="add" size={20} color="#6366F1" />
              <Text style={styles.addExerciseBtnText}>Add Exercise</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity
            style={[styles.finishWorkoutBtn, { backgroundColor: currentSession.color || '#6366F1' }]}
            onPress={finishWorkout}
          >
            <Ionicons name="flag" size={20} color="#fff" />
            <Text style={styles.finishWorkoutText}>Finish Workout</Text>
          </TouchableOpacity>
        </View>

        {/* Edit Exercise Modal */}
        <Modal animationType="slide" transparent={true} visible={activeExerciseModal !== null} onRequestClose={() => setActiveExerciseModal(null)}>
          <View style={styles.modalOverlay}>
            <View style={styles.modalContainer}>
              {activeExerciseModal !== null && currentSession.exercises[activeExerciseModal] && (
                <>
                  <Text style={styles.modalTitle}>{currentSession.exercises[activeExerciseModal].name}</Text>
                  <Text style={styles.modalSubtitle}>{currentSession.exercises[activeExerciseModal].muscle}</Text>

                  <View style={styles.modalRow}>
                    <View style={styles.modalHalf}>
                      <Text style={styles.modalLabel}>Sets Target</Text>
                      <Text style={styles.modalValue}>{currentSession.exercises[activeExerciseModal].sets}</Text>
                    </View>
                    <View style={styles.modalHalf}>
                      <Text style={styles.modalLabel}>Completed</Text>
                      <View style={styles.modalStepperRow}>
                        <TouchableOpacity
                          style={styles.modalStepperBtn}
                          onPress={() => {
                            const current = completedSets[activeExerciseModal] || 0;
                            if (current > 0) setCompletedSets(prev => ({ ...prev, [activeExerciseModal]: current - 1 }));
                          }}
                        >
                          <Ionicons name="remove" size={20} color="#F9FAFB" />
                        </TouchableOpacity>
                        <Text style={styles.modalStepperNum}>{completedSets[activeExerciseModal] || 0}</Text>
                        <TouchableOpacity
                          style={styles.modalStepperBtn}
                          onPress={() => logSetForExercise(activeExerciseModal)}
                        >
                          <Ionicons name="add" size={20} color="#F9FAFB" />
                        </TouchableOpacity>
                      </View>
                    </View>
                  </View>

                  <Text style={styles.modalLabel}>Weight (lb)</Text>
                  <TextInput
                    style={styles.modalTextInput}
                    value={currentSession.exercises[activeExerciseModal].weight?.toString() || '0'}
                    onChangeText={(val) => updateActiveExerciseWeight(activeExerciseModal, parseInt(val) || 0)}
                    keyboardType="numeric"
                    placeholder="0"
                    placeholderTextColor="#6B7280"
                  />

                  <TouchableOpacity style={styles.modalDoneBtn} onPress={() => setActiveExerciseModal(null)}>
                    <Text style={styles.modalDoneBtnText}>Done</Text>
                  </TouchableOpacity>
                </>
              )}
            </View>
          </View>
        </Modal>

        {/* Summary Modal */}
        <Modal animationType="slide" transparent={true} visible={showSummary} onRequestClose={() => setShowSummary(false)}>
          <View style={styles.modalOverlay}>
            <View style={styles.modalContainer}>
              <Text style={styles.summaryTitle}>Workout Complete!</Text>
              {summaryData && (
                <View style={styles.summaryContent}>
                  <Text style={styles.summaryText}>Duration: <Text style={styles.summaryHighlight}>{formatTime(summaryData.duration)}</Text></Text>
                  <Text style={styles.summaryText}>Total Sets: <Text style={styles.summaryHighlight}>{summaryData.totalSets}</Text></Text>
                  {summaryData.prs.length > 0 && (
                    <Text style={styles.summaryText}>New PRs: <Text style={styles.summaryHighlight}>{summaryData.prs.join(', ')}</Text></Text>
                  )}
                </View>
              )}
              <Pressable style={styles.modalBtn} onPress={() => setShowSummary(false)}>
                <Text style={styles.modalBtnText}>Awesome!</Text>
              </Pressable>
            </View>
          </View>
        </Modal>
      </ScrollView>
    );
  }

  if (!selectedWorkout || !selectedWorkout.exercises?.length) {
    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Workout</Text>
            <Text style={styles.date}>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</Text>
          </View>
          <TouchableOpacity style={styles.syncBadge} onPress={() => navigation.navigate('Program')}>
            <Ionicons name="barbell" size={16} color="#6366F1" />
          </TouchableOpacity>
        </View>

        <DaySelector selected={selectedDay} onSelect={setSelectedDay} />

        <View style={styles.restContainer}>
          <View style={styles.restIconWrapper}>
            <Ionicons name="moon" size={48} color="#374151" />
          </View>
          <Text style={styles.restTitle}>Rest Day</Text>
          <Text style={styles.restSubtitle}>No workout for {selectedDay}.</Text>
          <Text style={styles.restHint}>Recover, stretch, or go for a walk.</Text>
        </View>

        {workoutHistory.length > 0 && (
          <View style={styles.section}>
            <TouchableOpacity onPress={() => navigation.navigate('History')} style={styles.sectionHeaderBtn}>
              <Text style={styles.sectionTitle}>Recent Workouts</Text>
              <Ionicons name="chevron-forward" size={18} color="#6366F1" />
            </TouchableOpacity>
            {workoutHistory.slice(0, 3).map(session => (
              <View key={session.id} style={styles.historyCard}>
                <View style={styles.historyHeader}>
                  <Text style={styles.historyTitle}>{session.label}</Text>
                  <Text style={styles.historyDate}>{new Date(session.completedAt).toLocaleDateString()}</Text>
                </View>
                <Text style={styles.historyDuration}>{formatTime(session.durationSeconds)}</Text>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Today's Workout</Text>
          <Text style={styles.date}>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</Text>
        </View>
        <TouchableOpacity style={styles.syncBadge} onPress={() => navigation.navigate('Program')}>
          <Ionicons name="barbell" size={16} color="#6366F1" />
        </TouchableOpacity>
      </View>

      <DaySelector selected={selectedDay} onSelect={setSelectedDay} />

      <View style={[styles.workoutCard, { borderColor: selectedWorkout.color + '40' }]}>
        <View style={[styles.workoutHeader, { backgroundColor: selectedWorkout.color + '20' }]}>
          <View style={[styles.workoutIcon, { backgroundColor: selectedWorkout.color }]}>
            <Ionicons name={selectedWorkout.icon || 'fitness'} size={20} color="#fff" />
          </View>
          <View style={styles.workoutHeaderInfo}>
            <Text style={[styles.workoutLabel, { color: selectedWorkout.color }]}>{selectedWorkout.label}</Text>
            <Text style={styles.workoutFocus}>{selectedWorkout.focus}</Text>
          </View>
          <View style={styles.exerciseCount}>
            <Text style={styles.exerciseCountNum}>{selectedWorkout.exercises.length}</Text>
            <Text style={styles.exerciseCountLabel}>exercises</Text>
          </View>
        </View>

        <View style={styles.exerciseList}>
          {selectedWorkout.exercises.map((exercise, index) => {
            const { lastSession, suggestedWeight } = getExerciseDisplay(exercise);
            return (
              <ExerciseCard
                key={index}
                exercise={exercise}
                index={index}
                lastSession={lastSession}
                suggestedWeight={suggestedWeight}
              />
            );
          })}
        </View>

        {selectedWorkout.finisher && (
          <View style={styles.finisherSection}>
            <View style={styles.finisherHeader}>
              <Ionicons name="flash" size={18} color={selectedWorkout.color} />
              <Text style={styles.finisherTitle}>Finisher</Text>
            </View>
            <Text style={styles.finisherText}>{selectedWorkout.finisher}</Text>
          </View>
        )}

        {selectedWorkout.notes && (
          <View style={styles.notesSection}>
            <Ionicons name="information-circle-outline" size={18} color="#F59E0B" />
            <Text style={styles.notesText}>{selectedWorkout.notes}</Text>
          </View>
        )}

        <TouchableOpacity style={[styles.startWorkoutBtn, { backgroundColor: selectedWorkout.color }]} onPress={startWorkout}>
          <Ionicons name="play" size={20} color="#fff" />
          <Text style={styles.startWorkoutText}>Start Workout</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.quickStartBtn} onPress={() => {
          route.params.setWorkoutStackData({ customWorkoutData: { exercises: [], label: 'Custom Workout', color: '#6366F1', icon: 'fitness', focus: 'Mixed', unit: 'lb' }, addToExisting: false });
          navigation.navigate('QuickStart');
        }}>
          <Ionicons name="flash" size={18} color="#6366F1" />
          <Text style={styles.quickStartBtnText}>Quick Start Custom Workout</Text>
        </TouchableOpacity>
      </View>

      {(!selectedWorkout || !selectedWorkout.exercises?.length) && (
        <View style={styles.emptyWorkoutContainer}>
          <Text style={styles.emptyWorkoutText}>No exercises for {selectedDay}.</Text>
          <TouchableOpacity
            style={styles.emptyStartBtn}
            onPress={() => {
              route.params.setWorkoutStackData({ customWorkoutData: { exercises: [], label: 'Custom Workout', color: '#6366F1', icon: 'fitness', focus: 'Mixed', unit: 'lb' }, addToExisting: false });
              navigation.navigate('QuickStart');
            }}
          >
            <Ionicons name="flash" size={18} color="#6366F1" />
            <Text style={styles.emptyStartBtnText}>Start Custom Workout</Text>
          </TouchableOpacity>
        </View>
      )}

      {workoutHistory.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Workouts</Text>
          {workoutHistory.slice(0, 5).map(session => (
            <View key={session.id} style={styles.historyCard}>
              <View style={styles.historyHeader}>
                <Text style={styles.historyTitle}>{session.label}</Text>
                <Text style={styles.historyDate}>{new Date(session.completedAt).toLocaleDateString()}</Text>
              </View>
              <Text style={styles.historyDuration}>{formatTime(session.durationSeconds)}</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  content: { padding: 16, paddingBottom: 100 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  headerRight: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  unitToggle: {
    backgroundColor: '#1F2937',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#6366F1',
  },
  unitToggleText: { color: '#6366F1', fontSize: 14, fontWeight: '700' },
  greeting: { fontSize: 28, fontWeight: '700', color: '#F9FAFB' },
  date: { fontSize: 14, color: '#9CA3AF', marginTop: 2 },
  syncBadge: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#1F2937', justifyContent: 'center', alignItems: 'center' },
  daySelector: { marginBottom: 20 },
  dayPill: { paddingHorizontal: 16, paddingVertical: 10, backgroundColor: '#1F2937', borderRadius: 14, marginRight: 10, alignItems: 'center', minWidth: 60 },
  dayPillSelected: { backgroundColor: '#6366F1' },
  dayPillToday: { borderWidth: 1, borderColor: '#6366F1' },
  dayPillText: { fontSize: 13, fontWeight: '700', color: '#9CA3AF' },
  dayPillTextSelected: { color: '#fff' },
  dayPillSub: { fontSize: 11, color: '#6B7280', marginTop: 2 },
  workoutCard: { backgroundColor: '#1F2937', borderRadius: 20, overflow: 'hidden', marginBottom: 16, borderWidth: 1 },
  workoutHeader: { flexDirection: 'row', alignItems: 'center', padding: 20, gap: 14 },
  workoutIcon: { width: 44, height: 44, borderRadius: 14, justifyContent: 'center', alignItems: 'center' },
  workoutHeaderInfo: { flex: 1 },
  workoutLabel: { fontSize: 20, fontWeight: '800', color: '#F9FAFB' },
  workoutFocus: { fontSize: 13, color: '#D1D5DB', marginTop: 2 },
  exerciseCount: { alignItems: 'center' },
  exerciseCountNum: { fontSize: 24, fontWeight: '800', color: '#F9FAFB' },
  exerciseCountLabel: { fontSize: 10, color: '#9CA3AF', textTransform: 'uppercase' },
  exerciseCard: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: '#111827' },
  exerciseLeft: { flexDirection: 'row', alignItems: 'center', gap: 14, flex: 1 },
  exerciseIndex: { width: 28, height: 28, borderRadius: 14, backgroundColor: '#111827', justifyContent: 'center', alignItems: 'center' },
  exerciseIndexText: { fontSize: 12, fontWeight: '700', color: '#6366F1' },
  exerciseInfo: { flex: 1 },
  exerciseName: { fontSize: 15, fontWeight: '700', color: '#F9FAFB' },
  exerciseMuscle: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  exerciseRight: { alignItems: 'flex-end' },
  lastWeightText: { fontSize: 11, color: '#9CA3AF', marginBottom: 2 },
  suggestedText: { fontSize: 11, color: '#10B981', fontWeight: '600', marginBottom: 2 },
  exerciseSetsReps: { fontSize: 15, fontWeight: '700', color: '#F9FAFB' },
  exerciseWeight: { fontSize: 13, color: '#6366F1', marginTop: 2 },
  exerciseRest: { fontSize: 11, color: '#6B7280', marginTop: 2 },
  exerciseList: {},
  finisherSection: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#111827', padding: 16, gap: 10 },
  finisherHeader: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  finisherTitle: { fontSize: 14, fontWeight: '700', color: '#F9FAFB' },
  finisherText: { fontSize: 14, color: '#9CA3AF', marginLeft: 4 },
  notesSection: { flexDirection: 'row', alignItems: 'center', padding: 14, gap: 8, borderTopWidth: 1, borderTopColor: '#374151' },
  notesText: { fontSize: 13, color: '#F59E0B', flex: 1 },
  startWorkoutBtn: { padding: 16, borderRadius: 16, margin: 20, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 10 },
  startWorkoutText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  quickStartBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, backgroundColor: '#1F2937', padding: 14, borderRadius: 14, marginHorizontal: 20, marginBottom: 10, borderWidth: 1, borderColor: '#374151' },
  quickStartBtnText: { color: '#6366F1', fontSize: 15, fontWeight: '600' },
  section: { marginBottom: 24 },
  sectionHeaderBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 12 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#F9FAFB', marginLeft: 4 },
  historyCard: { backgroundColor: '#1F2937', borderRadius: 16, padding: 16, marginBottom: 10 },
  historyHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  historyTitle: { fontSize: 16, fontWeight: '700', color: '#F9FAFB' },
  historyDate: { fontSize: 13, color: '#9CA3AF' },
  historyDuration: { fontSize: 14, color: '#6366F1' },
  emptyWorkoutContainer: { alignItems: 'center', paddingVertical: 20 },
  emptyWorkoutText: { fontSize: 14, color: '#6B7280', marginBottom: 12 },
  emptyStartBtn: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: '#1F2937', paddingHorizontal: 18, paddingVertical: 12, borderRadius: 14, borderWidth: 1, borderColor: '#374151' },
  emptyStartBtnText: { color: '#6366F1', fontSize: 14, fontWeight: '600' },
  restContainer: { paddingVertical: 60, alignItems: 'center' },
  restIconWrapper: { width: 88, height: 88, borderRadius: 44, backgroundColor: '#1F2937', justifyContent: 'center', alignItems: 'center', marginBottom: 16 },
  restTitle: { fontSize: 22, fontWeight: '700', color: '#F9FAFB', marginTop: 4 },
  restSubtitle: { fontSize: 15, color: '#9CA3AF', marginTop: 8, textAlign: 'center' },
  restHint: { fontSize: 14, color: '#6B7280', marginTop: 6, textAlign: 'center', fontStyle: 'italic' },
  timerBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1F2937', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, gap: 6 },
  timerText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  activeExerciseCard: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: '#111827' },
  activeExerciseLeft: { flexDirection: 'row', alignItems: 'center', gap: 14, flex: 1 },
  activeExerciseName: { fontSize: 16, fontWeight: '700', color: '#F9FAFB' },
  activeExerciseMuscle: { fontSize: 13, color: '#6B7280', marginTop: 2 },
  activeExerciseInfo: { flex: 1, marginLeft: 4 },
  activeExerciseInputsRow: { flexDirection: 'row', gap: 10 },
  activeExerciseInputGroup: { alignItems: 'center' },
  activeExerciseInputLabel: { fontSize: 10, color: '#6B7280', marginBottom: 2, textTransform: 'uppercase' },
  activeExerciseInput: {
    backgroundColor: '#111827',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
    fontSize: 16,
    fontWeight: '700',
    color: '#F9FAFB',
    width: 65,
    textAlign: 'center',
    borderWidth: 1,
    borderColor: '#374151',
  },
  activeExerciseRight: { alignItems: 'flex-end' },
  activeExerciseSetsReps: { fontSize: 16, fontWeight: '700', color: '#6366F1' },
  activeExerciseWeight: { fontSize: 13, color: '#9CA3AF', marginTop: 2 },
  editWeightBtn: { marginTop: 4, padding: 4 },

  // Strong-style workout logging
  exerciseBlock: { flexDirection: 'row', marginBottom: 16, borderRadius: 16, overflow: 'hidden', backgroundColor: '#1F2937' },
  exerciseColorBar: { width: 5 },
  exerciseBlockContent: { flex: 1, padding: 16 },
  exerciseBlockHeader: { marginBottom: 12 },
  exerciseBlockTitleRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 2 },
  exerciseUnitToggle: {
    backgroundColor: '#111827',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#374151',
  },
  exerciseNameRow: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  sessionReorderBtn: { padding: 4 },
  exerciseUnitToggleText: { color: '#6366F1', fontSize: 12, fontWeight: '700' },
  exerciseBlockMuscle: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
  exerciseActions: { flexDirection: 'row', justifyContent: 'flex-end', marginTop: 8, paddingTop: 8, borderTopWidth: 1, borderTopColor: '#111827' },
  exerciseActionBtn: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 8, paddingVertical: 4 },
  exerciseActionBtnText: { color: '#EF4444', fontSize: 12, fontWeight: '600' },
  addExerciseBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, backgroundColor: '#1F2937', padding: 14, borderRadius: 14, borderWidth: 1, borderColor: '#374151', borderStyle: 'dashed' },
  addExerciseBtnText: { color: '#6366F1', fontSize: 14, fontWeight: '600' },
  exerciseBlockName: { fontSize: 18, fontWeight: '800' },
  setTableHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 6, paddingHorizontal: 4 },
  setTableHeaderText: { fontSize: 10, color: '#6B7280', fontWeight: '600', textTransform: 'uppercase' },
  setTableRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 6 },
  setNumLabelContainer: { flexDirection: 'row', alignItems: 'center', gap: 4, width: 36 },
  setNumLabel: { fontSize: 13, color: '#9CA3AF', fontWeight: '700' },
  deleteSetBtn: { width: 18, height: 18, borderRadius: 9, backgroundColor: '#374151', justifyContent: 'center', alignItems: 'center' },
  prevText: { flex: 1, fontSize: 12, color: '#6B7280', fontStyle: 'italic' },
  setInput: {
    backgroundColor: '#111827',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 15,
    fontWeight: '700',
    color: '#F9FAFB',
    width: 70,
    textAlign: 'center',
    borderWidth: 1,
    borderColor: '#374151',
  },
  setInputReps: { width: 60 },
  setInputDone: { borderColor: '#10B981', color: '#10B981' },
  setCheckCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#111827',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 6,
  },
  setCheckCircleDone: { backgroundColor: '#6366F1' },
  addSetBtn: { alignItems: 'center', paddingVertical: 10, marginTop: 4 },
  addSetBtnText: { color: '#6366F1', fontSize: 13, fontWeight: '700' },
  activeExerciseHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  setsContainer: { gap: 6 },
  setRow: { flexDirection: 'row', alignItems: 'center', gap: 10, backgroundColor: '#111827', borderRadius: 10, paddingHorizontal: 12, paddingVertical: 8 },
  setNumText: { fontSize: 12, color: '#9CA3AF', fontWeight: '600', width: 36 },
  setWeightInput: {
    backgroundColor: '#1F2937',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
    fontSize: 15,
    fontWeight: '700',
    color: '#F9FAFB',
    width: 70,
    textAlign: 'center',
    borderWidth: 1,
    borderColor: '#374151',
  },
  setWeightLabel: { fontSize: 13, color: '#6B7280', width: 20 },
  setCheckBtn: { width: 32, height: 32, borderRadius: 16, backgroundColor: '#1F2937', justifyContent: 'center', alignItems: 'center' },
  setCheckBtnDone: { backgroundColor: '#10B981' },
  finishWorkoutBtn: { padding: 16, borderRadius: 16, margin: 20, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 10 },
  finishWorkoutText: { color: '#fff', fontSize: 16, fontWeight: '700' },

  // Modal
  modalTitle: { fontSize: 22, fontWeight: '800', color: '#F9FAFB', marginBottom: 4 },
  modalSubtitle: { fontSize: 14, color: '#9CA3AF', marginBottom: 20 },
  modalRow: { flexDirection: 'row', gap: 12, marginBottom: 16 },
  modalHalf: { flex: 1 },
  modalLabel: { fontSize: 13, color: '#9CA3AF', marginBottom: 6 },
  modalValue: { fontSize: 28, fontWeight: '800', color: '#6366F1' },
  modalStepperRow: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  modalStepperBtn: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#374151', justifyContent: 'center', alignItems: 'center' },
  modalStepperNum: { fontSize: 24, fontWeight: '700', color: '#F9FAFB', minWidth: 40, textAlign: 'center' },
  modalTextInput: { backgroundColor: '#111827', borderRadius: 12, paddingHorizontal: 16, paddingVertical: 12, fontSize: 20, color: '#F9FAFB', borderWidth: 1, borderColor: '#374151', textAlign: 'center', marginTop: 4 },
  modalDoneBtn: { backgroundColor: '#6366F1', padding: 16, borderRadius: 16, marginTop: 20 },
  modalDoneBtnText: { color: '#fff', fontSize: 16, fontWeight: '700', textAlign: 'center' },

  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.7)' },
  modalContainer: { width: '90%', backgroundColor: '#1F2937', borderRadius: 20, padding: 24 },
  summaryTitle: { fontSize: 24, fontWeight: '800', color: '#F9FAFB', marginBottom: 20 },
  summaryContent: { marginBottom: 30, alignItems: 'center' },
  summaryText: { fontSize: 16, color: '#D1D5DB', marginBottom: 8 },
  summaryHighlight: { fontWeight: '700', color: '#6366F1' },
  modalBtn: { backgroundColor: '#6366F1', paddingHorizontal: 30, paddingVertical: 12, borderRadius: 14 },
  modalBtnText: { color: '#fff', fontSize: 18, fontWeight: '700' },
});