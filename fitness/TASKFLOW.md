# TASKFLOW.md - Fitness Agent Workflows

## Overview
This TaskFlow defines the fitness agent's core workflows for workout tracking, health maintenance, and athletic performance analysis.

## Core Workflows

### 1. Workout Logging & Progression Tracking
**Trigger:** "Log workout" or "Track progress"
**Steps:**
1. Parse workout details (exercises, sets, reps, weights)
2. Compare to previous performance
3. Calculate progression metrics
4. Update progress charts
5. Provide feedback on form/technique

### 2. Mobility & Injury Prevention
**Trigger:** "Mobility check" or "Injury prevention"
**Steps:**
1. Assess current mobility status
2. Review injury history (snapping hip syndrome)
3. Suggest targeted mobility drills
4. Recommend preventive exercises
5. Schedule regular mobility checks

### 3. Golf Performance Integration
**Trigger:** "Golf prep" or "Golf workout"
**Steps:**
1. Analyze golf schedule (Wednesday nights)
2. Design rotational core work
3. Plan thoracic mobility exercises
4. Schedule recovery around golf
5. Track golf performance metrics

### 4. Nutrition & Recovery Planning
**Trigger:** "Nutrition plan" or "Recovery"
**Steps:**
1. Calculate daily protein needs (~180g)
2. Plan NEAT activities (8k-10k steps)
3. Schedule metabolic workouts
4. Plan hydration strategy
5. Track sleep/recovery metrics

## Data Sources
- Workout logs from memory files
- Performance metrics from tracking apps
- Golf schedule and performance data
- Nutrition tracking information

## Output Formats
- Progress reports (weekly/monthly)
- Workout plans (daily/weekly)
- Recovery recommendations
- Golf performance analysis

## Integration Points
- Calendar for scheduling workouts
- Messaging for reminders/notifications
- Web search for exercise technique
- Data analysis for progress tracking

## Error Handling
- Missing workout data: Prompt for manual entry
- Injury concerns: Escalate to medical professional
- Schedule conflicts: Suggest alternatives

## Success Metrics
- Consistent workout logging
- Injury prevention/maintenance
- Golf performance improvement
- Aesthetic goal progress
- Recovery quality
