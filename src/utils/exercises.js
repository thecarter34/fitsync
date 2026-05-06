import AsyncStorage from '@react-native-async-storage/async-storage';

const EXERCISES_KEY = '@fitsync:exercises';
const LAST_SESSION_KEY = '@fitsync:last_session';

// Josh's actual workout program - seeded into AsyncStorage on first load
export const INITIAL_WORKOUTS = {
  monday: {
    label: 'Power Day',
    type: 'full-body',
    focus: 'Strength & Power',
    color: '#6366F1',
    icon: 'fitness',
    exercises: [
      { name: 'Strict Barbell OHP', sets: 4, reps: '5-6', weight: 115, rest: '90 sec', muscle: 'Shoulders' },
      { name: 'RDLs', sets: 4, reps: 8, weight: 185, rest: '90 sec', muscle: 'Posterior Chain' },
      { name: 'DB Bulgarian Split Squats', sets: 3, reps: '8/leg', weight: 40, rest: '75 sec', muscle: 'Quads/Glutes' },
      { name: 'SA DB Bent-Over Rows', sets: 4, reps: '8/hand', weight: 70, rest: '60 sec', muscle: 'Back' },
      { name: 'KB Swings', sets: 3, reps: 12, weight: 53, rest: '60 sec', muscle: 'Glutes/Hams' },
      { name: 'Pallof Press', sets: 3, reps: '10/hold', weight: 0, rest: '45 sec', muscle: 'Core' },
    ],
    finisher: 'Jump rope 1,000 reps (~6:45) or Air bike Tabata 8 rounds',
    notes: 'Back: watch for lower right tightness — reduce RDL weight if needed',
  },
  tuesday: {
    label: 'Recovery',
    type: 'active-recovery',
    focus: 'Mobility & Light Cardio',
    color: '#8B5CF6',
    icon: 'walk',
    exercises: [],
    finisher: 'Stretch or light walk',
    notes: 'Active recovery — keep it easy.',
  },
  wednesday: {
    label: 'Volleyball Day',
    type: 'sport-prep',
    focus: 'Dynamic Warm-Up + Power',
    color: '#10B981',
    icon: 'football',
    exercises: [
      { name: 'Band Pull-Aparts', sets: 3, reps: 15, weight: 0, rest: '45 sec', muscle: 'Rear Delts' },
      { name: 'Inchworms', sets: 3, reps: 6, weight: 0, rest: '45 sec', muscle: 'Hamstrings/Shoulders' },
      { name: 'Goblet Squats', sets: 3, reps: 10, weight: 40, rest: '60 sec', muscle: 'Legs' },
      { name: 'Box Jumps', sets: 3, reps: 6, weight: 0, rest: '60 sec', muscle: 'Power' },
      { name: 'MB Overhead Slams', sets: 3, reps: 8, weight: 10, rest: '45 sec', muscle: 'Core/Shoulders' },
      { name: 'Jump Rope Sprints', sets: 4, reps: '30 sec on', weight: 0, rest: '30 sec', muscle: 'Calves' },
    ],
    finisher: 'Light jump rope 2 min — stay loose',
    notes: 'Volleyball double header — keep workout snappy. Dynamic warm-up only, don\'t lift heavy.',
  },
  thursday: {
    label: 'Rest',
    type: 'rest',
    focus: 'Recovery',
    color: '#6B7280',
    icon: 'moon',
    exercises: [],
    finisher: '',
    notes: '',
  },
  friday: {
    label: 'Pump Day',
    type: 'hypertrophy',
    focus: 'Shoulders · Upper Chest · V-Taper',
    color: '#EC4899',
    icon: 'barbell',
    exercises: [
      { name: 'Incline DB Press', sets: 4, reps: '10-12', weight: 55, rest: '60-90 sec', muscle: 'Upper Chest' },
      { name: 'Lean-Away Lateral Raises', sets: 4, reps: '12-15', weight: 18, rest: '60 sec', muscle: 'Side Delts' },
      { name: 'Strict OHP', sets: 4, reps: '8-10', weight: 115, rest: '60-90 sec', muscle: 'Shoulders' },
      { name: 'High Cable Flyes', sets: 3, reps: 12, weight: 25, rest: '60 sec', muscle: 'Upper Chest' },
      { name: 'Lat Pull-Downs', sets: 4, reps: '10-12', weight: 135, rest: '60 sec', muscle: 'Lats' },
      { name: 'SA DB Bent-Over Rows', sets: 3, reps: '10/hand', weight: 70, rest: '60 sec', muscle: 'Back' },
      { name: 'Face Pulls', sets: 3, reps: 15, weight: 0, rest: '45 sec', muscle: 'Rear Delts' },
    ],
    finisher: 'Shrugs 3x20 (barbell or traps) + Rope Crush Curls or Reverse Flyes',
    notes: 'V-taper focus — back, shoulders, upper chest. 2-sec eccentrics, squeeze at top.',
  },
  saturday: {
    label: 'Metabolic Day',
    type: 'metabolic',
    focus: 'Conditioning & Endurance',
    color: '#F59E0B',
    icon: 'flame',
    exercises: [
      { name: 'Air Bike Tabata', sets: 8, reps: '20sec on / 10sec off', weight: 0, rest: 'none', muscle: 'Full Body' },
      { name: 'KB Swings (Circuit)', sets: 4, reps: 15, weight: 53, rest: '45 sec', muscle: 'Posterior Chain' },
      { name: 'Box Jumps / Step-Ups', sets: 3, reps: 10, weight: 0, rest: '60 sec', muscle: 'Legs' },
      { name: 'Wall Balls', sets: 3, reps: 15, weight: 0, rest: '45 sec', muscle: 'Full Body' },
      { name: 'Jump Rope Intervals', sets: 5, reps: '200 reps', weight: 0, rest: '30 sec', muscle: 'Calves' },
    ],
    finisher: 'Air bike Tabata 8 rounds or jump rope 1,000 reps',
    notes: 'Metabolic burn. Go hard, rest minimal between exercises.',
  },
  sunday: {
    label: 'Rest',
    type: 'rest',
    focus: 'Recovery',
    color: '#6B7280',
    icon: 'moon',
    exercises: [],
    finisher: '',
    notes: '',
  },
};

export async function getExercises() {
  try {
    const data = await AsyncStorage.getItem(EXERCISES_KEY);
    return data ? JSON.parse(data) : null;
  } catch (e) {
    console.error('getExercises error:', e);
    return null;
  }
}

export async function saveExercises(exercises) {
  try {
    await AsyncStorage.setItem(EXERCISES_KEY, JSON.stringify(exercises));
  } catch (e) {
    console.error('saveExercises error:', e);
  }
}

export async function getLastSession(exerciseName) {
  try {
    const data = await AsyncStorage.getItem(LAST_SESSION_KEY);
    if (!data) return null;
    const sessions = JSON.parse(data);
    const filtered = sessions.filter(s => s.exerciseName === exerciseName);
    return filtered.length > 0 ? filtered[0] : null;
  } catch (e) {
    console.error('getLastSession error:', e);
    return null;
  }
}

export async function saveSessionResult(exerciseName, weight, sets, reps, unit = 'lb') {
  try {
    const data = await AsyncStorage.getItem(LAST_SESSION_KEY);
    const sessions = data ? JSON.parse(data) : [];
    sessions.unshift({ exerciseName, weight, sets, reps, unit, date: new Date().toISOString() });
    const trimmed = sessions.slice(0, 100);
    await AsyncStorage.setItem(LAST_SESSION_KEY, JSON.stringify(trimmed));
  } catch (e) {
    console.error('saveSessionResult error:', e);
  }
}

export async function getAllLastSessions() {
  try {
    const data = await AsyncStorage.getItem(LAST_SESSION_KEY);
    if (!data) return {};
    const sessions = JSON.parse(data);
    const latest = {};
    for (const session of sessions) {
      if (!latest[session.exerciseName] || new Date(session.date) > new Date(latest[session.exerciseName].date)) {
        latest[session.exerciseName] = session;
      }
    }
    return latest;
  } catch (e) {
    console.error('getAllLastSessions error:', e);
    return {};
  }
}

export function getSuggestedWeight(lastWeight, lastSetsCompleted, targetSets) {
  if (!lastWeight) return null;
  if (lastSetsCompleted >= targetSets) {
    return lastWeight + 5;
  }
  return lastWeight;
}