import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity,
  FlatList, ActivityIndicator, Modal, KeyboardAvoidingView, Platform
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

const FOOD_LOG_KEY = '@fitsync_food_log';
const WATER_LOG_KEY = '@fitsync_water_log';
const DAILY_TARGETS_KEY = '@fitsync_daily_targets';

// Default daily targets (can be customized)
const DEFAULT_TARGETS = {
  calories: 2200,
  protein: 180,
  carbs: 220,
  fat: 73,
  fiber: 35,
  water: 8, // glasses
};

const WATER_KEY = '@fitsync_water_target';

// Search Open Food Facts API
async function searchFoods(query) {
  if (!query || query.length < 2) return [];
  try {
    const response = await fetch(
      `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(query)}&search_simple=1&action=process&json=1&page_size=20&fields=code,product_name,nutriments,serving_size,serving_quantity`,
      {
        headers: {
          'User-Agent': 'FitSync/1.0 (React Native; Android)',
        },
      }
    );
    if (!response.ok) {
      console.error('Food search HTTP error:', response.status);
      return [];
    }
    const text = await response.text();
    if (!text || text.startsWith('<')) {
      console.error('Food search invalid response');
      return [];
    }
    const data = JSON.parse(text);
    if (!data.products) return [];
    return data.products
      .filter(p => p.product_name)
      .map(p => {
        const n = p.nutriments || {};
        const serving_g = p.serving_quantity ? parseFloat(p.serving_quantity) : 100;
        const factor = serving_g / 100;
        return {
          id: p.code || `${p.product_name}-${Date.now()}`,
          name: p.product_name,
          brand: p.brands || '',
          serving: p.serving_size || `${serving_g}g`,
          calories: Math.round((n['energy-kcal_100g'] || 0) * factor),
          protein: Math.round((n.proteins_100g || 0) * factor * 10) / 10,
          carbs: Math.round((n.carbohydrates_100g || 0) * factor * 10) / 10,
          fat: Math.round((n['fat_100g'] || 0) * factor * 10) / 10,
          fiber: Math.round((n.fiber_100g || 0) * factor * 10) / 10,
          barcode: p.code || null,
        };
      });
  } catch (e) {
    console.error('Food search error:', e.message || e);
    return [];
  }
}

function getTodayKey() {
  return new Date().toISOString().split('T')[0];
}

// Food log
async function loadFoodLog() {
  try {
    const data = await AsyncStorage.getItem(FOOD_LOG_KEY);
    return data ? JSON.parse(data) : {};
  } catch (e) {
    return {};
  }
}

async function saveFoodLog(log) {
  try {
    await AsyncStorage.setItem(FOOD_LOG_KEY, JSON.stringify(log));
  } catch (e) {
    console.error('Save food log error:', e);
  }
}

// Water log
async function loadWaterLog() {
  try {
    const data = await AsyncStorage.getItem(WATER_LOG_KEY);
    return data ? JSON.parse(data) : {};
  } catch (e) {
    return {};
  }
}

async function saveWaterLog(log) {
  try {
    await AsyncStorage.setItem(WATER_LOG_KEY, JSON.stringify(log));
  } catch (e) {
    console.error('Save water log error:', e);
  }
}

// Targets
async function loadTargets() {
  try {
    const data = await AsyncStorage.getItem(DAILY_TARGETS_KEY);
    return data ? JSON.parse(data) : DEFAULT_TARGETS;
  } catch (e) {
    return DEFAULT_TARGETS;
  }
}

async function saveTargets(targets) {
  try {
    await AsyncStorage.setItem(DAILY_TARGETS_KEY, JSON.stringify(targets));
  } catch (e) {
    console.error('Save targets error:', e);
  }
}

function WaterTracker({ current, target, onAdd, onRemove }) {
  const pct = Math.min(current / target, 1);
  const size = 64;
  const stroke = 6;
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ * (1 - pct);

  return (
    <View style={waterStyles.container}>
      <View style={waterStyles.header}>
        <View style={waterStyles.titleRow}>
          <Ionicons name="water" size={18} color="#06B6D4" />
          <Text style={waterStyles.title}>Water</Text>
        </View>
        <View style={waterStyles.controls}>
          <TouchableOpacity style={waterStyles.controlBtn} onPress={onRemove}>
            <Ionicons name="remove" size={20} color="#6B7280" />
          </TouchableOpacity>
          <View style={waterStyles.countContainer}>
            <Text style={waterStyles.count}>{current}</Text>
            <Text style={waterStyles.target}>/ {target} glasses</Text>
          </View>
          <TouchableOpacity style={[waterStyles.controlBtn, waterStyles.addBtn]} onPress={onAdd}>
            <Ionicons name="add" size={20} color="#06B6D4" />
          </TouchableOpacity>
        </View>
      </View>
      <View style={waterStyles.barContainer}>
        <View style={[waterStyles.barFill, { width: `${pct * 100}%` }]} />
      </View>
    </View>
  );
}

const waterStyles = StyleSheet.create({
  container: { backgroundColor: '#1E3A5F', borderRadius: 16, padding: 14, marginBottom: 16 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  titleRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  title: { fontSize: 15, fontWeight: '700', color: '#F9FAFB' },
  controls: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  controlBtn: { width: 32, height: 32, borderRadius: 16, backgroundColor: '#0F172A', justifyContent: 'center', alignItems: 'center' },
  addBtn: { backgroundColor: '#0F172A' },
  countContainer: { flexDirection: 'row', alignItems: 'baseline', gap: 4 },
  count: { fontSize: 20, fontWeight: '800', color: '#06B6D4' },
  target: { fontSize: 13, color: '#6B7280' },
  barContainer: { height: 6, backgroundColor: '#0F172A', borderRadius: 3, overflow: 'hidden' },
  barFill: { height: '100%', backgroundColor: '#06B6D4', borderRadius: 3 },
});

function MacroRing({ current, target, color, label }) {
  const pct = Math.min(current / target, 1);
  const size = 56;
  const stroke = 5;
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ * (1 - pct);

  return (
    <View style={styles.macroRing}>
      <View style={{ width: size, height: size, position: 'relative' }}>
        <View style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, borderRadius: size/2, border: `${stroke}px solid #374151` }} />
        <View style={{
          width: size, height: size, borderRadius: size/2,
          border: `${stroke}px solid transparent`,
          borderTopColor: pct >= 0.25 ? color : 'transparent',
          borderRightColor: pct >= 0.5 ? color : 'transparent',
          borderBottomColor: pct >= 0.75 ? color : 'transparent',
          borderLeftColor: pct >= 0.125 ? color : 'transparent',
          position: 'absolute',
          transform: [{ rotate: '-90deg' }],
        }} />
        <View style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, justifyContent: 'center', alignItems: 'center' }}>
          <Text style={[styles.macroValue, { color }]}>{Math.round(current)}</Text>
        </View>
      </View>
      <Text style={styles.macroLabel}>{label}</Text>
    </View>
  );
}

export default function FoodLog({ navigation }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [todayLog, setTodayLog] = useState([]);
  const [waterCount, setWaterCount] = useState(0);
  const [targets, setTargets] = useState(DEFAULT_TARGETS);
  const [editModal, setEditModal] = useState(null);
  const [targetsModal, setTargetsModal] = useState(null);
  const [localTargets, setLocalTargets] = useState(DEFAULT_TARGETS);

  const todayKey = getTodayKey();
  const today = new Date();
  const dateStr = today.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

  // Load saved data
  useEffect(() => {
    async function load() {
      const [log, t, water] = await Promise.all([loadFoodLog(), loadTargets(), loadWaterLog()]);
      setTargets(t);
      setLocalTargets(t);
      setTodayLog(log[todayKey] || []);
      setWaterCount(water[todayKey] || 0);
    }
    load();
  }, []);

  // Search debounce
  useEffect(() => {
    if (!searchQuery || searchQuery.length < 2) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setIsSearching(true);
      const results = await searchFoods(searchQuery);
      setSearchResults(results);
      setIsSearching(false);
    }, 400);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Save food log
  const saveLog = useCallback(async (log) => {
    setTodayLog(log);
    const all = await loadFoodLog();
    all[todayKey] = log;
    await saveFoodLog(all);
  }, [todayKey]);

  // Save water
  const saveWater = useCallback(async (count) => {
    setWaterCount(count);
    const all = await loadWaterLog();
    all[todayKey] = count;
    await saveWaterLog(all);
  }, [todayKey]);

  // Water controls
  const addWater = useCallback(() => {
    saveWater(Math.min(waterCount + 1, 20));
  }, [waterCount, saveWater]);

  const removeWater = useCallback(() => {
    saveWater(Math.max(waterCount - 1, 0));
  }, [waterCount, saveWater]);

  // Delete food item
  const deleteItem = useCallback((item, index) => {
    const newLog = [...todayLog];
    newLog.splice(index, 1);
    saveLog(newLog);
  }, [todayLog, saveLog]);

  // Add food from search
  const addFood = useCallback((food) => {
    const newLog = [...todayLog, { ...food, loggedAt: new Date().toISOString() }];
    saveLog(newLog);
    setSearchQuery('');
    setSearchResults([]);
    setShowSearch(false);
  }, [saveLog]);

  // Edit existing food
  const editFood = useCallback((item, index) => {
    setEditModal({ item, index });
  }, []);

  // Save edited food
  const saveEdit = useCallback((updated) => {
    if (!editModal) return;
    const newLog = [...todayLog];
    newLog[editModal.index] = { ...newLog[editModal.index], ...updated };
    saveLog(newLog);
    setEditModal(null);
  }, [editModal, todayLog, saveLog]);

  // Open targets modal
  const openTargetsModal = useCallback(() => {
    setLocalTargets({ ...targets });
    setTargetsModal(true);
  }, [targets]);

  // Save targets
  const saveTargetsHandler = useCallback(async () => {
    await saveTargets(localTargets);
    setTargets(localTargets);
    setTargetsModal(null);
  }, [localTargets]);

  // Calculate daily totals
  const totals = todayLog.reduce((acc, item) => ({
    calories: acc.calories + (item.calories || 0),
    protein: acc.protein + (item.protein || 0),
    carbs: acc.carbs + (item.carbs || 0),
    fat: acc.fat + (item.fat || 0),
    fiber: acc.fiber + (item.fiber || 0),
  }), { calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0 });

  const remaining = {
    calories: Math.max(0, targets.calories - totals.calories),
    protein: Math.max(0, targets.protein - totals.protein),
    carbs: Math.max(0, targets.carbs - totals.carbs),
    fat: Math.max(0, targets.fat - totals.fat),
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Food Log</Text>
          <Text style={styles.subtitle}>{dateStr}</Text>
        </View>
        <View style={styles.headerRight}>
          <TouchableOpacity style={styles.searchToggle} onPress={() => setShowSearch(!showSearch)}>
            <Ionicons name={showSearch ? 'close' : 'search'} size={22} color="#6366F1" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.searchToggle} onPress={openTargetsModal}>
            <Ionicons name="options-outline" size={22} color="#6366F1" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Search Bar */}
      {showSearch && (
        <View style={styles.searchBar}>
          <Ionicons name="search" size={18} color="#6B7280" style={{ marginRight: 10 }} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search foods..."
            placeholderTextColor="#6B7280"
            value={searchQuery}
            onChangeText={setSearchQuery}
            autoFocus
          />
          <TouchableOpacity onPress={() => navigation.navigate('Scan')}>
            <Ionicons name="barcode-camera" size={22} color="#6366F1" />
          </TouchableOpacity>
        </View>
      )}

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Daily Summary */}
        <View style={styles.summaryCard}>
          <View style={styles.calorieSummary}>
            <View style={styles.calorieMain}>
              <Text style={styles.calorieEaten}>{totals.calories}</Text>
              <Text style={styles.calorieLabel}>eaten</Text>
            </View>
            <View style={styles.calorieDivider} />
            <View style={styles.calorieMain}>
              <Text style={[styles.calorieEaten, { color: '#10B981' }]}>{remaining.calories}</Text>
              <Text style={styles.calorieLabel}>remaining</Text>
            </View>
            <View style={styles.calorieDivider} />
            <View style={styles.calorieMain}>
              <Text style={styles.calorieTarget}>{targets.calories}</Text>
              <Text style={styles.calorieLabel}>target</Text>
            </View>
          </View>

          {/* Macro rings */}
          <View style={styles.macroRings}>
            <MacroRing current={totals.protein} target={targets.protein} color="#6366F1" label="Protein" />
            <MacroRing current={totals.carbs} target={targets.carbs} color="#F59E0B" label="Carbs" />
            <MacroRing current={totals.fat} target={targets.fat} color="#EC4899" label="Fat" />
          </View>
        </View>

        {/* Water Tracker */}
        <WaterTracker
          current={waterCount}
          target={targets.water}
          onAdd={addWater}
          onRemove={removeWater}
        />

        {/* Search Results */}
        {showSearch && searchResults.length > 0 && (
          <View style={styles.searchResultsContainer}>
            <Text style={styles.sectionTitle}>Search Results</Text>
            {searchResults.map((item) => (
              <TouchableOpacity key={item.id} style={styles.searchResult} onPress={() => addFood(item)}>
                <View style={styles.searchResultInfo}>
                  <Text style={styles.searchResultName}>{item.name}</Text>
                  {item.brand ? <Text style={styles.searchResultBrand}>{item.brand}</Text> : null}
                  <Text style={styles.searchResultServing}>{item.serving}</Text>
                </View>
                <View style={styles.searchResultMacros}>
                  <Text style={styles.searchResultCal}>{item.calories} kcal</Text>
                  <Text style={styles.searchResultMacroText}>P: {item.protein} C: {item.carbs} F: {item.fat}</Text>
                  <Ionicons name="add-circle" size={26} color="#6366F1" style={{ marginTop: 4 }} />
                </View>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {showSearch && isSearching && (
          <View style={styles.searchingContainer}>
            <ActivityIndicator color="#6366F1" />
            <Text style={styles.searchingText}>Searching...</Text>
          </View>
        )}

        {showSearch && searchQuery.length >= 2 && !isSearching && searchResults.length === 0 && (
          <View style={styles.noResults}>
            <Ionicons name="search-outline" size={40} color="#374151" />
            <Text style={styles.noResultsText}>No foods found for "{searchQuery}"</Text>
            <Text style={styles.noResultsSubtext}>Try a different search or scan a barcode</Text>
          </View>
        )}

        {/* Meals */}
        {todayLog.length === 0 && !showSearch && (
          <View style={styles.emptyState}>
            <Ionicons name="restaurant-outline" size={60} color="#374151" />
            <Text style={styles.emptyStateTitle}>No foods logged today</Text>
            <Text style={styles.emptyStateText}>Tap the + button below or search to add food</Text>
          </View>
        )}

        {todayLog.length > 0 && (
          <View style={styles.mealsList}>
            <Text style={styles.sectionTitle}>Today's Foods</Text>
            {todayLog.map((item, idx) => (
              <TouchableOpacity
                key={idx}
                style={styles.loggedFoodItem}
                onPress={() => editFood(item, idx)}
              >
                <View style={styles.loggedFoodInfo}>
                  <Text style={styles.loggedFoodName}>{item.name}</Text>
                  <Text style={styles.loggedFoodServing}>{item.serving}</Text>
                </View>
                <View style={styles.loggedFoodMacros}>
                  <Text style={styles.loggedFoodCal}>{item.calories} kcal</Text>
                  <Text style={styles.loggedFoodMacroText}>P: {item.protein} C: {item.carbs} F: {item.fat}</Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* Quick Add */}
        <TouchableOpacity style={styles.addMealBtn} onPress={() => setShowSearch(true)}>
          <Ionicons name="add" size={22} color="#6366F1" />
          <Text style={styles.addMealText}>Add Food</Text>
        </TouchableOpacity>
      </ScrollView>

      {/* Bottom Bar */}
      <View style={styles.bottomBar}>
        <TouchableOpacity style={styles.logFoodBtn} onPress={() => setShowSearch(true)}>
          <Ionicons name="add" size={22} color="#fff" />
          <Text style={styles.logFoodText}>Log Food</Text>
        </TouchableOpacity>
      </View>

      {/* Edit Modal */}
      <Modal visible={!!editModal} transparent animationType="slide">
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {editModal && (
              <>
                <View style={styles.modalHeader}>
                  <Text style={styles.modalTitle}>Edit Food</Text>
                  <TouchableOpacity onPress={() => setEditModal(null)}>
                    <Ionicons name="close" size={24} color="#9CA3AF" />
                  </TouchableOpacity>
                </View>
                <Text style={styles.modalFoodName}>{editModal.item.name}</Text>

                <View style={styles.editRow}>
                  <Text style={styles.editLabel}>Serving</Text>
                  <TextInput
                    style={styles.editInput}
                    defaultValue={editModal.item.serving}
                    onChangeText={(text) => { editModal.item.serving = text; }}
                    placeholder="e.g. 1 cup"
                    placeholderTextColor="#6B7280"
                  />
                </View>
                <View style={styles.editRow}>
                  <Text style={styles.editLabel}>Calories</Text>
                  <TextInput
                    style={styles.editInput}
                    defaultValue={String(editModal.item.calories)}
                    keyboardType="numeric"
                    placeholder="0"
                    placeholderTextColor="#6B7280"
                    onChangeText={(text) => { editModal.item.calories = parseInt(text) || 0; }}
                  />
                </View>
                <View style={styles.editRow}>
                  <Text style={styles.editLabel}>Protein (g)</Text>
                  <TextInput
                    style={styles.editInput}
                    defaultValue={String(editModal.item.protein)}
                    keyboardType="numeric"
                    placeholder="0"
                    placeholderTextColor="#6B7280"
                    onChangeText={(text) => { editModal.item.protein = parseFloat(text) || 0; }}
                  />
                </View>
                <View style={styles.editRow}>
                  <Text style={styles.editLabel}>Carbs (g)</Text>
                  <TextInput
                    style={styles.editInput}
                    defaultValue={String(editModal.item.carbs)}
                    keyboardType="numeric"
                    placeholder="0"
                    placeholderTextColor="#6B7280"
                    onChangeText={(text) => { editModal.item.carbs = parseFloat(text) || 0; }}
                  />
                </View>
                <View style={styles.editRow}>
                  <Text style={styles.editLabel}>Fat (g)</Text>
                  <TextInput
                    style={styles.editInput}
                    defaultValue={String(editModal.item.fat)}
                    keyboardType="numeric"
                    placeholder="0"
                    placeholderTextColor="#6B7280"
                    onChangeText={(text) => { editModal.item.fat = parseFloat(text) || 0; }}
                  />
                </View>

                <TouchableOpacity
                  style={styles.saveBtn}
                  onPress={() => saveEdit({ ...editModal.item })}
                >
                  <Text style={styles.saveBtnText}>Save Changes</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={styles.deleteBtnLarge}
                  onPress={() => { deleteItem(editModal.item, editModal.index); setEditModal(null); }}
                >
                  <Ionicons name="trash" size={18} color="#EF4444" />
                  <Text style={styles.deleteBtnText}>Delete</Text>
                </TouchableOpacity>
              </>
            )}
          </View>
        </KeyboardAvoidingView>
      </Modal>

      {/* Targets Modal */}
      <Modal visible={!!targetsModal} transparent animationType="slide">
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>Daily Targets</Text>
                <TouchableOpacity onPress={() => setTargetsModal(null)}>
                  <Ionicons name="close" size={24} color="#9CA3AF" />
                </TouchableOpacity>
              </View>
              <Text style={styles.modalFoodName}>Set your daily nutrition goals</Text>

              <View style={styles.editRow}>
                <Text style={styles.editLabel}>Calories</Text>
                <TextInput
                  style={styles.editInput}
                  value={String(localTargets.calories)}
                  keyboardType="numeric"
                  placeholder="2200"
                  placeholderTextColor="#6B7280"
                  onChangeText={(text) => setLocalTargets(t => ({ ...t, calories: parseInt(text) || 0 }))}
                />
              </View>
              <View style={styles.editRow}>
                <Text style={styles.editLabel}>Protein (g)</Text>
                <TextInput
                  style={styles.editInput}
                  value={String(localTargets.protein)}
                  keyboardType="numeric"
                  placeholder="180"
                  placeholderTextColor="#6B7280"
                  onChangeText={(text) => setLocalTargets(t => ({ ...t, protein: parseInt(text) || 0 }))}
                />
              </View>
              <View style={styles.editRow}>
                <Text style={styles.editLabel}>Carbs (g)</Text>
                <TextInput
                  style={styles.editInput}
                  value={String(localTargets.carbs)}
                  keyboardType="numeric"
                  placeholder="220"
                  placeholderTextColor="#6B7280"
                  onChangeText={(text) => setLocalTargets(t => ({ ...t, carbs: parseInt(text) || 0 }))}
                />
              </View>
              <View style={styles.editRow}>
                <Text style={styles.editLabel}>Fat (g)</Text>
                <TextInput
                  style={styles.editInput}
                  value={String(localTargets.fat)}
                  keyboardType="numeric"
                  placeholder="73"
                  placeholderTextColor="#6B7280"
                  onChangeText={(text) => setLocalTargets(t => ({ ...t, fat: parseInt(text) || 0 }))}
                />
              </View>
              <View style={styles.editRow}>
                <Text style={styles.editLabel}>Water (glasses)</Text>
                <TextInput
                  style={styles.editInput}
                  value={String(localTargets.water)}
                  keyboardType="numeric"
                  placeholder="8"
                  placeholderTextColor="#6B7280"
                  onChangeText={(text) => setLocalTargets(t => ({ ...t, water: parseInt(text) || 0 }))}
                />
              </View>

              <TouchableOpacity style={styles.saveBtn} onPress={saveTargetsHandler}>
                <Text style={styles.saveBtnText}>Save Targets</Text>
              </TouchableOpacity>
            </>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingTop: 16, paddingBottom: 8 },
  headerRight: { flexDirection: 'row', gap: 8 },
  title: { fontSize: 28, fontWeight: '700', color: '#F9FAFB' },
  subtitle: { fontSize: 14, color: '#9CA3AF', marginTop: 2 },
  searchToggle: { width: 44, height: 44, borderRadius: 22, backgroundColor: '#1F2937', justifyContent: 'center', alignItems: 'center' },
  searchBar: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1F2937', marginHorizontal: 16, marginBottom: 12, paddingHorizontal: 14, borderRadius: 14, height: 48 },
  searchInput: { flex: 1, fontSize: 16, color: '#F9FAFB' },
  scrollView: { flex: 1 },
  content: { padding: 16, paddingBottom: 100 },

  // Summary Card
  summaryCard: { backgroundColor: '#1F2937', borderRadius: 20, padding: 20, marginBottom: 16 },
  calorieSummary: { flexDirection: 'row', justifyContent: 'space-around', marginBottom: 16 },
  calorieMain: { alignItems: 'center' },
  calorieEaten: { fontSize: 26, fontWeight: '800', color: '#F9FAFB' },
  calorieTarget: { fontSize: 26, fontWeight: '800', color: '#6B7280' },
  calorieDivider: { width: 1, backgroundColor: '#374151', alignSelf: 'center' },
  calorieLabel: { fontSize: 12, color: '#9CA3AF', marginTop: 4 },
  macroRings: { flexDirection: 'row', justifyContent: 'space-around' },
  macroRing: { alignItems: 'center' },
  macroValue: { fontSize: 13, fontWeight: '700' },
  macroLabel: { fontSize: 11, color: '#9CA3AF', marginTop: 4 },

  // Search Results
  searchResultsContainer: { marginBottom: 20 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#F9FAFB', marginBottom: 12 },
  searchResult: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#1F2937', borderRadius: 12, padding: 14, marginBottom: 8 },
  searchResultInfo: { flex: 1 },
  searchResultName: { fontSize: 15, fontWeight: '600', color: '#F9FAFB' },
  searchResultBrand: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  searchResultServing: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
  searchResultMacros: { alignItems: 'flex-end', gap: 4 },
  searchResultCal: { fontSize: 15, fontWeight: '700', color: '#6366F1' },
  searchResultMacroText: { fontSize: 11, color: '#9CA3AF' },
  searchingContainer: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 20, gap: 12 },
  searchingText: { color: '#9CA3AF', fontSize: 15 },
  noResults: { alignItems: 'center', padding: 40, gap: 12 },
  noResultsText: { color: '#9CA3AF', fontSize: 16 },
  noResultsSubtext: { color: '#6B7280', fontSize: 13 },

  // Meals / Logged Foods
  emptyState: { alignItems: 'center', paddingVertical: 60, gap: 12 },
  emptyStateTitle: { color: '#F9FAFB', fontSize: 18, fontWeight: '700' },
  emptyStateText: { color: '#6B7280', fontSize: 14, textAlign: 'center' },
  mealsList: { marginBottom: 20 },
  loggedFoodItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#1F2937', borderRadius: 12, padding: 14, marginBottom: 8 },
  loggedFoodInfo: { flex: 1 },
  loggedFoodName: { fontSize: 15, fontWeight: '600', color: '#F9FAFB' },
  loggedFoodServing: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
  loggedFoodMacros: { alignItems: 'flex-end' },
  loggedFoodCal: { fontSize: 15, fontWeight: '700', color: '#6366F1' },
  loggedFoodMacroText: { fontSize: 11, color: '#9CA3AF' },

  addMealBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 16, borderRadius: 16, borderWidth: 2, borderColor: '#6366F1', borderStyle: 'dashed', gap: 8, marginBottom: 20 },
  addMealText: { color: '#6366F1', fontSize: 15, fontWeight: '600' },
  bottomBar: { position: 'absolute', bottom: 0, left: 0, right: 0, backgroundColor: '#0F172A', paddingHorizontal: 16, paddingVertical: 12, borderTopWidth: 1, borderTopColor: '#1F2937' },
  logFoodBtn: { backgroundColor: '#6366F1', borderRadius: 16, padding: 16, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 10 },
  logFoodText: { color: '#fff', fontSize: 16, fontWeight: '700' },

  // Edit Modal
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.7)', justifyContent: 'flex-end' },
  modalContent: { backgroundColor: '#1F2937', borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, paddingBottom: 40 },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  modalTitle: { fontSize: 20, fontWeight: '700', color: '#F9FAFB' },
  modalFoodName: { fontSize: 16, color: '#9CA3AF', marginBottom: 20, paddingBottom: 16, borderBottomWidth: 1, borderBottomColor: '#374151' },
  editRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 },
  editLabel: { fontSize: 15, color: '#D1D5DB' },
  editInput: { backgroundColor: '#0F172A', color: '#F9FAFB', fontSize: 15, paddingHorizontal: 14, paddingVertical: 10, borderRadius: 10, width: 160, textAlign: 'right' },
  saveBtn: { backgroundColor: '#6366F1', borderRadius: 14, padding: 16, alignItems: 'center', marginTop: 12 },
  saveBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  deleteBtnLarge: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 14, marginTop: 10 },
  deleteBtnText: { color: '#EF4444', fontSize: 15, fontWeight: '600' },
});