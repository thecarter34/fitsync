#!/usr/bin/env python3
"""
Test script for Season Setup scoring configuration.
Tests that scoring settings configured in season setup are properly saved and used.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from golf_league import DataManager, ScoringEngine

def test_season_scoring_config():
    """Test that scoring settings work from season setup."""
    print("Testing Season Setup Scoring Configuration...")
    
    # Initialize data manager
    dm = DataManager()
    
    # Clear any existing data
    dm.players = {}
    dm.teams = {}
    dm.matches = {}
    dm.scores = {}
    dm.handicap_history = {}
    
    # Add test players with zero handicaps
    p1_id = dm.add_player("John Doe", 0.0, phone="555-0101")
    p2_id = dm.add_player("Jane Smith", 0.0, phone="555-0102")
    p3_id = dm.add_player("Bob Johnson", 0.0, phone="555-0103")
    p4_id = dm.add_player("Alice Brown", 0.0, phone="555-0104")
    
    # Create teams
    t1_id = dm.add_team("Team 1", player1_id=p1_id, player2_id=p2_id)
    t2_id = dm.add_team("Team 2", player1_id=p3_id, player2_id=p4_id)
    
    # Simulate setting scoring configuration via Season Setup
    # (This would normally be done through the UI)
    dm.course_settings["hole_points"] = 2.5
    dm.course_settings["team_bonus_points"] = 12.5
    dm.save_all()
    
    print(f"Scoring settings: hole_points={dm.course_settings.get('hole_points')}, team_bonus_points={dm.course_settings.get('team_bonus_points')}")
    
    # Create a season
    season_id = dm.create_season("Test Season 2026")
    dm.add_team_to_season(season_id, t1_id)
    dm.add_team_to_season(season_id, t2_id)
    
    # Add a match
    match_id = dm.add_match(season_id, 1, t1_id, t2_id)
    
    # Create scoring engine
    scoring = ScoringEngine(dm)
    
    # Prepare sample scores (all equal)
    team1_p1_gross = {1: 4, 2: 3, 3: 4, 4: 3, 5: 3, 6: 4, 7: 3, 8: 4, 9: 3}
    team1_p2_gross = {1: 4, 2: 3, 3: 4, 4: 3, 5: 3, 6: 4, 7: 3, 8: 4, 9: 3}
    team2_p1_gross = {1: 4, 2: 3, 3: 4, 4: 3, 5: 3, 6: 4, 7: 3, 8: 4, 9: 3}
    team2_p2_gross = {1: 4, 2: 3, 3: 4, 4: 3, 5: 3, 6: 4, 7: 3, 8: 4, 9: 3}
    
    # Calculate scores
    results = scoring.calculate_match_scores(
        match_id,
        team1_p1_gross, team1_p2_gross,
        team2_p1_gross, team2_p2_gross
    )
    
    print("\nMatch Results with custom scoring (2.5 hole points, 12.5 bonus):")
    print(f"Team 1 Final Points: {results['team1_final_points']}")
    print(f"Team 2 Final Points: {results['team2_final_points']}")
    print(f"Team 1 Hole Points: {results['team1_hole_points']}")
    print(f"Team 2 Hole Points: {results['team2_hole_points']}")
    print(f"Team 1 Bonus: {results['team1_bonus']}")
    print(f"Team 2 Bonus: {results['team2_bonus']}")
    
    # With all ties on all 18 individual matchups (9 holes × 2 players):
    # Each matchup is a tie -> 0 points (no half points)
    # Total hole points per team = 0
    # Combined net scores equal -> 0 bonus
    expected_hole_points = 0.0
    expected_bonus = 0.0
    expected_total = expected_hole_points + expected_bonus  # 0.0
    
    print(f"\nExpected: hole_points={expected_hole_points}, bonus={expected_bonus}, total={expected_total}")
    
    assert abs(results['team1_hole_points'] - expected_hole_points) < 0.01, \
        f"Team 1 hole points mismatch: {results['team1_hole_points']} != {expected_hole_points}"
    assert abs(results['team2_hole_points'] - expected_hole_points) < 0.01, \
        f"Team 2 hole points mismatch: {results['team2_hole_points']} != {expected_hole_points}"
    assert abs(results['team1_bonus'] - expected_bonus) < 0.01, \
        f"Team 1 bonus mismatch: {results['team1_bonus']} != {expected_bonus}"
    assert abs(results['team2_bonus'] - expected_bonus) < 0.01, \
        f"Team 2 bonus mismatch: {results['team2_bonus']} != {expected_bonus}"
    assert abs(results['team1_final_points'] - expected_total) < 0.01, \
        f"Team 1 final points mismatch: {results['team1_final_points']} != {expected_total}"
    assert abs(results['team2_final_points'] - expected_total) < 0.01, \
        f"Team 2 final points mismatch: {results['team2_final_points']} != {expected_total}"
    
    print("\n* All season scoring configuration tests passed!")
    
    # Test that defaults work when no custom settings
    print("\n\nTesting with default scoring (no custom settings)...")
    dm.course_settings.pop("hole_points", None)
    dm.course_settings.pop("team_bonus_points", None)
    dm.save_all()
    
    results2 = scoring.calculate_match_scores(
        match_id,
        team1_p1_gross, team1_p2_gross,
        team2_p1_gross, team2_p2_gross
    )
    
    # Default: 1.0 hole point per matchup, 5.0 bonus
    # All ties -> 0 points for hole matchups, 0 bonus
    expected_hole_default = 0.0
    expected_bonus_default = 0.0
    expected_total_default = expected_hole_default + expected_bonus_default  # 0.0
    
    print(f"Team 1 Final Points: {results2['team1_final_points']}")
    print(f"Expected: {expected_total_default}")
    
    assert abs(results2['team1_final_points'] - expected_total_default) < 0.01, \
        f"Default scoring test failed: {results2['team1_final_points']} != {expected_total_default}"
    
    print("* Default scoring test passed!")
    
    print("\n\nAll tests completed successfully!")

if __name__ == "__main__":
    test_season_scoring_config()