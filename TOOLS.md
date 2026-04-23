# TOOLS.md - Local Notes

## What Goes Here

Environment-specific settings, project state, credentials, device configs. Update as projects grow.

---

# WORKSPACE (Josh)

## Workspace Root
`/home/thecarter34/.openclaw/workspace/`

## Projects

```
workspace/
├── development/
│   ├── CarterQualityConstruction/   # Construction co. website
│   ├── GolfLeague/                  # Golf league management app
│   ├── fitness/                      # Gym/health tracking (future)
│   └── [future projects]
├── mission_control/                  # Automation dashboard — http://localhost:5050
└── [root level files: MEMORY.md, AGENTS.md, SOUL.md, USER.md, etc.]
```

---

# PROJECTS

## CarterQualityConstruction
- **Path:** `development/CarterQualityConstruction/`
- **Dev Server:** `http://localhost:8080`
- **tmux session:** `dev-servers:cqc` (or start with `python3 -m http.server 8080`)

## GolfLeague
- **Path:** `development/GolfLeague/`
- **Golf League App:** `golf_league_app/` — Flask app, runs separately
- **Scorecard Automation:** `scorecard_automation/` — generate scorecards + leaderboards

## Mission Control
- **Path:** `mission_control/`
- **URL:** `http://localhost:5050`
- **Purpose:** General automation hub (Flask-based)
- **Automations:**
  - 🏌️ Scorecard Generator
  - 📊 Season Standings (leaderboard from Squabbit CSV)
  - 📚 Scorecards (Batch)
  - 🎮 WalkScape Advisor

---

# DEV SERVERS (tmux: dev-servers)

Dev servers run in a persistent tmux session so they survive between turns.

```bash
# List running servers
tmux list-windows -t dev-servers

# Check server output
tmux capture-pane -t dev-servers -p

# Kill a server
tmux kill-window -t dev-servers:PROJECT_NAME

# Start a new dev server
cd /path/to/project && python3 -m http.server PORT
# Then: Ctrl+B, D to detach
```

---

# AUTOMATIONS (Mission Control — http://localhost:5050)

## Scorecard Generator (🏌️)
- **Input:** PDF (matchups) + CSV (handicaps) → drop in `scorecard_automation/input/`
- **Output:** `scorecard_automation/output/Week_X_print.html`
- **Script:** `generate_scorecards.py`

## Season Standings / Leaderboard (📊)
- **Input:** Squabbit CSV export (standings section at bottom of file)
- **Output:** `scorecard_automation/output/leaderboard.html` — auto-downloads after run
- **Week detection:** Uses the week column with the most scores (ignores empty/zero columns)
- **Script:** `generate_leaderboard.py`

## Scorecards (Batch) (📚)
- Processes all ready `Week_X_data.json` + `Week_X.csv` pairs in `input/`

---

# BROWSER TESTING
- Browser plugin configured for localhost
- Can open pages, take screenshots, click, fill forms, verify changes

---

# KEY PATHS

| Purpose | Path |
|---------|------|
| Mission Control | `/workspace/mission_control/` |
| Mission Control uploads | `/workspace/mission_control/uploads/` |
| Scorecard input | `/workspace/development/GolfLeague/scorecard_automation/input/` |
| Scorecard output | `/workspace/development/GolfLeague/scorecard_automation/output/` |
| Golf league app data | `/workspace/development/GolfLeague/golf_league_app/data/` |
| Leaderboard (latest) | `/workspace/development/GolfLeague/scorecard_automation/output/leaderboard.html` |

---

# STACK-AGNOSTIC APPROACH
- Plain HTML/CSS/JS → fast, simple, no build step
- Need a framework? → suggest one based on the task
- Database? → SQLite for lightweight, Postgres for real projects
- Hosting? → local dev first, then suggest deployment options

---

# REMOTE ACCESS

- **Mission Control:** `http://localhost:5050` (local only for now)
- **CarterQualityConstruction:** `http://localhost:8080` (local only)

---

# ENVIRONMENT

- **WSL2** on Windows (Ubuntu-based)
- **Node:** v22.22.2
- **Python:** 3.12 (in `.venv` within scorecard_automation)
- **Shell:** bash
- **Discord:** Primary communication channel with Josh