"""
Scoring Engine Module
Handles all scoring calculations for the golf league.
No UI dependencies - pure Python business logic.
"""

from typing import Dict, List, Optional
from data_manager import DataManager, DEFAULT_STROKE_INDEX, HOLE_PARS


class ScoringEngine:
    """Handles all scoring calculations for the golf league."""

    def __init__(self, data_manager: DataManager):
        self.dm = data_manager

    def calculate_match_scores(self, match_id: str,
                               team1_p1_gross: Dict[int, int], team1_p2_gross: Dict[int, int],
                               team2_p1_gross: Dict[int, int], team2_p2_gross: Dict[int, int]) -> Dict:
        """
        Calculate all scores for a match using match-play scoring.

        Key feature: Players are paired by handicap - higher vs higher, lower vs lower.
        This ensures fair competition within each team match.
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

        # --- Pair players by handicap: higher vs higher, lower vs lower ---
        # Create sorted lists for each team: (player_id, handicap, gross_scores, original_label)
        team1_players = [
            (team1["player1_id"], h1_p1, team1_p1_gross, "player1"),
            (team1["player2_id"], h1_p2, team1_p2_gross, "player2")
        ]
        team1_players.sort(key=lambda x: x[1], reverse=True)  # Higher handicap first

        team2_players = [
            (team2["player1_id"], h2_p1, team2_p1_gross, "player1"),
            (team2["player2_id"], h2_p2, team2_p2_gross, "player2")
        ]
        team2_players.sort(key=lambda x: x[1], reverse=True)  # Higher handicap first

        # Pair: highest from team1 vs highest from team2, lowest vs lowest
        (t1_h_id, h1_h, t1_h_gross, _) = team1_players[0]
        (t1_l_id, h1_l, t1_l_gross, _) = team1_players[1]
        (t2_h_id, h2_h, t2_h_gross, _) = team2_players[0]
        (t2_l_id, h2_l, t2_l_gross, _) = team2_players[1]

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

        # Determine which holes are fully completed (all 4 players have non-zero scores)
        completed_holes = set()
        
        # Get all hole numbers that appear in any scores dict
        all_holes = set()
        for scores_dict in [t1_h_gross, t1_l_gross, t2_h_gross, t2_l_gross]:
            all_holes.update(scores_dict.keys())
        
        # A hole is complete only if all 4 players have a non-zero score for it
        for hole in all_holes:
            t1_h_score = t1_h_gross.get(hole, 0)
            t1_l_score = t1_l_gross.get(hole, 0)
            t2_h_score = t2_h_gross.get(hole, 0)
            t2_l_score = t2_l_gross.get(hole, 0)
            
            # All four must be > 0 for the hole to be considered complete
            if t1_h_score > 0 and t1_l_score > 0 and t2_h_score > 0 and t2_l_score > 0:
                completed_holes.add(hole)
        
        # Sort holes in order
        completed_holes = sorted(completed_holes)

        # If no holes have scores, return empty results
        if not completed_holes:
            return {
                "match_id": match_id,
                "hole_results": [],
                "team1_scores": {"player1": team1_p1_gross, "player2": team1_p2_gross},
                "team2_scores": {"player1": team2_p1_gross, "player2": team2_p2_gross},
                "team1_hole_points": 0.0,
                "team2_hole_points": 0.0,
                "team1_bonus": 0.0,
                "team2_bonus": 0.0,
                "team1_total": 0,
                "team2_total": 0,
                "team1_final_points": 0.0,
                "team2_final_points": 0.0,
                "winner": "tie"  # Both teams have 0 points, so it's a tie
            }

        # Process only completed holes
        for hole in completed_holes:
            si = stroke_index[hole - 1] if hole <= len(stroke_index) else hole

            # Get gross scores for this hole
            t1_h_gross_hole = t1_h_gross.get(hole, 0)
            t1_l_gross_hole = t1_l_gross.get(hole, 0)
            t2_h_gross_hole = t2_h_gross.get(hole, 0)
            t2_l_gross_hole = t2_l_gross.get(hole, 0)

            # Higher handicap matchup
            if h1_h > h2_h:
                diff = int(h1_h) - int(h2_h)
                t1_h_net = t1_h_gross_hole - (1 if si <= diff else 0)
                t2_h_net = t2_h_gross_hole
            elif h2_h > h1_h:
                diff = int(h2_h) - int(h1_h)
                t2_h_net = t2_h_gross_hole - (1 if si <= diff else 0)
                t1_h_net = t1_h_gross_hole
            else:
                t1_h_net = t1_h_gross_hole
                t2_h_net = t2_h_gross_hole

            # Lower handicap matchup
            if h1_l > h2_l:
                diff = int(h1_l) - int(h2_l)
                t1_l_net = t1_l_gross_hole - (1 if si <= diff else 0)
                t2_l_net = t2_l_gross_hole
            elif h2_l > h1_l:
                diff = int(h2_l) - int(h1_l)
                t2_l_net = t2_l_gross_hole - (1 if si <= diff else 0)
                t1_l_net = t1_l_gross_hole
            else:
                t1_l_net = t1_l_gross_hole
                t2_l_net = t2_l_gross_hole

            # Accumulate net totals for team bonus
            team1_net_total += t1_h_net + t1_l_net
            team2_net_total += t2_h_net + t2_l_net

            # Calculate hole points for each matchup (with ties - each gets half point)
            team1_points_this_hole = 0.0
            team2_points_this_hole = 0.0

            # Higher matchup
            if t1_h_net < t2_h_net:
                team1_points_this_hole += hole_point_value
            elif t2_h_net < t1_h_net:
                team2_points_this_hole += hole_point_value
            else:  # tie
                team1_points_this_hole += hole_point_value / 2
                team2_points_this_hole += hole_point_value / 2

            # Lower matchup
            if t1_l_net < t2_l_net:
                team1_points_this_hole += hole_point_value
            elif t2_l_net < t1_l_net:
                team2_points_this_hole += hole_point_value
            else:  # tie
                team1_points_this_hole += hole_point_value / 2
                team2_points_this_hole += hole_point_value / 2

            # Accumulate hole points
            team1_hole_points += team1_points_this_hole
            team2_hole_points += team2_points_this_hole

            # Map results back to original player labels (player1, player2) with tie handling
            # Team 1
            if t1_h_id == team1["player1_id"]:
                team1_p1_net = t1_h_net
                team1_p2_net = t1_l_net
                # Higher matchup points for player1
                if t1_h_net < t2_h_net:
                    team1_p1_points = hole_point_value
                elif t2_h_net < t1_h_net:
                    team1_p1_points = 0.0
                else:
                    team1_p1_points = hole_point_value / 2
                # Lower matchup points for player2
                if t1_l_net < t2_l_net:
                    team1_p2_points = hole_point_value
                elif t2_l_net < t1_l_net:
                    team1_p2_points = 0.0
                else:
                    team1_p2_points = hole_point_value / 2
            else:
                team1_p1_net = t1_l_net
                team1_p2_net = t1_h_net
                # Lower matchup points for player1
                if t1_l_net < t2_l_net:
                    team1_p1_points = hole_point_value
                elif t2_l_net < t1_l_net:
                    team1_p1_points = 0.0
                else:
                    team1_p1_points = hole_point_value / 2
                # Higher matchup points for player2
                if t1_h_net < t2_h_net:
                    team1_p2_points = hole_point_value
                elif t2_h_net < t1_h_net:
                    team1_p2_points = 0.0
                else:
                    team1_p2_points = hole_point_value / 2

            # Team 2
            if t2_h_id == team2["player1_id"]:
                team2_p1_net = t2_h_net
                team2_p2_net = t2_l_net
                # Higher matchup points for player1
                if t2_h_net < t1_h_net:
                    team2_p1_points = hole_point_value
                elif t1_h_net < t2_h_net:
                    team2_p1_points = 0.0
                else:
                    team2_p1_points = hole_point_value / 2
                # Lower matchup points for player2
                if t2_l_net < t1_l_net:
                    team2_p2_points = hole_point_value
                elif t1_l_net < t2_l_net:
                    team2_p2_points = 0.0
                else:
                    team2_p2_points = hole_point_value / 2
            else:
                team2_p1_net = t2_l_net
                team2_p2_net = t2_h_net
                # Lower matchup points for player1
                if t2_l_net < t1_l_net:
                    team2_p1_points = hole_point_value
                elif t1_l_net < t2_l_net:
                    team2_p1_points = 0.0
                else:
                    team2_p1_points = hole_point_value / 2
                # Higher matchup points for player2
                if t2_h_net < t1_h_net:
                    team2_p2_points = hole_point_value
                elif t1_h_net < t2_h_net:
                    team2_p2_points = 0.0
                else:
                    team2_p2_points = hole_point_value / 2

            hole_results.append({
                "hole": hole,
                "stroke_index": si,
                "team1_p1_net": team1_p1_net,
                "team1_p2_net": team1_p2_net,
                "team2_p1_net": team2_p1_net,
                "team2_p2_net": team2_p2_net,
                "team1_p1_points": team1_p1_points,
                "team1_p2_points": team1_p2_points,
                "team2_p1_points": team2_p1_points,
                "team2_p2_points": team2_p2_points,
                "team1_points": team1_points_this_hole,
                "team2_points": team2_points_this_hole
            })

        # Team bonus based on combined NET scores (not gross)
        # Only award bonus if all 9 holes are completed
        bonus_setting = self.dm.course_settings.get("team_bonus_points", 5.0)
        try:
            bonus_points = float(bonus_setting)
        except (ValueError, TypeError):
            bonus_points = 5.0

        # Check if all 9 holes have been completed
        all_holes_completed = len(completed_holes) == 9

        if all_holes_completed:
            if team1_net_total < team2_net_total:
                t1_bonus = bonus_points
                t2_bonus = 0.0
            elif team2_net_total < team1_net_total:
                t1_bonus = 0.0
                t2_bonus = bonus_points
            else:
                t1_bonus = bonus_points / 2
                t2_bonus = bonus_points / 2
        else:
            # No bonus for incomplete rounds
            t1_bonus = 0.0
            t2_bonus = 0.0

        team1_final = team1_hole_points + t1_bonus
        team2_final = team2_hole_points + t2_bonus

        return {
            "match_id": match_id,
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
" " 
