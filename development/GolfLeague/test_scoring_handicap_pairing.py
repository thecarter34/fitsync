#!/usr/bin/env python3
"""
Test script for the new handicap-based player pairing in scoring engine.
This verifies that higher handicap players play against higher handicap players,
and lower against lower.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from golf_league import DataManager, ScoringEngine
import json

def test_handicap_pairing():
    """Test that players are paired correctly by handicap."""
    print("Testing handicap-based player pairing...")

    # Initialize data manager
    dm = DataManager()

    # Clear existing data for clean test
    dm.players = {}
    dm.teams = {}
    dm.seasons = {}
    dm.matches = {}
    dm.scores = {}
    dm.handicap_history = {}

    # Create players with distinct handicaps
    p1_id = dm.add_player("Player A", 5.0)   # Low handicap
    p2_id = dm.add_player("Player B", 8.0)   # Medium-low
    p3_id = dm.add_player("Player C", 12.0)  # Medium-high
    p4_id = dm.add_player("Player D", 18.0)  # High handicap

    print(f"Created 4 players with handicaps: 5, 8, 12, 18")

    # Create teams with mixed handicaps
    # Team 1: 5 and 18 (very different)
    t1_id = dm.add_team("Team 1", player1_id=p1_id, player2_id=p4_id)
    # Team 2: 8 and 12 (closer but still different)
    t2_id = dm.add_team("Team 2", player1_id=p2_id, player2_id=p3_id)

    print(f"Team 1: Players with handicaps {dm.get_player(p1_id)['handicap']} and {dm.get_player(p4_id)['handicap']}")
    print(f"Team 2: Players with handicaps {dm.get_player(p2_id)['handicap']} and {dm.get_player(p3_id)['handicap']}")

    # Create season
    season_id = dm.create_season("Test Season 2026")
    dm.add_team_to_season(season_id, t1_id)
    dm.add_team_to_season(season_id, t2_id)

    # Create a match between these teams
    match_id = dm.add_match(season_id, 1, t1_id, t2_id)

    print(f"Created match: {match_id}")

    # Simulate score submission with dummy gross scores
    # All players score 36 (par) on all holes for simplicity
    team1_p1_gross = {h: 36 for h in range(1, 10)}
    team1_p2_gross = {h: 36 for h in range(1, 10)}
    team2_p1_gross = {h: 36 for h in range(1, 10)}
    team2_p2_gross = {h: 36 for h in range(1, 10)}

    # Calculate scores using the scoring engine
    se = ScoringEngine(dm)
    results = se.calculate_match_scores(
        match_id,
        team1_p1_gross, team1_p2_gross,
        team2_p1_gross, team2_p2_gross
    )

    if not results:
        print("ERROR: Failed to calculate scores")
        return False

    print("\nMatch Results:")
    print(f"Team 1 final points: {results['team1_final_points']}")
    print(f"Team 2 final points: {results['team2_final_points']}")
    print(f"Winner: {results['winner']}")

    # Verify that the pairing was correct
    # Since all gross scores are equal (36), the net scores will differ based on strokes
    # The higher handicap players should get strokes, making their net scores lower (better)
    print("\nNet scores per hole (first hole shown):")
    hole1 = results['hole_results'][0]
    print(f"Team1 Player1 net: {hole1['team1_p1_net']}")
    print(f"Team1 Player2 net: {hole1['team1_p2_net']}")
    print(f"Team2 Player1 net: {hole1['team2_p1_net']}")
    print(f"Team2 Player2 net: {hole1['team2_p2_net']}")

    # Check that the higher handicap players (18 and 12) are paired together
    # and lower handicap players (5 and 8) are paired together
    # This means the matchup between 18 vs 12 and 5 vs 8

    # Get the handicaps
    h1_p1 = dm.get_player_recent_handicap(p1_id, season_id, 1)  # 5
    h1_p2 = dm.get_player_recent_handicap(p4_id, season_id, 1)  # 18
    h2_p1 = dm.get_player_recent_handicap(p2_id, season_id, 1)  # 8
    h2_p2 = dm.get_player_recent_handicap(p3_id, season_id, 1)  # 12

    print(f"\nHandicaps: Team1 P1:{h1_p1}, P2:{h1_p2} | Team2 P1:{h2_p1}, P2:{h2_p2}")

    # The higher players should be: Team1 P2 (18) and Team2 P2 (12)
    # The lower players should be: Team1 P1 (5) and Team2 P1 (8)

    # Verify that in the results, the higher vs higher matchup occurred
    # We can check by looking at the stroke allocation pattern
    # Higher handicap players should receive strokes on more holes

    # Count how many strokes each player received across all holes
    strokes_received = {
        'team1_p1': 0,
        'team1_p2': 0,
        'team2_p1': 0,
        'team2_p2': 0
    }

    for hole_result in results['hole_results']:
        # If net < gross, player received a stroke
        if hole_result['team1_p1_net'] < 36:
            strokes_received['team1_p1'] += 1
        if hole_result['team1_p2_net'] < 36:
            strokes_received['team1_p2'] += 1
        if hole_result['team2_p1_net'] < 36:
            strokes_received['team2_p1'] += 1
        if hole_result['team2_p2_net'] < 36:
            strokes_received['team2_p2'] += 1

    print("\nStrokes received per player:")
    for player, count in strokes_received.items():
        print(f"  {player}: {count} holes")

    # Verify the pairing logic:
    # - Team1: P2 (18) is higher than P1 (5), so P2 should receive strokes, P1 should not
    # - Team2: P1 (8) is lower than P2 (12), so P1 should receive strokes, P2 should not
    # (Note: In the actual matchups, 18 vs 12 means 18 gets strokes, 12 doesn't;
    #        5 vs 8 means 8 gets strokes, 5 doesn't)

    success = True

    if strokes_received['team1_p2'] > strokes_received['team1_p1']:
        print("[OK] Team1: Higher handicap player (18) received strokes, lower (5) did not")
    else:
        print("[FAIL] Team1: Expected higher handicap to receive strokes")
        success = False

    if strokes_received['team2_p1'] > strokes_received['team2_p2']:
        print("[OK] Team2: Lower handicap player (8) received strokes against lower opponent (5), higher (12) did not")
    else:
        print("[FAIL] Team2: Expected lower handicap player to receive strokes against lower opponent")
        success = False

    if success:
        print("\n[SUCCESS] Handicap pairing is working correctly!")
    else:
        print("\n[FAILURE] Handicap pairing has issues")
        return False

    print("\nAll tests completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_handicap_pairing()
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
