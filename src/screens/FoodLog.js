import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity, FlatList } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const mockFoods = [
  { id: '1', name: 'Chicken Breast (grilled)', serving: '4 oz', calories: 187, protein: 36, carbs: 0, fat: 4 },
  { id: '2', name: 'Brown Rice', serving: '1 cup', calories: 216, protein: 5, carbs: 45, fat: 2 },
  { id: '3', name: 'Broccoli', serving: '1 cup', calories: 55, protein: 4, carbs: 11, fat: 0 },
  { id: '4', name: 'Egg (large, boiled)', serving: '1', calories: 78, protein: 6, carbs: 1, fat: 5 },
];

const todayMeals = [
  { id: '1', meal: 'Breakfast', time: '8:30 AM', items: [{ name: 'Egg (large, boiled)', serving: '2', calories: 156, protein: 12, carbs: 2, fat: 10 }] },
  { id: '2', meal: 'Lunch', time: '12:45 PM', items: [{ name: 'Chicken Breast (grilled)', serving: '4 oz', calories: 187, protein: 36, carbs: 0, fat: 4 }, { name: 'Brown Rice', serving: '1 cup', calories: 216, protein: 5, carbs: 45, fat: 2 }] },
];

function MealSection({ meal, time, items, onDelete }) {
  const totalCal = items.reduce((s, i) => s + i.calories, 0);
  const totalProtein = items.reduce((s, i) => s + (i.protein || 0), 0);

  return (
    <View style={styles.mealSection}>
      <View style={styles.mealHeader}>
        <View style={styles.mealTitle}>
          <Text style={styles.mealName}>{meal}</Text>
          <Text style={styles.mealTime}>{time}</Text>
        </View>
        <View style={styles.mealTotals}>
          <Text style={styles.mealCal}>{totalCal} kcal</Text>
          <Text style={styles.mealProtein}>{totalProtein}g protein</Text>
        </View>
      </View>
      {items.map((item, idx) => (
        <View key={idx} style={styles.foodItem}>
          <View style={styles.foodInfo}>
            <Text style={styles.foodName}>{item.name}</Text>
            <Text style={styles.foodServing}>{item.serving}</Text>
          </View>
          <View style={styles.foodMacros}>
            <Text style={styles.foodCal}>{item.calories}</Text>
            <TouchableOpacity onPress={() => onDelete(item)}>
              <Ionicons name="trash-outline" size={16} color="#6B7280" />
            </TouchableOpacity>
          </View>
        </View>
      ))}
    </View>
  );
}

export default function FoodLog({ navigation }) {
  const [search, setSearch] = useState('');
  const [showSearch, setShowSearch] = useState(false);

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Food Log</Text>
          <Text style={styles.subtitle}>{new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', weekday: 'short' })}</Text>
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
            value={search}
            onChangeText={setSearch}
          />
          <TouchableOpacity onPress={() => navigation.navigate('Scan')}>
            <Ionicons name="barcode-camera" size={22} color="#6366F1" />
          </TouchableOpacity>
        </View>
      )}

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Daily Summary */}
        <View style={styles.summaryCard}>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryValue}>1,450</Text>
            <Text style={styles.summaryLabel}>Eaten</Text>
          </View>
          <View style={styles.summaryDivider} />
          <View style={styles.summaryItem}>
            <Text style={styles.summaryValue}>2,200</Text>
            <Text style={styles.summaryLabel}>Target</Text>
          </View>
          <View style={styles.summaryDivider} />
          <View style={styles.summaryItem}>
            <Text style={[styles.summaryValue, { color: '#10B981' }]}>750</Text>
            <Text style={styles.summaryLabel}>Remaining</Text>
          </View>
        </View>

        {/* Meals */}
        {todayMeals.map((meal) => (
          <MealSection
            key={meal.id}
            meal={meal.meal}
            time={meal.time}
            items={meal.items}
            onDelete={(item) => {}}
          />
        ))}

        {/* Quick Add */}
        <TouchableOpacity style={styles.addMealBtn}>
          <Ionicons name="add" size={22} color="#6366F1" />
          <Text style={styles.addMealText}>Add Meal</Text>
        </TouchableOpacity>
      </ScrollView>

      {/* Bottom Button */}
      <View style={styles.bottomBar}>
        <TouchableOpacity style={styles.logFoodBtn} onPress={() => setShowSearch(true)}>
          <Ionicons name="add" size={22} color="#fff" />
          <Text style={styles.logFoodText}>Log Food</Text>
        </TouchableOpacity>
      </View>
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
  summaryCard: { backgroundColor: '#1F2937', borderRadius: 20, padding: 20, flexDirection: 'row', justifyContent: 'space-around', marginBottom: 20 },
  summaryItem: { alignItems: 'center' },
  summaryValue: { fontSize: 22, fontWeight: '800', color: '#F9FAFB' },
  summaryLabel: { fontSize: 12, color: '#9CA3AF', marginTop: 4 },
  summaryDivider: { width: 1, height: 40, backgroundColor: '#374151', alignSelf: 'center' },
  mealSection: { backgroundColor: '#1F2937', borderRadius: 16, padding: 16, marginBottom: 12 },
  mealHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12, paddingBottom: 12, borderBottomWidth: 1, borderBottomColor: '#374151' },
  mealTitle: {},
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
  addMealBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 16, borderRadius: 16, borderWidth: 2, borderColor: '#6366F1', borderStyle: 'dashed', gap: 8 },
  addMealText: { color: '#6366F1', fontSize: 15, fontWeight: '600' },
  bottomBar: { position: 'absolute', bottom: 0, left: 0, right: 0, backgroundColor: '#0F172A', paddingHorizontal: 16, paddingVertical: 12, borderTopWidth: 1, borderTopColor: '#1F2937' },
  logFoodBtn: { backgroundColor: '#6366F1', borderRadius: 16, padding: 16, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 10 },
  logFoodText: { color: '#fff', fontSize: 16, fontWeight: '700' },
});