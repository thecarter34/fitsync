#!/usr/bin/env python3
"""
Mission Control — Central dashboard for running automations.
Flask app with one-click automation execution.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from flask import send_from_directory,  Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
RUNS_DIR = BASE_DIR / "runs"
AUTOMATIONS_DIR = Path("/home/thecarter34/.openclaw/workspace/development/GolfLeague/scorecard_automation")

UPLOAD_DIR.mkdir(exist_ok=True)
RUNS_DIR.mkdir(exist_ok=True)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['UPLOAD_DIR'] = str(UPLOAD_DIR)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

@app.route('/ws_logo.png')
def ws_logo():
    return send_from_directory('static', 'ws_logo.png')

ALLOWED_EXTENSIONS = {'csv', 'json', 'png', 'jpg', 'jpeg', 'heic', 'pdf'}

WALKSCAPE_ADVISOR_FILE = BASE_DIR / "walkscape_advisor.json"
WALKSCAPE_GAME_DATA_FILE = BASE_DIR / "walkscape_player.json"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_automations():
    """Define available automations."""
    return [
        {
            "id": "scorecards",
            "name": "Generate Scorecards",
            "description": "Drops PDF + CSV in input/ → generates print-ready HTML scorecards",
            "input_type": "folder_watch",
            "script": "generate_scorecards.py",
            "working_dir": str(AUTOMATIONS_DIR),
            "icon": "🏌️"
        },
        {
            "id": "leaderboard",
            "name": "Generate Leaderboard",
            "description": "Reads matches + scores + teams data → generates season standings HTML",
            "input_type": "none",
            "script": "generate_leaderboard.py",
            "working_dir": str(AUTOMATIONS_DIR),
            "icon": "📊"
        },
        {
            "id": "scorecards_batch",
            "name": "Scorecards (Batch)",
            "description": "Process all ready files in input folder (both JSON + CSV must exist)",
            "input_type": "none",
            "script": "generate_scorecards.py",
            "working_dir": str(AUTOMATIONS_DIR),
            "icon": "📚"
        },
        {
            "id": "walkscape_advisor",
            "name": "WalkScape Advisor",
            "description": "Upload your WalkScape export → get a personalized recommended action",
            "input_type": "walkscape_json",
            "icon": "🎮"
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


@app.route("/walkscape_advisor")
def walkscape_advisor_page():
    """Return the WalkScape Advisor HTML panel."""
    # Load saved player data and recommendation
    player_data = {}
    recommendation = {}
    
    if WALKSCAPE_GAME_DATA_FILE.exists():
        with open(WALKSCAPE_GAME_DATA_FILE) as f:
            player_data = json.load(f)
    
    if WALKSCAPE_ADVISOR_FILE.exists():
        with open(WALKSCAPE_ADVISOR_FILE) as f:
            recommendation = json.load(f)
    
    # Also load any pending chat answer
    chat_answer_file = RUNS_DIR / "walkscape_chat.json"
    chat_answer = None
    if chat_answer_file.exists():
        try:
            with open(chat_answer_file) as f:
                chat_answer = json.load(f).get("answer")
        except Exception:
            pass

    return jsonify({
        "player": player_data,
        "recommendation": recommendation,
        "chat_answer": chat_answer
    })


@app.route("/walkscape/upload", methods=["POST"])
def walkscape_upload():
    """Handle WalkScape JSON export upload."""
    file = request.files.get('file')
    if not file:
        return jsonify({"success": False, "error": "No file provided"})
    
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"})
    
    try:
        content = file.read().decode('utf-8')
        player_data = json.loads(content)
        
        # Validate this looks like a WalkScape export
        if 'skills' not in player_data or 'name' not in player_data:
            return jsonify({"success": False, "error": "Invalid WalkScape export format"})
        
        # Save raw player data
        with open(WALKSCAPE_GAME_DATA_FILE, 'w') as f:
            json.dump(player_data, f, indent=2)
        
        # Save upload timestamp
        player_data['_imported_at'] = datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "player_name": player_data.get('name'),
            "skills": player_data.get('skills', {}),
            "imported_at": player_data['_imported_at']
        })
    except json.JSONDecodeError:
        return jsonify({"success": False, "error": "Invalid JSON file"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/walkscape/recommend", methods=["POST"])
def walkscape_recommend():
    """Generate a recommendation based on current player data."""
    if not WALKSCAPE_GAME_DATA_FILE.exists():
        return jsonify({"success": False, "error": "No player data uploaded yet"})
    
    with open(WALKSCAPE_GAME_DATA_FILE) as f:
        player_data = json.load(f)
    
    # Build context for AI recommendation
    skills = player_data.get('skills', {})
    gear = player_data.get('gear', {})
    inventory = player_data.get('inventory', {})
    bank = player_data.get('bank', {})
    currencies = player_data.get('currencies', {})
    reputation = player_data.get('reputation', {})
    
    context = {
        "player_name": player_data.get('name'),
        "steps": player_data.get('steps', 0),
        "coins": player_data.get('coins', 0),
        "achievement_points": player_data.get('achievement_points', 0),
        "skills": skills,
        "gear": gear,
        "currencies": currencies,
        "reputation": reputation,
        "inventory_count": len(inventory),
        "bank_count": len(bank),
        "top_bank_items": dict(list(bank.items())[:20]),
    }
    
    return jsonify({"success": True, "context": context})

@app.route("/walkscape/save_recommendation", methods=["POST"])
def walkscape_save_recommendation():
    """Save a recommendation from AI analysis."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"})
    
    with open(WALKSCAPE_ADVISOR_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return jsonify({"success": True})

@app.route("/walkscape/chat", methods=["POST"])
def walkscape_chat():
    """Handle a chat message with WalkScape context."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"success": False, "error": "No message provided"})
    
    user_message = data['message']
    
    # Load current player context if available
    context = {}
    if WALKSCAPE_GAME_DATA_FILE.exists():
        with open(WALKSCAPE_GAME_DATA_FILE) as f:
            player = json.load(f)
            skills = player.get('skills', {})
            gear = player.get('gear', {})
            bank = player.get('bank', {})
            currencies = player.get('currencies', {})
            reputation = player.get('reputation', {})
            context = {
                "player_name": player.get('name'),
                "steps": player.get('steps', 0),
                "coins": player.get('coins', 0),
                "achievement_points": player.get('achievement_points', 0),
                "skills": skills,
                "gear": gear,
                "currencies": currencies,
                "reputation": reputation,
                "bank_count": len(bank),
                "top_bank_items": dict(list(bank.items())[:30]),
            }
    
    # Return the context so the frontend can send it to the AI session
    return jsonify({
        "success": True,
        "context": context,
        "user_message": user_message
    })


WALKSCAPE_SYSTEM_PROMPT = """You are a WalkScape Advisor. You have deep knowledge of the WalkScape game (walkscape.app) — a mobile fitness RPG where real-world walking translates into in-game progress.

You help the player optimize their next activity by analyzing their character stats, gear, bank, inventory, currencies, and achievements.

Your responses should be:
- Direct and action-oriented (no fluffy language)
- Include specific activity name, location, and reasoning
- Always call out MISSING requirements (skill level minimums, required gear, etc.) in a dedicated field
- Suggest concrete alternatives when requirements aren't met

Game knowledge reference:
- Skills: Agility, Carpentry, Cooking, Crafting, Fishing, Foraging, Hunting, Mining, Smithing, Tailoring, Trinketry, Woodcutting
- Activities award XP in primary + sometimes secondary skills
- Work Efficiency caps vary by activity (150%-300%)
- Mining activities at Underwater Cave and Crown of Cinders offer highest XP/step for high-level miners
- Cave Diving (Mining 55+, Agility 55+) = dual skill activity at Underwater Cave
- Agility chips, foraging chips, mining chips, fishing chips are currencies earned through activities
- Achievement Points are earned by completing achievements — often tied to skill levels or activities

When given player stats, analyze and recommend the single best next activity with:
1. Activity name and location
2. Which skill(s) it levels
3. Why it fits their current state better than alternatives
4. **Missing requirements** — always include this, even if empty (e.g., "Missing: Mining level 55+ (you have 37), Leather Boots (check bank)")
5. What they'll gain (XP type, chips, items, achievement progress, etc.)
6. If the player mentioned a goal, prioritize that goal above all else
"""

def build_walkscape_prompt(user_message, context):
    """Build a detailed prompt for the WalkScape AI advisor."""
    skills = context.get('skills', {})
    gear = context.get('gear', {})
    currencies = context.get('currencies', {})
    
    # Sort skills by XP descending
    sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    
    prompt = f"""Player: {context.get('player_name', 'Unknown')}
Total Steps: {context.get('steps', 0):,}
Coins: {context.get('coins', 0):,}
Achievement Points: {context.get('achievement_points', 0)}

=== TOP SKILLS (by XP) ===
"""
    for skill, xp in sorted_skills[:6]:
        prompt += f"  {skill}: {xp:,} XP\n"
    
    prompt += f"""
=== EQUIPPED GEAR ===
"""
    for slot, item in gear.items():
        prompt += f"  {slot}: {item}\n"
    
    prompt += f"""
=== CURRENCIES ===
"""
    for currency, amount in currencies.items():
        prompt += f"  {currency}: {amount}\n"
    
    prompt += f"""
=== BANK (top items) ===
"""
    for item, count in list(context.get('top_bank_items', {}).items())[:25]:
        prompt += f"  {item}: {count}\n"
    
    prompt += f"""
=== PLAYER'S QUESTION ===
{user_message}

Please recommend a specific next activity and explain why."""
    return prompt


@app.route("/ai/ask", methods=["POST"])
def ai_ask():
    """Spawn an AI sub-agent to answer a WalkScape question and save the result."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"success": False, "error": "No message provided"})
    
    user_message = data['message']
    
    # Load player context
    context = {}
    if WALKSCAPE_GAME_DATA_FILE.exists():
        with open(WALKSCAPE_GAME_DATA_FILE) as f:
            player = json.load(f)
            skills = player.get('skills', {})
            gear = player.get('gear', {})
            bank = player.get('bank', {})
            currencies = player.get('currencies', {})
            context = {
                "player_name": player.get('name'),
                "steps": player.get('steps', 0),
                "coins": player.get('coins', 0),
                "achievement_points": player.get('achievement_points', 0),
                "skills": skills,
                "gear": gear,
                "currencies": currencies,
                "reputation": player.get('reputation', {}),
                "bank_count": len(bank),
                "top_bank_items": dict(list(bank.items())[:30]),
            }
    
    # Build the AI task prompt
    sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    prompt_lines = f"""Player: {context.get('player_name', 'Unknown')}
Total Steps: {context.get('steps', 0):,}
Coins: {context.get('coins', 0):,}
Achievement Points: {context.get('achievement_points', 0)}

=== TOP SKILLS (by XP) ===
"""
    for skill, xp in sorted_skills[:6]:
        prompt_lines += f"  {skill}: {xp:,} XP\n"
    
    prompt_lines += "\n=== EQUIPPED GEAR ===\n"
    for slot, item in gear.items():
        prompt_lines += f"  {slot}: {item}\n"
    
    prompt_lines += "\n=== CURRENCIES ===\n"
    for currency, amount in currencies.items():
        prompt_lines += f"  {currency}: {amount}\n"
    
    prompt_lines += "\n=== BANK (top items) ===\n"
    for item, count in list(context.get('top_bank_items', {}).items())[:25]:
        prompt_lines += f"  {item}: {count}\n"
    
    prompt_lines += f"""\n=== PLAYER'S QUESTION ===
{user_message}

Please recommend a specific next activity and explain why.

Respond with:
1. **Recommended Activity** (name + location)
2. **Skill(s) leveled**
3. **Why this is optimal for their current state**
4. **Missing requirements** (if any)
5. **What they'll gain** (XP type, chips, items, etc.)

Be specific and decisive. No hedging."""

    system_prompt = """You are a WalkScape Advisor with deep knowledge of walkscape.app game mechanics. You give specific, actionable recommendations based on player stats."""

    # Save pending request
    import uuid
    request_id = str(uuid.uuid4())[:8]
    pending_request = {
        "id": request_id,
        "message": user_message,
        "context": context,
        "prompt": prompt_lines,
        "system": system_prompt,
        "status": "pending"
    }
    
    pending_file = RUNS_DIR / f"ws_pending_{request_id}.json"
    with open(pending_file, 'w') as f:
        json.dump(pending_request, f, indent=2)
    
    return jsonify({
        "success": True,
        "request_id": request_id,
        "message": "AI is analyzing your stats. The recommendation will be saved automatically."
    })


@app.route("/ai/status/<request_id>", methods=["GET"])
def ai_status(request_id):
    """Check the status of an AI recommendation request."""
    pending_file = RUNS_DIR / f"ws_pending_{request_id}.json"
    if not pending_file.exists():
        return jsonify({"success": False, "error": "Request not found"})
    with open(pending_file) as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/ai/save", methods=["POST"])
def ai_save():
    """Save an AI recommendation result from the sub-agent."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"})
    
    activity = data.get('activity', 'Analyzing...')
    reason = data.get('reason', data.get('result', ''))
    skill = data.get('skill', '')
    location = data.get('location', '')
    est_xp = data.get('est_xp', '')
    why = data.get('why', '')
    
    recommendation = {
        "activity": activity,
        "reason": reason,
        "skill": skill,
        "location": location,
        "est_xp": est_xp,
        "why": why,
        "updated_at": datetime.now().isoformat()
    }
    
    with open(WALKSCAPE_ADVISOR_FILE, 'w') as f:
        json.dump(recommendation, f, indent=2)
    
    return jsonify({"success": True})

@app.route("/ai/answer", methods=["POST"])
def ai_answer():
    """Spawn a sub-agent via openclaw agent command to answer the question and save the recommendation."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"success": False, "error": "No message provided"})
    
    user_message = data['message']
    
    # Build context from player data
    context = {}
    if WALKSCAPE_GAME_DATA_FILE.exists():
        with open(WALKSCAPE_GAME_DATA_FILE) as f:
            player = json.load(f)
            skills = player.get('skills', {})
            gear = player.get('gear', {})
            currencies = player.get('currencies', {})
            bank = player.get('bank', {})
            context = {
                "player_name": player.get('name'),
                "steps": player.get('steps', 0),
                "coins": player.get('coins', 0),
                "achievement_points": player.get('achievement_points', 0),
                "skills": skills,
                "gear": gear,
                "currencies": currencies,
                "bank_count": len(bank),
                "top_bank_items": dict(list(bank.items())[:30]),
            }
    
    # Build the task prompt
    sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    prompt_lines = f"""Player: {context.get('player_name', 'Unknown')}
Total Steps: {context.get('steps', 0):,}
Coins: {context.get('coins', 0):,}
Achievement Points: {context.get('achievement_points', 0)}

=== TOP SKILLS (by XP) ===
"""
    for skill, xp in sorted_skills[:6]:
        prompt_lines += f"  {skill}: {xp:,} XP\n"
    
    prompt_lines += "\n=== EQUIPPED GEAR ===\n"
    for slot, item in gear.items():
        prompt_lines += f"  {slot}: {item}\n"
    
    prompt_lines += "\n=== CURRENCIES ===\n"
    for currency, amount in currencies.items():
        prompt_lines += f"  {currency}: {amount}\n"
    
    prompt_lines += "\n=== BANK (top items) ===\n"
    for item, count in list(context.get('top_bank_items', {}).items())[:25]:
        prompt_lines += f"  {item}: {count}\n"
    
    # Build task without f-string to avoid $ACTIVITY being interpreted as Python vars
    task = "You are a WalkScape Advisor. Answer the player's question with a specific activity recommendation.\n\n"
    task += prompt_lines + "\n\n"
    task += "=== PLAYER'S QUESTION ===\n"
    task += user_message + "\n\n"
    task += "Your response must end with this EXACT JSON block (nothing else after it):\n"
    task += '{"activity": "...", "reason": "...", "skill": "...", "location": "...", "est_xp": "...", "why": "...", "missing_requirements": "...", "updated_at": "ISO timestamp"}\n\n'
    task += "After your recommendation text, output the JSON on its own line. No markdown code blocks. No explanations after the JSON."

    # Spawn via openclaw agent command (async - no waiting for response)
    try:
        import threading

        def run_agent_and_save():
            result = subprocess.run([
                'openclaw', 'agent', '--local',
                '--session-id', 'main',
                '--message', task,
                '--timeout', '90'
            ], capture_output=True, text=True, timeout=95)
            import re, json
            try:
                # Split stdout into lines, find the last {...} JSON block
                lines = result.stdout.strip().split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('{') and '"activity"' in stripped:
                        in_json = True
                    if in_json:
                        json_lines.append(line)
                        if stripped.endswith('}') and len(json_lines) > 1:
                            break
                if json_lines:
                    json_str = '\n'.join(json_lines)
                    with open(WALKSCAPE_ADVISOR_FILE, 'w') as f:
                        f.write(json_str)
                # Save chat answer text (everything BEFORE the JSON block)
                if json_lines:
                    answer_text = '\n'.join(lines[:len(lines) - len(json_lines)]).strip()
                    if answer_text:
                        with open(RUNS_DIR / "walkscape_chat.json", 'w') as f:
                            json.dump({"answer": answer_text, "ts": datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')}, f)
            except Exception:
                pass

        threading.Thread(target=run_agent_and_save, daemon=True).start()
        return jsonify({"success": True, "thinking": "🤖 Analyzing your stats — recommendation card will update shortly..."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

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
