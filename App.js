import React, { useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import Dashboard from './src/screens/Dashboard';
import FoodLog from './src/screens/FoodLog';
import Scanner from './src/screens/Scanner';
import Progress from './src/screens/Progress';
import Settings from './src/screens/Settings';
import Workout from './src/screens/Workout';
import QuickStartWorkout from './src/screens/QuickStartWorkout';
import ProgramManager from './src/screens/ProgramManager';
import WorkoutHistory from './src/screens/WorkoutHistory';

const WorkoutStack = createNativeStackNavigator();

function WorkoutStackScreen() {
  const [workoutStackState, setWorkoutStackState] = React.useState({
    customWorkoutData: null,
    addToExisting: false,
  });
  
  const updateWorkoutStack = (updates) => {
    setWorkoutStackState(prev => ({ ...prev, ...updates }));
  };
  
  return (
    <WorkoutStack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: '#111827' },
        headerTintColor: '#F9FAFB',
        headerTitleStyle: { fontWeight: '700' },
      }}
    >
      <WorkoutStack.Screen
        name="WorkoutMain"
        component={Workout}
        initialParams={{ 
          workoutStackState, 
          setWorkoutStackData: updateWorkoutStack 
        }}
        options={{ headerShown: false }}
      />
      <WorkoutStack.Screen
        name="QuickStart"
        component={QuickStartWorkout}
        initialParams={{ 
          setWorkoutStackData: updateWorkoutStack,
          workoutStackState,
        }}
        options={{
          title: 'Quick Start',
          presentation: 'modal',
          headerStyle: { backgroundColor: '#0F172A' },
        }}
      />
      <WorkoutStack.Screen
        name="History"
        component={WorkoutHistory}
        options={{
          title: 'Workout History',
          headerStyle: { backgroundColor: '#0F172A' },
        }}
      />
    </WorkoutStack.Navigator>
  );
}

const Tab = createBottomTabNavigator();

function App() {
  return (
    <NavigationContainer>
      <StatusBar style="light" />
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;
            if (route.name === 'Dashboard') iconName = focused ? 'home' : 'home-outline';
            else if (route.name === 'Food') iconName = focused ? 'restaurant' : 'restaurant-outline';
            else if (route.name === 'Scan') iconName = focused ? 'barcode' : 'barcode-outline';
            else if (route.name === 'Progress') iconName = focused ? 'trending-up' : 'trending-up-outline';
            else if (route.name === 'Workout') iconName = focused ? 'fitness' : 'fitness-outline';
            else if (route.name === 'Program') iconName = focused ? 'barbell' : 'barbell-outline';
            else if (route.name === 'Settings') iconName = focused ? 'settings' : 'settings-outline';
            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#6366F1',
          tabBarInactiveTintColor: '#9CA3AF',
          tabBarStyle: {
            backgroundColor: '#1F2937',
            borderTopColor: '#374151',
            paddingTop: 8,
            paddingBottom: 8,
            height: 70,
          },
          tabBarLabelStyle: {
            fontSize: 11,
            fontWeight: '600',
            marginTop: 4,
          },
          headerStyle: {
            backgroundColor: '#111827',
          },
          headerTintColor: '#F9FAFB',
          headerTitleStyle: {
            fontWeight: '700',
          },
        })}
      >
        <Tab.Screen name="Dashboard" component={Dashboard} options={{ title: 'Today' }} />
        <Tab.Screen name="Food" component={FoodLog} options={{ title: 'Food Log' }} />
        <Tab.Screen name="Scan" component={Scanner} options={{ title: 'Scan' }} />
        <Tab.Screen name="Progress" component={Progress} options={{ title: 'Progress' }} />
        <Tab.Screen name="Workout" component={WorkoutStackScreen} options={{ title: 'Workout' }} />
        <Tab.Screen name="Program" component={ProgramManager} options={{ title: 'Program' }} />
        <Tab.Screen name="Settings" component={Settings} options={{ title: 'Settings' }} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
  },
});

export default App;