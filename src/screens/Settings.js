import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert, Modal, TextInput, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

function Toggle({ value, onValueChange, color = '#6366F1' }) {
  const bg = value ? color : '#4B5563';
  const thumbLeft = value ? 'auto' : 3;
  const thumbRight = value ? 3 : 'auto';

  return (
    <Pressable
      onPress={() => {
        console.log('[Toggle] Pressed! value was', value, 'will set to', !value);
        onValueChange(!value);
        console.log('[Toggle] onValueChange called');
      }}
      style={{ width: 52, height: 28, backgroundColor: bg, borderRadius: 14, padding: 3, flexDirection: 'row', alignItems: 'center' }}
    >
      <View style={{ width: 22, height: 22, borderRadius: 11, backgroundColor: '#fff', position: 'absolute', top: 3, left: thumbLeft, right: thumbRight }} />
    </Pressable>
  );
}

const mockUser = {
  name: 'Josh',
  email: 'josh@example.com',
};

const CALORIES_PER_LB = 3500;

function SettingRow({ icon, label, value, onPress, color = '#6366F1', showArrow = true, disabled = false }) {
  return (
    <TouchableOpacity style={[styles.settingRow, disabled && styles.settingRowDisabled]} onPress={disabled ? null : onPress} activeOpacity={onPress && !disabled ? 0.7 : 1}>
      <View style={[styles.settingIcon, { backgroundColor: disabled ? '#374151' : color + '20' }]}>
        <Ionicons name={icon} size={20} color={disabled ? '#6B7280' : color} />
      </View>
      <View style={styles.settingContent}>
        <Text style={[styles.settingLabel, disabled && styles.textDisabled]}>{label}</Text>
        {value && <Text style={[styles.settingValue, disabled && styles.textDisabled]}>{value}</Text>}
      </View>
      {showArrow && onPress && !disabled && <Ionicons name="chevron-forward" size={20} color="#4B5563" />}
    </TouchableOpacity>
  );
}

function SettingSwitch({ icon, label, value, onValueChange, color = '#6366F1' }) {
  return (
    <TouchableOpacity style={styles.settingRow} onPress={() => onValueChange(!value)} activeOpacity={0.7}>
      <View style={[styles.settingIcon, { backgroundColor: color + '20' }]}>
        <Ionicons name={icon} size={20} color={color} />
      </View>
      <View style={styles.settingContent}>
        <Text style={styles.settingLabel}>{label}</Text>
      </View>
      <Toggle value={value} onValueChange={onValueChange} color={color} />
    </TouchableOpacity>
  );
}

function calcGoalStats(currentWeight, goalWeight, goalDate, tdee) {
  const lbsToLose = currentWeight - goalWeight;
  const daysLeft = Math.max(1, Math.ceil((new Date(goalDate) - new Date()) / (1000 * 60 * 60 * 24)));
  const weeklyRate = (lbsToLose / daysLeft) * 7;
  const dailyDeficit = Math.round((lbsToLose * CALORIES_PER_LB) / daysLeft);
  const recommendedIntake = tdee - dailyDeficit;
  return { lbsToLose, daysLeft, weeklyRate, dailyDeficit, recommendedIntake };
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function Settings({ navigation }) {
  // Garmin sync toggle
  const [garminSync, setGarminSync] = useState(false);
  // Manual body stats (used when garminSync is OFF)
  const [manualWeight, setManualWeight] = useState('180.4');
  const [manualTdee, setManualTdee] = useState('2400');
  const [manualHeight, setManualHeight] = useState("5'10\"");
  const [manualAge, setManualAge] = useState('34');
  const [manualGender, setManualGender] = useState('Male');
  // Garmin data (used when garminSync is ON — would come from API in production)
  const [garminData] = useState({ weight: 180.4, tdee: 2400, height: "5'10\"", age: 34, gender: 'Male' });

  const [notifications, setNotifications] = useState(true);
  const [waterReminders, setWaterReminders] = useState(true);
  const [goalModal, setGoalModal] = useState(false);
  const [goalWeight, setGoalWeight] = useState('175');
  const [goalDate, setGoalDate] = useState('2026-06-01');

  // Data source — Garmin or manual
  const currentWeight = garminSync ? garminData.weight : parseFloat(manualWeight);
  const tdee = garminSync ? garminData.tdee : parseInt(manualTdee) || 2000;
  const stats = calcGoalStats(currentWeight, parseFloat(goalWeight), goalDate, tdee);

  const handleGarminToggle = (val) => {
    // Toggle immediately - alert is just for confirmation
    setGarminSync(val);
    if (val) {
      Alert.alert('Garmin Sync Enabled', 'Body stats and TDEE will sync from Garmin Connect.');
    } else {
      Alert.alert('Garmin Sync Disabled', 'Enter body stats and TDEE manually below.');
    }
  };

  const handleExportData = () => {
    Alert.alert('Export Data', 'Your data will be exported as a CSV file.', [
      { text: 'OK' },
    ]);
  };

  const handleBodyStatEdit = (field, value) => {
    switch (field) {
      case 'weight': setManualWeight(value); break;
      case 'tdee': setManualTdee(value); break;
      case 'height': setManualHeight(value); break;
      case 'age': setManualAge(value); break;
      case 'gender': setManualGender(value); break;
    }
  };

  const garminStatus = garminSync
    ? { icon: 'checkmark-circle', color: '#10B981', text: 'Connected' }
    : { icon: 'ellipse-outline', color: '#6B7280', text: 'Manual mode' };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>

        {/* Profile Card */}
        <View style={styles.profileCard}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>{mockUser.name[0]}</Text>
          </View>
          <View style={styles.profileInfo}>
            <Text style={styles.profileName}>{mockUser.name}</Text>
            <Text style={styles.profileEmail}>{mockUser.email}</Text>
          </View>
          <TouchableOpacity style={styles.editBtn}>
            <Ionicons name="pencil" size={18} color="#6366F1" />
          </TouchableOpacity>
        </View>

        {/* Weight Goal Card */}
        <TouchableOpacity style={styles.goalCard} onPress={() => setGoalModal(true)} activeOpacity={0.8}>
          <View style={styles.goalHeader}>
            <View>
              <Text style={styles.goalTitle}>Weight Goal</Text>
              <Text style={styles.goalSubtitle}>Tap to edit goal</Text>
            </View>
            <View style={styles.goalArrow}>
              <Ionicons name="chevron-forward" size={22} color="#6366F1" />
            </View>
          </View>

          <View style={styles.goalBody}>
            <View style={styles.goalWeightRow}>
              <View style={styles.goalWeightItem}>
                <Text style={styles.goalWeightLabel}>Current</Text>
                <Text style={styles.goalWeightValue}>{currentWeight.toFixed(1)}</Text>
                <Text style={styles.goalWeightUnit}>lbs</Text>
              </View>
              <Ionicons name="arrow-forward" size={20} color="#374151" style={{ marginTop: 16 }} />
              <View style={styles.goalWeightItem}>
                <Text style={styles.goalWeightLabel}>Goal</Text>
                <Text style={[styles.goalWeightValue, { color: '#10B981' }]}>{goalWeight}</Text>
                <Text style={styles.goalWeightUnit}>lbs</Text>
              </View>
              <View style={styles.goalWeightItem}>
                <Text style={styles.goalWeightLabel}>By</Text>
                <Text style={[styles.goalWeightValue, { color: '#6366F1' }]}>{formatDate(goalDate)}</Text>
                <Text style={styles.goalWeightUnit}></Text>
              </View>
            </View>

            <View style={styles.goalStatsRow}>
              <View style={styles.goalStat}>
                <Text style={styles.goalStatValue}>{stats.lbsToLose.toFixed(1)}</Text>
                <Text style={styles.goalStatLabel}>lbs to lose</Text>
              </View>
              <View style={styles.goalStatDivider} />
              <View style={styles.goalStat}>
                <Text style={[styles.goalStatValue, { color: '#F59E0B' }]}>{stats.dailyDeficit}</Text>
                <Text style={styles.goalStatLabel}>cal/day deficit</Text>
              </View>
              <View style={styles.goalStatDivider} />
              <View style={styles.goalStat}>
                <Text style={[styles.goalStatValue, { color: '#6366F1' }]}>{stats.recommendedIntake}</Text>
                <Text style={styles.goalStatLabel}>target kcal/day</Text>
              </View>
            </View>
          </View>

          <View style={styles.goalFooter}>
            <Text style={styles.goalFooterText}>
              Loses {stats.weeklyRate.toFixed(1)} lbs/week · {stats.daysLeft} days to goal
            </Text>
          </View>
        </TouchableOpacity>

        {/* Garmin Integration Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Data Source</Text>
          <View style={styles.card}>
            {/* Main Garmin Sync Toggle */}
            <View style={styles.settingRow}>
              <View style={[styles.settingIcon, { backgroundColor: '#007CC3' + '20' }]}>
                <Ionicons name="watch" size={20} color="#007CC3" />
              </View>
              <View style={styles.settingContent}>
                <Text style={styles.settingLabel}>Garmin Sync</Text>
                <Text style={styles.settingValue}>Auto-import body stats & TDEE</Text>
              </View>
              <Toggle value={garminSync} onValueChange={handleGarminToggle} color="#007CC3" />
            </View>

            {/* Status */}
            <View style={styles.garminStatusRow}>
              <Ionicons name={garminStatus.icon} size={16} color={garminStatus.color} />
              <Text style={[styles.garminStatusText, { color: garminStatus.color }]}>{garminStatus.text}</Text>
              {garminSync && (
                <Text style={styles.garminSyncNote}>Weight, TDEE, height, age synced</Text>
              )}
              {!garminSync && (
                <Text style={styles.garminSyncNote}>Enter body stats manually below</Text>
              )}
            </View>

            {!garminSync && (
              <View style={styles.manualInputs}>
                <Text style={styles.manualInputsTitle}>Manual Entry</Text>

                <View style={styles.inputRow}>
                  <View style={styles.inputGroup}>
                    <Text style={styles.inputLabel}>Current Weight (lbs)</Text>
                    <TextInput
                      style={styles.textInput}
                      value={manualWeight}
                      onChangeText={(v) => handleBodyStatEdit('weight', v)}
                      keyboardType="numeric"
                      placeholder="180"
                      placeholderTextColor="#6B7280"
                    />
                  </View>
                  <View style={styles.inputGroup}>
                    <Text style={styles.inputLabel}>Daily TDEE (kcal)</Text>
                    <TextInput
                      style={styles.textInput}
                      value={manualTdee}
                      onChangeText={(v) => handleBodyStatEdit('tdee', v)}
                      keyboardType="numeric"
                      placeholder="2400"
                      placeholderTextColor="#6B7280"
                    />
                  </View>
                </View>
              </View>
            )}
          </View>
        </View>

        {/* Body Stats Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Body Stats</Text>
          <View style={styles.card}>
            <SettingRow
              icon="resize-outline"
              label="Height"
              value={garminSync ? "5'10\" (from Garmin)" : manualHeight}
              onPress={() => {}}
              color="#8B5CF6"
              showArrow={false}
              disabled={garminSync}
            />
            <SettingRow
              icon="calendar-outline"
              label="Age"
              value={garminSync ? '34 (from Garmin)' : `${manualAge} years`}
              onPress={() => {}}
              color="#8B5CF6"
              showArrow={false}
              disabled={garminSync}
            />
            <SettingRow
              icon="person-outline"
              label="Gender"
              value={garminSync ? 'Male (from Garmin)' : manualGender}
              onPress={() => {}}
              color="#8B5CF6"
              showArrow={false}
              disabled={garminSync}
            />
            {!garminSync && (
              <>
                <View style={styles.inlineEditRow}>
                  <Text style={styles.inlineEditLabel}>Height</Text>
                  <TextInput
                    style={styles.inlineInput}
                    value={manualHeight}
                    onChangeText={(v) => handleBodyStatEdit('height', v)}
                    placeholder={`5'10"`}
                    placeholderTextColor="#6B7280"
                  />
                </View>
                <View style={styles.inlineEditRow}>
                  <Text style={styles.inlineEditLabel}>Age</Text>
                  <TextInput
                    style={styles.inlineInput}
                    value={manualAge}
                    onChangeText={(v) => handleBodyStatEdit('age', v)}
                    keyboardType="numeric"
                    placeholder="34"
                    placeholderTextColor="#6B7280"
                  />
                </View>
                <View style={styles.inlineEditRow}>
                  <Text style={styles.inlineEditLabel}>Gender</Text>
                  <TextInput
                    style={styles.inlineInput}
                    value={manualGender}
                    onChangeText={(v) => handleBodyStatEdit('gender', v)}
                    placeholder="Male"
                    placeholderTextColor="#6B7280"
                  />
                </View>
              </>
            )}
          </View>
        </View>

        {/* Macro Goals */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Macro Goals</Text>
          <View style={styles.card}>
            <SettingRow icon="flame-outline" label="Calorie Target" value={`${stats.recommendedIntake} kcal`} onPress={() => {}} color="#EF4444" showArrow={false} />
            <SettingRow icon="barbell-outline" label="Protein Target" value="180g" onPress={() => {}} color="#EF4444" showArrow={false} />
            <SettingRow icon="layers-outline" label="Carb Target" value="220g" onPress={() => {}} color="#3B82F6" showArrow={false} />
            <SettingRow icon="water-outline" label="Water Target" value="8 glasses" onPress={() => {}} color="#06B6D4" showArrow={false} />
          </View>
        </View>

        {/* Notifications */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notifications</Text>
          <View style={styles.card}>
            <SettingSwitch icon="notifications-outline" label="Daily Reminders" value={notifications} onValueChange={setNotifications} color="#6366F1" />
            <SettingSwitch icon="water-outline" label="Water Reminders" value={waterReminders} onValueChange={setWaterReminders} color="#06B6D4" />
          </View>
        </View>

        {/* Data */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Data</Text>
          <View style={styles.card}>
            <SettingRow icon="download-outline" label="Export Data" value="" onPress={handleExportData} color="#10B981" showArrow={false} />
            <SettingRow icon="trash-outline" label="Delete Account" value="" onPress={() => Alert.alert('Delete Account', 'This action cannot be undone.')} color="#EF4444" showArrow={false} />
          </View>
        </View>

        <View style={styles.appInfo}>
          <Text style={styles.appName}>FitSync</Text>
          <Text style={styles.appVersion}>Version 1.0.0</Text>
        </View>
      </ScrollView>

      {/* Goal Edit Modal */}
      <Modal visible={goalModal} animationType="slide" transparent onRequestClose={() => setGoalModal(false)}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Set Weight Goal</Text>
              <TouchableOpacity onPress={() => setGoalModal(false)}>
                <Ionicons name="close" size={24} color="#9CA3AF" />
              </TouchableOpacity>
            </View>

            <View style={styles.modalBody}>
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Goal Weight (lbs)</Text>
                <TextInput
                  style={styles.textInput}
                  value={goalWeight}
                  onChangeText={setGoalWeight}
                  keyboardType="numeric"
                  placeholder="175"
                  placeholderTextColor="#6B7280"
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Target Date</Text>
                <TextInput
                  style={styles.textInput}
                  value={goalDate}
                  onChangeText={setGoalDate}
                  placeholder="YYYY-MM-DD"
                  placeholderTextColor="#6B7280"
                />
                <Text style={styles.inputHint}>Format: 2026-06-01</Text>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Daily TDEE (kcal)</Text>
                <TextInput
                  style={styles.textInput}
                  value={garminSync ? garminData.tdee.toString() : manualTdee}
                  onChangeText={(v) => garminSync ? null : handleBodyStatEdit('tdee', v)}
                  keyboardType="numeric"
                  placeholder="2400"
                  placeholderTextColor="#6B7280"
                  editable={!garminSync}
                />
                {garminSync && (
                  <Text style={styles.inputHint}>Synced from Garmin — disable sync to edit</Text>
                )}
                {!garminSync && (
                  <Text style={styles.inputHint}>Your total daily energy expenditure</Text>
                )}
              </View>

              {/* Live Preview */}
              <View style={styles.goalPreview}>
                <Text style={styles.goalPreviewTitle}>Your Plan</Text>
                <View style={styles.goalPreviewRow}>
                  <Text style={styles.goalPreviewLabel}>Current → Goal</Text>
                  <Text style={styles.goalPreviewValue}>{currentWeight.toFixed(1)} → {goalWeight} lbs</Text>
                </View>
                <View style={styles.goalPreviewRow}>
                  <Text style={styles.goalPreviewLabel}>Lose</Text>
                  <Text style={styles.goalPreviewValue}>{stats.lbsToLose.toFixed(1)} lbs</Text>
                </View>
                <View style={styles.goalPreviewRow}>
                  <Text style={styles.goalPreviewLabel}>Daily deficit</Text>
                  <Text style={[styles.goalPreviewValue, { color: '#F59E0B' }]}>{stats.dailyDeficit} kcal</Text>
                </View>
                <View style={styles.goalPreviewRow}>
                  <Text style={styles.goalPreviewLabel}>Daily target</Text>
                  <Text style={[styles.goalPreviewValue, { color: '#6366F1' }]}>{stats.recommendedIntake} kcal</Text>
                </View>
                <View style={styles.goalPreviewRow}>
                  <Text style={styles.goalPreviewLabel}>Pace</Text>
                  <Text style={styles.goalPreviewValue}>{stats.weeklyRate.toFixed(1)} lbs/week</Text>
                </View>
              </View>
            </View>

            <TouchableOpacity style={styles.saveBtn} onPress={() => setGoalModal(false)}>
              <Text style={styles.saveBtnText}>Save Goal</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  scrollView: { flex: 1 },
  content: { padding: 16, paddingBottom: 100 },
  profileCard: { backgroundColor: '#1F2937', borderRadius: 20, padding: 20, flexDirection: 'row', alignItems: 'center', marginBottom: 16, gap: 16 },
  avatar: { width: 60, height: 60, borderRadius: 30, backgroundColor: '#6366F1', justifyContent: 'center', alignItems: 'center' },
  avatarText: { fontSize: 24, fontWeight: '800', color: '#fff' },
  profileInfo: { flex: 1 },
  profileName: { fontSize: 20, fontWeight: '700', color: '#F9FAFB' },
  profileEmail: { fontSize: 14, color: '#9CA3AF', marginTop: 2 },
  editBtn: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#111827', justifyContent: 'center', alignItems: 'center' },
  goalCard: { backgroundColor: '#1F2937', borderRadius: 20, marginBottom: 16, overflow: 'hidden', borderWidth: 1, borderColor: '#6366F1' },
  goalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 18, paddingBottom: 0 },
  goalTitle: { fontSize: 18, fontWeight: '700', color: '#F9FAFB' },
  goalSubtitle: { fontSize: 12, color: '#6366F1', marginTop: 2 },
  goalArrow: { width: 36, height: 36, borderRadius: 18, backgroundColor: '#6366F1' + '20', justifyContent: 'center', alignItems: 'center' },
  goalBody: { padding: 18 },
  goalWeightRow: { flexDirection: 'row', justifyContent: 'space-around', alignItems: 'flex-start', marginBottom: 20 },
  goalWeightItem: { alignItems: 'center' },
  goalWeightLabel: { fontSize: 11, color: '#6B7280', textTransform: 'uppercase', letterSpacing: 0.5 },
  goalWeightValue: { fontSize: 26, fontWeight: '800', color: '#F9FAFB', marginTop: 4 },
  goalWeightUnit: { fontSize: 12, color: '#9CA3AF' },
  goalStatsRow: { flexDirection: 'row', justifyContent: 'space-around', backgroundColor: '#111827', borderRadius: 14, padding: 16 },
  goalStat: { alignItems: 'center' },
  goalStatValue: { fontSize: 18, fontWeight: '800', color: '#F9FAFB' },
  goalStatLabel: { fontSize: 11, color: '#9CA3AF', marginTop: 2 },
  goalStatDivider: { width: 1, height: 36, backgroundColor: '#374151', alignSelf: 'center' },
  goalFooter: { borderTopWidth: 1, borderTopColor: '#374151', padding: 14, alignItems: 'center' },
  goalFooterText: { fontSize: 12, color: '#6B7280' },
  section: { marginBottom: 24 },
  sectionTitle: { fontSize: 13, fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 10, marginLeft: 4 },
  card: { backgroundColor: '#1F2937', borderRadius: 16, overflow: 'hidden' },
  settingRow: { flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: '#111827' },
  settingRowDisabled: { opacity: 0.7 },
  settingIcon: { width: 40, height: 40, borderRadius: 12, justifyContent: 'center', alignItems: 'center', marginRight: 14 },
  settingContent: { flex: 1 },
  settingLabel: { fontSize: 15, fontWeight: '600', color: '#F9FAFB' },
  settingValue: { fontSize: 13, color: '#9CA3AF', marginTop: 2 },
  textDisabled: { color: '#6B7280' },
  garminStatusRow: { flexDirection: 'row', alignItems: 'center', padding: 14, gap: 8, borderBottomWidth: 1, borderBottomColor: '#111827', flexWrap: 'wrap' },
  garminStatusText: { fontSize: 14, fontWeight: '600' },
  garminSyncNote: { fontSize: 12, color: '#6B7280', marginLeft: 4 },
  manualInputs: { padding: 16 },
  manualInputsTitle: { fontSize: 12, fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 12 },
  inputRow: { flexDirection: 'row', gap: 12 },
  inlineEditRow: { flexDirection: 'row', alignItems: 'center', padding: 14, borderBottomWidth: 1, borderBottomColor: '#111827', gap: 12 },
  inlineEditLabel: { fontSize: 14, fontWeight: '600', color: '#9CA3AF', width: 70 },
  inlineInput: { flex: 1, backgroundColor: '#111827', borderRadius: 10, paddingHorizontal: 14, paddingVertical: 10, fontSize: 15, fontWeight: '600', color: '#F9FAFB', borderWidth: 1, borderColor: '#374151' },
  appInfo: { alignItems: 'center', marginTop: 16, marginBottom: 32 },
  appName: { fontSize: 16, fontWeight: '700', color: '#4B5563' },
  appVersion: { fontSize: 13, color: '#374151', marginTop: 4 },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.7)', justifyContent: 'flex-end' },
  modalContent: { backgroundColor: '#1F2937', borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, paddingBottom: 40 },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
  modalTitle: { fontSize: 22, fontWeight: '800', color: '#F9FAFB' },
  modalBody: { gap: 20 },
  inputGroup: { gap: 8 },
  inputLabel: { fontSize: 13, fontWeight: '600', color: '#D1D5DB', textTransform: 'uppercase', letterSpacing: 0.5 },
  textInput: { backgroundColor: '#111827', borderRadius: 12, padding: 16, fontSize: 18, fontWeight: '700', color: '#F9FAFB', borderWidth: 1, borderColor: '#374151' },
  inputHint: { fontSize: 12, color: '#6B7280', marginTop: 4 },
  goalPreview: { backgroundColor: '#111827', borderRadius: 16, padding: 18, marginTop: 8 },
  goalPreviewTitle: { fontSize: 14, fontWeight: '700', color: '#9CA3AF', marginBottom: 12 },
  goalPreviewRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 10 },
  goalPreviewLabel: { fontSize: 15, color: '#9CA3AF' },
  goalPreviewValue: { fontSize: 15, fontWeight: '700', color: '#F9FAFB' },
  saveBtn: { backgroundColor: '#6366F1', borderRadius: 14, padding: 16, alignItems: 'center', marginTop: 24 },
  saveBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
});