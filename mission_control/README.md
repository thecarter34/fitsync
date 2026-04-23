# Mission Control — Automation Hub

A web dashboard for running your automations with one click. General-purpose — any script can be added.

## Quick Start

```bash
cd /home/thecarter34/.openclaw/workspace/mission_control
./start.sh
```

Then open **http://localhost:5050** in your browser.

## Automations

### 🏌️ Generate Scorecards
Generates print-ready HTML scorecards from league data.

**Workflow:**
1. Upload your `Week_X_data.json` (group/tee time data)
2. Upload your `Week_X.csv` (player handicap data)
3. Click **Execute**
4. Check the scorecard output folder for generated HTML

**Note:** The script expects both files to be in the input folder.

### 📚 Scorecards (Batch)
Runs the scorecard generator on all ready files in the input folder.

## File Locations

| Purpose | Path |
|---------|------|
| Dashboard | `mission_control/` |
| Uploaded files | `mission_control/uploads/` |
| Run history | `mission_control/runs/` |
| Scorecard input | `development/GolfLeague/scorecard_automation/input/` |
| Scorecard output | `development/GolfLeague/scorecard_automation/output/` |

## Managing the Server

```bash
# Check if running
ps aux | grep mission_control | grep -v grep

# View logs
tail -f /tmp/mission_control.log

# Stop
pkill -f "mission_control.py"

# Restart
./start.sh
```

## Adding New Automations

Edit `mission_control.py` and add a new entry to `get_automations()`:

```python
{
    "id": "my_automation",
    "name": "My Automation",
    "description": "What it does",
    "input_type": "file",  # or "multi" or "none"
    "allowed_ext": ["csv"],  # for file/multi types
    "script": "my_script.py",
    "working_dir": "/path/to/script/dir",
    "icon": "🤖"
}
```

The `input_type` options:
- `file` — single file upload
- `multi` — multiple file upload
- `none` — runs without file input

## Architecture

- **Flask** web server (Python)
- **Dark-themed** dashboard with drag-and-drop
- **Run history** persisted in `runs/runs.json`
- **Job logs** saved to `runs/run_<timestamp>.log`
