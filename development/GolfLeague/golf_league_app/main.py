"""
FastAPI Application for Golf League Manager
Main entry point for the web API.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os
from datetime import datetime

from data_manager import DataManager
from scoring_engine import ScoringEngine
from models import *

# Suppress uvicorn access logs
import logging
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# =============================================================================
# APPLICATION SETUP
# =============================================================================
app = FastAPI(
    title="Golf League Manager API",
    description="API for managing golf league operations",
    version="1.0.0"
)

# CORS configuration for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files - serve logo and other static assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates - custom Jinja2-like renderer (avoids Jinja2/Python 3.13 compatibility issues)
from starlette.responses import HTMLResponse
import re

# Simple template cache
_template_cache = {}

def _load_template(name: str) -> str:
    """Load template from file with caching."""
    if name not in _template_cache:
        with open(f"templates/{name}", "r", encoding="utf-8") as f:
            _template_cache[name] = f.read()
    return _template_cache[name]

def _process_variables(text: str, context: dict) -> str:
    """Replace {{ variable }} with values from context."""
    def replace_var(match):
        var_name = match.group(1).strip()
        # Handle nested attributes like request.url.path
        if '.' in var_name:
            parts = var_name.split('.')
            value = context
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    try:
                        value = getattr(value, part)
                    except AttributeError:
                        return match.group(0)
                if value is None:
                    return match.group(0)
            return str(value) if value is not None else match.group(0)
        else:
            value = context.get(var_name)
            return str(value) if value is not None else match.group(0)
    
    return re.sub(r'\{\{\s*(.+?)\s*\}\}', replace_var, text)

def _process_conditionals(text: str, context: dict) -> str:
    """Process {% if condition %}...{% endif %} blocks."""
    # Simple if pattern - only handles the specific pattern used in base.html
    # {% if request.url.path == '/' %}active{% endif %}
    def replace_if(match):
        condition = match.group(1).strip()
        content = match.group(2)
        # Evaluate simple equality conditions
        if '==' in condition:
            left, right = condition.split('==', 1)
            left = left.strip()
            right = right.strip().strip("'\"")
            
            # Get left value from context
            if '.' in left:
                parts = left.split('.')
                value = context
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part)
                    else:
                        value = getattr(value, part, None)
            else:
                value = context.get(left)
            
            # Compare
            if str(value) == right:
                return content
        return ''
    
    # Process {% if ... %}content{% endif %}
    pattern = r'\{%\s*if\s+(.+?)\s*%\}(.*?)\{%\s*endif\s*%\}'
    text = re.sub(pattern, replace_if, text, flags=re.DOTALL)
    
    # Process {% with var = expression %}content{% endwith %}
    def replace_with(match):
        expression = match.group(1).strip()
        content = match.group(2)
        # Parse "var = expression"
        if '=' in expression:
            var_name, expr = expression.split('=', 1)
            var_name = var_name.strip()
            expr = expr.strip()
            
            # Evaluate the expression (currently only supports simple function calls like get_flashed_messages())
            if expr == 'get_flashed_messages()':
                # For now, return empty content since flash messages aren't implemented
                # In a full implementation, this would call a function to get flash messages
                return ''
            else:
                # Try to evaluate other expressions
                return content
        return content
    
    with_pattern = r'\{%\s*with\s+(.+?)\s*%\}(.*?)\{%\s*endwith\s*%\}'
    text = re.sub(with_pattern, replace_with, text, flags=re.DOTALL)
    
    return text

def _extract_blocks(template_str: str) -> dict:
    """Extract block definitions from template."""
    blocks = {}
    # Pattern to match: {% block name %}content{% endblock %}
    pattern = r'\{%\s*block\s+(\w+)\s*%\}(.*?)\{%\s*endblock\s*%\}'
    for match in re.finditer(pattern, template_str, re.DOTALL):
        block_name = match.group(1)
        block_content = match.group(2).strip()
        blocks[block_name] = block_content
    return blocks

def _apply_extends(template_str: str, context: dict) -> str:
    """Process {% extends "base.html" %} and replace blocks."""
    extends_match = re.search(r'\{%\s*extends\s+"([^"]+)"\s*%\}', template_str)
    if not extends_match:
        # No extends, return processed template as-is
        return _process_conditionals(_process_variables(template_str, context), context)
    
    parent_name = extends_match.group(1)
    parent_str = _load_template(parent_name)
    
    # Extract blocks from child template
    child_blocks = _extract_blocks(template_str)
    
    # Replace blocks in parent
    result = parent_str
    for block_name, block_content in child_blocks.items():
        # Process the block content (variables and conditionals)
        processed_block = _process_conditionals(_process_variables(block_content, context), context)
        # Replace block in parent
        block_pattern = r'\{%\s*block\s+' + re.escape(block_name) + r'\s*%\}.*?\{%\s*endblock\s*%\}'
        result = re.sub(block_pattern, processed_block, result, flags=re.DOTALL)
    
    # Process any remaining variables and conditionals in the parent
    result = _process_conditionals(_process_variables(result, context), context)
    
    # Remove any remaining block tags (blocks that weren't overridden)
    result = re.sub(r'\{%\s*block\s+\w+\s*%\}.*?\{%\s*endblock\s*%\}', '', result, flags=re.DOTALL)
    
    # Remove any remaining with tags (with blocks that weren't processed)
    result = re.sub(r'\{%\s*with\s+.*?\s*%\}(.*?)\{%\s*endwith\s*%\}', '', result, flags=re.DOTALL)
    
    # Remove any remaining for loops (loops not supported)
    result = re.sub(r'\{%\s*for\s+.*?\s*%\}(.*?)\{%\s*endfor\s*%\}', '', result, flags=re.DOTALL)
    
    return result

def render_template(name: str, context: dict) -> HTMLResponse:
    """Render a template with the given context using custom Jinja2-like parser."""
    template_str = _load_template(name)
    html = _apply_extends(template_str, context)
    return HTMLResponse(html)

# Initialize data manager and scoring engine
dm = DataManager()
se = ScoringEngine(dm)

# =============================================================================
# HTML PAGE ROUTES (Frontend Pages)
# =============================================================================
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page."""
    players = dm.get_players()
    teams = dm.get_teams()
    matches = list(dm.matches.values())
    completed = sum(1 for m in matches if m.get("completed", False))

    return render_template("index.html", {
        "request": request,
        "players_count": len(players),
        "teams_count": len(teams),
        "matches_count": len(matches),
        "completed_count": completed
    })

@app.get("/players", response_class=HTMLResponse)
async def players_page(request: Request):
    """Players management page."""
    return render_template("players.html", {"request": request})

@app.get("/teams", response_class=HTMLResponse)
async def teams_page(request: Request):
    """Teams management page."""
    return render_template("teams.html", {"request": request})

@app.get("/course-settings", response_class=HTMLResponse)
async def course_settings_page(request: Request):
    """Course settings page."""
    return render_template("course_settings.html", {"request": request})

@app.get("/season-setup", response_class=HTMLResponse)
async def season_setup_page(request: Request):
    """Season setup page."""
    return render_template("season_setup.html", {"request": request})

@app.get("/schedule", response_class=HTMLResponse)
async def schedule_page(request: Request):
    """Schedule page."""
    return render_template("schedule.html", {"request": request})

@app.get("/match-entry", response_class=HTMLResponse)
async def match_entry_page(request: Request):
    """Match entry page."""
    return render_template("match_entry.html", {"request": request})

@app.get("/standings", response_class=HTMLResponse)
async def standings_page(request: Request):
    """Standings page."""
    return render_template("standings.html", {"request": request})

# =============================================================================
# NEW UI ROUTES - Under /new prefix
# =============================================================================

@app.get("/new", response_class=HTMLResponse)
async def new_dashboard(request: Request):
    """New UI dashboard page."""
    players = dm.get_players()
    teams = dm.get_teams()
    matches = list(dm.matches.values())
    completed = sum(1 for m in matches if m.get("completed", False))
    
    return render_template("new/index.html", {
        "request": request,
        "players_count": len(players),
        "teams_count": len(teams),
        "matches_count": len(matches),
        "completed_count": completed
    })

@app.get("/new/players", response_class=HTMLResponse)
async def new_players_page(request: Request):
    """New UI players page."""
    return render_template("new/players.html", {"request": request})

@app.get("/new/teams", response_class=HTMLResponse)
async def new_teams_page(request: Request):
    """New UI teams page."""
    return render_template("new/teams.html", {"request": request})

@app.get("/new/match-entry", response_class=HTMLResponse)
async def new_match_entry_page(request: Request):
    """New UI match entry page."""
    return render_template("new/match_entry.html", {"request": request})

@app.get("/new/schedule", response_class=HTMLResponse)
async def new_schedule_page(request: Request):
    """New UI schedule page."""
    return render_template("new/schedule.html", {"request": request})

@app.get("/new/standings", response_class=HTMLResponse)
async def new_standings_page(request: Request):
    """New UI standings page."""
    return render_template("new/standings.html", {"request": request})

@app.get("/new/course-settings", response_class=HTMLResponse)
async def new_course_settings_page(request: Request):
    """New UI course settings page."""
    return render_template("new/course_settings.html", {"request": request})

@app.get("/new/season-setup", response_class=HTMLResponse)
async def new_season_setup_page(request: Request):
    """New UI season setup page."""
    return render_template("new/season_setup.html", {"request": request})

# =============================================================================
# API ENDPOINTS
# =============================================================================

# -----------------------------
# Players Endpoints
# -----------------------------
@app.get("/api/players", response_model=List[PlayerResponse])
async def get_players():
    """Get all players."""
    return dm.get_players()

@app.get("/api/players/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: str):
    """Get a single player by ID."""
    player = dm.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.post("/api/players", response_model=PlayerResponse)
async def create_player(player: PlayerCreate):
    """Create a new player."""
    player_id = dm.add_player(
        name=player.name,
        handicap=player.handicap,
        phone=player.phone or "",
        email=player.email or "",
        address=player.address or ""
    )
    return dm.get_player(player_id)

@app.put("/api/players/{player_id}", response_model=PlayerResponse)
async def update_player(player_id: str, player_update: PlayerUpdate):
    """Update a player."""
    if player_id not in dm.players:
        raise HTTPException(status_code=404, detail="Player not found")
    dm.update_player(
        player_id=player_id,
        name=player_update.name,
        handicap=player_update.handicap,
        phone=player_update.phone,
        email=player_update.email,
        address=player_update.address
    )
    return dm.get_player(player_id)

@app.delete("/api/players/{player_id}")
async def delete_player(player_id: str):
    """Delete a player."""
    if player_id not in dm.players:
        raise HTTPException(status_code=404, detail="Player not found")
    dm.delete_player(player_id)
    return {"message": "Player deleted successfully"}

# -----------------------------
# Teams Endpoints
# -----------------------------
@app.get("/api/teams", response_model=List[TeamResponse])
async def get_teams():
    """Get all teams."""
    return dm.get_teams()

@app.get("/api/teams/{team_id}", response_model=TeamResponse)
async def get_team(team_id: str):
    """Get a single team by ID."""
    team = dm.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@app.post("/api/teams", response_model=TeamResponse)
async def create_team(team: TeamCreate):
    """Create a new team."""
    team_id = dm.add_team(
        name=team.name,
        player1_id=team.player1_id,
        player2_id=team.player2_id,
        team_number=team.team_number
    )
    return dm.get_team(team_id)

@app.put("/api/teams/{team_id}", response_model=TeamResponse)
async def update_team(team_id: str, team_update: TeamUpdate):
    """Update a team."""
    if team_id not in dm.teams:
        raise HTTPException(status_code=404, detail="Team not found")
    dm.update_team(
        team_id=team_id,
        name=team_update.name,
        player1_id=team_update.player1_id,
        player2_id=team_update.player2_id,
        team_number=team_update.team_number
    )
    return dm.get_team(team_id)

@app.delete("/api/teams/{team_id}")
async def delete_team(team_id: str):
    """Delete a team."""
    if team_id not in dm.teams:
        raise HTTPException(status_code=404, detail="Team not found")
    dm.delete_team(team_id)
    return {"message": "Team deleted successfully"}

# -----------------------------
# Seasons Endpoints
# -----------------------------
@app.get("/api/seasons", response_model=List[SeasonResponse])
async def get_seasons():
    """Get all seasons."""
    return dm.get_seasons()

@app.get("/api/seasons/{season_id}", response_model=SeasonResponse)
async def get_season(season_id: str):
    """Get a single season by ID."""
    season = dm.get_season(season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    return season

@app.post("/api/seasons", response_model=SeasonResponse)
async def create_season(season: SeasonCreate):
    """Create a new season."""
    season_id = dm.create_season(
        name=season.name,
        course_id=season.course_id
    )
    return dm.get_season(season_id)

@app.post("/api/seasons/{season_id}/teams/{team_id}")
async def add_team_to_season(season_id: str, team_id: str):
    """Add a team to a season."""
    if season_id not in dm.seasons:
        raise HTTPException(status_code=404, detail="Season not found")
    if team_id not in dm.teams:
        raise HTTPException(status_code=404, detail="Team not found")
    dm.add_team_to_season(season_id, team_id)
    return {"message": "Team added to season successfully"}

@app.delete("/api/seasons/{season_id}")
async def delete_season(season_id: str):
    """Delete a season and all its associated matches and scores."""
    if season_id not in dm.seasons:
        raise HTTPException(status_code=404, detail="Season not found")
    dm.delete_season(season_id)
    return {"message": "Season deleted successfully"}

# -----------------------------
# Matches Endpoints
# -----------------------------
@app.get("/api/matches", response_model=List[MatchResponse])
async def get_matches(season_id: Optional[str] = None, week: Optional[int] = None):
    """Get all matches, with optional filters."""
    matches = list(dm.matches.values())

    if season_id:
        matches = [m for m in matches if m["season_id"] == season_id]

    if week:
        matches = [m for m in matches if m["week_number"] == week]

    return matches

@app.get("/api/matches/{match_id}", response_model=MatchResponse)
async def get_match(match_id: str):
    """Get a single match by ID."""
    match = dm.matches.get(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@app.post("/api/matches", response_model=MatchResponse)
async def create_match(match: MatchCreate):
    """Create a new match."""
    match_id = dm.add_match(
        season_id=match.season_id,
        week_number=match.week_number,
        team1_id=match.team1_id,
        team2_id=match.team2_id,
        date_played=match.date_played
    )
    return dm.matches[match_id]

@app.delete("/api/matches/{match_id}")
async def delete_match(match_id: str):
    """Delete a match and its scores."""
    if match_id not in dm.matches:
        raise HTTPException(status_code=404, detail="Match not found")
    dm.delete_match(match_id)
    return {"message": "Match deleted successfully"}

# -----------------------------
# Schedule Generation Endpoints
# -----------------------------
@app.post("/api/schedule/generate")
async def generate_schedule(season_id: str, team_ids: List[str]):
    """Generate a full round-robin schedule for a season."""
    if season_id not in dm.seasons:
        raise HTTPException(status_code=404, detail="Season not found")

    schedule = dm.generate_schedule(season_id, team_ids)

    # Create matches from schedule
    for item in schedule:
        dm.add_match(
            season_id=season_id,
            week_number=item["week"],
            team1_id=item["team1_id"],
            team2_id=item["team2_id"]
        )

    return {"message": f"Generated {len(schedule)} matches", "schedule": schedule}

@app.post("/api/schedule/generate-week")
async def generate_week_schedule(season_id: str, week_number: int):
    """Generate matches for a specific week."""
    if season_id not in dm.seasons:
        raise HTTPException(status_code=404, detail="Season not found")

    week_matchups = dm.generate_weekly_schedule(season_id, week_number)

    # Create matches for this week
    for t1, t2 in week_matchups:
        dm.add_match(
            season_id=season_id,
            week_number=week_number,
            team1_id=t1,
            team2_id=t2
        )

    return {"message": f"Generated {len(week_matchups)} matches for week {week_number}", "matchups": week_matchups}

# -----------------------------
# Score Submission Endpoint
# -----------------------------
@app.post("/api/scores/submit", response_model=ScoreResponse)
async def submit_scores(submission: ScoreSubmission):
    """Submit hole-by-hole scores for a match."""
    match_id = submission.match_id

    if match_id not in dm.matches:
        raise HTTPException(status_code=404, detail="Match not found")

    # Calculate scores using ScoringEngine
    results = se.calculate_match_scores(
        match_id,
        submission.team1_player1_scores,
        submission.team1_player2_scores,
        submission.team2_player1_scores,
        submission.team2_player2_scores
    )

    if not results:
        raise HTTPException(status_code=400, detail="Failed to calculate scores")

    # Save scores
    dm.save_match_scores(match_id, results)

    # Mark match as completed
    dm.complete_match(match_id)

    return results

# -----------------------------
# Scores Retrieval Endpoint
# -----------------------------
@app.get("/api/scores/{match_id}", response_model=Dict)
async def get_match_scores(match_id: str):
    """Get scores for a match, including hole-by-hole details."""
    match = dm.matches.get(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    scores = dm.get_match_scores(match_id)
    if not scores:
        return {"match_id": match_id, "has_scores": False}
    
    return scores

@app.get("/api/match-results/{match_id}", response_model=Dict)
async def get_match_results(match_id: str):
    """Get calculated match results (final scores, hole results, winner)."""
    try:
        match = dm.matches.get(match_id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        if not match.get("completed", False):
            raise HTTPException(status_code=400, detail="Match is not completed")
        
        # Get raw scores
        scores = dm.get_match_scores(match_id)
        if not scores:
            raise HTTPException(status_code=404, detail="No scores found for this match")
        
        # Get course settings for stroke index
        stroke_index = dm.course_settings.get("stroke_index", [])
        
        # Get teams and players
        team1 = dm.teams.get(match["team1_id"], {})
        team2 = dm.teams.get(match["team2_id"], {})
        
        # Get player details
        team1_player1 = dm.players.get(team1.get("player1_id"), {})
        team1_player2 = dm.players.get(team1.get("player2_id"), {})
        team2_player1 = dm.players.get(team2.get("player1_id"), {})
        team2_player2 = dm.players.get(team2.get("player2_id"), {})
        
        # Get handicaps for this week
        season_id = match.get("season_id")
        week_number = match.get("week_number")
        
        h1_p1 = dm.get_player_recent_handicap(team1.get("player1_id"), season_id, week_number)
        h1_p2 = dm.get_player_recent_handicap(team1.get("player2_id"), season_id, week_number)
        h2_p1 = dm.get_player_recent_handicap(team2.get("player1_id"), season_id, week_number)
        h2_p2 = dm.get_player_recent_handicap(team2.get("player2_id"), season_id, week_number)
        
        # Use scoring engine to calculate results
        # Extract raw scores from saved format: team1_scores.player1, etc.
        team1_scores = scores.get("team1_scores", {})
        team2_scores = scores.get("team2_scores", {})
        
        # Convert hole numbers from strings to integers
        def convert_hole_keys(scores_dict):
            """Convert hole numbers from strings to integers."""
            return {int(k): v for k, v in scores_dict.items()}
        
        team1_p1_scores = convert_hole_keys(team1_scores.get("player1", {}))
        team1_p2_scores = convert_hole_keys(team1_scores.get("player2", {}))
        team2_p1_scores = convert_hole_keys(team2_scores.get("player1", {}))
        team2_p2_scores = convert_hole_keys(team2_scores.get("player2", {}))
        
        results = se.calculate_match_scores(
            match_id,
            team1_p1_scores,
            team1_p2_scores,
            team2_p1_scores,
            team2_p2_scores
        )
        
        if not results:
            raise HTTPException(status_code=500, detail="Failed to calculate results")
        
        return results
    except Exception as e:
        raise e
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# -----------------------------
# Course Settings Endpoints
# -----------------------------
@app.get("/api/course-settings", response_model=CourseSettingsResponse)
async def get_course_settings():
    """Get course settings (stroke index, hole pars, etc.)."""
    return dm.course_settings

@app.put("/api/course-settings")
async def update_course_settings(settings: Dict):
    """Update course settings."""
    dm.course_settings.update(settings)
    dm.save_all()
    return {"message": "Course settings updated successfully"}

# -----------------------------
# Standings Endpoint
# -----------------------------
@app.get("/api/standings", response_model=StandingsResponse)
async def get_standings(season_id: Optional[str] = None):
    """Get team standings for a season."""
    if not season_id:
        # Get the most recent season
        seasons = dm.get_seasons()
        if not seasons:
            return StandingsResponse(season_id=None, standings=[])
        season_id = seasons[-1]["id"]

    season = dm.get_season(season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")

    team_ids = season.get("team_ids", [])
    standings = []

    for team_id in team_ids:
        team = dm.get_team(team_id)
        if not team:
            continue

        # Get all matches for this team in this season
        season_matches = dm.get_matches_for_season(season_id)
        team_matches = [m for m in season_matches if m["team1_id"] == team_id or m["team2_id"] == team_id]

        matches_played = 0
        matches_won = 0
        matches_lost = 0
        matches_tied = 0
        total_points = 0.0

        for match in team_matches:
            if not match.get("completed", False):
                continue

            match_scores = dm.get_match_scores(match["id"])
            if not match_scores:
                continue

            matches_played += 1

            # Determine if this team is team1 or team2
            is_team1 = match["team1_id"] == team_id
            team_final_points = match_scores.get("team1_final_points" if is_team1 else "team2_final_points", 0.0)
            opponent_final_points = match_scores.get("team2_final_points" if is_team1 else "team1_final_points", 0.0)

            total_points += team_final_points

            if team_final_points > opponent_final_points:
                matches_won += 1
            elif team_final_points < opponent_final_points:
                matches_lost += 1
            else:
                matches_tied += 1

        standings.append(TeamStandings(
            team_id=team_id,
            team_name=team["name"],
            total_points=round(total_points, 2),
            matches_played=matches_played,
            matches_won=matches_won,
            matches_lost=matches_lost,
            matches_tied=matches_tied
        ))

    # Sort by total points descending
    standings.sort(key=lambda x: x.total_points, reverse=True)

    return StandingsResponse(season_id=season_id, standings=standings)

# =============================================================================
# HEALTH CHECK
# =============================================================================
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "players_count": len(dm.players),
        "teams_count": len(dm.teams),
        "matches_count": len(dm.matches)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1234)
