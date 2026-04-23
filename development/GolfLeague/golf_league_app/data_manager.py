"""
Data Manager Module
Handles all data persistence and business logic for the golf league.
No UI dependencies - pure Python with JSON file I/O.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from itertools import combinations

# =============================================================================
# DATA FILE PATHS
# =============================================================================
DATA_DIR = os.environ.get("DATA_DIR", "data")
os.makedirs(DATA_DIR, exist_ok=True)

COURSE_SETTINGS_FILE = os.path.join(DATA_DIR, "course_settings.json")
PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")
SEASONS_FILE = os.path.join(DATA_DIR, "seasons.json")
MATCHES_FILE = os.path.join(DATA_DIR, "matches.json")
SCORES_FILE = os.path.join(DATA_DIR, "scores.json")
HANDICAP_HISTORY_FILE = os.path.join(DATA_DIR, "handicap_history.json")

# =============================================================================
# DEFAULT DATA
# =============================================================================
# Default stroke index order (placeholder - can be edited in Course Settings)
# Based on official Hickory Hills data:
# Front 9: Hole 1=5, 2=13, 3=1, 4=11, 5=15, 6=9, 7=17, 8=3, 9=7
# For 9-hole play, we use: 1=hardest, 9=easiest
DEFAULT_STROKE_INDEX = [3, 8, 1, 6, 9, 4, 7, 2, 5]  # Remapped for 9 holes

# Par for each hole at Hickory Hills (par 63 course, 9 holes = par 31)
HOLE_PARS = {
    1: 4,
    2: 3,
    3: 4,
    4: 3,
    5: 3,
    6: 4,
    7: 3,
    8: 4,
    9: 3
}

# Course information
DEFAULT_COURSE = {
    "name": "Hickory Hills Golf Course",
    "location": "Eau Claire, WI",
    "par_total": 63,
    "holes": 9
}

# =============================================================================
# UTILITY I/O FUNCTIONS
# =============================================================================
def load_json(filepath: str) -> Dict:
    """Load JSON data from filepath; return empty dict if file doesn't exist."""
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_json(filepath: str, data: Dict) -> bool:
    """Save data as JSON to filepath."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except IOError as e:
        print(f"Error saving {filepath}: {e}")
        return False

def generate_id(prefix: str = "") -> str:
    """Generate a unique ID."""
    import uuid
    return f"{prefix}{uuid.uuid4().hex[:8]}"

def generate_team_name(player1_name: str, player2_name: str) -> str:
    """Generate a team name from the last names of two players."""
    # Strip whitespace
    p1_name = player1_name.strip()
    p2_name = player2_name.strip()

    # Extract last names (take the last word of each name)
    p1_parts = p1_name.split()
    p2_parts = p2_name.split()

    p1_last = p1_parts[-1] if p1_parts else ""
    p2_last = p2_parts[-1] if p2_parts else ""

    # If both have last names, combine them
    if p1_last and p2_last:
        return f"{p1_last}-{p2_last}"
    # If only one has a name, use that name
    elif p1_last:
        return p1_last
    elif p2_last:
        return p2_last
    else:
        return "Team"

# =============================================================================
# DATA MANAGER
# =============================================================================
class DataManager:
    """Centralized data management for the golf league."""

    def __init__(self):
        self.course_settings = {}
        self.players = {}
        self.teams = {}
        self.seasons = {}
        self.matches = {}
        self.scores = {}
        self.handicap_history = {}
        self._load_all_data()

    def _load_all_data(self):
        """Load all data from JSON files."""
        self.course_settings = load_json(COURSE_SETTINGS_FILE)
        if "stroke_index" not in self.course_settings:
            self.course_settings["stroke_index"] = DEFAULT_STROKE_INDEX.copy()
            self.course_settings["hole_pars"] = HOLE_PARS.copy()
            self.course_settings["course_name"] = DEFAULT_COURSE["name"]
            self.course_settings["course_location"] = DEFAULT_COURSE["location"]
            save_json(COURSE_SETTINGS_FILE, self.course_settings)
        else:
            # Ensure hole_pars exists even if settings were saved before it was added
            if "hole_pars" not in self.course_settings:
                self.course_settings["hole_pars"] = HOLE_PARS.copy()
                save_json(COURSE_SETTINGS_FILE, self.course_settings)
            else:
                # Normalize hole_pars keys to integers (JSON may have string keys)
                hole_pars = {}
                for k, v in self.course_settings["hole_pars"].items():
                    try:
                        hole_num = int(k)
                        hole_pars[hole_num] = v
                    except (ValueError, TypeError):
                        # Keep as is if not convertible
                        hole_pars[k] = v
                self.course_settings["hole_pars"] = hole_pars

        self.players = load_json(PLAYERS_FILE)
        self.teams = load_json(TEAMS_FILE)
        self.seasons = load_json(SEASONS_FILE)
        self.matches = load_json(MATCHES_FILE)
        self.scores = load_json(SCORES_FILE)
        self.handicap_history = load_json(HANDICAP_HISTORY_FILE)

    def save_all(self):
        """Save all data to JSON files."""
        save_json(COURSE_SETTINGS_FILE, self.course_settings)
        save_json(PLAYERS_FILE, self.players)
        save_json(TEAMS_FILE, self.teams)
        save_json(SEASONS_FILE, self.seasons)
        save_json(MATCHES_FILE, self.matches)
        save_json(SCORES_FILE, self.scores)
        save_json(HANDICAP_HISTORY_FILE, self.handicap_history)

    # -------------------------------------------------------------------------
    # Player Management
    # -------------------------------------------------------------------------
    def add_player(self, name: str, handicap: float, phone: str = None, email: str = None, address: str = None) -> str:
        """Add a new player."""
        player_id = generate_id("P")
        self.players[player_id] = {
            "id": player_id,
            "name": name,
            "handicap": handicap,
            "phone": phone or "",
            "email": email or "",
            "address": address or "",
            "created_at": datetime.now().isoformat()
        }
        self.save_all()
        return player_id

    def update_player(self, player_id: str, name: str = None, handicap: float = None, phone: str = None, email: str = None, address: str = None):
        """Update player information."""
        if player_id in self.players:
            if name is not None:
                self.players[player_id]["name"] = name
            if handicap is not None:
                self.players[player_id]["handicap"] = handicap
            if phone is not None:
                self.players[player_id]["phone"] = phone
            if email is not None:
                self.players[player_id]["email"] = email
            if address is not None:
                self.players[player_id]["address"] = address
            self.players[player_id]["updated_at"] = datetime.now().isoformat()
            self.save_all()

    def delete_player(self, player_id: str):
        """Delete a player."""
        if player_id in self.players:
            del self.players[player_id]
            self.save_all()

    def get_players(self) -> List[Dict]:
        """Get all players as a list."""
        return list(self.players.values())

    def get_player(self, player_id: str) -> Optional[Dict]:
        """Get a single player by ID."""
        return self.players.get(player_id)

    # -------------------------------------------------------------------------
    # Team Management
    # -------------------------------------------------------------------------
    def add_team(self, name: str = None, player1_id: str = None, player2_id: str = None, team_number: int = None) -> str:
        """Add a new team. If name is not provided, auto-generate from player names."""
        team_id = generate_id("T")

        # Get player names for auto-generation if needed
        if not name:
            p1_name = self.players.get(player1_id, {}).get("name", "") if player1_id else ""
            p2_name = self.players.get(player2_id, {}).get("name", "") if player2_id else ""
            name = generate_team_name(p1_name, p2_name)

        self.teams[team_id] = {
            "id": team_id,
            "name": name,
            "player1_id": player1_id,
            "player2_id": player2_id,
            "team_number": team_number,
            "created_at": datetime.now().isoformat()
        }
        self.save_all()
        return team_id

    def update_team(self, team_id: str, name: str = None, player1_id: str = None, player2_id: str = None, team_number: int = None):
        """Update team information."""
        if team_id in self.teams:
            if name is not None:
                self.teams[team_id]["name"] = name
            if player1_id is not None:
                self.teams[team_id]["player1_id"] = player1_id
            if player2_id is not None:
                self.teams[team_id]["player2_id"] = player2_id
            if team_number is not None:
                self.teams[team_id]["team_number"] = team_number
            self.teams[team_id]["updated_at"] = datetime.now().isoformat()
            self.save_all()

    def delete_team(self, team_id: str):
        """Delete a team."""
        if team_id in self.teams:
            del self.teams[team_id]
            self.save_all()

    def get_teams(self) -> List[Dict]:
        """Get all teams as a list."""
        return list(self.teams.values())

    def get_team(self, team_id: str) -> Optional[Dict]:
        """Get a single team by ID."""
        return self.teams.get(team_id)

    def get_team_handicap(self, team_id: str) -> float:
        """Get team handicap (average of both players' handicaps)."""
        team = self.teams.get(team_id)
        if not team:
            return 0.0
        p1 = self.players.get(team["player1_id"], {})
        p2 = self.players.get(team["player2_id"], {})
        h1 = p1.get("handicap", 0)
        h2 = p2.get("handicap", 0)
        return (h1 + h2) / 2

    # -------------------------------------------------------------------------
    # Season Management
    # -------------------------------------------------------------------------
    def create_season(self, name: str, course_id: str = "default") -> str:
        """Create a new season."""
        season_id = generate_id("S")
        self.seasons[season_id] = {
            "id": season_id,
            "name": name,
            "course_id": course_id,
            "team_ids": [],
            "created_at": datetime.now().isoformat()
        }
        self.save_all()
        return season_id

    def add_team_to_season(self, season_id: str, team_id: str):
        """Add a team to a season."""
        if season_id in self.seasons:
            if team_id not in self.seasons[season_id]["team_ids"]:
                self.seasons[season_id]["team_ids"].append(team_id)
            self.save_all()

    def get_season(self, season_id: str) -> Optional[Dict]:
        """Get a season by ID."""
        return self.seasons.get(season_id)

    def get_seasons(self) -> List[Dict]:
        """Get all seasons."""
        return list(self.seasons.values())

    def delete_season(self, season_id: str):
        """Delete a season and all its associated matches and scores."""
        if season_id in self.seasons:
            del self.seasons[season_id]
            # Also delete all matches for this season
            matches_to_delete = [m_id for m_id, m in self.matches.items() if m["season_id"] == season_id]
            for match_id in matches_to_delete:
                if match_id in self.matches:
                    del self.matches[match_id]
                if match_id in self.scores:
                    del self.scores[match_id]
            self.save_all()

    # -------------------------------------------------------------------------
    # Match Management
    # -------------------------------------------------------------------------
    def add_match(self, season_id: str, week_number: int, team1_id: str, team2_id: str, date_played: str = None):
        """Add a match to the schedule."""
        match_id = generate_id("M")
        self.matches[match_id] = {
            "id": match_id,
            "season_id": season_id,
            "week_number": week_number,
            "team1_id": team1_id,
            "team2_id": team2_id,
            "date_played": date_played or datetime.now().strftime("%Y-%m-%d"),
            "completed": False
        }
        self.save_all()
        return match_id

    def get_matches_for_season(self, season_id: str) -> List[Dict]:
        """Get all matches for a season."""
        return [m for m in self.matches.values() if m["season_id"] == season_id]

    def get_matches_for_week(self, season_id: str, week_number: int) -> List[Dict]:
        """Get all matches for a specific week."""
        return [m for m in self.matches.values()
                if m["season_id"] == season_id and m["week_number"] == week_number]

    def complete_match(self, match_id: str):
        """Mark a match as completed."""
        if match_id in self.matches:
            self.matches[match_id]["completed"] = True
            self.save_all()

    def delete_match(self, match_id: str):
        """Delete a match and its associated scores."""
        if match_id in self.matches:
            del self.matches[match_id]
        if match_id in self.scores:
            del self.scores[match_id]
        self.save_all()

    # -------------------------------------------------------------------------
    # Score Management
    # -------------------------------------------------------------------------
    def save_match_scores(self, match_id: str, results: Dict):
        """Save scores for a match.

        Args:
            match_id: The match ID
            results: Dict from calculate_match_scores containing all scores and points
        """
        self.scores[match_id] = {
            "match_id": match_id,
            "team1_scores": results.get("team1_scores", {}),
            "team2_scores": results.get("team2_scores", {}),
            "team1_hole_points": results.get("team1_hole_points", 0.0),
            "team2_hole_points": results.get("team2_hole_points", 0.0),
            "team1_bonus": results.get("team1_bonus", 0.0),
            "team2_bonus": results.get("team2_bonus", 0.0),
            "team1_final_points": results.get("team1_final_points", 0.0),
            "team2_final_points": results.get("team2_final_points", 0.0),
            "team1_total": results.get("team1_total", 0),
            "team2_total": results.get("team2_total", 0),
            "saved_at": datetime.now().isoformat()
        }
        self.save_all()

    def get_match_scores(self, match_id: str) -> Optional[Dict]:
        """Get scores for a match."""
        return self.scores.get(match_id)

    # -------------------------------------------------------------------------
    # Handicap Management
    # -------------------------------------------------------------------------
    def record_handicap(self, player_id: str, season_id: str, week_number: int, handicap_value: float):
        """Record a handicap for a player in a specific week."""
        key = f"{player_id}_{season_id}_{week_number}"
        self.handicap_history[key] = {
            "player_id": player_id,
            "season_id": season_id,
            "week_number": week_number,
            "handicap_value": handicap_value,
            "recorded_at": datetime.now().isoformat()
        }
        self.save_all()

    def get_player_recent_handicap(self, player_id: str, season_id: str, current_week: int) -> float:
        """Get rolling 3-week average handicap for a player."""
        handicaps = []
        for week in range(max(1, current_week - 2), current_week + 1):
            key = f"{player_id}_{season_id}_{week}"
            if key in self.handicap_history:
                handicaps.append(self.handicap_history[key]["handicap_value"])

        if handicaps:
            return sum(handicaps) / len(handicaps)
        return self.players.get(player_id, {}).get("handicap", 0.0)

    # -------------------------------------------------------------------------
    # Schedule Generation
    # -------------------------------------------------------------------------
    def generate_schedule(self, season_id: str, team_ids: List[str]) -> List[Dict]:
        """
        Generate a complete round-robin schedule.
        Each team plays every other team exactly once.
        Uses standard round-robin algorithm with bye handling for odd number of teams.
        """
        if len(team_ids) < 2:
            return []
        
        teams = list(team_ids)
        n = len(teams)
        
        # If odd number of teams, add a dummy team (bye)
        has_bye = n % 2 == 1
        if has_bye:
            teams.append(None)  # Bye team
            n += 1
        
        # Round-robin schedule generation using circle method
        schedule = []
        weeks = n - 1
        
        for week in range(1, weeks + 1):
            week_matchups = []
            
            for i in range(n // 2):
                team1 = teams[i]
                team2 = teams[n - 1 - i]
                
                # Skip if either team is None (bye)
                if team1 is not None and team2 is not None:
                    week_matchups.append((team1, team2))
            
            # Rotate teams (except first team stays fixed)
            teams = [teams[0]] + [teams[-1]] + teams[1:-1]
            
            # Add matchups to schedule
            for t1, t2 in week_matchups:
                schedule.append({
                    "week": week,
                    "team1_id": t1,
                    "team2_id": t2
                })
        
        return schedule

    def generate_weekly_schedule(self, season_id: str, week_number: int) -> List[Dict]:
        """
        Generate matches for a specific week based on current handicaps.
        Only generates matches that haven't been scheduled yet.
        Teams are paired based on similar current handicaps (rolling 3-week average).

        Args:
            season_id: The season ID
            week_number: The week number to generate matches for

        Returns:
            List of generated match dicts
        """
        # Get all teams in the season
        season = self.seasons.get(season_id)
        if not season:
            return []

        team_ids = season.get("team_ids", [])
        if len(team_ids) < 2:
            return []

        # Get all existing matches for this season to find which matchups have already been scheduled
        # We consider ALL matches (scheduled or completed) to avoid duplicate matchups in the season
        existing_matches = self.get_matches_for_season(season_id)
        scheduled_matchups = set()
        for match in existing_matches:
            # Consider all matches as scheduled, regardless of completion status
            scheduled_matchups.add((match["team1_id"], match["team2_id"]))
            scheduled_matchups.add((match["team2_id"], match["team1_id"]))

        # Get matches already scheduled for this week
        week_matches = self.get_matches_for_week(season_id, week_number)
        teams_scheduled_this_week = set()
        for match in week_matches:
            teams_scheduled_this_week.add(match["team1_id"])
            teams_scheduled_this_week.add(match["team2_id"])

        # Get all possible matchups that haven't been scheduled yet
        available_matchups = []
        for t1, t2 in combinations(team_ids, 2):
            if (t1, t2) not in scheduled_matchups:
                available_matchups.append((t1, t2))

        if not available_matchups:
            return []  # All teams have already played each other

        # Calculate current team handicaps using rolling average for this week
        team_handicaps = {}
        for tid in team_ids:
            # Get team handicap from current player handicaps
            team_handicaps[tid] = self.get_team_handicap(tid)

        # Sort available matchups by handicap difference (closest first)
        def handicap_diff(matchup):
            return abs(team_handicaps[matchup[0]] - team_handicaps[matchup[1]])

        available_matchups.sort(key=handicap_diff)

        # Greedy algorithm to assign matchups for this week
        # Prioritize teams that haven't played this week yet
        week_matchups = []
        teams_playing_this_week = teams_scheduled_this_week.copy()

        for matchup in available_matchups:
            t1, t2 = matchup
            if t1 not in teams_playing_this_week and t2 not in teams_playing_this_week:
                week_matchups.append((t1, t2))
                teams_playing_this_week.add(t1)
                teams_playing_this_week.add(t2)

        return week_matchups
