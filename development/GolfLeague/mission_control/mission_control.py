#!/usr/bin/env python3
"""
Mission Control — Central dashboard for golf league automations.
Flask app with one-click automation execution.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
RUNS_DIR = BASE_DIR / "runs"
AUTOMATIONS_DIR = Path(__file__).parent.parent / "scorecard_automation"

UPLOAD_DIR.mkdir(exist_ok=True)
RUNS_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_DIR'] = str(UPLOAD_DIR)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'csv', 'json', 'png', 'jpg', 'jpeg', 'heic', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_automations():
    """Define available automations."""
    return [
        {
            "id": "scorecards",
            "name": "Generate Scorecards",
            "description": "Upload Week_data.json + CSV → generates print-ready HTML scorecards",
            "input_type": "multi",  # expects _data.json + CSV
            "allowed_ext": ["json", "csv"],
            "script": "generate_scorecards.py",
            "working_dir": str(AUTOMATIONS_DIR),
            "icon": "🏌️"
        },
        {
            "id": "scorecards_batch",
            "name": "Scorecards (Batch)",
            "description": "Process all ready files in input folder (both JSON + CSV must exist)",
            "input_type": "none",
            "script": "generate_scorecards.py",
            "working_dir": str(AUTOMATIONS_DIR),
            "icon": "📚"
        }
    ]


def get_runs():
    """Load run history."""
    runs_file = RUNS_DIR / "runs.json"
    if runs_file.exists():
        with open(runs_file) as f:
            return json.load(f)
    return []


def save_run(run):
    """Save a run record."""
    runs_file = RUNS_DIR / "runs.json"
    runs = get_runs()
    runs.insert(0, run)  # newest first
    # Keep last 50 runs
    runs = runs[:50]
    with open(runs_file, 'w') as f:
        json.dump(runs, f, indent=2)


def run_automation(automation_id, uploaded_files=None):
    """Execute an automation and return result."""
    import shutil
    
    automations = {a["id"]: a for a in get_automations()}
    
    if automation_id not in automations:
        return {"success": False, "error": f"Unknown automation: {automation_id}"}
    
    automation = automations[automation_id]
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_time = datetime.now()
    
    # Prepare input files
    input_paths = []
    if uploaded_files:
        if not isinstance(uploaded_files, list):
            uploaded_files = [uploaded_files]
        for uploaded_file in uploaded_files:
            if uploaded_file and uploaded_file.filename:
                filename = secure_filename(uploaded_file.filename)
                input_path = UPLOAD_DIR / filename
                uploaded_file.save(input_path)
                
                # If scorecards, copy to scorecard_automation/input/
                if automation_id == "scorecards":
                    scorecard_input = Path(automation["working_dir"]) / "input" / filename
                    shutil.copy(input_path, scorecard_input)
                    input_paths.append(scorecard_input)
                else:
                    input_paths.append(input_path)
    
    # Execute the script
    script = automation["working_dir"] + "/" + automation["script"]
    output_file = RUNS_DIR / f"run_{run_id}.log"
    
    try:
        # Run without arguments - script finds files in INPUT_DIR
        result = subprocess.run(
            [sys.executable, script],
            cwd=automation["working_dir"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Save output log
        with open(output_file, 'w') as f:
            f.write(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}\n")
        
        success = result.returncode == 0
        
        run_record = {
            "id": run_id,
            "automation": automation_id,
            "automation_name": automation["name"],
            "timestamp": start_time.isoformat(),
            "elapsed_seconds": round(elapsed, 1),
            "success": success,
            "return_code": result.returncode,
            "stdout": result.stdout[:2000],
            "stderr": result.stderr[:2000],
            "log_file": str(output_file),
            "input_files": [str(p) for p in input_paths] if input_paths else None
        }
        
        save_run(run_record)
        
        return {
            "success": success,
            "run_id": run_id,
            "elapsed": elapsed,
            "stdout": result.stdout[:1000],
            "stderr": result.stderr[:1000],
            "return_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Automation timed out after 120 seconds"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.route("/")
def index():
    automations = get_automations()
    runs = get_runs()[:10]  # Last 10 runs
    return render_template("dashboard.html", automations=automations, runs=runs)


@app.route("/upload/<automation_id>", methods=["POST"])
def upload_file(automation_id):
    files = request.files.getlist('files')
    
    if not files or all(f.filename == '' for f in files):
        return jsonify({"success": False, "error": "No files provided"})
    
    for f in files:
        if f.filename and not allowed_file(f.filename):
            return jsonify({"success": False, "error": f"File type not allowed: {f.filename}"})
    
    result = run_automation(automation_id, files)
    return jsonify(result)


@app.route("/run/<automation_id>", methods=["POST"])
def run_now(automation_id):
    result = run_automation(automation_id)
    return jsonify(result)


@app.route("/runs")
def list_runs():
    runs = get_runs()
    return jsonify(runs)


@app.route("/log/<run_id>")
def get_log(run_id):
    log_file = RUNS_DIR / f"run_{run_id}.log"
    if log_file.exists():
        with open(log_file) as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    return "Log not found", 404


@app.route("/clear_runs", methods=["POST"])
def clear_runs():
    """Clear all run history."""
    runs_file = RUNS_DIR / "runs.json"
    if runs_file.exists():
        runs_file.unlink()
    # Clear log files
    for log_file in RUNS_DIR.glob("run_*.log"):
        log_file.unlink()
    return redirect(url_for("index"))


if __name__ == "__main__":
    print("🚀 Mission Control starting on http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=False)
