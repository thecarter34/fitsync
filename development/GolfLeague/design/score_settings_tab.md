# Scoring Settings Design

## Overview

Add a dedicated Scoring Settings tab to configure scoring parameters:

- Hole points configuration (1 point per hole win, adjustable)
- Team bonus configuration (5 points total, adjustable)
- Optionally, other scoring parameters

## UI Layout

Create a new tab in the main notebook called "Scoring Settings"

Controls:

1. Hole Points Configuration:
   - Label: "Hole Points per Hole"
   - Display: List of 9 input fields, one for each hole
   - Default values: 1.0 for all holes (standard scoring)
   - Tooltip: "Points awarded for winning a hole"

2. Team Bonus Configuration:
   - Label: "Team Bonus Points"
   - Display: Input field for total bonus points (default: 5)
   - Tooltip: "Points awarded to team with lower gross score"

3. Validation:
   - Hole points must be positive numbers
   - Team bonus must be positive number
   - Validate on input change

4. Save Button:
   - "Save Scoring Settings" button to persist changes

## Data Storage

- Store configuration in Course Settings JSON:
  - "hole_points": [1.0, 1.0, ..., 1.0] (9 values)
  - "team_bonus_points": 5.0

## Integration

- Modify ScoringEngine to read configurable values:
  - Use hole_points list for hole point values
  - Use team_bonus_points for bonus points
- Default values should match current hardcoded values for backward compatibility

## Implementation Steps

1. Add new tab in main UI
2. Create form controls for scoring parameters
3. Implement save functionality
4. Update ScoringEngine to use configurable values
5. Add validation logic
6. Update Course Settings schema
