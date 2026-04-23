#!/usr/bin/env python3
"""
Test script for Scoring Settings functionality.
Tests that custom hole points and bonus points are correctly applied.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from golf_league import DataManager, ScoringEngine

def test_scoring_settings():
    """Test that scoring settings are properly used in calculations."""
    print("Testing Scoring Settings...")
    
    # Initialize data manager
    dm = DataManager()
    
    # Clear any existing data
    dm.players = {}
    dm.teams = {}
    dm.matches = {}
    dm.scores = {}
    dm.handicap_history = {}
    
    # Add test players with zero handicaps to ensure equal net scores
    p1_id = dm.add_player("John Doe", 0.0, phone="555-0101")
    p2_id = dm.add_player("Jane Smith", 0.0, phone="555-0102")
    p3_id = dm.add_player("Bob Johnson", 0.0, phone="555-0103")
    p4_id = dm.add_player("Alice Brown", 0.0, phone="555-0104")
    
    # Create teams
    t1_id = dm.add_team("Team 1", player1_id=p1_id, player2_id=p2_id)
    t2_id = dm.add_team("Team 2", player1_id=p3_id, player2_id=p4_id)
    
    # Create a season
    season_id = dm.create_season("Test Season")
    dm.add_team_to_season(season_id, t1_id)
    dm.add_team_to_season(season_id, t2_id)
    
    # Add a match
    match_id = dm.add_match(season_id, 1, t1_id, t2_id)
    
    # Set custom scoring settings
    # Hole points: 2.0 per hole per matchup (double points)
    # Team bonus: 10.0 (double the standard 5)
    dm.course_settings["hole_points"] = 2.0
    dm.course_settings["team_bonus_points"] = 10.0
    dm.save_all()
    
    print(f"Course settings: {dm.course_settings}")
    
    # Create scoring engine
    scoring = ScoringEngine(dm)
    
    # Prepare sample scores (all pars for simplicity)
    # Hole pars: 4,3,4,3,3,4,3,4,3
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
    
    print("\nMatch Results:")
    print(f"Team 1 Final Points: {results['team1_final_points']}")
    print(f"Team 2 Final Points: {results['team2_final_points']}")
    print(f"Team 1 Hole Points: {results['team1_hole_points']}")
    print(f"Team 2 Hole Points: {results['team2_hole_points']}")
    print(f"Team 1 Bonus: {results['team1_bonus']}")
    print(f"Team 2 Bonus: {results['team2_bonus']}")
    
    # With all scores equal (all ties on each individual matchup):
    # - 9 holes × 2 matchups = 18 individual matchups
    # - Each matchup is a tie -> 0 points (no half points)
    # - Total hole points per team = 0
    # - Combined net scores equal -> 0 bonus (no split)
    # - Total: 0 points each
    
    expected_hole_points_per_team = 0.0  # All ties = 0 points
    expected_bonus_per_team = 0.0  # Tie on net = 0 bonus
    expected_total = 0.0  # 0 + 0
    
    print("\nExpected values (with 2.0 hole points and 10.0 bonus):")
    print(f"  Expected hole points per team: {expected_hole_points_per_team}")
    print(f"  Expected bonus per team: {expected_bonus_per_team}")
    print(f"  Expected total per team: {expected_total}")
    
    # Verify
    assert abs(results['team1_hole_points'] - expected_hole_points_per_team) < 0.01, \
        f"Team 1 hole points mismatch: {results['team1_hole_points']} != {expected_hole_points_per_team}"
    assert abs(results['team2_hole_points'] - expected_hole_points_per_team) < 0.01, \
        f"Team 2 hole points mismatch: {results['team2_hole_points']} != {expected_hole_points_per_team}"
    assert abs(results['team1_bonus'] - expected_bonus_per_team) < 0.01, \
        f"Team 1 bonus mismatch: {results['team1_bonus']} != {expected_bonus_per_team}"
    assert abs(results['team2_bonus'] - expected_bonus_per_team) < 0.01, \
        f"Team 2 bonus mismatch: {results['team2_bonus']} != {expected_bonus_per_team}"
    assert abs(results['team1_final_points'] - expected_total) < 0.01, \
        f"Team 1 final points mismatch: {results['team1_final_points']} != {expected_total}"
    assert abs(results['team2_final_points'] - expected_total) < 0.01, \
        f"Team 2 final points mismatch: {results['team2_final_points']} != {expected_total}"
    
    print("\n* All tests passed!")
    
    # Test with different hole point value
    print("\n\nTesting with different hole point value...")
    dm.course_settings["hole_points"] = 1.5
    dm.save_all()
    
    # Recalculate
    results2 = scoring.calculate_match_scores(
        match_id,
        team1_p1_gross, team1_p2_gross,
        team2_p1_gross, team2_p2_gross
    )
    
    # With all ties on all 18 individual matchups (9 holes × 2 players):
    # Each matchup is a tie -> 0 points
    # Total hole points per team = 0
    # Combined net scores equal -> 0 bonus
    expected_hole_total = 0.0
    expected_bonus = 0.0
    expected_total2 = expected_hole_total + expected_bonus
    
    print(f"Hole point value: {dm.course_settings['hole_points']}")
    print(f"Expected hole points per team: {expected_hole_total}")
    print(f"Team 1 Hole Points: {results2['team1_hole_points']}")
    print(f"Team 2 Hole Points: {results2['team2_hole_points']}")
    print(f"Team 1 Bonus: {results2['team1_bonus']}")
    print(f"Team 2 Bonus: {results2['team2_bonus']}")
    
    assert abs(results2['team1_hole_points'] - expected_hole_total) < 0.01, \
        f"Team 1 hole points mismatch with 1.5 points: {results2['team1_hole_points']} != {expected_hole_total}"
    assert abs(results2['team2_hole_points'] - expected_hole_total) < 0.01, \
        f"Team 2 hole points mismatch with 1.5 points: {results2['team2_hole_points']} != {expected_hole_total}"
    
    print("* Different hole point value test passed!")
    
    print("\n\nAll scoring settings tests completed successfully!")

if __name__ == "__main__":
    test_scoring_settings()