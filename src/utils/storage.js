import AsyncStorage from '@react-native-async-storage/async-storage';

const WORKOUT_HISTORY_KEY = '@fitsync:workout_history';

export async function saveWorkoutSession(session) {
  try {
    const history = await getWorkoutHistory();
    const sessionWithId = {
      ...session,
      id: Date.now().toString(),
      completedAt: new Date().toISOString(),
    };
    history.unshift(sessionWithId); // newest first
    await AsyncStorage.setItem(WORKOUT_HISTORY_KEY, JSON.stringify(history));
    return sessionWithId;
  } catch (e) {
    console.error('saveWorkoutSession error:', e);
    throw e;
  }
}

export async function getWorkoutHistory() {
  try {
    const data = await AsyncStorage.getItem(WORKOUT_HISTORY_KEY);
    return data ? JSON.parse(data) : [];
  } catch (e) {
    console.error('getWorkoutHistory error:', e);
    return [];
  }
}

export async function deleteWorkoutSession(sessionId) {
  try {
    const history = await getWorkoutHistory();
    const filtered = history.filter(s => s.id !== sessionId);
    await AsyncStorage.setItem(WORKOUT_HISTORY_KEY, JSON.stringify(filtered));
  } catch (e) {
    console.error('deleteWorkoutSession error:', e);
  }
}

export async function clearWorkoutHistory() {
  try {
    await AsyncStorage.removeItem(WORKOUT_HISTORY_KEY);
  } catch (e) {
    console.error('clearWorkoutHistory error:', e);
  }
}