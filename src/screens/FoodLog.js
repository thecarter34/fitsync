import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity,
  FlatList, ActivityIndicator, Modal, KeyboardAvoidingView, Platform
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

const FOOD_LOG_KEY = '@fitsync_food_log';
const DAILY_TARGETS_KEY = '@fitsync_daily_targets';

// Default daily targets (can be customized in Settings)
const DEFAULT_TARGETS = {
  calories: 2200,
  protein: 180,
  carbs: 220,
  fat: 73,
  fiber: 35,
  water: 8, // glasses
};

// Search Open Food Facts API
async function searchFoods(query) {
  if (!query || query.length < 2) return [];
  try {
    const response = await fetch(
      `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(query)}&search_simple=1&action=process&json=1&page_size=20&fields=code,product_name,nutriments,serving_size,serving_quantity`
    );
    const data = await response.json();
    if (!data.products) return [];
    return data.products
      .filter(p => p.product_name)
      .map(p => {
        const n = p.nutriments || {};
        // Open Food Facts stores per 100g, normalize serving
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
    console.error('Food search error:', e);
    return [];
  }
}

// Lookup product by barcode
async function lookupBarcode(barcode) {
  try {
    const response = await fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
    const data = await response.json();
    if (data.status !== 1 || !data.product) return null;
    const p = data.product;
    const n = p.nutriments || {};
    const serving_g = p.serving_quantity ? parseFloat(p.serving_quantity) : 100;
    const factor = serving_g / 100;
    return {
      id: p.code,
      name: p.product_name,
      brand: p.brands || '',
      serving: p.serving_size || `${serving_g}g`,
      calories: Math.round((n['energy-kcal_100g'] || 0) * factor),
      protein: Math.round((n.proteins_100g || 0) * factor * 10) / 10,
      carbs: Math.round((n.carbohydrates_100g || 0) * factor * 10) / 10,
      fat: Math.round((n['fat_100g'] || 0) * factor * 10) / 10,
      fiber: Math.round((n.fiber_100g || 0) * factor * 10) / 10,
      barcode: p.code,
    };
  } catch (e) {
    console.error('Barcode lookup error:', e);
    return null;
  }
}

// Get today's date string as key
function getTodayKey() {
  return new Date().toISOString().split('T')[0]; // YYYY-MM-DD
}

// Load food log from storage
async function loadFoodLog() {
  try {
    const data = await AsyncStorage.getItem(FOOD_LOG_KEY);
    return data ? JSON.parse(data) : {};
  } catch (e) {
    return {};
  }
}

// Save food log to storage
async function saveFoodLog(log) {
  try {
    await AsyncStorage.setItem(FOOD_LOG_KEY, JSON.stringify(log));
  } catch (e) {
    console.error('Save food log error:', e);
  }
}

// Load daily targets
async function loadTargets() {
  try {
    const data = await AsyncStorage.getItem(DAILY_TARGETS_KEY);
    return data ? JSON.parse(data) : DEFAULT_TARGETS;
  } catch (e) {
    return DEFAULT_TARGETS;
  }
}

// Save daily targets
async function saveTargets(targets) {
  try {
    await AsyncStorage.setItem(DAILY_TARGETS_KEY, JSON.stringify(targets));
  } catch (e) {
    console.error('Save targets error:', e);
  }
}

function MealSection({ meal, time, items, onDelete, onEdit }) {
  const totalCal = items.reduce((s, i) => s + (i.calories || 0), 0);
  const totalProtein = items.reduce((s, i) => s + (i.protein || 0), 0);
  const totalCarbs = items.reduce((s, i) => s + (i.carbs || 0), 0);
  const totalFat = items.reduce((s, i) => s + (i.fat || 0), 0);

  return (
    <View style={styles.mealSection}>
      <View style={styles.mealHeader}>
        <View>
          <Text style={styles.mealName}>{meal}</Text>
          {time && <Text style={styles.mealTime}>{time}</Text>}
        </View>
        <View style={styles.mealTotals}>
          <Text style={styles.mealCal}>{totalCal} kcal</Text>
          <Text style={styles.mealProtein}>{totalProtein}g P · {totalCarbs}g C · {totalFat}g F</Text>
        </View>
      </View>
      {items.map((item, idx) => (
        <TouchableOpacity
          key={idx}
          style={styles.foodItem}
          onPress={() => onEdit && onEdit(item, idx)}
          onLongPress={() => onDelete && onDelete(item, idx)}
        >
          <View style={styles.foodInfo}>
            <Text style={styles.foodName}>{item.name}</Text>
            <Text style={styles.foodServing}>{item.serving} · {item.calories} kcal</Text>
          </View>
          <View style={styles.foodMacros}>
            <Text style={styles.foodMacro}>{item.protein}g P</Text>
            <TouchableOpacity onPress={() => onDelete && onDelete(item, idx)} style={styles.deleteBtn}>
              <Ionicons name="trash-outline" size={15} color="#6B7280" />
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
      ))}
      {items.length === 0 && (
        <Text style={styles.emptyMeal}>No foods logged</Text>
      )}
    </View>
  );
}

function FoodSearchResult({ item, onAdd }) {
  return (
    <TouchableOpacity style={styles.searchResult} onPress={() => onAdd(item)}>
      <View style={styles.searchResultInfo}>
        <Text style={styles.searchResultName}>{item.name}</Text>
        {item.brand ? <Text style={styles.searchResultBrand}>{item.brand}</Text> : null}
        <Text style={styles.searchResultServing}>{item.serving}</Text>
      </View>
      <View style={styles.searchResultMacros}>
        <Text style={styles.searchResultCal}>{item.calories} kcal</Text>
        <Text style={styles.searchResultMacroText}>P: {item.protein} C: {item.carbs} F: {item.fat}</Text>
        <TouchableOpacity style={styles.addBtn}>
          <Ionicons name="add-circle" size={26} color="#6366F1" />
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );
}

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
  const [targets, setTargets] = useState(DEFAULT_TARGETS);
  const [editModal, setEditModal] = useState(null); // { item, index, meal }
  const [addModal, setAddModal] = useState(null); // { food, meal }

  const todayKey = getTodayKey();
  const today = new Date();
  const dateStr = today.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

  // Load saved data
  useEffect(() => {
    async function load() {
      const [log, t] = await Promise.all([loadFoodLog(), loadTargets()]);
      setTargets(t);
      setTodayLog(log[todayKey] || []);
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

  // Save log whenever it changes
  const saveLog = useCallback(async (log) => {
    setTodayLog(log);
    const all = await loadFoodLog();
    all[todayKey] = log;
    await saveFoodLog(all);
  }, [todayKey]);

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

  // Edit existing food (update serving size)
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
        <TouchableOpacity style={styles.searchToggle} onPress={() => setShowSearch(!showSearch)}>
          <Ionicons name={showSearch ? 'close' : 'search'} size={22} color="#6366F1" />
        </TouchableOpacity>
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

        {/* Search Results */}
        {showSearch && searchResults.length > 0 && (
          <View style={styles.searchResultsContainer}>
            <Text style={styles.sectionTitle}>Search Results</Text>
            {searchResults.map((item) => (
              <FoodSearchResult key={item.id} item={item} onAdd={addFood} />
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
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingTop: 16, paddingBottom: 8 },
  title: { fontSize: 28, fontWeight: '700', color: '#F9FAFB' },
  subtitle: { fontSize: 14, color: '#9CA3AF', marginTop: 2 },
  searchToggle: { width: 44, height: 44, borderRadius: 22, backgroundColor: '#1F2937', justifyContent: 'center', alignItems: 'center' },
  searchBar: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1F2937', marginHorizontal: 16, marginBottom: 12, paddingHorizontal: 14, borderRadius: 14, height: 48 },
  searchInput: { flex: 1, fontSize: 16, color: '#F9FAFB' },
  scrollView: { flex: 1 },
  content: { padding: 16, paddingBottom: 100 },

  // Summary Card
  summaryCard: { backgroundColor: '#1F2937', borderRadius: 20, padding: 20, marginBottom: 20 },
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
  addBtn: { marginTop: 4 },
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

  // Meal Section (legacy compatibility)
  mealSection: { backgroundColor: '#1F2937', borderRadius: 16, padding: 16, marginBottom: 12 },
  mealHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12, paddingBottom: 12, borderBottomWidth: 1, borderBottomColor: '#374151' },
  mealName: { fontSize: 16, fontWeight: '700', color: '#F9FAFB' },
  mealTime: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
  mealTotals: { alignItems: 'flex-end' },
  mealCal: { fontSize: 15, fontWeight: '700', color: '#6366F1' },
  mealProtein: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
  foodItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 8 },
  foodInfo: {},
  foodName: { fontSize: 15, fontWeight: '600', color: '#D1D5DB' },
  foodServing: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  foodMacros: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  foodCal: { fontSize: 15, fontWeight: '600', color: '#F9FAFB' },
  foodMacro: { fontSize: 13, color: '#9CA3AF' },
  deleteBtn: { padding: 4 },
  emptyMeal: { color: '#6B7280', fontSize: 13, textAlign: 'center', paddingVertical: 8 },

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