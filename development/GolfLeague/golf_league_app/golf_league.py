"""
Golf League Manager - Desktop Application
A complete golf league management system for 2026 Season at Hickory Hills.

Features:
- Player & team management
- Course settings (stroke index, par)
- Season setup with schedule generation
- Match entry with net score calculation
- Standings view
- Rolling 3-week handicap average

Author: Generated for Golf League
License: MIT
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import random
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple, Any
from itertools import combinations

# =============================================================================
# TOOLTIP CLASS
# =============================================================================
class ToolTip:
    """Create a tooltip for a given widget."""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """Display the tooltip."""
        if self.tooltip or not self.text:
            return
        
        # Calculate position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create label with tooltip text
        label = ttk.Label(self.tooltip, text=self.text,
                         background="#FFFFE0", foreground="#333333",
                         relief="solid", borderwidth=1,
                         font=("Segoe UI", 9), padding=(5, 3))
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide the tooltip."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

# =============================================================================
# DATA FILE PATHS
# =============================================================================
DATA_DIR = "data"
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
# DATA MODELS & MANAGERS
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
    def generate_schedule(self, season_id: str, team_ids: List[str], schedule_type: str = "round_robin") -> List[Dict]:
        """
        Generate a complete schedule for the season.
        
        Args:
            season_id: The season ID
            team_ids: List of team IDs
            schedule_type: "round_robin" for everyone plays everyone once,
                          "handicap_based" for balanced handicap matchups
            
        Returns:
            List of schedule match dicts with week, team1_id, team2_id
        """
        if len(team_ids) < 2:
            return []
        
        if schedule_type == "round_robin":
            return self._generate_round_robin_schedule(team_ids)
        elif schedule_type == "handicap_based":
            return self._generate_handicap_based_schedule(team_ids)
        else:
            return self._generate_round_robin_schedule(team_ids)
    
    def _generate_round_robin_schedule(self, team_ids: List[str]) -> List[Dict]:
        """
        Generate a complete round-robin schedule.
        Each team plays every other team exactly once.
        Teams are sorted by handicap to create balanced matchups (higher vs higher, lower vs lower).
        Uses standard round-robin algorithm with bye handling.
        """
        # Get team handicaps and sort teams by handicap (descending)
        team_handicaps = {tid: self.get_team_handicap(tid) for tid in team_ids}
        # Sort teams by handicap, highest first, to ensure similar handicaps play each other
        sorted_teams = sorted(team_ids, key=lambda tid: team_handicaps[tid], reverse=True)
        
        teams = list(sorted_teams)
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
    
    def _generate_handicap_based_schedule(self, team_ids: List[str]) -> List[Dict]:
        """
        Generate schedule based on team handicaps.
        Teams are grouped into tiers (top, middle, bottom) and primarily play within their tier.
        This ensures higher handicap teams play higher handicap teams,
        and lower handicap teams play lower handicap teams.
        
        Returns a balanced schedule over multiple weeks.
        """
        # Calculate team handicaps
        team_handicaps = {tid: self.get_team_handicap(tid) for tid in team_ids}
        
        # Sort teams by handicap (descending - higher handicap first)
        sorted_teams = sorted(team_ids, key=lambda tid: team_handicaps[tid], reverse=True)
        
        # Divide into tiers (top 1/3, middle 1/3, bottom 1/3)
        n = len(sorted_teams)
        tier_size = max(2, n // 3)  # At least 2 teams per tier
        
        tiers = []
        for i in range(0, n, tier_size):
            tier = sorted_teams[i:i + tier_size]
            if len(tier) >= 2:
                tiers.append(tier)
        
        # Generate matchups prioritizing intra-tier play
        schedule = []
        week_number = 1
        all_matchups = set()
        
        # First, schedule all intra-tier matchups
        for tier_idx, tier in enumerate(tiers):
            tier_matchups = list(combinations(tier, 2))
            # Sort by handicap difference within tier (closest first)
            tier_matchups.sort(key=lambda m: abs(team_handicaps[m[0]] - team_handicaps[m[1]]))
            
            # Distribute tier matchups across weeks
            week = 1
            for t1, t2 in tier_matchups:
                schedule.append({
                    "week": week,
                    "team1_id": t1,
                    "team2_id": t2
                })
                all_matchups.add((t1, t2))
                week += 1
        
        # Then, schedule inter-tier matchups if needed (to ensure everyone plays everyone)
        # This is a simplified approach - could be enhanced
        remaining_matchups = []
        for t1, t2 in combinations(team_ids, 2):
            if (t1, t2) not in all_matchups and (t2, t1) not in all_matchups:
                remaining_matchups.append((t1, t2))
        
        # Sort remaining by handicap difference (closest first)
        remaining_matchups.sort(key=lambda m: abs(team_handicaps[m[0]] - team_handicaps[m[1]]))
        
        # Distribute remaining matchups
        week = 1
        for t1, t2 in remaining_matchups:
            schedule.append({
                "week": week,
                "team1_id": t1,
                "team2_id": t2
            })
            week += 1
            if week > len(tiers) * tier_size:
                week = 1
        
        # Sort schedule by week
        schedule.sort(key=lambda x: x["week"])
        
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

# =============================================================================
# SCORING UTILITIES
# =============================================================================
class ScoringEngine:
    """Handles all scoring calculations for the golf league."""
    
    def __init__(self, data_manager: DataManager):
        self.dm = data_manager
    
    def calculate_match_scores(self, match_id: str,
                               team1_p1_gross: Dict[int, int], team1_p2_gross: Dict[int, int],
                               team2_p1_gross: Dict[int, int], team2_p2_gross: Dict[int, int]) -> Dict:
        """
        Calculate all scores for a match using match-play scoring.
        
        Changes:
        - Handicap strokes: difference between players in each matchup, allocated to hardest holes.
        - Hole points: winner takes all (no half points for ties).
        - Team bonus: based on combined NET scores (not gross), winner takes all (no half points).
        """
        stroke_index = self.dm.course_settings.get("stroke_index", DEFAULT_STROKE_INDEX)
        
        # Get match and team info
        match = self.dm.matches.get(match_id, {})
        season_id = match.get("season_id", "")
        week_number = match.get("week_number", 1)
        
        team1 = self.dm.get_team(match.get("team1_id", ""))
        team2 = self.dm.get_team(match.get("team2_id", ""))
        
        if not team1 or not team2:
            return {}
        
        # Get handicaps (rolling average)
        h1_p1 = self.dm.get_player_recent_handicap(team1["player1_id"], season_id, week_number)
        h1_p2 = self.dm.get_player_recent_handicap(team1["player2_id"], season_id, week_number)
        h2_p1 = self.dm.get_player_recent_handicap(team2["player1_id"], season_id, week_number)
        h2_p2 = self.dm.get_player_recent_handicap(team2["player2_id"], season_id, week_number)
        
        hole_results = []
        team1_hole_points = 0.0
        team2_hole_points = 0.0
        team1_net_total = 0
        team2_net_total = 0
        
        # Get hole points setting
        hole_points_setting = self.dm.course_settings.get("hole_points", 1.0)
        try:
            hole_point_value = float(hole_points_setting)
        except (ValueError, TypeError):
            hole_point_value = 1.0
        
        for hole in range(1, 10):
            si = stroke_index[hole - 1] if hole <= len(stroke_index) else hole
            
            # Get gross scores for this hole
            t1_p1_gross = team1_p1_gross.get(hole, 0)
            t1_p2_gross = team1_p2_gross.get(hole, 0)
            t2_p1_gross = team2_p1_gross.get(hole, 0)
            t2_p2_gross = team2_p2_gross.get(hole, 0)
            
            # --- Matchup 1: Team1 Player1 vs Team2 Player1 ---
            # Determine stroke allocation based on handicap difference
            if h1_p1 > h2_p1:
                diff = int(h1_p1) - int(h2_p1)
                # Team1 player gets strokes (higher handicap)
                t1_p1_net = t1_p1_gross - (1 if si <= diff else 0)
                t2_p1_net = t2_p1_gross
            elif h2_p1 > h1_p1:
                diff = int(h2_p1) - int(h1_p1)
                t2_p1_net = t2_p1_gross - (1 if si <= diff else 0)
                t1_p1_net = t1_p1_gross
            else:
                t1_p1_net = t1_p1_gross
                t2_p1_net = t2_p1_gross
            
            # --- Matchup 2: Team1 Player2 vs Team2 Player2 ---
            if h1_p2 > h2_p2:
                diff = int(h1_p2) - int(h2_p2)
                t1_p2_net = t1_p2_gross - (1 if si <= diff else 0)
                t2_p2_net = t2_p2_gross
            elif h2_p2 > h1_p2:
                diff = int(h2_p2) - int(h1_p2)
                t2_p2_net = t2_p2_gross - (1 if si <= diff else 0)
                t1_p2_net = t1_p2_gross
            else:
                t1_p2_net = t1_p2_gross
                t2_p2_net = t2_p2_gross
            
            # Accumulate net totals for team bonus
            team1_net_total += t1_p1_net + t1_p2_net
            team2_net_total += t2_p1_net + t2_p2_net
            
            # Calculate hole points for each matchup (with ties - each gets half point)
            p1_points = 0.0
            p2_points = 0.0
            
            # Matchup 1
            if t1_p1_net < t2_p1_net:
                p1_points += hole_point_value
            elif t2_p1_net < t1_p1_net:
                p2_points += hole_point_value
            else:  # tie
                p1_points += hole_point_value / 2
                p2_points += hole_point_value / 2
            
            # Matchup 2
            if t1_p2_net < t2_p2_net:
                p1_points += hole_point_value
            elif t2_p2_net < t1_p2_net:
                p2_points += hole_point_value
            else:  # tie
                p1_points += hole_point_value / 2
                p2_points += hole_point_value / 2
            
            team1_hole_points += p1_points
            team2_hole_points += p2_points
            
            hole_results.append({
                "hole": hole,
                "stroke_index": si,
                "team1_p1_net": t1_p1_net,
                "team1_p2_net": t1_p2_net,
                "team2_p1_net": t2_p1_net,
                "team2_p2_net": t2_p2_net,
                "team1_p1_points": hole_point_value if t1_p1_net < t2_p1_net else (hole_point_value / 2 if t1_p1_net == t2_p1_net else 0.0),
                "team1_p2_points": hole_point_value if t1_p2_net < t2_p2_net else (hole_point_value / 2 if t1_p2_net == t2_p2_net else 0.0),
                "team2_p1_points": hole_point_value if t2_p1_net < t1_p1_net else (hole_point_value / 2 if t2_p1_net == t1_p1_net else 0.0),
                "team2_p2_points": hole_point_value if t2_p2_net < t1_p2_net else (hole_point_value / 2 if t2_p2_net == t1_p2_net else 0.0),
                "team1_points": p1_points,
                "team2_points": p2_points
            })
        
        # Team bonus based on combined NET scores (not gross)
        bonus_setting = self.dm.course_settings.get("team_bonus_points", 5.0)
        try:
            bonus_points = float(bonus_setting)
        except (ValueError, TypeError):
            bonus_points = 5.0
        
        if team1_net_total < team2_net_total:
            t1_bonus = bonus_points
            t2_bonus = 0.0
        elif team2_net_total < team1_net_total:
            t1_bonus = 0.0
            t2_bonus = bonus_points
        else:
            t1_bonus = bonus_points / 2
            t2_bonus = bonus_points / 2
        
        team1_final = team1_hole_points + t1_bonus
        team2_final = team2_hole_points + t2_bonus
        
        return {
            "hole_results": hole_results,
            "team1_scores": {"player1": team1_p1_gross, "player2": team1_p2_gross},
            "team2_scores": {"player1": team2_p1_gross, "player2": team2_p2_gross},
            "team1_hole_points": team1_hole_points,
            "team2_hole_points": team2_hole_points,
            "team1_bonus": t1_bonus,
            "team2_bonus": t2_bonus,
            "team1_total": team1_net_total,
            "team2_total": team2_net_total,
            "team1_final_points": team1_final,
            "team2_final_points": team2_final,
            "winner": "team1" if team1_final > team2_final else ("team2" if team2_final > team1_final else "tie")
        }

# =============================================================================
# MAIN APPLICATION
# =============================================================================
class GolfLeagueApp:
    """Main application class for the Golf League Manager."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Golf League Manager - 2026 Season")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize data manager and scoring engine
        self.dm = DataManager()
        self.scoring = ScoringEngine(self.dm)
        
        # Initialize sorting state
        self._players_sort_column = None
        self._players_sort_reverse = False
        self._teams_sort_column = None
        self._teams_sort_reverse = False
        
        # Configure modern styling
        self._setup_styles()
        
        # Create UI
        self._create_menu()
        self._create_main_ui()
        self._create_status_bar()
        
        # Load initial data into UI
        self._refresh_all_views()
        
        # Show startup message
        self._set_status("Ready", "info")
    
    def _setup_styles(self):
        """Configure modern ttk styles with golf-themed palette."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Professional golf-themed color palette
        primary_green = "#2E7D32"      # Main brand color
        dark_green = "#1B5E20"         # Darker green for hover/active
        accent_gold = "#FFD700"        # Gold accent for highlights
        light_green_bg = "#E8F5E9"     # Light green background
        card_bg = "#FFFFFF"            # White card background
        text_primary = "#212121"       # Primary text
        text_secondary = "#757575"     # Secondary text
        border_color = "#BDBDBD"       # Border color
        hover_bg = "#F5F5F5"           # Hover background
        
        # Frame styles
        style.configure("TFrame", background=light_green_bg)
        style.configure("Card.TFrame", background=card_bg, relief="raised", borderwidth=1)
        
        # Label styles
        style.configure("TLabel", background=light_green_bg, foreground=text_primary, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground=primary_green)
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground=primary_green)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 12, "bold"), foreground=text_secondary)
        style.configure("Card.TLabel", background=card_bg, foreground=text_primary, font=("Segoe UI", 10))
        style.configure("Status.TLabel", background=card_bg, font=("Segoe UI", 9))
        
        # Button styles
        style.configure("TButton", font=("Segoe UI", 10), padding=8)
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=10,
                       background=primary_green, foreground="white")
        style.map("Accent.TButton",
                  background=[('active', dark_green), ('pressed', dark_green)],
                  foreground=[('active', 'white'), ('pressed', 'white')])
        
        # Checkbutton and Combobox
        style.configure("TCheckbutton", background=light_green_bg, font=("Segoe UI", 10))
        style.configure("TCombobox", font=("Segoe UI", 10), fieldbackground="white")
        
        # Treeview with improved styling
        style.configure("Treeview",
                      font=("Segoe UI", 10),
                      rowheight=30,
                      background=card_bg,
                      fieldbackground=card_bg)
        style.configure("Treeview.Heading",
                      font=("Segoe UI", 10, "bold"),
                      background=primary_green,
                      foreground="white")
        style.map("Treeview",
                 background=[('selected', primary_green)],
                 foreground=[('selected', 'white')])
        
        # Notebook tabs
        style.configure("TNotebook", background=light_green_bg)
        style.configure("TNotebook.Tab",
                      font=("Segoe UI", 11, "bold"),
                      padding=[20, 10],
                      background=hover_bg,
                      foreground=text_primary)
        style.map("TNotebook.Tab",
                 background=[('selected', card_bg)],
                 foreground=[('selected', primary_green)])
        
        # Entry fields
        style.configure("TEntry", fieldbackground="white", bordercolor=border_color)
        
        # Custom style for stroke hole entries
        style.configure("StrokeEntry.TEntry",
                      fieldbackground="#FFF3E0",
                      bordercolor=accent_gold,
                      darkcolor=accent_gold,
                      lightcolor=accent_gold)
        
        # Status badge styles
        style.configure("Success.TLabel", background="#E8F5E9", foreground="#2E7D32", font=("Segoe UI", 9, "bold"))
        style.configure("Warning.TLabel", background="#FFF3E0", foreground="#F57C00", font=("Segoe UI", 9, "bold"))
        style.configure("Danger.TLabel", background="#FFEBEE", foreground="#C62828", font=("Segoe UI", 9, "bold"))
        style.configure("Info.TLabel", background="#E3F2FD", foreground="#1565C0", font=("Segoe UI", 9, "bold"))
    
    def _create_menu(self):
        """Create application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save All Data", command=self._save_all_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_ui(self):
        """Create the main tabbed interface."""
        # Main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create tabs
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.course_frame = ttk.Frame(self.notebook)
        self.players_frame = ttk.Frame(self.notebook)
        self.teams_frame = ttk.Frame(self.notebook)
        self.season_frame = ttk.Frame(self.notebook)
        self.schedule_frame = ttk.Frame(self.notebook)
        self.match_entry_frame = ttk.Frame(self.notebook)
        self.standings_frame = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.course_frame, text="Course Settings")
        self.notebook.add(self.players_frame, text="Players")
        self.notebook.add(self.teams_frame, text="Teams")
        self.notebook.add(self.season_frame, text="Season Setup")
        self.notebook.add(self.schedule_frame, text="Schedule")
        self.notebook.add(self.match_entry_frame, text="Match Entry")
        self.notebook.add(self.standings_frame, text="Standings")
        
        # Build each tab
        self._build_dashboard()
        self._build_course_settings()
        self._build_players_tab()
        self._build_teams_tab()
        self._build_season_setup()
        self._build_schedule_tab()
        self._build_match_entry()
        self._build_standings()
    
    def _create_status_bar(self):
        """Create status bar at the bottom of the window."""
        self.status_frame = ttk.Frame(self.root, relief="sunken", borderwidth=1)
        self.status_frame.pack(side="bottom", fill="x")
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", padding=(10, 5))
        self.status_label.pack(side="left")
        
        # Add a separator
        ttk.Separator(self.status_frame, orient="vertical").pack(side="left", fill="y", padx=10)
        
        # Add timestamp
        self.timestamp_label = ttk.Label(self.status_frame, text="", padding=(10, 5))
        self.timestamp_label.pack(side="right")
        
        # Update timestamp periodically
        self._update_timestamp()
    
    def _update_timestamp(self):
        """Update the timestamp label with current time."""
        from datetime import datetime
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.config(text=timestamp)
        # Update every second
        self.root.after(1000, self._update_timestamp)
    
    def _set_status(self, message: str, level: str = "info"):
        """Set status bar message with color coding."""
        self.status_label.config(text=message)
        # You could add color coding based on level if desired
        # For now, just update the text
    
    # -------------------------------------------------------------------------
    # Dashboard Tab
    # -------------------------------------------------------------------------
    def _build_dashboard(self):
        """Build the dashboard tab."""
        frame = self.dashboard_frame
        
        # Title with golf icon
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill="x", padx=20, pady=20)
        
        title = ttk.Label(title_frame, text="🏌️ Golf League Manager", style="Title.TLabel")
        title.pack(side="left")
        
        # Season info in a styled card
        season_card = ttk.Frame(frame, style="Card.TFrame", padding=15)
        season_card.pack(fill="x", padx=20, pady=5)
        
        season_info = ttk.Label(season_card,
                               text="2026 Season - Hickory Hills Golf Course",
                               style="Subtitle.TLabel")
        season_info.pack()
        
        # Quick stats in card layout
        stats_container = ttk.Frame(frame)
        stats_container.pack(fill="x", padx=20, pady=20)
        
        # Create stat cards with icons
        card_configs = [
            ("👥", "Players", 0),
            ("🏌️", "Teams", 1),
            ("📅", "Matches", 2),
            ("✅", "Completed", 3)
        ]
        
        for icon, label_text, col in card_configs:
            card = ttk.Frame(stats_container, style="Card.TFrame", padding=15)
            card.grid(row=0, column=col, padx=10, sticky="nsew")
            
            # Icon
            icon_label = ttk.Label(card, text=icon, font=("Segoe UI", 24))
            icon_label.pack()
            
            # Label
            ttk.Label(card, text=label_text, style="Subtitle.TLabel").pack(pady=(5, 0))
            
            # Value (will be updated by _update_dashboard_stats)
            stat_label = ttk.Label(card, text="0", style="Header.TLabel")
            stat_label.pack(pady=(5, 0))
            
            # Store reference with consistent naming
            setattr(self, f"stats_{label_text.lower()}", stat_label)
        
        # Configure grid weights
        for i in range(4):
            stats_container.grid_columnconfigure(i, weight=1)
        
        # Quick actions section
        actions_card = ttk.Frame(frame, style="Card.TFrame", padding=15)
        actions_card.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(actions_card, text="Quick Actions", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
        
        actions_inner = ttk.Frame(actions_card)
        actions_inner.pack(fill="x")
        
        actions = [
            ("➕ Add Player", lambda: self.notebook.select(2), "Add a new player to the league"),
            ("➕ Add Team", lambda: self.notebook.select(3), "Create a new team from two players"),
            ("⚙️ Setup Season", lambda: self.notebook.select(4), "Configure season and select teams"),
            ("📝 Enter Scores", lambda: self.notebook.select(6), "Enter match scores for completed matches"),
            ("📊 View Standings", lambda: self.notebook.select(7), "View current team rankings"),
            ("📅 View Schedule", lambda: self.notebook.select(5), "View and manage the match schedule")
        ]
        
        for i, (text, command, tooltip_text) in enumerate(actions):
            if i % 3 == 0:
                row_frame = ttk.Frame(actions_inner)
                row_frame.pack(fill="x", pady=5)
            
            btn = ttk.Button(row_frame, text=text, command=command, width=20)
            btn.pack(side="left", padx=5)
            ToolTip(btn, tooltip_text)
    
    def _update_dashboard_stats(self):
        """Update dashboard statistics."""
        players = self.dm.get_players()
        teams = self.dm.get_teams()
        matches = list(self.dm.matches.values())
        completed = sum(1 for m in matches if m.get("completed", False))
        
        # Update stat labels using consistent naming
        if hasattr(self, 'stats_players'):
            self.stats_players.config(text=f"Players: {len(players)}")
        if hasattr(self, 'stats_teams'):
            self.stats_teams.config(text=f"Teams: {len(teams)}")
        if hasattr(self, 'stats_matches'):
            self.stats_matches.config(text=f"Matches: {len(matches)}")
        if hasattr(self, 'stats_completed'):
            self.stats_completed.config(text=f"Completed: {completed}")
    
    def _center_dialog(self, dialog):
        """Center a dialog window on the root window."""
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    # -------------------------------------------------------------------------
    # Course Settings Tab
    # -------------------------------------------------------------------------
    def _build_course_settings(self):
        """Build the course settings tab."""
        frame = self.course_frame
        
        # Title
        ttk.Label(frame, text="Course Settings", style="Title.TLabel").pack(pady=10)
        
        # Edit mode state variables
        self.si_edit_mode = False
        self.par_edit_mode = False
        
        # Course info
        info_frame = ttk.LabelFrame(frame, text="Course Information", padding=10)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(info_frame, text="Course Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.course_name_var = tk.StringVar(value=self.dm.course_settings.get("course_name", "Hickory Hills"))
        ttk.Entry(info_frame, textvariable=self.course_name_var, width=40).grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(info_frame, text="Location:").grid(row=1, column=0, sticky="w", pady=5)
        self.course_location_var = tk.StringVar(value=self.dm.course_settings.get("course_location", "Eau Claire, WI"))
        ttk.Entry(info_frame, textvariable=self.course_location_var, width=40).grid(row=1, column=1, pady=5, padx=5)
        
        # Stroke index editor
        si_frame = ttk.LabelFrame(frame, text="Stroke Index Order (1=hardest, 9=easiest)", padding=10)
        si_frame.pack(fill="x", padx=20, pady=10)
        
        # Stroke index header with edit button
        si_header = ttk.Frame(si_frame)
        si_header.grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 10))
        ttk.Label(si_header, text="Stroke Index Values:", style="Header.TLabel").pack(side="left")
        self.si_edit_btn = ttk.Button(si_header, text="Edit", command=self._toggle_si_edit)
        self.si_edit_btn.pack(side="left", padx=10)
        
        # Display current stroke index - 5 holes per row
        self.stroke_index_vars = []
        self.stroke_index_entries = []
        for i in range(9):
            row = i // 5 + 1
            col = (i % 5) * 2
            ttk.Label(si_frame, text=f"Hole {i+1}:").grid(row=row, column=col, padx=(5,2), pady=8, sticky="e")
            var = tk.StringVar(value=str(self.dm.course_settings.get("stroke_index", DEFAULT_STROKE_INDEX)[i]))
            self.stroke_index_vars.append(var)
            entry = ttk.Entry(si_frame, textvariable=var, width=5, state="readonly", justify="center")
            entry.grid(row=row, column=col+1, padx=(2,10), pady=8)
            self.stroke_index_entries.append(entry)
        
        # Par display
        par_frame = ttk.LabelFrame(frame, text="Hole Pars (Par 63 Course)", padding=10)
        par_frame.pack(fill="x", padx=20, pady=10)
        
        # Par header with edit button
        par_header = ttk.Frame(par_frame)
        par_header.grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 10))
        ttk.Label(par_header, text="Hole Par Values:", style="Header.TLabel").pack(side="left")
        self.par_edit_btn = ttk.Button(par_header, text="Edit", command=self._toggle_par_edit)
        self.par_edit_btn.pack(side="left", padx=10)
        
        # Display current hole pars (as entries for editing) - 5 holes per row
        self.hole_par_vars = []
        self.hole_par_entries = []
        for i in range(9):
            row = i // 5 + 1
            col = (i % 5) * 2
            ttk.Label(par_frame, text=f"Hole {i+1}:").grid(row=row, column=col, padx=(10,2), pady=8, sticky="e")
            var = tk.StringVar(value=str(self.dm.course_settings.get("hole_pars", HOLE_PARS).get(i+1, HOLE_PARS[i+1])))
            self.hole_par_vars.append(var)
            entry = ttk.Entry(par_frame, textvariable=var, width=5, state="readonly", justify="center")
            entry.grid(row=row, column=col+1, padx=(2,10), pady=8)
            self.hole_par_entries.append(entry)
        
        # Total par label in its own row below the entries
        current_hole_pars = self.dm.course_settings.get("hole_pars", HOLE_PARS)
        total_par = sum(current_hole_pars.values())
        self.total_par_label = ttk.Label(par_frame, text=f"Total Par: {total_par}",
                  style="Header.TLabel")
        self.total_par_label.grid(row=3, column=0, columnspan=10, padx=10, pady=10, sticky="w")
        
        # Save button
        ttk.Button(frame, text="Save Course Settings", style="Accent.TButton",
                   command=self._save_course_settings).pack(pady=20)
    
    def _save_stroke_index_data(self):
        """Validate and save stroke index to model. Returns (success, error_msg)."""
        try:
            stroke_index = []
            for var in self.stroke_index_vars:
                val = int(var.get())
                if val < 1 or val > 9:
                    raise ValueError("Stroke index must be 1-9")
                stroke_index.append(val)
            if len(set(stroke_index)) != 9:
                raise ValueError("Each stroke index value must be unique")
            self.dm.course_settings["stroke_index"] = stroke_index
            return True, None
        except ValueError as e:
            return False, str(e)
    
    def _save_hole_pars_data(self):
        """Validate and save hole pars to model and update total label. Returns (success, error_msg, total_par)."""
        try:
            hole_pars = {}
            total_par = 0
            for i, var in enumerate(self.hole_par_vars):
                val = int(var.get())
                if val < 3 or val > 5:
                    raise ValueError(f"Hole {i+1} par must be 3, 4, or 5")
                hole_pars[i+1] = val
                total_par += val
            self.dm.course_settings["hole_pars"] = hole_pars
            self.total_par_label.config(text=f"Total Par: {total_par}")
            return True, None, total_par
        except ValueError as e:
            return False, str(e), None
    
    def _toggle_si_edit(self):
        """Toggle stroke index edit mode or save if in edit mode."""
        if self.si_edit_mode:
            # Attempt to save
            success, error_msg = self._save_stroke_index_data()
            if success:
                self.dm.save_all()
                self.si_edit_mode = False
                for entry in self.stroke_index_entries:
                    entry.config(state="readonly")
                self.si_edit_btn.config(text="Edit")
                messagebox.showinfo("Success", "Stroke index saved successfully!")
            else:
                messagebox.showerror("Error", error_msg)
        else:
            # Enter edit mode
            self.si_edit_mode = True
            for entry in self.stroke_index_entries:
                entry.config(state="normal")
            self.si_edit_btn.config(text="Save")
    
    def _toggle_par_edit(self):
        """Toggle hole pars edit mode or save if in edit mode."""
        if self.par_edit_mode:
            # Attempt to save
            success, error_msg, total_par = self._save_hole_pars_data()
            if success:
                self.dm.save_all()
                self.par_edit_mode = False
                for entry in self.hole_par_entries:
                    entry.config(state="readonly")
                self.par_edit_btn.config(text="Edit")
                messagebox.showinfo("Success", "Hole pars saved successfully!")
            else:
                messagebox.showerror("Error", error_msg)
        else:
            # Enter edit mode
            self.par_edit_mode = True
            for entry in self.hole_par_entries:
                entry.config(state="normal")
            self.par_edit_btn.config(text="Save")
    
    def _save_course_settings(self):
        """Save course settings (course name and location)."""
        try:
            # If any section is in edit mode, prompt user to save those first
            if self.si_edit_mode or self.par_edit_mode:
                messagebox.showwarning("Warning", "Please save the Stroke Index and/or Hole Pars sections first using their Edit/Save buttons.")
                return
            
            # Save course name and location
            self.dm.course_settings["course_name"] = self.course_name_var.get()
            self.dm.course_settings["course_location"] = self.course_location_var.get()
            
            self.dm.save_all()
            
            messagebox.showinfo("Success", "Course settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
     
    # -------------------------------------------------------------------------
    # Players Tab
    # -------------------------------------------------------------------------
    def _build_players_tab(self):
        """Build the players management tab."""
        frame = self.players_frame
        
        # Configure grid for responsive layout
        frame.grid_rowconfigure(1, weight=1)  # treeview row expands
        frame.grid_columnconfigure(0, weight=1)
        
        # Title and add button
        header_frame = ttk.Frame(frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        header_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(header_frame, text="Player Management", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(header_frame, text="Add Player", command=self._show_add_player_dialog).grid(row=0, column=1, padx=5)
        
        # Players treeview with scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = ("name", "handicap", "phone", "email")
        self.players_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        self.players_tree.heading("name", text="Name")
        self.players_tree.heading("handicap", text="Handicap")
        self.players_tree.heading("phone", text="Phone")
        self.players_tree.heading("email", text="Email")
        
        self.players_tree.column("name", width=180, minwidth=100)
        self.players_tree.column("handicap", width=80, minwidth=60)
        self.players_tree.column("phone", width=120, minwidth=80)
        self.players_tree.column("email", width=200, minwidth=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.players_tree.yview)
        self.players_tree.configure(yscrollcommand=scrollbar.set)
        
        self.players_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure tags for striped rows and hover effect
        self.players_tree.tag_configure("oddrow", background="#F5F5F5")
        self.players_tree.tag_configure("evenrow", background="#FFFFFF")
        self.players_tree.tag_configure("hover", background="#E3F2FD")
        
        # Bind events for hover effect
        self.players_tree.bind("<Motion>", self._on_players_hover)
        self.players_tree.bind("<Leave>", self._on_players_leave)
        
        # Bind double-click to edit player
        self.players_tree.bind("<Double-1>", lambda e: self._edit_player())
        
        # Bind column headings to sorting
        for col in columns:
            self.players_tree.heading(col, command=lambda c=col: self._sort_players(c))
        
        # Action buttons - always visible at bottom
        btn_frame = ttk.Frame(frame, relief="groove", borderwidth=2)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        edit_btn = ttk.Button(btn_frame, text="Edit Player", command=self._edit_player)
        edit_btn.grid(row=0, column=0, padx=5, pady=5)
        ToolTip(edit_btn, "Edit the selected player's information")
        
        delete_btn = ttk.Button(btn_frame, text="Delete Player", command=self._delete_player)
        delete_btn.grid(row=0, column=1, padx=5, pady=5)
        ToolTip(delete_btn, "Remove the selected player from the league")
        
        refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self._refresh_players)
        refresh_btn.grid(row=0, column=2, padx=5, pady=5)
        ToolTip(refresh_btn, "Reload the player list from database")
    
    def _refresh_players(self):
        """Refresh the players list."""
        for item in self.players_tree.get_children():
            self.players_tree.delete(item)
        
        # Get sorted players
        sorted_players = self._get_sorted_players()
        
        for index, player in enumerate(sorted_players):
            # Apply striped row tags
            tags = ("oddrow" if index % 2 == 0 else "evenrow",)
            
            self.players_tree.insert("", "end", iid=player["id"],
                                     values=(player["name"], f"{player['handicap']:.1f}",
                                            player.get("phone", ""), player.get("email", "")),
                                     tags=tags)
    
    def _show_add_player_dialog(self):
        """Show dialog to add a new player."""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Add Player")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        # Center the dialog on the root window
        self._center_dialog(dialog)
        
        # Create main frame with padding and card style
        main_frame = ttk.Frame(dialog, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Add New Player", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Player Name
        ttk.Label(main_frame, text="Player Name:", style="Header.TLabel").grid(row=1, column=0, sticky="w", pady=10)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=40)
        name_entry.grid(row=1, column=1, pady=10, padx=10, sticky="w")
        ToolTip(name_entry, "Enter the player's full name")
        
        # Handicap
        ttk.Label(main_frame, text="Handicap:", style="Header.TLabel").grid(row=2, column=0, sticky="w", pady=10)
        handicap_var = tk.StringVar()
        handicap_entry = ttk.Entry(main_frame, textvariable=handicap_var, width=20)
        handicap_entry.grid(row=2, column=1, pady=10, padx=10, sticky="w")
        ToolTip(handicap_entry, "Enter the player's current handicap (can be 0)")
        
        # Phone
        ttk.Label(main_frame, text="Phone:", style="Header.TLabel").grid(row=3, column=0, sticky="w", pady=10)
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(main_frame, textvariable=phone_var, width=40)
        phone_entry.grid(row=3, column=1, pady=10, padx=10, sticky="w")
        ToolTip(phone_entry, "Optional: Player's phone number")
        
        # Email
        ttk.Label(main_frame, text="Email:", style="Header.TLabel").grid(row=4, column=0, sticky="w", pady=10)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(main_frame, textvariable=email_var, width=40)
        email_entry.grid(row=4, column=1, pady=10, padx=10, sticky="w")
        ToolTip(email_entry, "Optional: Player's email address")
        
        # Address
        ttk.Label(main_frame, text="Address:", style="Header.TLabel").grid(row=5, column=0, sticky="w", pady=10)
        address_var = tk.StringVar()
        address_entry = ttk.Entry(main_frame, textvariable=address_var, width=40)
        address_entry.grid(row=5, column=1, pady=10, padx=10, sticky="w")
        ToolTip(address_entry, "Optional: Player's address")
        
        def save():
            try:
                name = name_var.get().strip()
                handicap = float(handicap_var.get())
                phone = phone_var.get().strip()
                email = email_var.get().strip()
                address = address_var.get().strip()
                
                if not name:
                    raise ValueError("Name is required")
                if handicap < 0:
                    raise ValueError("Handicap must be non-negative")
                
                self.dm.add_player(name, handicap, phone=phone, email=email, address=address)
                self._refresh_players()
                self._update_dashboard_stats()
                self._set_status(f"Added player: {name}", "success")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        save_btn = ttk.Button(btn_frame, text="💾 Save Player", command=save, style="Accent.TButton")
        save_btn.pack(side="left", padx=5)
        ToolTip(save_btn, "Save the player to the database")
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)
        ToolTip(cancel_btn, "Close this dialog without saving")
    
    def _edit_player(self):
        """Edit selected player."""
        selected = self.players_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a player to edit")
            return
        
        player_id = selected[0]
        player = self.dm.get_player(player_id)
        if not player:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ Edit Player")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        # Center the dialog on the root window
        self._center_dialog(dialog)
        
        # Create main frame with padding and card style
        main_frame = ttk.Frame(dialog, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Edit Player", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        # Player Name
        ttk.Label(main_frame, text="Player Name:", style="Header.TLabel").grid(row=1, column=0, sticky="w", pady=10)
        name_var = tk.StringVar(value=player.get("name", ""))
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=40)
        name_entry.grid(row=1, column=1, pady=10, padx=10, sticky="w")
        ToolTip(name_entry, "Edit the player's full name")
        
        # Handicap
        ttk.Label(main_frame, text="Handicap:", style="Header.TLabel").grid(row=2, column=0, sticky="w", pady=10)
        handicap_var = tk.StringVar(value=str(player.get("handicap", 0.0)))
        handicap_entry = ttk.Entry(main_frame, textvariable=handicap_var, width=20)
        handicap_entry.grid(row=2, column=1, pady=10, padx=10, sticky="w")
        ToolTip(handicap_entry, "Edit the player's current handicap")
        
        # Phone
        ttk.Label(main_frame, text="Phone:", style="Header.TLabel").grid(row=3, column=0, sticky="w", pady=10)
        phone_var = tk.StringVar(value=player.get("phone", ""))
        phone_entry = ttk.Entry(main_frame, textvariable=phone_var, width=40)
        phone_entry.grid(row=3, column=1, pady=10, padx=10, sticky="w")
        ToolTip(phone_entry, "Edit the player's phone number")
        
        # Email
        ttk.Label(main_frame, text="Email:", style="Header.TLabel").grid(row=4, column=0, sticky="w", pady=10)
        email_var = tk.StringVar(value=player.get("email", ""))
        email_entry = ttk.Entry(main_frame, textvariable=email_var, width=40)
        email_entry.grid(row=4, column=1, pady=10, padx=10, sticky="w")
        ToolTip(email_entry, "Edit the player's email address")
        
        # Address
        ttk.Label(main_frame, text="Address:", style="Header.TLabel").grid(row=5, column=0, sticky="w", pady=10)
        address_var = tk.StringVar(value=player.get("address", ""))
        address_entry = ttk.Entry(main_frame, textvariable=address_var, width=40)
        address_entry.grid(row=5, column=1, pady=10, padx=10, sticky="w")
        ToolTip(address_entry, "Edit the player's address")
        
        def save():
            try:
                name = name_var.get().strip()
                handicap = float(handicap_var.get())
                phone = phone_var.get().strip()
                email = email_var.get().strip()
                address = address_var.get().strip()
                
                if not name:
                    raise ValueError("Name is required")
                if handicap < 0:
                    raise ValueError("Handicap must be non-negative")
                
                self.dm.update_player(player_id, name=name, handicap=handicap,
                                     phone=phone, email=email, address=address)
                self._refresh_players()
                self._update_dashboard_stats()
                self._set_status(f"Updated player: {name}", "success")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        save_btn = ttk.Button(btn_frame, text="💾 Save Changes", command=save, style="Accent.TButton")
        save_btn.pack(side="left", padx=5)
        ToolTip(save_btn, "Save changes to the player")
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)
        ToolTip(cancel_btn, "Close without saving changes")
    
    def _delete_player(self):
        """Delete selected player."""
        selected = self.players_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a player to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this player?"):
            player = self.dm.get_player(selected[0])
            player_name = player["name"] if player else "Unknown"
            self.dm.delete_player(selected[0])
            self._refresh_players()
            self._update_dashboard_stats()
            self._set_status(f"Deleted player: {player_name}", "info")
    
    # -------------------------------------------------------------------------
    # Players Tab - Sorting
    # -------------------------------------------------------------------------
    def _get_sorted_players(self) -> List[Dict]:
        """Get players sorted according to current sort state."""
        players = self.dm.get_players()
        
        if not self._players_sort_column:
            return players
        
        # Define sort key functions for each column
        sort_keys = {
            "name": lambda p: p["name"].lower(),
            "handicap": lambda p: p["handicap"],
            "phone": lambda p: p.get("phone", "").lower(),
            "email": lambda p: p.get("email", "").lower()
        }
        
        key_func = sort_keys.get(self._players_sort_column)
        if key_func:
            players.sort(key=key_func, reverse=self._players_sort_reverse)
        
        return players
    
    def _sort_players(self, column: str):
        """Sort players by the specified column, toggling direction if same column."""
        if self._players_sort_column == column:
            # Toggle sort direction
            self._players_sort_reverse = not self._players_sort_reverse
        else:
            # New column, default to ascending
            self._players_sort_column = column
            self._players_sort_reverse = False
        
        self._refresh_players()
    
    def _on_players_hover(self, event):
        """Handle mouse hover over players treeview."""
        # Get the item under the cursor
        item = self.players_tree.identify_row(event.y)
        if item:
            # Remove hover tag from all items
            for i in self.players_tree.get_children():
                current_tags = self.players_tree.item(i, "tags")
                if current_tags:
                    new_tags = [t for t in current_tags if t != "hover"]
                    self.players_tree.item(i, tags=new_tags)
            # Add hover tag to current item
        current_tags = self.players_tree.item(item, "tags") or ()
        if "hover" not in current_tags:
            self.players_tree.item(item, tags=list(current_tags) + ["hover"])
    
    def _on_players_leave(self, event):
        """Handle mouse leave from players treeview."""
        # Remove hover tag from all items
        for i in self.players_tree.get_children():
            current_tags = self.players_tree.item(i, "tags")
            if current_tags and "hover" in current_tags:
                new_tags = [t for t in current_tags if t != "hover"]
                self.players_tree.item(i, tags=new_tags)
    
    # -------------------------------------------------------------------------
    # Teams Tab - Sorting
    # -------------------------------------------------------------------------
    def _get_sorted_teams(self) -> List[Dict]:
        """Get teams sorted according to current sort state."""
        teams = self.dm.get_teams()
        
        if not self._teams_sort_column:
            return teams
        
        # Define sort key functions for each column
        sort_keys = {
            "team_number": lambda t: t.get("team_number") or 0,
            "name": lambda t: t["name"].lower(),
            "player1": lambda t: self.dm.get_player(t["player1_id"])["name"].lower() if t["player1_id"] in self.dm.players else "",
            "player2": lambda t: self.dm.get_player(t["player2_id"])["name"].lower() if t["player2_id"] in self.dm.players else "",
            "avg_handicap": lambda t: self.dm.get_team_handicap(t["id"])
        }
        
        key_func = sort_keys.get(self._teams_sort_column)
        if key_func:
            teams.sort(key=key_func, reverse=self._teams_sort_reverse)
        
        return teams
    
    def _sort_teams(self, column: str):
        """Sort teams by the specified column, toggling direction if same column."""
        if self._teams_sort_column == column:
            # Toggle sort direction
            self._teams_sort_reverse = not self._teams_sort_reverse
        else:
            # New column, default to ascending
            self._teams_sort_column = column
            self._teams_sort_reverse = False
        
        self._refresh_teams()
    
    def _on_teams_hover(self, event):
        """Handle mouse hover over teams treeview."""
        # Get the item under the cursor
        item = self.teams_tree.identify_row(event.y)
        if item:
            # Remove hover tag from all items
            for i in self.teams_tree.get_children():
                current_tags = self.teams_tree.item(i, "tags")
                if current_tags:
                    new_tags = [t for t in current_tags if t != "hover"]
                    self.teams_tree.item(i, tags=new_tags)
            # Add hover tag to current item
        current_tags = self.teams_tree.item(item, "tags") or ()
        if "hover" not in current_tags:
            self.teams_tree.item(item, tags=list(current_tags) + ["hover"])
    
    def _on_teams_leave(self, event):
        """Handle mouse leave from teams treeview."""
        # Remove hover tag from all items
        for i in self.teams_tree.get_children():
            current_tags = self.teams_tree.item(i, "tags")
            if current_tags and "hover" in current_tags:
                new_tags = [t for t in current_tags if t != "hover"]
                self.teams_tree.item(i, tags=new_tags)
    
    # -------------------------------------------------------------------------
    # Teams Tab
    # -------------------------------------------------------------------------
    def _build_teams_tab(self):
        """Build the teams management tab."""
        frame = self.teams_frame
        
        # Configure grid for responsive layout
        frame.grid_rowconfigure(1, weight=1)  # treeview row expands
        frame.grid_columnconfigure(0, weight=1)
        
        # Title and add button
        header_frame = ttk.Frame(frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        header_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(header_frame, text="Team Management", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(header_frame, text="Add Team", command=self._show_add_team_dialog).grid(row=0, column=1, padx=5)
        
        # Teams treeview with scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = ("team_number", "name", "player1", "player2", "avg_handicap")
        self.teams_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        self.teams_tree.heading("team_number", text="#")
        self.teams_tree.heading("name", text="Team Name")
        self.teams_tree.heading("player1", text="Player 1")
        self.teams_tree.heading("player2", text="Player 2")
        self.teams_tree.heading("avg_handicap", text="Avg Handicap")
        
        self.teams_tree.column("team_number", width=40, minwidth=30)
        self.teams_tree.column("name", width=150, minwidth=100)
        self.teams_tree.column("player1", width=150, minwidth=100)
        self.teams_tree.column("player2", width=150, minwidth=100)
        self.teams_tree.column("avg_handicap", width=100, minwidth=70)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.teams_tree.yview)
        self.teams_tree.configure(yscrollcommand=scrollbar.set)
        
        self.teams_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure tags for striped rows and hover effect
        self.teams_tree.tag_configure("oddrow", background="#F5F5F5")
        self.teams_tree.tag_configure("evenrow", background="#FFFFFF")
        self.teams_tree.tag_configure("hover", background="#E3F2FD")
        
        # Bind events for hover effect
        self.teams_tree.bind("<Motion>", self._on_teams_hover)
        self.teams_tree.bind("<Leave>", self._on_teams_leave)
        
        # Bind double-click to edit team
        self.teams_tree.bind("<Double-1>", lambda e: self._edit_team())
        
        # Bind column headings to sorting
        for col in columns:
            self.teams_tree.heading(col, command=lambda c=col: self._sort_teams(c))
        
        # Action buttons - always visible at bottom
        btn_frame = ttk.Frame(frame, relief="groove", borderwidth=2)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        edit_btn = ttk.Button(btn_frame, text="Edit Team", command=self._edit_team)
        edit_btn.grid(row=0, column=0, padx=5, pady=5)
        ToolTip(edit_btn, "Edit the selected team's composition")
        
        delete_btn = ttk.Button(btn_frame, text="Delete Team", command=self._delete_team)
        delete_btn.grid(row=0, column=1, padx=5, pady=5)
        ToolTip(delete_btn, "Remove the selected team from the league")
        
        refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self._refresh_teams)
        refresh_btn.grid(row=0, column=2, padx=5, pady=5)
        ToolTip(refresh_btn, "Reload the team list from database")
    
    def _refresh_teams(self):
        """Refresh the teams list."""
        for item in self.teams_tree.get_children():
            self.teams_tree.delete(item)
        
        # Get sorted teams
        sorted_teams = self._get_sorted_teams()
        
        for index, team in enumerate(sorted_teams):
            p1 = self.dm.get_player(team["player1_id"])
            p2 = self.dm.get_player(team["player2_id"])
            p1_name = p1["name"] if p1 else "Unknown"
            p2_name = p2["name"] if p2 else "Unknown"
            avg_hcp = self.dm.get_team_handicap(team["id"])
            
            # Get team number, use empty string if not set
            team_num = team.get("team_number", "")
            if team_num is None:
                team_num = ""
            
            # Apply striped row tags
            tags = ("oddrow" if index % 2 == 0 else "evenrow",)
            
            self.teams_tree.insert("", "end", iid=team["id"],
                                   values=(team_num, team["name"], p1_name, p2_name, f"{avg_hcp:.1f}"),
                                   tags=tags)
    
    def _show_add_team_dialog(self):
        """Show dialog to add a new team."""
        players = self.dm.get_players()
        if len(players) < 2:
            messagebox.showwarning("Warning", "You need at least 2 players to create a team")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Add Team")
        dialog.geometry("550x450")
        dialog.transient(self.root)
        dialog.grab_set()
        # Center the dialog on the root window
        self._center_dialog(dialog)
        
        # Create main frame with padding and card style
        main_frame = ttk.Frame(dialog, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Create New Team", style="Title.TLabel")
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Team number
        ttk.Label(main_frame, text="Team Number (optional):", style="Header.TLabel").pack(anchor="w", pady=5)
        team_number_var = tk.StringVar()
        team_number_entry = ttk.Entry(main_frame, textvariable=team_number_var, width=10)
        team_number_entry.pack(anchor="w", pady=5)
        ToolTip(team_number_entry, "Optional: Assign a team number for easy identification")
        
        # Team name (auto-generated but editable)
        ttk.Label(main_frame, text="Team Name:", style="Header.TLabel").pack(anchor="w", pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=40)
        name_entry.pack(anchor="w", pady=5)
        ToolTip(name_entry, "Team name (auto-generated from player names, but editable)")
        
        # Player selection section
        ttk.Label(main_frame, text="Select Players:", style="Header.TLabel").pack(anchor="w", pady=(15, 5))
        
        ttk.Label(main_frame, text="Player 1:").pack(anchor="w", pady=5)
        player1_var = tk.StringVar()
        player_combo1 = ttk.Combobox(main_frame, textvariable=player1_var, width=37, state="readonly")
        player_combo1["values"] = [f"{p['name']} (HCP: {p['handicap']})" for p in players]
        player_combo1.pack(pady=5)
        ToolTip(player_combo1, "Select the first player for this team")
        
        ttk.Label(main_frame, text="Player 2:").pack(anchor="w", pady=5)
        player2_var = tk.StringVar()
        player_combo2 = ttk.Combobox(main_frame, textvariable=player2_var, width=37, state="readonly")
        player_combo2["values"] = [f"{p['name']} (HCP: {p['handicap']})" for p in players]
        player_combo2.pack(pady=5)
        ToolTip(player_combo2, "Select the second player for this team")
        
        def update_team_name(event=None):
            """Auto-generate team name when both players are selected."""
            p1_idx = player_combo1.current()
            p2_idx = player_combo2.current()
            if p1_idx >= 0 and p2_idx >= 0 and p1_idx != p2_idx:
                p1_name = players[p1_idx]["name"]
                p2_name = players[p2_idx]["name"]
                generated_name = generate_team_name(p1_name, p2_name)
                name_var.set(generated_name)
            elif p1_idx >= 0 and p2_idx >= 0 and p1_idx == p2_idx:
                name_var.set("Cannot select same player twice")
            else:
                name_var.set("")
        
        player_combo1.bind("<<ComboboxSelected>>", update_team_name)
        player_combo2.bind("<<ComboboxSelected>>", update_team_name)
        
        def save():
            try:
                name = name_var.get().strip()
                if not name:
                    raise ValueError("Team name is required")
                
                p1_idx = player_combo1.current()
                p2_idx = player_combo2.current()
                
                if p1_idx < 0 or p2_idx < 0:
                    raise ValueError("Please select both players")
                
                if p1_idx == p2_idx:
                    raise ValueError("Cannot select the same player twice")
                
                player1_id = players[p1_idx]["id"]
                player2_id = players[p2_idx]["id"]
                
                team_number = int(team_number_var.get()) if team_number_var.get().strip() else None
                self.dm.add_team(name=name, player1_id=player1_id, player2_id=player2_id, team_number=team_number)
                self._refresh_teams()
                self._update_dashboard_stats()
                self._set_status(f"Added team: {name}", "success")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        save_btn = ttk.Button(btn_frame, text="💾 Save Team", command=save, style="Accent.TButton")
        save_btn.pack(side="left", padx=5)
        ToolTip(save_btn, "Create the team with selected players")
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)
        ToolTip(cancel_btn, "Close this dialog without creating the team")
    
    def _edit_team(self):
        """Edit selected team."""
        selected = self.teams_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a team to edit")
            return
        
        team_id = selected[0]
        team = self.dm.get_team(team_id)
        if not team:
            return
        
        players = self.dm.get_players()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ Edit Team")
        dialog.geometry("550x500")
        dialog.transient(self.root)
        dialog.grab_set()
        # Center the dialog on the root window
        self._center_dialog(dialog)
        
        # Create main frame with padding and card style
        main_frame = ttk.Frame(dialog, style="Card.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Edit Team", style="Title.TLabel")
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Team number
        ttk.Label(main_frame, text="Team Number (optional):", style="Header.TLabel").pack(anchor="w", pady=5)
        team_number_var = tk.StringVar(value=str(team.get("team_number", "")))
        team_number_entry = ttk.Entry(main_frame, textvariable=team_number_var, width=10)
        team_number_entry.pack(anchor="w", pady=5)
        ToolTip(team_number_entry, "Optional: Team number for easy identification")
        
        # Team name (auto-generated but editable)
        ttk.Label(main_frame, text="Team Name:", style="Header.TLabel").pack(anchor="w", pady=5)
        name_var = tk.StringVar(value=team["name"])
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=40)
        name_entry.pack(anchor="w", pady=5)
        ToolTip(name_entry, "Team name (auto-generated from player names, but editable)")
        
        # Player selection section
        ttk.Label(main_frame, text="Select Players:", style="Header.TLabel").pack(anchor="w", pady=(15, 5))
        
        ttk.Label(main_frame, text="Player 1:").pack(anchor="w", pady=5)
        player1_var = tk.StringVar()
        player_combo1 = ttk.Combobox(main_frame, textvariable=player1_var, width=37, state="readonly")
        player_combo1["values"] = [f"{p['name']} (HCP: {p['handicap']})" for p in players]
        player_combo1.pack(pady=5)
        ToolTip(player_combo1, "Select the first player for this team")
        
        # Set current selection
        for i, p in enumerate(players):
            if p["id"] == team["player1_id"]:
                player_combo1.current(i)
                break
        
        ttk.Label(main_frame, text="Player 2:").pack(anchor="w", pady=5)
        player2_var = tk.StringVar()
        player_combo2 = ttk.Combobox(main_frame, textvariable=player2_var, width=37, state="readonly")
        player_combo2["values"] = [f"{p['name']} (HCP: {p['handicap']})" for p in players]
        player_combo2.pack(pady=5)
        ToolTip(player_combo2, "Select the second player for this team")
        
        for i, p in enumerate(players):
            if p["id"] == team["player2_id"]:
                player_combo2.current(i)
                break
        
        def update_team_name(event=None):
            """Auto-generate team name when both players are selected."""
            p1_idx = player_combo1.current()
            p2_idx = player_combo2.current()
            if p1_idx >= 0 and p2_idx >= 0 and p1_idx != p2_idx:
                p1_name = players[p1_idx]["name"]
                p2_name = players[p2_idx]["name"]
                generated_name = generate_team_name(p1_name, p2_name)
                name_var.set(generated_name)
            elif p1_idx >= 0 and p2_idx >= 0 and p1_idx == p2_idx:
                name_var.set("Cannot select same player twice")
            # else: keep existing name
        
        player_combo1.bind("<<ComboboxSelected>>", update_team_name)
        player_combo2.bind("<<ComboboxSelected>>", update_team_name)
        
        def save():
            try:
                name = name_var.get().strip()
                if not name:
                    raise ValueError("Team name is required")
                
                team_number = int(team_number_var.get()) if team_number_var.get().strip() else None
                
                p1_idx = player_combo1.current()
                p2_idx = player_combo2.current()
                
                if p1_idx < 0 or p2_idx < 0:
                    raise ValueError("Please select both players")
                
                if p1_idx == p2_idx:
                    raise ValueError("Cannot select the same player twice")
                
                player1_id = players[p1_idx]["id"]
                player2_id = players[p2_idx]["id"]
                
                self.dm.update_team(team_id, name=name, player1_id=player1_id, player2_id=player2_id, team_number=team_number)
                self._refresh_teams()
                self._update_dashboard_stats()
                self._set_status(f"Updated team: {name}", "success")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        save_btn = ttk.Button(btn_frame, text="💾 Save Changes", command=save, style="Accent.TButton")
        save_btn.pack(side="left", padx=5)
        ToolTip(save_btn, "Save changes to the team")
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)
        ToolTip(cancel_btn, "Close without saving changes")
    
    def _delete_team(self):
        """Delete selected team."""
        selected = self.teams_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a team to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this team?"):
            team = self.dm.get_team(selected[0])
            team_name = team["name"] if team else "Unknown"
            self.dm.delete_team(selected[0])
            self._refresh_teams()
            self._update_dashboard_stats()
            self._set_status(f"Deleted team: {team_name}", "info")
    
    # -------------------------------------------------------------------------
    # Season Setup Tab
    # -------------------------------------------------------------------------
    def _build_season_setup(self):
        """Build the season setup tab."""
        frame = self.season_frame
        
        # Configure grid for responsive layout
        frame.grid_rowconfigure(3, weight=1)  # teams selection area expands (was 2, now 3 for scoring section)
        frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ttk.Label(frame, text="Season Setup", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        # Create new season
        create_frame = ttk.LabelFrame(frame, text="Create New Season", padding=10)
        create_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        create_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(create_frame, text="Season Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.season_name_var = tk.StringVar(value="2026 Season")
        ttk.Entry(create_frame, textvariable=self.season_name_var, width=40).grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Button(create_frame, text="Create Season", command=self._create_season).grid(row=0, column=2, pady=5, padx=10)
        
        # Scoring Configuration
        scoring_frame = ttk.LabelFrame(frame, text="Scoring Configuration", padding=10)
        scoring_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        scoring_frame.grid_columnconfigure(1, weight=1)
        
        # Edit mode state for scoring
        self.season_scoring_edit_mode = False
        
        # Hole Points
        ttk.Label(scoring_frame, text="Hole Points:",
                 style="Header.TLabel").grid(row=0, column=0, sticky="w", pady=5)
        
        current_hole_points = self.dm.course_settings.get("hole_points", 1.0)
        try:
            current_hole_points = float(current_hole_points)
        except (ValueError, TypeError):
            current_hole_points = 1.0
            
        self.season_hole_points_var = tk.StringVar(value=str(current_hole_points))
        self.season_hole_points_entry = ttk.Entry(scoring_frame,
                                                  textvariable=self.season_hole_points_var,
                                                  width=10, state="readonly", justify="center")
        self.season_hole_points_entry.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(scoring_frame, text="points per hole").grid(row=0, column=2, sticky="w", pady=5, padx=(5,10))
        
        # Team Bonus
        ttk.Label(scoring_frame, text="Match Bonus:",
                 style="Header.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        
        current_bonus = self.dm.course_settings.get("team_bonus_points", 5.0)
        try:
            current_bonus = float(current_bonus)
        except (ValueError, TypeError):
            current_bonus = 5.0
            
        self.season_bonus_var = tk.StringVar(value=str(current_bonus))
        self.season_bonus_entry = ttk.Entry(scoring_frame,
                                            textvariable=self.season_bonus_var,
                                            width=10, state="readonly", justify="center")
        self.season_bonus_entry.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(scoring_frame, text="points per match").grid(row=1, column=2, sticky="w", pady=5, padx=(5,10))
        
        # Edit/Save button for scoring
        self.season_scoring_edit_btn = ttk.Button(scoring_frame, text="Edit",
                                                  command=self._toggle_season_scoring_edit)
        self.season_scoring_edit_btn.grid(row=0, column=3, rowspan=2, padx=20, pady=5)
        
        
        # Select teams for season
        teams_frame = ttk.LabelFrame(frame, text="Select Teams for Season", padding=10)
        teams_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=5)
        teams_frame.grid_columnconfigure(0, weight=1)
        teams_frame.grid_columnconfigure(2, weight=1)
        teams_frame.grid_rowconfigure(1, weight=1)
        
        # Available teams
        ttk.Label(teams_frame, text="Available Teams:").grid(row=0, column=0, sticky="w", pady=5)
        self.available_teams_list = tk.Listbox(teams_frame, height=10, width=40, selectmode="extended")
        self.available_teams_list.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Buttons
        btn_frame = ttk.Frame(teams_frame)
        btn_frame.grid(row=1, column=1, padx=10)
        
        ttk.Button(btn_frame, text="Add All >>", command=self._add_all_teams_to_season).pack(pady=5)
        ttk.Button(btn_frame, text="Add Selected >", command=self._add_selected_teams_to_season).pack(pady=5)
        ttk.Button(btn_frame, text="< Remove Selected", command=self._remove_selected_teams_from_season).pack(pady=5)
        ttk.Button(btn_frame, text="<< Remove All", command=self._remove_all_teams_from_season).pack(pady=5)
        
        # Selected teams
        ttk.Label(teams_frame, text="Selected Teams:").grid(row=0, column=2, sticky="w", pady=5)
        self.selected_teams_list = tk.Listbox(teams_frame, height=10, width=40, selectmode="extended")
        self.selected_teams_list.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
        
        # Save button only in Season Setup
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        button_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Button(button_frame, text="Save Season", command=self._save_season_teams).grid(row=0, column=0, padx=5)
        
        # Current season info
        self.current_season_var = tk.StringVar(value="No season selected")
        season_label = ttk.Label(button_frame, textvariable=self.current_season_var)
        season_label.grid(row=0, column=1, padx=20, sticky="w")
    
    def _create_season(self):
        """Create a new season."""
        name = self.season_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Season name is required")
            return
        
        season_id = self.dm.create_season(name)
        self._refresh_season_teams()
        self.current_season_var.set(f"Current Season: {name}")
        self._current_season_id = season_id
        self._set_status(f"Created season: {name}", "success")
        messagebox.showinfo("Success", f"Season '{name}' created!")
    
    def _save_season_teams(self):
        """Save the selected teams to the current season without generating schedule."""
        if not hasattr(self, "_current_season_id") or not self._current_season_id:
            messagebox.showerror("Error", "Please create a season first")
            return
        
        # Get selected team names
        team_names = []
        for i in range(self.selected_teams_list.size()):
            team_names.append(self.selected_teams_list.get(i))
        
        if len(team_names) < 2:
            messagebox.showerror("Error", "Select at least 2 teams for the season")
            return
        
        # Get team IDs from names
        all_teams = self.dm.get_teams()
        team_map = {f"{t['name']} (Avg HCP: {self.dm.get_team_handicap(t['id']):.1f})": t["id"] for t in all_teams}
        team_ids = []
        for name in team_names:
            if name in team_map:
                team_ids.append(team_map[name])
        
        # Update season with selected teams
        season = self.dm.get_season(self._current_season_id)
        if season:
            season["team_ids"] = team_ids
            self.dm.seasons[self._current_season_id] = season
            self.dm.save_all()
            self._set_status(f"Saved {len(team_ids)} teams to season", "success")
            messagebox.showinfo("Success", f"Saved {len(team_ids)} teams to season!")
        else:
            messagebox.showerror("Error", "Season not found")
    
    def _toggle_season_scoring_edit(self):
        """Toggle scoring settings edit mode or save if in edit mode."""
        if self.season_scoring_edit_mode:
            # Attempt to save
            success_hole = True
            success_bonus = True
            error_msg = None
            
            # Validate and save hole points
            try:
                val = float(self.season_hole_points_var.get())
                if val < 0.1:
                    raise ValueError("Hole points must be at least 0.1")
                self.dm.course_settings["hole_points"] = val
            except ValueError as e:
                success_hole = False
                error_msg = f"Hole points: {str(e)}"
            
            # Validate and save bonus points
            try:
                bonus = float(self.season_bonus_var.get())
                if bonus < 0.1:
                    raise ValueError("Bonus points must be at least 0.1")
                self.dm.course_settings["team_bonus_points"] = bonus
            except ValueError as e:
                success_bonus = False
                error_msg = f"Bonus points: {str(e)}" if not error_msg else f"{error_msg}\nBonus points: {str(e)}"
            
            if success_hole and success_bonus:
                self.dm.save_all()
                self.season_scoring_edit_mode = False
                self.season_hole_points_entry.config(state="readonly")
                self.season_bonus_entry.config(state="readonly")
                self.season_scoring_edit_btn.config(text="Edit")
                messagebox.showinfo("Success", "Scoring settings saved successfully!")
            else:
                messagebox.showerror("Error", error_msg)
        else:
            # Enter edit mode
            self.season_scoring_edit_mode = True
            self.season_hole_points_entry.config(state="normal")
            self.season_bonus_entry.config(state="normal")
            self.season_scoring_edit_btn.config(text="Save")
    
    def _refresh_season_teams(self):
        """Refresh the team selection lists."""
        self.available_teams_list.delete(0, "end")
        self.selected_teams_list.delete(0, "end")
        
        all_teams = self.dm.get_teams()
        for team in all_teams:
            self.available_teams_list.insert("end", f"{team['name']} (Avg HCP: {self.dm.get_team_handicap(team['id']):.1f})")
    
    def _add_all_teams_to_season(self):
        """Add all teams to the season."""
        for i in range(self.available_teams_list.size()):
            item = self.available_teams_list.get(i)
            self.selected_teams_list.insert("end", item)
        self.available_teams_list.delete(0, "end")
    
    def _add_selected_teams_to_season(self):
        """Add selected teams to the season."""
        selected = self.available_teams_list.curselection()
        for i in reversed(selected):
            item = self.available_teams_list.get(i)
            self.selected_teams_list.insert("end", item)
            self.available_teams_list.delete(i)
    
    def _remove_selected_teams_from_season(self):
        """Remove selected teams from the season."""
        selected = self.selected_teams_list.curselection()
        for i in reversed(selected):
            item = self.selected_teams_list.get(i)
            self.available_teams_list.insert("end", item)
            self.selected_teams_list.delete(i)
    
    def _remove_all_teams_from_season(self):
        """Remove all teams from the season."""
        for i in range(self.selected_teams_list.size()):
            item = self.selected_teams_list.get(i)
            self.available_teams_list.insert("end", item)
        self.selected_teams_list.delete(0, "end")
    
    def _generate_schedule(self):
        """Generate the season schedule."""
        # Check if we have a current season with saved teams
        season_id = None
        team_ids = []
        
        if hasattr(self, "_current_season_id") and self._current_season_id:
            season = self.dm.get_season(self._current_season_id)
            if season and season.get("team_ids"):
                season_id = self._current_season_id
                team_ids = season["team_ids"]
        
        # If no saved season teams, fall back to listbox selection
        if not team_ids:
            team_names = []
            for i in range(self.selected_teams_list.size()):
                team_names.append(self.selected_teams_list.get(i))
            
            if len(team_names) < 2:
                messagebox.showerror("Error", "Select at least 2 teams to generate a schedule")
                return
            
            # Get team IDs from names
            all_teams = self.dm.get_teams()
            team_map = {f"{t['name']} (Avg HCP: {self.dm.get_team_handicap(t['id']):.1f})": t["id"] for t in all_teams}
            for name in team_names:
                if name in team_map:
                    team_ids.append(team_map[name])
            
            if len(team_ids) < 2:
                messagebox.showerror("Error", "Could not find team IDs")
                return
            
            # Create season if not exists
            if not season_id:
                season_id = self.dm.create_season("2026 Season")
                self._current_season_id = season_id
        else:
            # Use existing season
            season_id = self._current_season_id
        
        # Generate schedule using greedy algorithm
        schedule = self.dm.generate_schedule(season_id, team_ids)
        
        if not schedule:
            messagebox.showerror("Error", "Could not generate schedule")
            return
        
        # Add matches to database
        for match in schedule:
            self.dm.add_match(season_id, match["week"], match["team1_id"], match["team2_id"])
        
        self._set_status(f"Generated {len(schedule)} matches for season", "success")
        messagebox.showinfo("Success", f"Generated {len(schedule)} matches!")
        self._refresh_schedule()
    
    def _generate_week_schedule(self):
        """Generate schedule for a specific week based on current handicaps."""
        # Get selected week
        week_str = self.week_filter_var.get()
        if week_str == "All":
            messagebox.showwarning("Warning", "Please select a specific week to generate")
            return
        
        try:
            week_number = int(week_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid week number")
            return
        
        # Check if season exists
        if not hasattr(self, "_current_season_id") or not self._current_season_id:
            messagebox.showerror("Error", "Please create a season first in Season Setup tab")
            return
        
        season_id = self._current_season_id
        
        # Get teams in the season
        season = self.dm.get_season(season_id)
        if not season:
            messagebox.showerror("Error", "Season not found")
            return
        
        team_ids = season.get("team_ids", [])
        if len(team_ids) < 2:
            messagebox.showerror("Error", "Need at least 2 teams in the season to generate matches")
            return
        
        # Generate weekly matchups
        week_matchups = self.dm.generate_weekly_schedule(season_id, week_number)
        
        if not week_matchups:
            messagebox.showinfo("Info", "No matches to generate for this week. All teams may have already played each other, or no matchups available.")
            return
        
        # Add matches to database
        added_count = 0
        for t1_id, t2_id in week_matchups:
            # Check if this matchup is already scheduled for this week
            existing = self.dm.get_matches_for_week(season_id, week_number)
            already_scheduled = any(
                (m["team1_id"] == t1_id and m["team2_id"] == t2_id) or
                (m["team1_id"] == t2_id and m["team2_id"] == t1_id)
                for m in existing
            )
            if not already_scheduled:
                self.dm.add_match(season_id, week_number, t1_id, t2_id)
                added_count += 1
        
        self._set_status(f"Generated {added_count} matches for Week {week_number}", "success")
        messagebox.showinfo("Success", f"Generated {added_count} matches for Week {week_number}!")
        self._refresh_schedule()
   
   # -------------------------------------------------------------------------
   # Schedule Tab
    # -------------------------------------------------------------------------
    def _build_schedule_tab(self):
        """Build the schedule tab."""
        frame = self.schedule_frame
        
        # Configure grid for responsive layout
        frame.grid_rowconfigure(1, weight=1)  # treeview row expands
        frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ttk.Label(frame, text="Season Schedule", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        # Filter and controls frame
        controls_frame = ttk.Frame(frame)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Week filter
        ttk.Label(controls_frame, text="Week:").grid(row=0, column=0, padx=5)
        self.week_filter_var = tk.StringVar(value="All")
        week_combo = ttk.Combobox(controls_frame, textvariable=self.week_filter_var, width=10, state="readonly")
        week_combo["values"] = ["All"] + [str(i) for i in range(1, 26)]
        week_combo.grid(row=0, column=1, padx=5, sticky="w")
        week_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_schedule())
        
        ttk.Button(controls_frame, text="Generate Week", command=self._generate_week_schedule).grid(row=0, column=2, padx=5)
        ttk.Button(controls_frame, text="Generate Full Schedule", style="Accent.TButton",
                   command=self._generate_schedule).grid(row=0, column=3, padx=5)
        ttk.Button(controls_frame, text="Refresh", command=self._refresh_schedule).grid(row=0, column=4, padx=5)
        
        # Schedule treeview with scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = ("week", "team1", "team2", "status", "score")
        self.schedule_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15, selectmode="extended")
        
        self.schedule_tree.heading("week", text="Week")
        self.schedule_tree.heading("team1", text="Team 1")
        self.schedule_tree.heading("team2", text="Team 2")
        self.schedule_tree.heading("status", text="Status")
        self.schedule_tree.heading("score", text="Score")
        
        self.schedule_tree.column("week", width=60, minwidth=50)
        self.schedule_tree.column("team1", width=150, minwidth=100)
        self.schedule_tree.column("team2", width=150, minwidth=100)
        self.schedule_tree.column("status", width=100, minwidth=80)
        self.schedule_tree.column("score", width=100, minwidth=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)
        
        self.schedule_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure tags for status badges and striped rows
        self.schedule_tree.tag_configure("completed", foreground="#2E7D32", font=("Segoe UI", 9, "bold"))
        self.schedule_tree.tag_configure("scheduled", foreground="#F57C00", font=("Segoe UI", 9, "bold"))
        self.schedule_tree.tag_configure("oddrow", background="#F5F5F5")
        self.schedule_tree.tag_configure("evenrow", background="#FFFFFF")
        self.schedule_tree.tag_configure("hover", background="#E3F2FD")
        
        # Bind events for hover effect
        self.schedule_tree.bind("<Motion>", self._on_schedule_hover)
        self.schedule_tree.bind("<Leave>", self._on_schedule_leave)
        
        # Bind double-click to view/edit match details
        self.schedule_tree.bind("<Double-1>", lambda e: self._view_match_details())
        # Bind Delete key to delete selected schedule items
        self.schedule_tree.bind("<Delete>", lambda e: self._delete_schedule_item())
        
        # Action buttons frame - always visible at bottom
        btn_frame = ttk.Frame(frame, relief="groove", borderwidth=2)
        btn_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        delete_btn = ttk.Button(btn_frame, text="Delete Selected", command=self._delete_schedule_item)
        delete_btn.grid(row=0, column=0, padx=5, pady=5)
        ToolTip(delete_btn, "Delete selected matches from schedule (including scores)")
        
        print_btn = ttk.Button(btn_frame, text="Print Scorecard", command=self._print_scorecard_from_schedule)
        print_btn.grid(row=0, column=1, padx=5, pady=5)
        ToolTip(print_btn, "Print or save scorecard for selected match")
        
        refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self._refresh_schedule)
        refresh_btn.grid(row=0, column=2, padx=5, pady=5)
        ToolTip(refresh_btn, "Reload the schedule from database")
    
    def _refresh_schedule(self):
        """Refresh the schedule view."""
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
        
        week_filter = self.week_filter_var.get()
        
        matches_list = list(self.dm.matches.values())
        # Sort by week number
        matches_list.sort(key=lambda m: m["week_number"])
        
        for index, match in enumerate(matches_list):
            if week_filter != "All" and str(match["week_number"]) != week_filter:
                continue
            
            team1 = self.dm.get_team(match["team1_id"])
            team2 = self.dm.get_team(match["team2_id"])
            team1_name = team1["name"] if team1 else "Unknown"
            team2_name = team2["name"] if team2 else "Unknown"
            
            status = "Completed" if match.get("completed", False) else "Scheduled"
            
            # Get score if available
            score = "-"
            match_scores = self.dm.get_match_scores(match["id"])
            if match_scores:
                t1 = match_scores.get("team1_final_points", 0.0)
                t2 = match_scores.get("team2_final_points", 0.0)
                score = f"{t1}-{t2}"
            
            # Apply striped row and status tags
            tags = []
            if index % 2 == 0:
                tags.append("oddrow")
            else:
                tags.append("evenrow")
            
            if match.get("completed", False):
                tags.append("completed")
            else:
                tags.append("scheduled")
            
            self.schedule_tree.insert("", "end", iid=match["id"],
                                      values=(match["week_number"], team1_name, team2_name, status, score),
                                      tags=tags)
    
    def _on_schedule_hover(self, event):
        """Handle mouse hover over schedule treeview."""
        # Get the item under the cursor
        item = self.schedule_tree.identify_row(event.y)
        if item:
            # Remove hover tag from all items
            for i in self.schedule_tree.get_children():
                current_tags = self.schedule_tree.item(i, "tags")
                if current_tags:
                    new_tags = [t for t in current_tags if t != "hover"]
                    self.schedule_tree.item(i, tags=new_tags)
            # Add hover tag to current item
        current_tags = self.schedule_tree.item(item, "tags") or ()
        if "hover" not in current_tags:
            self.schedule_tree.item(item, tags=list(current_tags) + ["hover"])
    
    def _on_schedule_leave(self, event):
        """Handle mouse leave from schedule treeview."""
        # Remove hover tag from all items
        for i in self.schedule_tree.get_children():
            current_tags = self.schedule_tree.item(i, "tags")
            if current_tags and "hover" in current_tags:
                new_tags = [t for t in current_tags if t != "hover"]
                self.schedule_tree.item(i, tags=new_tags)
    
    def _delete_schedule_item(self):
        """Delete selected schedule items (supports multiple selection)."""
        selected = self.schedule_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select at least one schedule item to delete")
            return
        
        # Gather information about all selected matches
        matches_to_delete = []
        total_has_scores = False
        
        for match_id in selected:
            match = self.dm.matches.get(match_id)
            if not match:
                continue
            
            team1 = self.dm.get_team(match["team1_id"])
            team2 = self.dm.get_team(match["team2_id"])
            team1_name = team1["name"] if team1 else "Unknown"
            team2_name = team2["name"] if team2 else "Unknown"
            
            has_scores = match_id in self.dm.scores
            if has_scores:
                total_has_scores = True
            
            matches_to_delete.append({
                "id": match_id,
                "week": match["week_number"],
                "team1": team1_name,
                "team2": team2_name,
                "status": "Completed" if match.get("completed", False) else "Scheduled",
                "has_scores": has_scores
            })
        
        if not matches_to_delete:
            messagebox.showerror("Error", "No valid matches selected")
            return
        
        # Build confirmation message
        msg = f"Delete {len(matches_to_delete)} schedule item(s)?\n\n"
        
        # Show first 5 matches to keep dialog manageable
        for i, m in enumerate(matches_to_delete[:5]):
            msg += f"Week {m['week']}: {m['team1']} vs {m['team2']} ({m['status']})\n"
        
        if len(matches_to_delete) > 5:
            msg += f"... and {len(matches_to_delete) - 5} more\n"
        
        if total_has_scores:
            msg += "\nWarning: Some matches have scores recorded. They will also be deleted."
        
        if messagebox.askyesno("Confirm Delete", msg):
            # Delete all selected matches
            deleted_count = 0
            for m in matches_to_delete:
                self.dm.delete_match(m["id"])
                deleted_count += 1
            
            self._refresh_schedule()
            self._refresh_standings()
            self._update_dashboard_stats()
            self._set_status(f"Deleted {deleted_count} schedule item(s)", "info")
            messagebox.showinfo("Success", f"Deleted {len(matches_to_delete)} schedule item(s)")
    
    def _view_match_details(self):
        """View/Edit match details on double-click."""
        selected = self.schedule_tree.selection()
        if not selected:
            return
        
        match_id = selected[0]
        match = self.dm.matches.get(match_id)
        if not match:
            return
        
        # Switch to match entry tab and load this match
        self.notebook.select(6)  # Match Entry tab index
        self._refresh_match_combo()
        
        # Find and select the match in the combo
        for i, mid in enumerate(self._match_ids):
            if mid == match_id:
                self.match_combo.current(i)
                self._load_match_for_entry()
                break
    
    def _print_scorecard_from_schedule(self):
        """Handle print scorecard button from schedule tab."""
        selected = self.schedule_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a match from the schedule")
            return
        
        if len(selected) > 1:
            messagebox.showwarning("Warning", "Please select only one match to print")
            return
        
        match_id = selected[0]
        match = self.dm.matches.get(match_id)
        if not match:
            messagebox.showerror("Error", "Selected match not found")
            return
        
        self.print_scorecard(match_id)
    
    # -------------------------------------------------------------------------
    # Match Entry Tab
    # -------------------------------------------------------------------------
    def _build_match_entry(self):
        """Build the match entry tab."""
        frame = self.match_entry_frame
        
        # Configure grid for responsive layout
        frame.grid_rowconfigure(2, weight=1)  # score entry frame expands
        frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ttk.Label(frame, text="Match Score Entry", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        # Match selection
        select_frame = ttk.Frame(frame)
        select_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        select_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(select_frame, text="Select Match:").grid(row=0, column=0, padx=5)
        self.match_select_var = tk.StringVar()
        self.match_combo = ttk.Combobox(select_frame, textvariable=self.match_select_var, width=60, state="readonly")
        self.match_combo.grid(row=0, column=1, padx=5, sticky="ew")
        self.match_combo.bind("<<ComboboxSelected>>", lambda e: self._load_match_for_entry())
        
        ttk.Button(select_frame, text="Refresh", command=self._refresh_match_combo).grid(row=0, column=2, padx=5)
        
        # Score entry frame
        self.score_entry_frame = ttk.LabelFrame(frame, text="Enter Scores", padding=10)
        self.score_entry_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=5)
        
        # This will be populated when a match is selected
        self.score_entries = {}
        
        # Save and Print buttons - always visible at bottom
        btn_frame = ttk.Frame(frame, relief="groove", borderwidth=2)
        btn_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        save_btn = ttk.Button(btn_frame, text="Save Scores", style="Accent.TButton",
                             command=self._save_match_scores)
        save_btn.grid(row=0, column=0, padx=5, pady=5)
        ToolTip(save_btn, "Save entered scores and calculate match results")
        
        print_btn = ttk.Button(btn_frame, text="Print Scorecard",
                              command=self._print_scorecard_from_match_entry)
        print_btn.grid(row=0, column=2, padx=5, pady=5)
        ToolTip(print_btn, "Print or save a formatted scorecard for this match")
    
    def _refresh_match_combo(self):
        """Refresh the match selection combo box."""
        matches = []
        for match in self.dm.matches.values():
            team1 = self.dm.get_team(match["team1_id"])
            team2 = self.dm.get_team(match["team2_id"])
            team1_name = team1["name"] if team1 else "Unknown"
            team2_name = team2["name"] if team2 else "Unknown"
            status = "✓" if match.get("completed", False) else "○"
            matches.append((match["id"], f"Week {match['week_number']}: {team1_name} vs {team2_name} [{status}]"))
        
        self.match_combo["values"] = [m[1] for m in matches]
        self._match_ids = [m[0] for m in matches]
    
    def _load_match_for_entry(self):
        """Load the selected match for score entry."""
        # Clear existing entries
        for widget in self.score_entry_frame.winfo_children():
            widget.destroy()
        self.score_entries = {}
        
        selected_idx = self.match_combo.current()
        if selected_idx < 0:
            return
        
        match_id = self._match_ids[selected_idx]
        match = self.dm.matches.get(match_id)
        if not match:
            return
        
        team1 = self.dm.get_team(match["team1_id"])
        team2 = self.dm.get_team(match["team2_id"])
        
        if not team1 or not team2:
            return
        
        # Get player info
        p1_1 = self.dm.get_player(team1["player1_id"])
        p1_2 = self.dm.get_player(team1["player2_id"])
        p2_1 = self.dm.get_player(team2["player1_id"])
        p2_2 = self.dm.get_player(team2["player2_id"])
        
        # Get stroke index and pars
        stroke_index = self.dm.course_settings.get("stroke_index", DEFAULT_STROKE_INDEX)
        hole_pars = self.dm.course_settings.get("hole_pars", HOLE_PARS)
        
        # Get current handicaps (using rolling average if available)
        season_id = match.get("season_id", "")
        week_number = match.get("week_number", 1)
        
        h1_p1 = self.dm.get_player_recent_handicap(team1["player1_id"], season_id, week_number)
        h1_p2 = self.dm.get_player_recent_handicap(team1["player2_id"], season_id, week_number)
        h2_p1 = self.dm.get_player_recent_handicap(team2["player1_id"], season_id, week_number)
        h2_p2 = self.dm.get_player_recent_handicap(team2["player2_id"], season_id, week_number)
        
        # Determine which holes each player gets strokes on (match play style)
        # Strokes are given by the higher handicap player equal to the difference
        # allocated to the hardest holes first (based on stroke index)
        def get_matchplay_stroke_holes(handicap_a, handicap_b, stroke_index):
            """
            Determine which holes the higher handicap player gets strokes on.
            Returns list of hole numbers (1-9).
            """
            diff = abs(int(handicap_a) - int(handicap_b))
            if diff <= 0:
                return []
            
            # Create list of holes sorted by stroke index (hardest first)
            holes_by_si = sorted(range(1, 10), key=lambda h: stroke_index[h-1] if h <= len(stroke_index) else h)
            
            # Return the first 'diff' holes (hardest ones)
            return holes_by_si[:diff]
        
        # For each player, determine if they receive strokes in their matchups
        # Team1 Player1 vs Team2 Player1
        if h1_p1 > h2_p1:
            t1_p1_strokes = get_matchplay_stroke_holes(h1_p1, h2_p1, stroke_index)
            t2_p1_strokes = []
        elif h2_p1 > h1_p1:
            t2_p1_strokes = get_matchplay_stroke_holes(h2_p1, h1_p1, stroke_index)
            t1_p1_strokes = []
        else:
            t1_p1_strokes = []
            t2_p1_strokes = []
        
        # Team1 Player2 vs Team2 Player2
        if h1_p2 > h2_p2:
            t1_p2_strokes = get_matchplay_stroke_holes(h1_p2, h2_p2, stroke_index)
            t2_p2_strokes = []
        elif h2_p2 > h1_p2:
            t2_p2_strokes = get_matchplay_stroke_holes(h2_p2, h1_p2, stroke_index)
            t1_p2_strokes = []
        else:
            t1_p2_strokes = []
            t2_p2_strokes = []
        
        # Create enhanced golf card layout with team grouping
        # Header row: Par row
        ttk.Label(self.score_entry_frame, text="Player", style="Header.TLabel").grid(row=0, column=0, padx=5, pady=5)
        
        # Hole headers with stroke index indicators in a styled frame
        for hole in range(1, 10):
            si = stroke_index[hole - 1] if hole <= len(stroke_index) else hole
            par = hole_pars.get(hole, 4)
            header_text = f"H{hole}\nSI:{si}\nP:{par}"
            label = ttk.Label(self.score_entry_frame, text=header_text, style="Header.TLabel")
            label.grid(row=0, column=hole, padx=3, pady=5)
        
        # Team 1 Section with background
        team1_frame = ttk.Frame(self.score_entry_frame, style="Card.TFrame", padding=5)
        team1_frame.grid(row=1, column=0, columnspan=10, padx=2, pady=2, sticky="ew")
        
        # Team 1 label
        ttk.Label(team1_frame, text=f"Team 1: {team1['name']}", style="Subtitle.TLabel").grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 5))
        
        # Team 1 Player 1 - show strokes received
        t1_p1_stroke_count = len(t1_p1_strokes)
        stroke_text = f" - {t1_p1_stroke_count} stroke{'s' if t1_p1_stroke_count != 1 else ''}" if t1_p1_stroke_count > 0 else ""
        ttk.Label(team1_frame, text=f"{p1_1['name']}\n(HCP: {h1_p1:.1f}){stroke_text}").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        for hole in range(1, 10):
            var = tk.StringVar()
            entry = ttk.Entry(team1_frame, textvariable=var, width=6, justify="center")
            entry.grid(row=1, column=hole, padx=2, pady=2)
            self.score_entries[(match_id, "team1", "p1", hole)] = var
            
            # Highlight if stroke is given on this hole
            if hole in t1_p1_strokes:
                entry.configure(style="StrokeEntry.TEntry")
        
        # Team 1 Player 2 - show strokes received
        t1_p2_stroke_count = len(t1_p2_strokes)
        stroke_text = f" - {t1_p2_stroke_count} stroke{'s' if t1_p2_stroke_count != 1 else ''}" if t1_p2_stroke_count > 0 else ""
        ttk.Label(team1_frame, text=f"{p1_2['name']}\n(HCP: {h1_p2:.1f}){stroke_text}").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        for hole in range(1, 10):
            var = tk.StringVar()
            entry = ttk.Entry(team1_frame, textvariable=var, width=6, justify="center")
            entry.grid(row=2, column=hole, padx=2, pady=2)
            self.score_entries[(match_id, "team1", "p2", hole)] = var
            
            if hole in t1_p2_strokes:
                entry.configure(style="StrokeEntry.TEntry")
        
        # Separator between teams
        separator1 = ttk.Separator(self.score_entry_frame, orient="horizontal")
        separator1.grid(row=2, column=0, columnspan=10, sticky="ew", pady=5)
        
        # Team 2 Section with background
        team2_frame = ttk.Frame(self.score_entry_frame, style="Card.TFrame", padding=5)
        team2_frame.grid(row=3, column=0, columnspan=10, padx=2, pady=2, sticky="ew")
        
        # Team 2 label
        ttk.Label(team2_frame, text=f"Team 2: {team2['name']}", style="Subtitle.TLabel").grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 5))
        
        # Team 2 Player 1 - show strokes received
        t2_p1_stroke_count = len(t2_p1_strokes)
        stroke_text = f" - {t2_p1_stroke_count} stroke{'s' if t2_p1_stroke_count != 1 else ''}" if t2_p1_stroke_count > 0 else ""
        ttk.Label(team2_frame, text=f"{p2_1['name']}\n(HCP: {h2_p1:.1f}){stroke_text}").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        for hole in range(1, 10):
            var = tk.StringVar()
            entry = ttk.Entry(team2_frame, textvariable=var, width=6, justify="center")
            entry.grid(row=1, column=hole, padx=2, pady=2)
            self.score_entries[(match_id, "team2", "p1", hole)] = var
            
            if hole in t2_p1_strokes:
                entry.configure(style="StrokeEntry.TEntry")
        
        # Team 2 Player 2 - show strokes received
        t2_p2_stroke_count = len(t2_p2_strokes)
        stroke_text = f" - {t2_p2_stroke_count} stroke{'s' if t2_p2_stroke_count != 1 else ''}" if t2_p2_stroke_count > 0 else ""
        ttk.Label(team2_frame, text=f"{p2_2['name']}\n(HCP: {h2_p2:.1f}){stroke_text}").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        for hole in range(1, 10):
            var = tk.StringVar()
            entry = ttk.Entry(team2_frame, textvariable=var, width=6, justify="center")
            entry.grid(row=2, column=hole, padx=2, pady=2)
            self.score_entries[(match_id, "team2", "p2", hole)] = var
            
            if hole in t2_p2_strokes:
                entry.configure(style="StrokeEntry.TEntry")
        
        # Info section with better styling
        info_frame = ttk.Frame(self.score_entry_frame, style="Card.TFrame", padding=10)
        info_frame.grid(row=4, column=0, columnspan=10, pady=10, sticky="ew")
        
        info_label = ttk.Label(info_frame,
                              text="💡 Highlighted cells indicate holes where strokes are received based on handicap",
                              style="Info.TLabel")
        info_label.pack()
        
        # Add a results preview frame (will be populated when scores are calculated)
        self.results_preview_frame = ttk.LabelFrame(self.score_entry_frame, text="Match Results Preview", padding=10)
        self.results_preview_frame.grid(row=5, column=0, columnspan=10, pady=10, sticky="ew")
        
        self.results_preview_label = ttk.Label(self.results_preview_frame,
                                              text="Enter scores and click 'Save Scores' to see results",
                                              style="Subtitle.TLabel")
        self.results_preview_label.pack()
        
        self._current_match_id = match_id
    
    def _save_match_scores(self):
        """Save the entered match scores."""
        if not hasattr(self, "_current_match_id"):
            messagebox.showwarning("Warning", "Please select a match first")
            return
        
        match_id = self._current_match_id
        
        # Collect scores
        try:
            team1_p1 = {}
            team1_p2 = {}
            team2_p1 = {}
            team2_p2 = {}
            
            for hole in range(1, 10):
                t1_p1 = self.score_entries[(match_id, "team1", "p1", hole)].get()
                t1_p2 = self.score_entries[(match_id, "team1", "p2", hole)].get()
                t2_p1 = self.score_entries[(match_id, "team2", "p1", hole)].get()
                t2_p2 = self.score_entries[(match_id, "team2", "p2", hole)].get()
                
                if not all([t1_p1, t1_p2, t2_p1, t2_p2]):
                    raise ValueError(f"Please enter all scores for hole {hole}")
                
                team1_p1[hole] = int(t1_p1)
                team1_p2[hole] = int(t1_p2)
                team2_p1[hole] = int(t2_p1)
                team2_p2[hole] = int(t2_p2)
            
            # Calculate scores
            results = self.scoring.calculate_match_scores(
                match_id, team1_p1, team1_p2, team2_p1, team2_p2
            )
            
            if not results:
                messagebox.showerror("Error", "Could not calculate scores")
                return
            
            # Save scores
            self.dm.save_match_scores(match_id, results)
            
            # Mark match as completed
            self.dm.complete_match(match_id)
            
            # Get match info for status message
            match = self.dm.get_match(match_id)
            team1 = self.dm.get_team(match.get("team1_id", "")) if match else None
            team2 = self.dm.get_team(match.get("team2_id", "")) if match else None
            team1_name = team1["name"] if team1 else "Team 1"
            team2_name = team2["name"] if team2 else "Team 2"
            winner = results['winner'].replace('_', ' ').title()
            
            self._set_status(f"Saved match: {team1_name} vs {team2_name} - Winner: {winner}", "success")
            
            # Show results
            result_msg = f"""Match Results:
            
Team 1: {results['team1_final_points']:.1f} points
  - Hole Points: {results['team1_hole_points']:.1f}
  - Team Bonus: {results['team1_bonus']:.1f}
  - Total Gross: {results['team1_total']}

Team 2: {results['team2_final_points']:.1f} points
  - Hole Points: {results['team2_hole_points']:.1f}
  - Team Bonus: {results['team2_bonus']:.1f}
  - Total Gross: {results['team2_total']}

Winner: {results['winner'].replace('_', ' ').title()}"""
            
            messagebox.showinfo("Match Complete", result_msg)
            
            self._refresh_schedule()
            self._refresh_standings()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
    
    def _print_scorecard_from_match_entry(self):
        """Handle print scorecard button from match entry tab."""
        if not hasattr(self, "_current_match_id"):
            messagebox.showwarning("Warning", "Please select a match first")
            return
        
        match_id = self._current_match_id
        self.print_scorecard(match_id)
    
    # -------------------------------------------------------------------------
    # Standings Tab
    # -------------------------------------------------------------------------
    def _build_standings(self):
        """Build the standings tab."""
        frame = self.standings_frame
        
        # Configure grid for responsive layout
        frame.grid_rowconfigure(1, weight=1)  # treeview row expands
        frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ttk.Label(frame, text="Season Standings", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        # Standings treeview with scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = ("rank", "team", "matches", "wins", "losses", "ties", "points", "hole_diff")
        self.standings_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        self.standings_tree.heading("rank", text="Rank")
        self.standings_tree.heading("team", text="Team")
        self.standings_tree.heading("matches", text="Matches")
        self.standings_tree.heading("wins", text="Wins")
        self.standings_tree.heading("losses", text="Losses")
        self.standings_tree.heading("ties", text="Ties")
        self.standings_tree.heading("points", text="Points")
        self.standings_tree.heading("hole_diff", text="Hole Diff")
        
        self.standings_tree.column("rank", width=50, minwidth=40)
        self.standings_tree.column("team", width=200, minwidth=150)
        self.standings_tree.column("matches", width=70, minwidth=50)
        self.standings_tree.column("wins", width=70, minwidth=50)
        self.standings_tree.column("losses", width=70, minwidth=50)
        self.standings_tree.column("ties", width=70, minwidth=50)
        self.standings_tree.column("points", width=80, minwidth=60)
        self.standings_tree.column("hole_diff", width=80, minwidth=60)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.standings_tree.yview)
        self.standings_tree.configure(yscrollcommand=scrollbar.set)
        
        self.standings_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure tags for striped rows, hover effect, and first place highlight
        self.standings_tree.tag_configure("oddrow", background="#F5F5F5")
        self.standings_tree.tag_configure("evenrow", background="#FFFFFF")
        self.standings_tree.tag_configure("hover", background="#E3F2FD")
        self.standings_tree.tag_configure("firstplace", background="#FFF9C4", font=("Segoe UI", 10, "bold"))
        
        # Bind events for hover effect
        self.standings_tree.bind("<Motion>", self._on_standings_hover)
        self.standings_tree.bind("<Leave>", self._on_standings_leave)
        
        # Action buttons frame - always visible at bottom
        btn_frame = ttk.Frame(frame, relief="groove", borderwidth=2)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        print_btn = ttk.Button(btn_frame, text="Print Scorecard", command=self._print_scorecard_from_standings)
        print_btn.grid(row=0, column=0, padx=5, pady=5)
        ToolTip(print_btn, "Print scorecard for selected completed match")
        
        refresh_btn = ttk.Button(btn_frame, text="Refresh Standings", command=self._refresh_standings)
        refresh_btn.grid(row=0, column=2, padx=5, pady=5)
        ToolTip(refresh_btn, "Recalculate and display current team rankings")
    
    def _refresh_standings(self):
        """Refresh the standings view."""
        for item in self.standings_tree.get_children():
            self.standings_tree.delete(item)
        
        # Calculate standings from match results
        team_stats = {}
        for team in self.dm.get_teams():
            team_stats[team["id"]] = {
                "team": team,
                "matches": 0,
                "wins": 0,
                "losses": 0,
                "ties": 0,
                "points": 0.0,
                "hole_points_for": 0.0,
                "hole_points_against": 0.0
            }
        
        # Process all completed matches
        for match in self.dm.matches.values():
            if not match.get("completed", False):
                continue
            
            scores = self.dm.get_match_scores(match["id"])
            if not scores:
                continue
            
            t1_id = match["team1_id"]
            t2_id = match["team2_id"]
            
            # Skip if team not in current team roster
            if t1_id not in team_stats or t2_id not in team_stats:
                continue
            
            team_stats[t1_id]["matches"] += 1
            team_stats[t2_id]["matches"] += 1
            
            t1_points = scores.get("team1_final_points", 0.0)
            t2_points = scores.get("team2_final_points", 0.0)
            
            team_stats[t1_id]["points"] += t1_points
            team_stats[t2_id]["points"] += t2_points
            
            team_stats[t1_id]["hole_points_for"] += scores.get("team1_hole_points", 0.0)
            team_stats[t1_id]["hole_points_against"] += scores.get("team2_hole_points", 0.0)
            team_stats[t2_id]["hole_points_for"] += scores.get("team2_hole_points", 0.0)
            team_stats[t2_id]["hole_points_against"] += scores.get("team1_hole_points", 0.0)
            
            if t1_points > t2_points:
                team_stats[t1_id]["wins"] += 1
                team_stats[t2_id]["losses"] += 1
            elif t2_points > t1_points:
                team_stats[t2_id]["wins"] += 1
                team_stats[t1_id]["losses"] += 1
            else:
                team_stats[t1_id]["ties"] += 1
                team_stats[t2_id]["ties"] += 1
        
        # Sort by points (descending)
        sorted_teams = sorted(team_stats.values(), key=lambda x: x["points"], reverse=True)
        
        # Display standings
        for index, stats in enumerate(sorted_teams):
            rank = index + 1
            team = stats["team"]
            hole_diff = stats["hole_points_for"] - stats["hole_points_against"]
            
            # Apply special tag for first place, otherwise striped rows
            if index == 0 and stats["points"] > 0:
                tags = ("firstplace",)
            else:
                tags = ("oddrow" if index % 2 == 0 else "evenrow",)
            
            self.standings_tree.insert("", "end",
                                       values=(rank, team["name"], stats["matches"],
                                              stats["wins"], stats["losses"], stats["ties"],
                                              f"{stats['points']:.1f}", f"{hole_diff:+.1f}"),
                                       tags=tags)
        
        # Update status bar
        if sorted_teams:
            leader = sorted_teams[0]["team"]["name"] if sorted_teams[0]["points"] > 0 else "No leader yet"
            self._set_status(f"Standings updated - Leader: {leader}", "info")
    
    def _on_standings_hover(self, event):
        """Handle mouse hover over standings treeview."""
        # Get the item under the cursor
        item = self.standings_tree.identify_row(event.y)
        if item:
            # Remove hover tag from all items
            for i in self.standings_tree.get_children():
                current_tags = self.standings_tree.item(i, "tags")
                if current_tags:
                    new_tags = [t for t in current_tags if t != "hover"]
                    self.standings_tree.item(i, tags=new_tags)
            # Add hover tag to current item
        current_tags = self.standings_tree.item(item, "tags") or ()
        if "hover" not in current_tags:
            self.standings_tree.item(item, tags=list(current_tags) + ["hover"])
    
    def _on_standings_leave(self, event):
        """Handle mouse leave from standings treeview."""
        # Remove hover tag from all items
        for i in self.standings_tree.get_children():
            current_tags = self.standings_tree.item(i, "tags")
            if current_tags and "hover" in current_tags:
                new_tags = [t for t in current_tags if t != "hover"]
                self.standings_tree.item(i, tags=new_tags)
    
    def _print_scorecard_from_standings(self):
        """Handle print scorecard button from standings tab."""
        selected = self.standings_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a match from the standings")
            return
        
        if len(selected) > 1:
            messagebox.showwarning("Warning", "Please select only one match to print")
            return
        
        item = selected[0]
        values = self.standings_tree.item(item, "values")
        if not values:
            return
        
        # The match ID should be stored in the item's iid or we need to find it
        # Since standings doesn't store match IDs directly, we need to get the match
        # from the team and week info. This is more complex, so for now we'll
        # prompt the user to select from schedule instead.
        messagebox.showinfo("Info",
            "Please use the Schedule tab to print scorecards.\n\n"
            "The standings view shows aggregated results, not individual matches.")
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    def _refresh_all_views(self):
        """Refresh all UI views."""
        self._update_dashboard_stats()
        self._refresh_players()
        self._refresh_teams()
        self._refresh_schedule()
        self._refresh_match_combo()
        self._refresh_standings()
    
    def _save_all_data(self):
        """Save all data to files."""
        self.dm.save_all()
        messagebox.showinfo("Success", "All data saved successfully!")
    
    # -------------------------------------------------------------------------
    # Scorecard Printing
    # -------------------------------------------------------------------------
    def generate_blank_scorecard_text(self, match_id: str) -> str:
        """Generate a blank printable scorecard for manual score entry.
        
        Returns a string containing the scorecard with empty boxes for players to fill in.
        """
        match = self.dm.matches.get(match_id)
        if not match:
            return "Match not found"
        
        team1 = self.dm.get_team(match["team1_id"])
        team2 = self.dm.get_team(match["team2_id"])
        if not team1 or not team2:
            return "Team data not found"
        
        # Get season info
        season = self.dm.get_season(match["season_id"])
        season_name = season["name"] if season else "Unknown Season"
        
        # Get course settings
        stroke_index = self.dm.course_settings.get("stroke_index", DEFAULT_STROKE_INDEX)
        hole_pars = self.dm.course_settings.get("hole_pars", HOLE_PARS)
        course_name = self.dm.course_settings.get("course_name", DEFAULT_COURSE["name"])
        
        # Get player info and handicaps
        p1_1 = self.dm.get_player(team1["player1_id"])
        p1_2 = self.dm.get_player(team1["player2_id"])
        p2_1 = self.dm.get_player(team2["player1_id"])
        p2_2 = self.dm.get_player(team2["player2_id"])
        
        week_number = match.get("week_number", 1)
        h1_p1 = self.dm.get_player_recent_handicap(team1["player1_id"], match["season_id"], week_number)
        h1_p2 = self.dm.get_player_recent_handicap(team1["player2_id"], match["season_id"], week_number)
        h2_p1 = self.dm.get_player_recent_handicap(team2["player1_id"], match["season_id"], week_number)
        h2_p2 = self.dm.get_player_recent_handicap(team2["player2_id"], match["season_id"], week_number)
        
        # Determine which holes each player gets strokes on
        def get_stroke_holes(handicap_a, handicap_b):
            diff = abs(int(handicap_a) - int(handicap_b))
            if diff <= 0:
                return []
            # Create list of holes sorted by stroke index (hardest first)
            holes_by_si = sorted(range(1, 10), key=lambda h: stroke_index[h-1] if h <= len(stroke_index) else h)
            return holes_by_si[:diff]
        
        t1_p1_strokes = get_stroke_holes(h1_p1, h2_p1) if h1_p1 > h2_p1 else (get_stroke_holes(h2_p1, h1_p1) if h2_p1 > h1_p1 else [])
        t1_p2_strokes = get_stroke_holes(h1_p2, h2_p2) if h1_p2 > h2_p2 else (get_stroke_holes(h2_p2, h1_p2) if h2_p2 > h1_p2 else [])
        t2_p1_strokes = get_stroke_holes(h2_p1, h1_p1) if h2_p1 > h1_p1 else (get_stroke_holes(h1_p1, h2_p1) if h1_p1 > h2_p1 else [])
        t2_p2_strokes = get_stroke_holes(h2_p2, h1_p2) if h2_p2 > h1_p2 else (get_stroke_holes(h1_p2, h2_p2) if h1_p2 > h2_p2 else [])
        
        # Build the blank scorecard - traditional golf format with holes across top
        lines = []
        lines.append("=" * 80)
        lines.append("BLANK SCORECARD - FOR PLAYER USE".center(80))
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Match: {team1['name']} vs {team2['name']}".ljust(80))
        lines.append(f"Season: {season_name}   Week: {week_number}   Date: {match.get('date_played', '_____')}".ljust(80))
        lines.append(f"Course: {course_name}".ljust(80))
        lines.append("")
        
        # Column headers - holes across top
        # Build header row with hole numbers, SI, and Par in a multi-line header
        header_line1 = f"{'Player':<25} {'HCP':<6} {'Stk':<5}"
        header_line2 = f"{'':-<25} {'':-<6} {'':-<5}"
        for hole in range(1, 10):
            si = stroke_index[hole - 1] if hole <= len(stroke_index) else hole
            par = hole_pars.get(hole, 4)
            header_line1 += f" {hole:^4}"
            header_line2 += f" {si:>2}/{par:<2}"
        
        lines.append(header_line1)
        lines.append(header_line2)
        lines.append("-" * 80)
        
        # Player rows
        players = [
            (p1_1, h1_p1, t1_p1_strokes, f"Team 1 - Player 1"),
            (p1_2, h1_p2, t1_p2_strokes, f"Team 1 - Player 2"),
            (p2_1, h2_p1, t2_p1_strokes, f"Team 2 - Player 1"),
            (p2_2, h2_p2, t2_p2_strokes, f"Team 2 - Player 2")
        ]
        
        for player, handicap, strokes, label in players:
            player_name = player['name'] if player else "Unknown"
            stroke_count = len(strokes)
            stroke_display = f"{stroke_count}" if stroke_count > 0 else "-"
            
            # Main row with player name and gross score boxes
            row = f"{player_name[:25]:<25} {handicap:>6.1f} {stroke_display:>5}"
            for hole in range(1, 10):
                row += f" {'______':^6}"
            lines.append(row)
            
            # Second row for net scores (calculated) - aligned with boxes
            row2 = f"{'(' + label + ')':<25} {'':>6} {'':>5}"
            for hole in range(1, 10):
                if hole in strokes:
                    row2 += f" {'(__)':^6}"
                else:
                    row2 += f" {'(--)':^6}"
            lines.append(row2)
        
        lines.append("=" * 80)
        lines.append("")
        lines.append("NOTES:")
        lines.append("  - Write GROSS scores (actual strokes) in the boxes above")
        lines.append("  - NET score = Gross - strokes received (shown in parentheses below each box)")
        lines.append("  - Compare NET scores to determine winner (lower net wins the hole)")
        lines.append("  - (__) indicates holes where you receive strokes")
        lines.append("")
        lines.append("=" * 80)
        lines.append("MATCH SCORING (to be completed after match):")
        lines.append("-" * 80)
        lines.append("Team 1 Gross Total: ______    Team 2 Gross Total: ______")
        lines.append("")
        lines.append("Hole Points (1 point per matchup win, 2 matchups per hole):")
        lines.append("  Team 1: ______    Team 2: ______")
        lines.append("")
        lines.append("Team Bonus (5 points to team with lower combined net score):")
        lines.append("  Team 1: ______    Team 2: ______")
        lines.append("")
        lines.append("FINAL SCORES:")
        lines.append("  Team 1: ______ points    Team 2: ______ points")
        lines.append("")
        lines.append("Winner: _______________________________")
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
        
        return "\n".join(lines)
    
    def generate_blank_scorecard_html(self, match_id: str) -> str:
        """Generate a blank printable scorecard as HTML for manual score entry.
        
        Returns an HTML string containing a beautifully styled scorecard.
        """
        match = self.dm.matches.get(match_id)
        if not match:
            return "<html><body>Match not found</body></html>"
        
        team1 = self.dm.get_team(match["team1_id"])
        team2 = self.dm.get_team(match["team2_id"])
        if not team1 or not team2:
            return "<html><body>Team data not found</body></html>"
        
        # Get season info
        season = self.dm.get_season(match["season_id"])
        season_name = season["name"] if season else "Unknown Season"
        
        # Get course settings
        stroke_index = self.dm.course_settings.get("stroke_index", DEFAULT_STROKE_INDEX)
        hole_pars = self.dm.course_settings.get("hole_pars", HOLE_PARS)
        course_name = self.dm.course_settings.get("course_name", DEFAULT_COURSE["name"])
        
        # Get player info and handicaps
        p1_1 = self.dm.get_player(team1["player1_id"])
        p1_2 = self.dm.get_player(team1["player2_id"])
        p2_1 = self.dm.get_player(team2["player1_id"])
        p2_2 = self.dm.get_player(team2["player2_id"])
        
        week_number = match.get("week_number", 1)
        h1_p1 = self.dm.get_player_recent_handicap(team1["player1_id"], match["season_id"], week_number)
        h1_p2 = self.dm.get_player_recent_handicap(team1["player2_id"], match["season_id"], week_number)
        h2_p1 = self.dm.get_player_recent_handicap(team2["player1_id"], match["season_id"], week_number)
        h2_p2 = self.dm.get_player_recent_handicap(team2["player2_id"], match["season_id"], week_number)
        
        # Determine which holes each player gets strokes on
        def get_stroke_holes(handicap_a, handicap_b):
            diff = abs(int(handicap_a) - int(handicap_b))
            if diff <= 0:
                return []
            holes_by_si = sorted(range(1, 10), key=lambda h: stroke_index[h-1] if h <= len(stroke_index) else h)
            return holes_by_si[:diff]
        
        t1_p1_strokes = get_stroke_holes(h1_p1, h2_p1) if h1_p1 > h2_p1 else (get_stroke_holes(h2_p1, h1_p1) if h2_p1 > h1_p1 else [])
        t1_p2_strokes = get_stroke_holes(h1_p2, h2_p2) if h1_p2 > h2_p2 else (get_stroke_holes(h2_p2, h1_p2) if h2_p2 > h1_p2 else [])
        t2_p1_strokes = get_stroke_holes(h2_p1, h1_p1) if h2_p1 > h1_p1 else (get_stroke_holes(h1_p1, h2_p1) if h1_p1 > h2_p1 else [])
        t2_p2_strokes = get_stroke_holes(h2_p2, h1_p2) if h2_p2 > h1_p2 else (get_stroke_holes(h1_p2, h2_p2) if h1_p2 > h2_p2 else [])
        
        # Get player names
        p1_name = p1_1['name'] if p1_1 else "Unknown"
        p2_name = p1_2['name'] if p1_2 else "Unknown"
        p3_name = p2_1['name'] if p2_1 else "Unknown"
        p4_name = p2_2['name'] if p2_2 else "Unknown"
        
        # Build HTML
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scorecard - {team1['name']} vs {team2['name']}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.4;
        }}
        
        .scorecard {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border: 2px solid #2E7D32;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #2E7D32, #1B5E20);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .header .match-info {{
            font-size: 16px;
            margin: 5px 0;
        }}
        
        .teams {{
            display: flex;
            justify-content: space-around;
            background: #E8F5E9;
            padding: 15px;
            border-bottom: 2px solid #2E7D32;
        }}
        
        .team {{
            text-align: center;
            flex: 1;
        }}
        
        .team h2 {{
            color: #2E7D32;
            font-size: 20px;
            margin-bottom: 10px;
            border-bottom: 2px solid #2E7D32;
            padding-bottom: 5px;
        }}
        
        .player {{
            margin: 8px 0;
            font-size: 14px;
        }}
        
        .player .name {{
            font-weight: 600;
            color: #333;
        }}
        
        .player .handicap {{
            color: #666;
            font-size: 13px;
        }}
        
        .player .strokes {{
            display: inline-block;
            background: #FFD700;
            color: #333;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 600;
            margin-left: 5px;
        }}
        
        .instructions {{
            background: #FFF3E0;
            padding: 15px 20px;
            border-bottom: 2px solid #2E7D32;
            font-size: 13px;
        }}
        
        .instructions h3 {{
            color: #2E7D32;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        
        .instructions ul {{
            margin-left: 20px;
        }}
        
        .instructions li {{
            margin: 4px 0;
        }}
        
        .score-table {{
            width: 100%;
            border-collapse: collapse;
            padding: 0 20px;
        }}
        
        .score-table th {{
            background: #2E7D32;
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: 600;
            border: 1px solid #1B5E20;
        }}
        
        .score-table th.hole-header {{
            width: 60px;
        }}
        
        .score-table th.par-header {{
            width: 50px;
        }}
        
        .score-table th.player-header {{
            width: 140px;
        }}
        
        .score-table td {{
            padding: 0;
            text-align: center;
            border: 1px solid #ddd;
            vertical-align: middle;
        }}
        
        .score-table .player-row {{
            background: #f9f9f9;
        }}
        
        .score-table .player-row:nth-child(even) {{
            background: #f0f0f0;
        }}
        
        .score-table .player-label {{
            text-align: left;
            padding: 8px 12px;
            font-weight: 600;
            color: #333;
            white-space: nowrap;
        }}
        
        .score-table .gross-box {{
            width: 60px;
            height: 40px;
            border: 2px dashed #999;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: #999;
            background: #fff;
        }}
        
        .score-table .net-box {{
            background: #E3F2FD;
            width: 50px;
            height: 30px;
            border: 1px solid #90CAF9;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: #1976D2;
        }}
        
        .score-table .net-box.stroke {{
            background: #FFF3E0;
            color: #F57C00;
            font-weight: 600;
        }}
        
        .summary {{
            background: #F5F5F5;
            padding: 20px;
            border-top: 2px solid #2E7D32;
        }}
        
        .summary h3 {{
            color: #2E7D32;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .summary-item {{
            background: white;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        
        .summary-item label {{
            display: block;
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
        }}
        
        .summary-item input {{
            width: 100%;
            padding: 6px;
            border: 1px solid #ddd;
            border-radius: 3px;
            font-size: 14px;
            font-weight: 600;
        }}
        
        .winner-section {{
            text-align: center;
            padding: 15px;
            background: white;
            border: 2px dashed #2E7D32;
            border-radius: 4px;
            margin-top: 15px;
        }}
        
        .winner-section label {{
            display: block;
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }}
        
        .winner-section input {{
            width: 300px;
            padding: 8px;
            border: 2px solid #2E7D32;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 600;
            text-align: center;
        }}
        
        @media print {{
            body {{ background: white; padding: 0; }}
            .scorecard {{ border: none; box-shadow: none; }}
        }}
        
        @page {{
            size: landscape;
            margin: 0.5in;
        }}
    </style>
</head>
<body>
    <div class="scorecard">
        <div class="header">
            <h1>Golf Match Scorecard</h1>
            <div class="match-info">{season_name} - Week {week_number}</div>
            <div class="match-info">{match.get('date_played', '_____')} | {course_name}</div>
        </div>
        
        <div class="teams">
            <div class="team">
                <h2>{team1['name']}</h2>
                <div class="player">
                    <span class="name">{p1_name}</span>
                    <span class="handicap">HCP: {h1_p1:.1f}</span>
                    <span class="strokes">{len(t1_p1_strokes)} strokes</span>
                </div>
                <div class="player">
                    <span class="name">{p2_name}</span>
                    <span class="handicap">HCP: {h1_p2:.1f}</span>
                    <span class="strokes">{len(t1_p2_strokes)} strokes</span>
                </div>
            </div>
            <div class="team">
                <h2>{team2['name']}</h2>
                <div class="player">
                    <span class="name">{p3_name}</span>
                    <span class="handicap">HCP: {h2_p1:.1f}</span>
                    <span class="strokes">{len(t2_p1_strokes)} strokes</span>
                </div>
                <div class="player">
                    <span class="name">{p4_name}</span>
                    <span class="handicap">HCP: {h2_p2:.1f}</span>
                    <span class="strokes">{len(t2_p2_strokes)} strokes</span>
                </div>
            </div>
        </div>
        
        <div class="instructions">
            <h3>How to Use This Scorecard</h3>
            <ul>
                <li><strong>Write GROSS scores</strong> (actual strokes) in the blank boxes for each hole</li>
                <li><strong>NET score</strong> = Gross - strokes received (shown in blue/orange boxes below)</li>
                <li>Compare NET scores hole-by-hole to determine winner (lower net wins)</li>
                <li>Each hole has 2 matchups: Team1-P1 vs Team2-P1, and Team1-P2 vs Team2-P2</li>
                <li>Winner gets 1 point per matchup win (2 points max per hole)</li>
                <li>Team Bonus: 5 points to team with lower combined net score</li>
            </ul>
        </div>
        
        <div style="padding: 20px;">
            <table class="score-table">
                <thead>
                    <tr>
                        <th class="player-header">Player</th>
                        <th class="hole-header">HCP</th>
                        <th class="hole-header">Stk</th>'''
        
        # Add hole headers
        for hole in range(1, 10):
            si = stroke_index[hole - 1] if hole <= len(stroke_index) else hole
            par = hole_pars.get(hole, 4)
            html += f'\n                        <th class="hole-header">{hole}<br><span style="font-size:11px;">SI:{si} P:{par}</span></th>'
        
        html += '''\n                    </tr>
                </thead>
                <tbody>'''
        
        # Player rows
        players_data = [
            (p1_name, h1_p1, t1_p1_strokes, "Team 1 - Player 1"),
            (p2_name, h1_p2, t1_p2_strokes, "Team 1 - Player 2"),
            (p3_name, h2_p1, t2_p1_strokes, "Team 2 - Player 1"),
            (p4_name, h2_p2, t2_p2_strokes, "Team 2 - Player 2")
        ]
        
        for player_name, handicap, strokes, label in players_data:
            html += f'''
                <tr class="player-row">
                    <td class="player-label">{player_name}</td>
                    <td>{handicap:.1f}</td>
                    <td>{len(strokes) if strokes else '-'}</td>'''
            
            # Gross score boxes
            for hole in range(1, 10):
                html += '\n                        <td class="gross-box">______</td>'
            
            html += '''\n                    </tr>
                    <tr>
                        <td class="player-label" style="font-size:11px;color:#666;">(''' + label + ''')</td>
                        <td></td>
                        <td></td>'''
            
            # Net score boxes
            for hole in range(1, 10):
                if hole in strokes:
                    html += '\n                        <td class="net-box stroke">(__)</td>'
                else:
                    html += '\n                        <td class="net-box">(--)</td>'
            
            html += '''\n                    </tr>'''
        
        html += '''\n                </tbody>
            </table>
        </div>
        
        <div class="summary">
            <h3>Match Scoring Summary</h3>
            <div class="summary-grid">
                <div class="summary-item">
                    <label>Team 1 Gross Total</label>
                    <input type="text" placeholder="______" readonly>
                </div>
                <div class="summary-item">
                    <label>Team 2 Gross Total</label>
                    <input type="text" placeholder="______" readonly>
                </div>
                <div class="summary-item">
                    <label>Hole Points - Team 1</label>
                    <input type="text" placeholder="______" readonly>
                </div>
                <div class="summary-item">
                    <label>Hole Points - Team 2</label>
                    <input type="text" placeholder="______" readonly>
                </div>
                <div class="summary-item">
                    <label>Team Bonus - Team 1</label>
                    <input type="text" placeholder="______" readonly>
                </div>
                <div class="summary-item">
                    <label>Team Bonus - Team 2</label>
                    <input type="text" placeholder="______" readonly>
                </div>
                <div class="summary-item">
                    <label>Final Score - Team 1</label>
                    <input type="text" placeholder="______ points" readonly>
                </div>
                <div class="summary-item">
                    <label>Final Score - Team 2</label>
                    <input type="text" placeholder="______ points" readonly>
                </div>
            </div>
            <div class="winner-section">
                <label>Match Winner</label>
                <input type="text" placeholder="Enter winning team name" readonly>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        return html
    
    def generate_scorecard_text(self, match_id: str) -> str:
        """Generate a formatted scorecard for printing.
        
        Returns a string containing the complete scorecard with all match details.
        """
        match = self.dm.matches.get(match_id)
        if not match:
            return "Match not found"
        
        team1 = self.dm.get_team(match["team1_id"])
        team2 = self.dm.get_team(match["team2_id"])
        if not team1 or not team2:
            return "Team data not found"
        
        # Get season info
        season = self.dm.get_season(match["season_id"])
        season_name = season["name"] if season else "Unknown Season"
        
        # Get course settings
        stroke_index = self.dm.course_settings.get("stroke_index", DEFAULT_STROKE_INDEX)
        hole_pars = self.dm.course_settings.get("hole_pars", HOLE_PARS)
        course_name = self.dm.course_settings.get("course_name", DEFAULT_COURSE["name"])
        
        # Get player info and handicaps
        p1_1 = self.dm.get_player(team1["player1_id"])
        p1_2 = self.dm.get_player(team1["player2_id"])
        p2_1 = self.dm.get_player(team2["player1_id"])
        p2_2 = self.dm.get_player(team2["player2_id"])
        
        week_number = match.get("week_number", 1)
        h1_p1 = self.dm.get_player_recent_handicap(team1["player1_id"], match["season_id"], week_number)
        h1_p2 = self.dm.get_player_recent_handicap(team1["player2_id"], match["season_id"], week_number)
        h2_p1 = self.dm.get_player_recent_handicap(team2["player1_id"], match["season_id"], week_number)
        h2_p2 = self.dm.get_player_recent_handicap(team2["player2_id"], match["season_id"], week_number)
        
        # Get scores if available
        scores = self.dm.get_match_scores(match_id)
        
        # Build the scorecard
        lines = []
        lines.append("=" * 80)
        lines.append(f"MATCH SCORECARD".center(80))
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Season: {season_name}")
        lines.append(f"Week: {week_number}")
        lines.append(f"Date: {match.get('date_played', 'TBD')}")
        lines.append(f"Course: {course_name}")
        lines.append("")
        
        # Team headers
        lines.append(f"{team1['name']:^40}|{team2['name']:^40}")
        lines.append("-" * 80)
        
        # Player info with handicaps
        p1_name = p1_1['name'] if p1_1 else "Unknown"
        p2_name = p1_2['name'] if p1_2 else "Unknown"
        p3_name = p2_1['name'] if p2_1 else "Unknown"
        p4_name = p2_2['name'] if p2_2 else "Unknown"
        
        lines.append(f"Player 1: {p1_name:30} (HCP: {h1_p1:5.1f})|Player 1: {p3_name:30} (HCP: {h2_p1:5.1f})")
        lines.append(f"Player 2: {p2_name:30} (HCP: {h1_p2:5.1f})|Player 2: {p4_name:30} (HCP: {h2_p2:5.1f})")
        lines.append("")
        
        # Column headers
        col_header = f"{'Hole':>4} | {'SI':>3} | {'Par':>3} | {p1_name[:10]:>10} | {p2_name[:10]:>10} | {p3_name[:10]:>10} | {p4_name[:10]:>10} | {'Pts':>4} | {'Pts':>4}"
        lines.append(col_header)
        lines.append("-" * 80)
        
        # Hole-by-hole data
        if scores:
            hole_results = scores.get("hole_results", [])
            team1_gross = scores.get("team1_scores", {}).get("player1", {})
            team1_gross2 = scores.get("team1_scores", {}).get("player2", {})
            team2_gross = scores.get("team2_scores", {}).get("player1", {})
            team2_gross2 = scores.get("team2_scores", {}).get("player2", {})
            
            # Build a dict for quick hole result lookup
            hole_results_dict = {h["hole"]: h for h in hole_results} if hole_results else {}
            
            for hole in range(1, 10):
                si = stroke_index[hole - 1] if hole <= len(stroke_index) else hole
                par = hole_pars.get(hole, 4)
                
                # JSON keys are strings, so use str(hole) for lookup
                hole_key = str(hole)
                g1 = team1_gross.get(hole_key, 0)
                g2 = team1_gross2.get(hole_key, 0)
                g3 = team2_gross.get(hole_key, 0)
                g4 = team2_gross2.get(hole_key, 0)
                
                # Get hole result if available
                hr = hole_results_dict.get(hole, {})
                n1 = hr.get("team1_p1_net", g1)  # Default to gross if not available
                n2 = hr.get("team1_p2_net", g2)
                n3 = hr.get("team2_p1_net", g3)
                n4 = hr.get("team2_p2_net", g4)
                
                p1_pts = hr.get("team1_p1_points", 0.0)
                p2_pts = hr.get("team1_p2_points", 0.0)
                p3_pts = hr.get("team2_p1_points", 0.0)
                p4_pts = hr.get("team2_p2_points", 0.0)
                
                # Format scores: show gross with net in parentheses if different
                def fmt(gross, net):
                    return f"{gross}({net})" if gross != net else f"{gross}"
                
                line = f"{hole:>4} | {si:>3} | {par:>3} | {fmt(g1, n1):>10} | {fmt(g2, n2):>10} | {fmt(g3, n3):>10} | {fmt(g4, n4):>10} | {p1_pts:>4.1f} | {p3_pts:>4.1f}"
                lines.append(line)
                line2 = f"{'':>4} | {'':>3} | {'':>3} | {'':>10} | {'':>10} | {'':>10} | {'':>10} | {p2_pts:>4.1f} | {p4_pts:>4.1f}"
                lines.append(line2)
            
            lines.append("-" * 80)
            
            # Totals
            t1_total = scores.get("team1_total", 0)
            t2_total = scores.get("team2_total", 0)
            t1_hole_pts = scores.get("team1_hole_points", 0.0)
            t2_hole_pts = scores.get("team2_hole_points", 0.0)
            t1_bonus = scores.get("team1_bonus", 0.0)
            t2_bonus = scores.get("team2_bonus", 0.0)
            t1_final = scores.get("team1_final_points", 0.0)
            t2_final = scores.get("team2_final_points", 0.0)
            
            lines.append(f"{'TOTAL':>4} | {'':>3} | {'':>3} | {t1_total:>10} | {'':>10} | {t2_total:>10} | {'':>10} | {t1_hole_pts:>4.1f} | {t2_hole_pts:>4.1f}")
            lines.append(f"{'':>4} | {'':>3} | {'':>3} | {'':>10} | {'':>10} | {'':>10} | {'':>10} | {t1_bonus:>4.1f} | {t2_bonus:>4.1f}")
            lines.append(f"{'FINAL':>4} | {'':>3} | {'':>3} | {'':>10} | {'':>10} | {'':>10} | {'':>10} | {t1_final:>4.1f} | {t2_final:>4.1f}")
            lines.append("")
            
            # Winner
            winner = scores.get("winner", "tie")
            if winner == "team1":
                lines.append(f"Winner: {team1['name']}".center(80))
            elif winner == "team2":
                lines.append(f"Winner: {team2['name']}".center(80))
            else:
                lines.append(f"Result: TIE".center(80))
        else:
            lines.append("Scores not yet entered for this match.")
            lines.append("")
            lines.append("Gross scores grid (to be filled):")
            for hole in range(1, 10):
                si = stroke_index[hole - 1] if hole <= len(stroke_index) else hole
                par = hole_pars.get(hole, 4)
                line = f"{hole:>4} | {si:>3} | {par:>3} | {'':>10} | {'':>10} | {'':>10} | {'':>10} | {'':>4} | {'':>4}"
                lines.append(line)
                lines.append(f"{'':>4} | {'':>3} | {'':>3} | {'':>10} | {'':>10} | {'':>10} | {'':>10} | {'':>4} | {'':>4}")
        
        lines.append("=" * 80)
        lines.append("")
        
        return "\n".join(lines)
    
    def print_scorecard(self, match_id: str, blank: bool = True):
        """Print or save a scorecard for the given match.
        
        Args:
            match_id: The match ID
            blank: If True, generate blank scorecard for manual entry. If False, show filled scorecard with scores.
        """
        if blank:
            scorecard_html = self.generate_blank_scorecard_html(match_id)
            title = "Blank Scorecard"
        else:
            scorecard_html = self.generate_scorecard_text(match_id)
            title = "Completed Scorecard"
        
        # Create a dialog to show preview and print options
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("900x700")
        dialog.transient(self.root)
        dialog.grab_set()
        self._center_dialog(dialog)
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=title, style="Title.TLabel")
        title_label.pack(pady=(0, 10))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def save_to_file():
            match = self.dm.matches.get(match_id)
            team1 = self.dm.get_team(match["team1_id"]) if match else {}
            team2 = self.dm.get_team(match["team2_id"]) if match else {}
            week_number = match.get("week_number", 1) if match else 1
            team1_name = team1.get("name", "team1") if team1 else "team1"
            team2_name = team2.get("name", "team2") if team2 else "team2"
            
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                initialfile=f"scorecard_week{week_number}_{team1_name}_vs_{team2_name}.html"
            )
            if filename:
                try:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(scorecard_html)
                    messagebox.showinfo("Success", f"Scorecard saved to {filename}")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}")
        
        def open_in_browser():
            try:
                import tempfile
                import webbrowser
                import os
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
                    temp_file = f.name
                    f.write(scorecard_html)
                
                # Open in default browser
                webbrowser.open(f"file://{os.path.abspath(temp_file)}")
                
                messagebox.showinfo("Browser", "Scorecard opened in your browser.\n\nYou can print from there (Ctrl+P or Cmd+P).")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open browser: {e}\n\nPlease use 'Save to File' as an alternative.")
        
        def print_to_printer():
            try:
                import tempfile
                import webbrowser
                import os
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
                    temp_file = f.name
                    f.write(scorecard_html)
                
                # Open in default browser (user can print from there)
                webbrowser.open(f"file://{os.path.abspath(temp_file)}")
                
                messagebox.showinfo("Print", "Scorecard opened in browser for printing.\n\nUse Ctrl+P (Windows) or Cmd+P (Mac) to print.")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Print Error", f"Could not open browser: {e}\n\nPlease use 'Save to File' as an alternative.")
        
        ttk.Button(btn_frame, text="💾 Save to File", command=save_to_file, style="Accent.TButton").pack(side="left", padx=10)
        ttk.Button(btn_frame, text="🌐 Open in Browser", command=open_in_browser).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="🖨️ Print", command=print_to_printer).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=10)
    
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About", """Golf League Manager
Version 1.0

A desktop application for managing
your golf league season.

Features:
• Player & Team Management
• Course Settings
• Schedule Generation
• Match Score Entry
• Net Score Calculation
• Standings Tracking

2026 Season - Hickory Hills""")

# =============================================================================
# ENTRY POINT
# =============================================================================
def main():
    """Main entry point for the application."""
    root = tk.Tk()
    
    # Set window icon (optional)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    app = GolfLeagueApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()