import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Dimensions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { CameraView, useCameraPermissions } from 'expo-camera';

const { width, height } = Dimensions.get('window');

export default function Scanner({ navigation }) {
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);
  const [lastScanned, setLastScanned] = useState(null);

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

  const handleBarcodeScanned = ({ type, data }) => {
    if (scanned) return;
    setScanned(true);
    setLastScanned({ type, data, time: new Date() });
  };

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
          {scanned && lastScanned ? (
            <View style={styles.resultCard}>
              <View style={styles.resultHeader}>
                <Ionicons name="checkmark-circle" size={24} color="#10B981" />
                <Text style={styles.resultTitle}>Barcode Found</Text>
              </View>
              <Text style={styles.resultData}>{lastScanned.data}</Text>
              <Text style={styles.resultType}>Type: {lastScanned.type}</Text>
              <View style={styles.resultActions}>
                <TouchableOpacity style={styles.resultBtnSecondary} onPress={() => setScanned(false)}>
                  <Text style={styles.resultBtnSecondaryText}>Scan Again</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.resultBtnPrimary} onPress={() => navigation.navigate('Food')}>
                  <Text style={styles.resultBtnPrimaryText}>Add to Log</Text>
                </TouchableOpacity>
              </View>
            </View>
          ) : (
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
  resultHeader: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 12 },
  resultTitle: { fontSize: 18, fontWeight: '700', color: '#F9FAFB' },
  resultData: { fontSize: 15, color: '#6366F1', fontFamily: 'monospace', marginBottom: 4 },
  resultType: { fontSize: 12, color: '#6B7280', marginBottom: 16 },
  resultActions: { flexDirection: 'row', gap: 12 },
  resultBtnSecondary: { flex: 1, padding: 14, borderRadius: 12, borderWidth: 1, borderColor: '#374151', alignItems: 'center' },
  resultBtnSecondaryText: { color: '#9CA3AF', fontSize: 14, fontWeight: '600' },
  resultBtnPrimary: { flex: 1, padding: 14, borderRadius: 12, backgroundColor: '#6366F1', alignItems: 'center' },
  resultBtnPrimaryText: { color: '#fff', fontSize: 14, fontWeight: '700' },
});