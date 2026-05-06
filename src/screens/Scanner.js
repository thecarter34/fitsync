import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Dimensions, ActivityIndicator, Modal } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { CameraView, useCameraPermissions } from 'expo-camera';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { width, height } = Dimensions.get('window');
const FOOD_LOG_KEY = '@fitsync_food_log';

// Lookup product by barcode via Open Food Facts
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

function getTodayKey() {
  return new Date().toISOString().split('T')[0];
}

async function addToLog(food) {
  const todayKey = getTodayKey();
  try {
    const data = await AsyncStorage.getItem(FOOD_LOG_KEY);
    const log = data ? JSON.parse(data) : {};
    if (!log[todayKey]) log[todayKey] = [];
    log[todayKey].push({ ...food, loggedAt: new Date().toISOString() });
    await AsyncStorage.setItem(FOOD_LOG_KEY, JSON.stringify(log));
    return true;
  } catch (e) {
    console.error('Add to log error:', e);
    return false;
  }
}

export default function Scanner({ navigation }) {
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);
  const [scannedBarcode, setScannedBarcode] = useState(null);
  const [lookupResult, setLookupResult] = useState(null); // null = not looked up, { product } = found, 'not_found', 'error'
  const [isLooking, setIsLooking] = useState(false);

  const handleBarcodeScanned = async ({ type, data }) => {
    if (scanned) return;
    setScanned(true);
    setScannedBarcode({ type, data });
    setIsLooking(true);

    const result = await lookupBarcode(data);
    setLookupResult(result || 'not_found');
    setIsLooking(false);
  };

  const handleAddToLog = async () => {
    if (!lookupResult || lookupResult === 'not_found' || lookupResult === 'error') return;
    const success = await addToLog(lookupResult);
    if (success) {
      navigation.navigate('Food');
    }
  };

  const handleScanAgain = () => {
    setScanned(false);
    setScannedBarcode(null);
    setLookupResult(null);
  };

  if (!permission) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Requesting camera permission...</Text>
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <View style={styles.permissionCard}>
          <Ionicons name="camera-outline" size={64} color="#6366F1" />
          <Text style={styles.permissionTitle}>Camera Access Needed</Text>
          <Text style={styles.permissionText}>
            To scan barcodes, we need access to your camera. Your privacy is important — we only use the camera for barcode scanning.
          </Text>
          <TouchableOpacity style={styles.permissionBtn} onPress={requestPermission}>
            <Text style={styles.permissionBtnText}>Grant Permission</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView
        style={StyleSheet.absoluteFill}
        facing="back"
        barcodeScannerSettings={{
          barcodeTypes: ['ean13', 'ean8', 'upc_a', 'upc_e', 'code128', 'code39', 'qr'],
        }}
        onBarcodeScanned={scanned ? undefined : handleBarcodeScanned}
      />

      {/* Overlay */}
      <View style={styles.overlay}>
        {/* Top */}
        <View style={styles.overlayTop}>
          <Text style={styles.scanTitle}>Scan Barcode</Text>
          <Text style={styles.scanSubtitle}>Point camera at food barcode</Text>
        </View>

        {/* Scan window */}
        <View style={styles.scanArea}>
          <View style={styles.cornerTL} />
          <View style={styles.cornerTR} />
          <View style={styles.cornerBL} />
          <View style={styles.cornerBR} />
        </View>

        {/* Bottom */}
        <View style={styles.overlayBottom}>
          {isLooking && (
            <View style={styles.resultCard}>
              <ActivityIndicator color="#6366F1" size="large" />
              <Text style={styles.loadingLookupText}>Looking up product...</Text>
            </View>
          )}

          {!isLooking && scanned && scannedBarcode && lookupResult && lookupResult !== 'not_found' && lookupResult !== 'error' && (
            <View style={styles.resultCard}>
              <View style={styles.productHeader}>
                <View style={styles.productIcon}>
                  <Ionicons name="checkmark-circle" size={28} color="#10B981" />
                </View>
                <View style={styles.productTitleArea}>
                  <Text style={styles.productName} numberOfLines={2}>{lookupResult.name}</Text>
                  {lookupResult.brand ? <Text style={styles.productBrand}>{lookupResult.brand}</Text> : null}
                </View>
              </View>

              <View style={styles.productNutrition}>
                <View style={styles.nutritionMain}>
                  <Text style={styles.nutritionCal}>{lookupResult.calories}</Text>
                  <Text style={styles.nutritionCalLabel}>kcal</Text>
                </View>
                <View style={styles.nutritionMacros}>
                  <Text style={styles.nutritionMacro}>P: {lookupResult.protein}g</Text>
                  <Text style={styles.nutritionMacro}>C: {lookupResult.carbs}g</Text>
                  <Text style={styles.nutritionMacro}>F: {lookupResult.fat}g</Text>
                </View>
                <Text style={styles.nutritionServing}>per {lookupResult.serving}</Text>
              </View>

              <View style={styles.resultActions}>
                <TouchableOpacity style={styles.resultBtnSecondary} onPress={handleScanAgain}>
                  <Text style={styles.resultBtnSecondaryText}>Scan Again</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.resultBtnPrimary} onPress={handleAddToLog}>
                  <Ionicons name="add" size={18} color="#fff" />
                  <Text style={styles.resultBtnPrimaryText}>Add to Log</Text>
                </TouchableOpacity>
              </View>
            </View>
          )}

          {!isLooking && scanned && scannedBarcode && lookupResult === 'not_found' && (
            <View style={styles.resultCard}>
              <View style={styles.productHeader}>
                <View style={[styles.productIcon, { backgroundColor: '#374151' }]}>
                  <Ionicons name="help-circle" size={28} color="#9CA3AF" />
                </View>
                <View style={styles.productTitleArea}>
                  <Text style={styles.productName}>Product Not Found</Text>
                  <Text style={styles.productBrand}>{scannedBarcode.data}</Text>
                </View>
              </View>
              <Text style={styles.notFoundText}>
                This barcode isn't in the Open Food Facts database. Try searching by name instead.
              </Text>
              <View style={styles.resultActions}>
                <TouchableOpacity style={styles.resultBtnSecondary} onPress={handleScanAgain}>
                  <Text style={styles.resultBtnSecondaryText}>Scan Again</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.resultBtnSecondary} onPress={() => navigation.navigate('Food')}>
                  <Text style={styles.resultBtnSecondaryText}>Search Instead</Text>
                </TouchableOpacity>
              </View>
            </View>
          )}

          {!scanned && (
            <TouchableOpacity style={styles.manualEntryBtn} onPress={() => navigation.navigate('Food')}>
              <Ionicons name="keyboard" size={20} color="#9CA3AF" />
              <Text style={styles.manualEntryText}>Enter manually instead</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );
}

const cornerSize = 40;
const cornerThickness = 4;
const scanBoxSize = width * 0.7;

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  loadingText: { color: '#9CA3AF', fontSize: 16, textAlign: 'center', marginTop: 100 },
  permissionCard: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 40, backgroundColor: '#0F172A' },
  permissionTitle: { fontSize: 22, fontWeight: '700', color: '#F9FAFB', marginTop: 20, marginBottom: 12 },
  permissionText: { fontSize: 15, color: '#9CA3AF', textAlign: 'center', lineHeight: 22, marginBottom: 28 },
  permissionBtn: { backgroundColor: '#6366F1', paddingHorizontal: 32, paddingVertical: 14, borderRadius: 14 },
  permissionBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  overlay: { flex: 1 },
  overlayTop: { flex: 1, justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 30 },
  scanTitle: { fontSize: 24, fontWeight: '800', color: '#fff' },
  scanSubtitle: { fontSize: 14, color: '#D1D5DB', marginTop: 8 },
  scanArea: { width: scanBoxSize, height: scanBoxSize, alignSelf: 'center', position: 'relative' },
  cornerTL: { position: 'absolute', top: 0, left: 0, width: cornerSize, height: cornerSize, borderTopWidth: cornerThickness, borderLeftWidth: cornerThickness, borderColor: '#6366F1', borderTopLeftRadius: 8 },
  cornerTR: { position: 'absolute', top: 0, right: 0, width: cornerSize, height: cornerSize, borderTopWidth: cornerThickness, borderRightWidth: cornerThickness, borderColor: '#6366F1', borderTopRightRadius: 8 },
  cornerBL: { position: 'absolute', bottom: 0, left: 0, width: cornerSize, height: cornerSize, borderBottomWidth: cornerThickness, borderLeftWidth: cornerThickness, borderColor: '#6366F1', borderBottomLeftRadius: 8 },
  cornerBR: { position: 'absolute', bottom: 0, right: 0, width: cornerSize, height: cornerSize, borderBottomWidth: cornerThickness, borderRightWidth: cornerThickness, borderColor: '#6366F1', borderBottomRightRadius: 8 },
  overlayBottom: { flex: 1, justifyContent: 'flex-start', alignItems: 'center', paddingTop: 30 },
  manualEntryBtn: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: 'rgba(0,0,0,0.6)', paddingHorizontal: 20, paddingVertical: 12, borderRadius: 24 },
  manualEntryText: { color: '#9CA3AF', fontSize: 14 },
  resultCard: { backgroundColor: '#1F2937', borderRadius: 20, padding: 20, width: width - 40, alignSelf: 'center' },
  loadingLookupText: { color: '#9CA3AF', fontSize: 14, marginTop: 12 },
  productHeader: { flexDirection: 'row', alignItems: 'flex-start', gap: 14, marginBottom: 16 },
  productIcon: { width: 52, height: 52, borderRadius: 14, backgroundColor: '#0F172A', justifyContent: 'center', alignItems: 'center' },
  productTitleArea: { flex: 1 },
  productName: { fontSize: 17, fontWeight: '700', color: '#F9FAFB', lineHeight: 22 },
  productBrand: { fontSize: 13, color: '#6B7280', marginTop: 2 },
  productNutrition: { backgroundColor: '#0F172A', borderRadius: 14, padding: 16, marginBottom: 16 },
  nutritionMain: { flexDirection: 'row', alignItems: 'baseline', gap: 6, marginBottom: 10 },
  nutritionCal: { fontSize: 36, fontWeight: '800', color: '#6366F1' },
  nutritionCalLabel: { fontSize: 16, color: '#6B7280' },
  nutritionMacros: { flexDirection: 'row', gap: 16, marginBottom: 4 },
  nutritionMacro: { fontSize: 14, color: '#D1D5DB', fontWeight: '600' },
  nutritionServing: { fontSize: 12, color: '#6B7280', marginTop: 4 },
  notFoundText: { fontSize: 14, color: '#9CA3AF', lineHeight: 20, marginBottom: 16, textAlign: 'center' },
  resultActions: { flexDirection: 'row', gap: 12 },
  resultBtnSecondary: { flex: 1, padding: 14, borderRadius: 12, borderWidth: 1, borderColor: '#374151', alignItems: 'center' },
  resultBtnSecondaryText: { color: '#9CA3AF', fontSize: 14, fontWeight: '600' },
  resultBtnPrimary: { flex: 1, padding: 14, borderRadius: 12, backgroundColor: '#6366F1', alignItems: 'center', flexDirection: 'row', justifyContent: 'center', gap: 6 },
  resultBtnPrimaryText: { color: '#fff', fontSize: 14, fontWeight: '700' },
});