# Golf League Web Migration Architecture

## Current Architecture Overview

Your current application (`golf_league.py`, 4,120 lines) follows an MVC-like pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    GolfLeagueApp (Tkinter)                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  DataManager (Lines 165-596)                        │    │
│  │  - JSON I/O for players, teams, matches, scores     │    │
│  │  - Schedule generation algorithms                   │    │
│  │  - Handicap management                              │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  ScoringEngine (Lines 600-759)                      │    │
│  │  - Match-play scoring calculations                  │    │
│  │  - Stroke index allocation (Hickory Hills)          │    │
│  │  - Hole points and team bonus calculation           │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  UI Components (Lines 764-4120)                     │    │
│  │  - Tkinter widgets, ttk, messagebox                 │    │
│  │  - 8 tabs: Dashboard, Course, Players, Teams,       │    │
│  │    Season, Schedule, Match Entry, Standings         │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────────────────────────��─────────────────────────┘
```

## Target Web Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Mobile Browser                               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              HTML5 + Tailwind CSS (Jinja2 Templates)         │   │
│  │  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │   │
│  │  │   Players   │   Matches   │ Match Entry │  Standings  │  │   │
│  │  └─────────────┴─────────────┴─────────────┴─────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──��──────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/JSON
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Application (main.py)                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  API Endpoints                                               │   │
│  │  GET  /api/players          → List all players              │   │
│  │  GET  /api/players/{id}     → Get single player             │   │
│  │  GET  /api/teams            → List all teams                │   │
│  │  GET  /api/matches          → List all matches              │   │
│  │  GET  /api/matches/{id}     → Get match details + scores    │   │
│  │  GET  /api/seasons          → List all seasons              │   │
│  │  POST /api/scores/submit    → Submit hole-by-hole scores    │   │
│  │  GET  /api/standings        → Get current standings         │   │
│  │  GET  /api/course-settings  → Get stroke index, pars        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Pydantic Models (Request/Response Validation)              │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Python imports
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Core Business Logic                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  data_manager.py                                             │   │
│  │  - JSON file I/O (players, teams, matches, scores)          │   │
│  │  - Schedule generation algorithms                           │   │
│  │  - Handicap tracking (rolling 3-week average)               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  scoring_engine.py                                           │   │
│  │  - Match-play scoring with Hickory Hills stroke index       │   │
│  │  - Net score calculation (gross - strokes received)         │   │
│  │  - Hole points and team bonus calculation                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ File I/O
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      JSON Data Files (/data)                         │
│  players.json | teams.json | matches.json | scores.json | ...       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Decoupling the "Brain" from the "Face"

### Files to Create

1. **`data_manager.py`** (~500 lines)
   - Extract [`DataManager`](golf_league.py:165) class
   - Keep all JSON I/O methods
   - Keep schedule generation logic
   - Remove: All tkinter references, UI callbacks

2. **`scoring_engine.py`** (~200 lines)
   - Extract [`ScoringEngine`](golf_league.py:600) class
   - Keep [`calculate_match_scores()`](golf_league.py:606) method
   - Preserve Hickory Hills stroke index logic
   - Remove: All tkinter references

### Key Changes

```python
# BEFORE (in golf_league.py)
import tkinter as tk
from tkinter import ttk, messagebox

class DataManager:
    # Uses messagebox for errors
    # References tkinter variables

# AFTER (in data_manager.py)
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from itertools import combinations

class DataManager:
    # Pure JSON I/O
    # Returns data, no UI dependencies
    # Raises exceptions instead of messagebox
```

### Stroke Index Logic (Hickory Hills)

The current stroke index order from [`data/course_settings.json`](data/course_settings.json):

```
Hole:  1  2  3  4  5  6  7  8  9
SI:    3  7  1  6  8  5  9  2  4
```

This is used in [`ScoringEngine.calculate_match_scores()`](golf_league.py:606) at lines 650-684:

- Higher handicap player receives strokes equal to the **difference** between handicaps
- Strokes applied to hardest holes first (SI=1 is hardest, SI=9 is easiest)
- Net = Gross - (1 if stroke_index <= handicap_diff else 0)

---

## Phase 2: Building the FastAPI Backend

### Project Structure

```
web_app/
├── main.py                 # FastAPI application entry point
├── data_manager.py         # Extracted from golf_league.py
├── scoring_engine.py       # Extracted from golf_league.py
├── models.py               # Pydantic models for API
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── match_entry.html
│   ├── players.html
│   └── standings.html
├── static/                 # Static assets (if needed)
│   └── css/
├── data/                   # JSON data files (mounted volume)
│   ├── players.json
│   ├── teams.json
│   ├── matches.json
│   └── scores.json
├── Dockerfile
└── requirements.txt
```

### API Endpoints

| Method | Endpoint                   | Description                                  |
| ------ | -------------------------- | -------------------------------------------- |
| GET    | `/api/players`             | List all players                             |
| GET    | `/api/players/{player_id}` | Get single player                            |
| GET    | `/api/teams`               | List all teams                               |
| GET    | `/api/matches`             | List all matches (with optional week filter) |
| GET    | `/api/matches/{match_id}`  | Get match details with scores                |
| POST   | `/api/scores/submit`       | Submit hole-by-hole scores                   |
| GET    | `/api/seasons`             | List all seasons                             |
| GET    | `/api/standings`           | Get current team standings                   |
| GET    | `/api/course-settings`     | Get stroke index and hole pars               |

### Pydantic Models

```python
from pydantic import BaseModel
from typing import Dict, List, Optional

class Player(BaseModel):
    id: str
    name: str
    handicap: float
    phone: str = ""
    email: str = ""

class ScoreSubmission(BaseModel):
    match_id: str
    team1_player1_scores: Dict[int, int]  # {hole_number: gross_score}
    team1_player2_scores: Dict[int, int]
    team2_player1_scores: Dict[int, int]
    team2_player2_scores: Dict[int, int]

class MatchResult(BaseModel):
    match_id: str
    team1_final_points: float
    team2_final_points: float
    winner: str  # "team1", "team2", "tie"
    hole_results: List[Dict]
```

### JSON Persistence for Docker

```python
# In data_manager.py
DATA_DIR = os.environ.get("DATA_DIR", "/app/data")

# This allows mounting a volume from the NAS
# Docker compose will mount: ./data:/app/data
```

---

## Phase 3: Complete HTML Frontend (All 8 Tabs Converted)

Yes - **every single feature** from your Tkinter desktop app will be converted to HTML pages. You'll access everything through a web browser on your computer, phone, or tablet.

### Navigation Structure

```
┌─────────────────────────────────────────────────────────────┐
│  🏌️ Golf League Manager                              [☰]    │
├─────────────────────────────────────────────────────────────┤
│  Sidebar Navigation:                                        │
│  ┌─────────────────────────────────────────────────────┐   │
��  │ 📊 Dashboard          (overview & quick actions)    │   │
│  │ ⛳ Course Settings    (stroke index, hole pars)     │   │
│  │ 👥 Players            (add, edit, delete players)   │   │
│  │ 🏌️ Teams              (create teams, pair players)  │   │
│  │ 📅 Season Setup       (create seasons, scoring)     │   │
│  │ 📆 Schedule           (generate/view schedule)      │   │
│  │ 📝 Match Entry        (on-course scorecard)         │   │
│  │ 🏆 Standings          (team rankings)               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Page-by-Page Breakdown

| Page                | Features                                                   | Mobile Optimized |
| ------------------- | ---------------------------------------------------------- | ---------------- |
| **Dashboard**       | Stats cards, quick action buttons, season info             | ✅               |
| **Course Settings** | Stroke index editor, hole pars editor, save buttons        | ✅               |
| **Players**         | Player list, add/edit/delete dialogs, search/sort          | ✅               |
| **Teams**           | Team list, create team modal, player dropdowns             | ✅               |
| **Season Setup**    | Create season, select teams, configure hole points & bonus | ✅               |
| **Schedule**        | Week filter, generate week/full schedule, match list       | ✅               |
| **Match Entry**     | Scorecard view, large inputs, stroke highlighting          | ✅✅ (Primary)   |
| **Standings**       | Team rankings table, points breakdown                      | ✅               |

---

## Match Entry Scorecard Design (Mobile-First)

```
┌─────────────────────────────────────────────────────────┐
│  Week 1: Hanson-Topper vs VanderWegen-Carter           │
├──────────────���──────────────────────────────────────────┤
│                                                         │
│  Hole    1    2    3    4    5    6    7    8    9     │
│  Par     4    3    4    4    3    4    3    4    4     │
│  SI      3    7    1    6    8    5    9    2    4     │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Gene Hanson (hcp: 8)      | Pete Wollum (hcp: 10)│  │
│  │ ┌──┬──┬──┬──┬──┬──┬──┬──┬──┐| ┌──┬──┬──┬──┬──┬──┬──┬──┬──┐│  │
│  │ │  │  │  │  │  │  │  │  │  ││ │  │  │  │  │  │  │  │  │  ││  │
│  │ └──┴──┴──┴──┴──┴──┴──┴──┴──┘| └──┴──┴──┴──┴──┴──┴──┴──┴──┘│  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Brandon Topper (hcp: 3)   | Matt V.Wegen (hcp: 2)│  │
│  │ ┌──┬──┬──┬──┬──┬──┬──┬──┬──┐| ┌──┬──┬──┬──┬──┬──┬──┬──┬──┐│  │
│  │ │  │  │  │  │  │  │  │  │  ││ │  │  │  │  │  │  │  │  │  ││  │
│  │ └──┴──┴──┴──┴──┴──┴──┴──┴──┘| └──┴──┴──┴──┴──┴──┴──┴──┴──┘│  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  [Submit Scores]                                        │
└─────────────────────────────────────────────────────────┘
```

### Stroke Highlighting Logic

For each matchup, calculate handicap difference and highlight holes where SI <= diff:

```javascript
// Example: Gene Hanson (8) vs Pete Wollum (10)
// Handicap difference = 2
// Wollum receives strokes on holes where SI <= 2
// Stroke Index order: [3, 7, 1, 6, 8, 5, 9, 2, 4]
// Holes with SI <= 2: Hole 3 (SI=1), Hole 8 (SI=2)
// These holes get highlighted with a gold/orange background
```

### Tailwind CSS Classes

```html
<!-- Stroke hole highlight -->
<input
  class="w-12 h-12 text-center text-lg border-2 border-orange-400 bg-orange-100 rounded-lg"
/>

<!-- Normal hole input -->
<input
  class="w-12 h-12 text-center text-lg border-2 border-gray-300 rounded-lg"
/>

<!-- Large number pad (mobile) -->
<div class="grid grid-cols-3 gap-2 mt-4">
  <button class="p-4 text-2xl bg-gray-100 rounded-lg">1</button>
  <button class="p-4 text-2xl bg-gray-100 rounded-lg">2</button>
  ...
</div>
```

---

## Phase 4: Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: "3.8"

services:
  golf-league:
    build: .
    container_name: golf-league-app
    ports:
      - "1234:1234"
    volumes:
      - /volume1/data/golf-league:/app/data
    environment:
      - DATA_DIR=/app/data
      - ENVIRONMENT=production
    restart: unless-stopped
```

### requirements.txt

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
jinja2==3.1.3
python-multipart==0.0.6
```

---

## Implementation Notes

### Data Migration

No data migration needed - the web app will use the same JSON files:

- [`data/players.json`](data/players.json) - 46 players
- [`data/teams.json`](data/teams.json) - 23 teams
- [`data/matches.json`](data/matches.json) - 33 matches scheduled
- [`data/course_settings.json`](data/course_settings.json) - Stroke index and pars

### Key Scoring Logic to Preserve

From [`ScoringEngine.calculate_match_scores()`](golf_league.py:606):

1. **Hole Points**: Configurable (default 1.0 per matchup, 2 matchups per hole = 2 points max)
2. **Team Bonus**: Configurable (default 5.0 points for lower combined net score)
3. **Ties**: Award 0 points (no splitting)
4. **Net Calculation**:
   ```python
   # For each hole, for each matchup:
   if player_a_hcp > player_b_hcp:
       diff = int(player_a_hcp) - int(player_b_hcp)
       player_a_net = gross - (1 if stroke_index <= diff else 0)
   ```

---

## Testing Strategy

1. **Unit Tests**: Test `data_manager.py` and `scoring_engine.py` independently
2. **API Tests**: Use pytest with TestClient to verify endpoints
3. **Integration Tests**: Test full score submission flow
4. **UI Tests**: Manual testing on mobile devices

---

## Next Steps

1. Review this architecture plan
2. Approve to proceed with Phase 1 implementation
3. Switch to Code mode for implementation
