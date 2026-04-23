# Golf League Manager

A desktop Python application for managing your golf league season at Hickory Hills Golf Course.

## Features

- **Player Management**: Add, edit, and delete players with handicaps
- **Team Management**: Create teams of 2 players each
- **Course Settings**: Configure stroke index order for net score calculation
- **Season Setup**: Create seasons, select participating teams, and configure scoring
- **Schedule Generation**:
  - Generate full season schedule at once (Season Setup tab)
  - Generate weekly schedule on-demand (Schedule tab) - matches are created based on current handicaps each week
- **Match Entry**: Enter 9-hole gross scores for all 4 players
- **Net Score Calculation**: Automatic net scores based on stroke index and player handicaps
- **Scoring Configuration**: Set hole points and match bonus points during season setup
- **Standings**: View team rankings by total points
- **Rolling Handicap**: 3-week average handicap calculation

## Requirements

- Python 3.8 or higher
- Windows 10/11 (for `.exe` conversion)

## Running the Application

### Option 1: Run with Python

1. Ensure Python 3.8+ is installed
2. Open a terminal in the `GolfLeague` directory
3. Run:
   ```
   python golf_league.py
   ```

### Option 2: Convert to Standalone .exe

To create a standalone executable that doesn't require Python:

1. Install PyInstaller:

   ```
   pip install pyinstaller
   ```

2. Create the executable:

   ```
   pyinstaller --onefile --windowed --name "GolfLeague" --icon=icon.ico golf_league.py
   ```

   Or without an icon:

   ```
   pyinstaller --onefile --windowed --name "GolfLeague" golf_league.py
   ```

3. The executable will be created in the `dist` folder:

   ```
   dist/GolfLeague.exe
   ```

4. Copy `GolfLeague.exe` to any location and run it directly

## Data Storage

All data is stored in JSON files in the `data` folder:

| File                    | Description                               |
| ----------------------- | ----------------------------------------- |
| `course_settings.json`  | Stroke index order, course name, location |
| `players.json`          | Player names and handicaps                |
| `teams.json`            | Team compositions                         |
| `seasons.json`          | Season information                        |
| `matches.json`          | Match schedule                            |
| `scores.json`           | Match scores and results                  |
| `handicap_history.json` | Historical handicap records               |

## Scoring System

### Hole Points

- Each hole features **two individual matchups**: Player 1 vs Player 1, and Player 2 vs Player 2
- Each matchup awards a configurable number of points (default: 1.0 per matchup)
- Therefore, each hole can award up to **2 points total** (1 point per matchup × 2 matchups)
- The player with the lower net score wins their matchup
- **Ties award 0 points to both players** (no split)

### Team Bonus

- Configurable points awarded to the team with the lower **combined net score** (default: 5.0)
- **Ties award 0 points to both teams** (no split)

### Net Score Calculation (Match Play Style)

- In each individual matchup, the player with the **higher handicap** receives strokes equal to the **difference** between the two players' handicaps
- Strokes are allocated to the hardest holes first, based on the stroke index (1 = hardest, 9 = easiest)
- Example: Player A (5 hcp) vs Player B (12 hcp) → Player B receives 7 strokes on holes 1-7 (hardest 7 holes)
- Net = Gross - Strokes Received

**Note**: Scoring settings (hole points per matchup and bonus points) are configured in the Season Setup tab when creating/editing a season.

## Schedule Generation

The schedule uses a greedy algorithm:

1. Calculate all possible team matchups
2. Sort matchups by handicap difference (closest handicaps first)
3. For each week, assign matchups ensuring no team plays twice
4. Continue until all teams have played each other once

For 6 teams, this generates 15 matches over approximately 5-6 weeks.

## Course Information

### Hickory Hills Golf Course (Eau Claire, WI)

- **Par**: 63 (9 holes)
- **Hole Pars**: 4, 3, 4, 3, 3, 4, 3, 4, 3

### Default Stroke Index (Editable in Course Settings)

| Hole  | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   | 9   |
| ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Index | 3   | 8   | 1   | 6   | 9   | 4   | 7   | 2   | 5   |

_Note: Update the stroke index in Course Settings once you have the official order from the scorecard._

## Season Setup with Scoring Configuration

When creating a season in the **Season Setup** tab, you can configure the scoring system:

1. Go to the **Season Setup** tab
2. Create a season by entering a name and clicking **Create Season**
3. In the **Scoring Configuration** section:
   - **Hole Points**: Enter points awarded for winning a single hole (default: 1.0)
   - **Match Bonus**: Enter bonus points for the team with lower combined gross score (default: 5.0)
4. Click **Edit** to enable editing, enter your desired values, then click **Save**
5. Select teams for the season and save

**Scoring Examples**:

- Standard: 1.0 point per hole × 2 matchups = 2 points per hole, plus 5.0 bonus = **7 total points per match** (if one team wins all matchups)
- Double: 2.0 points per hole × 2 matchups = 4 points per hole, plus 10.0 bonus = **14 total points per match** (if one team wins all matchups)
- Half: 0.5 point per hole × 2 matchups = 1 point per hole, plus 2.5 bonus = **3.5 total points per match** (if one team wins all matchups)

_Note: Actual points awarded depend on match results. Ties award 0 points for both hole matchups and team bonus._

All scoring settings are saved in `data/course_settings.json` and apply to all matches in the season.

## Usage Guide

### 1. Add Players

1. Go to the **Players** tab
2. Click **Add Player**
3. Enter name and handicap
4. Repeat for all players (minimum 12 for 6 teams)

### 2. Create Teams

1. Go to the **Teams** tab
2. Click **Add Team**
3. Enter team name and select 2 players
4. Repeat for all teams

### 3. Setup Season

1. Go to the **Season Setup** tab
2. Enter season name (e.g., "2026 Season")
3. Click **Create Season**
4. Select teams for the season using the add/remove buttons
5. Click **Save Season** to save the season configuration (no matches generated yet)
6. Close the application or proceed to match entry

### 4. Generate Weekly Schedule

**Option A: Full Season Schedule (if not done in Season Setup)**

1. In **Season Setup** tab, after selecting teams
2. Click **Generate Full Schedule** to create all matches at once

**Option B: Weekly Generation (Recommended)**

1. Go to the **Schedule** tab
2. Select the week number from the dropdown (1-25)
3. Click **Generate Week** to create matches for that specific week
4. Each week, repeat: select the current week and click **Generate Week**
   - Matchups are based on current player handicaps
   - Handicap changes throughout the season will affect future matchups
   - No duplicate matchups - each team plays every other team exactly once

### 4. Enter Match Scores

1. Go to the **Match Entry** tab
2. Select a match from the dropdown
3. Enter gross scores for all 4 players (9 holes each)
4. Click **Save Scores**
5. View the results dialog

### 5. View Standings

1. Go to the **Standings** tab
2. Click **Refresh Standings** to update
3. Teams are ranked by total points

## Troubleshooting

### Application won't start

- Ensure Python 3.8+ is installed
- Run `python --version` to check
- Try running from terminal to see error messages

### Data not saving

- Check that the `data` folder exists and is writable
- Ensure no other program has the JSON files open

### Schedule generation fails

- Ensure at least 2 teams are selected
- Ensure all selected teams have 2 players each

## License

MIT License - Free for personal and commercial use

## Version

1.0 - Initial Release (2026 Season)
