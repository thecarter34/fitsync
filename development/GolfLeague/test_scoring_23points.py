#!/usr/bin/env python3
"""
Test script to verify that the scoring engine awards exactly 23 points per match
and properly handles ties (0.5 points per player matchup, 2.5 team bonus on tie).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from golf_league import DataManager, ScoringEngine
import json

def test_total_points_always_23():
    """Test that every match results in exactly 23 total points awarded."""
    print("Testing that total points per match equals 23...")
    
    dm = DataManager()
    
    # Clear existing data
    dm.players = {}
    dm.teams = {}
    dm.seasons = {}
    dm.matches = {}
    dm.scores = {}
    dm.handicap_history = {}
    
    # Create players
    p1_id = dm.add_player("Player 1", 10.0)
    p2_id = dm.add_player("Player 2", 12.0)
    p3_id = dm.add_player("Player 3", 14.0)
    p4_id = dm.add_player("Player 4", 16.0)
    
    # Create teams
    t1_id = dm.add_team("Team 1", player1_id=p1_id, player2_id=p2_id)
    t2_id = dm.add_team("Team 2", player1_id=p3_id, player2_id=p4_id)
    
    # Create season and match
    season_id = dm.create_season("Test Season")
    dm.add_team_to_season(season_id, t1_id)
    dm.add_team_to_season(season_id, t2_id)
    match_id = dm.add_match(season_id, 1, t1_id, t2_id)
    
    se = ScoringEngine(dm)
    
    # Test various score scenarios
    test_cases = [
        {
            "name": "All equal scores (all ties)",
            "team1_p1": {h: 36 for h in range(1, 10)},
            "team1_p2": {h: 36 for h in range(1, 10)},
            "team2_p1": {h: 36 for h in range(1, 10)},
            "team2_p2": {h: 36 for h in range(1, 10)},
        },
        {
            "name": "Team 1 wins all matchups",
            "team1_p1": {h: 30 for h in range(1, 10)},
            "team1_p2": {h: 31 for h in range(1, 10)},
            "team2_p1": {h: 40 for h in range(1, 10)},
            "team2_p2": {h: 41 for h in range(1, 10)},
        },
        {
            "name": "Team 2 wins all matchups",
            "team1_p1": {h: 40 for h in range(1, 10)},
            "team1_p2": {h: 41 for h in range(1, 10)},
            "team2_p1": {h: 30 for h in range(1, 10)},
            "team2_p2": {h: 31 for h in range(1, 10)},
        },
        {
            "name": "Mixed results",
            "team1_p1": {h: 35 for h in range(1, 10)},
            "team1_p2": {h: 37 for h in range(1, 10)},
            "team2_p1": {h: 36 for h in range(1, 10)},
            "team2_p2": {h: 38 for h in range(1, 10)},
        },
    ]
    
    all_passed = True
    for tc in test_cases:
        results = se.calculate_match_scores(
            match_id,
            tc["team1_p1"], tc["team1_p2"],
            tc["team2_p1"], tc["team2_p2"]
        )
        
        total_points = results['team1_final_points'] + results['team2_final_points']
        print(f"\n{tc['name']}:")
        print(f"  Team 1: {results['team1_final_points']} points")
        print(f"  Team 2: {results['team2_final_points']} points")
        print(f"  Total: {total_points} points")
        
        # Verify total is exactly 23
        if abs(total_points - 23.0) < 0.001:  # Allow for floating point
            print(f"  [PASS] Total = 23")
        else:
            print(f"  [FAIL] Expected 23, got {total_points}")
            all_passed = False
            
        # Verify hole points sum to 18 (9 holes × 2 points per hole)
        hole_points_total = results['team1_hole_points'] + results['team2_hole_points']
        if abs(hole_points_total - 18.0) < 0.001:
            print(f"  [PASS] Hole points total = 18")
        else:
            print(f"  [FAIL] Hole points total = {hole_points_total}, expected 18")
            all_passed = False
            
        # Verify bonus points sum to 5
        bonus_total = results['team1_bonus'] + results['team2_bonus']
        if abs(bonus_total - 5.0) < 0.001:
            print(f"  [PASS] Bonus points total = 5")
        else:
            print(f"  [FAIL] Bonus points total = {bonus_total}, expected 5")
            all_passed = False
    
    return all_passed

def test_tie_scenarios():
    """Test specific tie scenarios to ensure proper point splitting."""
    print("\n\nTesting tie scenarios...")
    
    dm = DataManager()
    dm.players = {}
    dm.teams = {}
    dm.seasons = {}
    dm.matches = {}
    dm.scores = {}
    dm.handicap_history = {}
    
    # Use equal handicaps for all players to ensure net scores are equal when gross scores are equal
    p1_id = dm.add_player("Player 1", 10.0)
    p2_id = dm.add_player("Player 2", 10.0)
    p3_id = dm.add_player("Player 3", 10.0)
    p4_id = dm.add_player("Player 4", 10.0)
    
    t1_id = dm.add_team("Team 1", player1_id=p1_id, player2_id=p2_id)
    t2_id = dm.add_team("Team 2", player1_id=p3_id, player2_id=p4_id)
    
    season_id = dm.create_season("Test Season")
    dm.add_team_to_season(season_id, t1_id)
    dm.add_team_to_season(season_id, t2_id)
    match_id = dm.add_match(season_id, 1, t1_id, t2_id)
    
    se = ScoringEngine(dm)
    
    # Test case: All net scores equal on every hole
    # Both players on each matchup shoot same net score
    # Each player should get 0.5 points per hole
    # Team net totals equal, so bonus split 2.5 each
    print("\nScenario: All net scores tied on every hole")
    team1_p1_gross = {h: 36 for h in range(1, 10)}
    team1_p2_gross = {h: 36 for h in range(1, 10)}
    team2_p1_gross = {h: 36 for h in range(1, 10)}
    team2_p2_gross = {h: 36 for h in range(1, 10)}
    
    results = se.calculate_match_scores(
        match_id,
        team1_p1_gross, team1_p2_gross,
        team2_p1_gross, team2_p2_gross
    )
    
    print(f"Team 1 final: {results['team1_final_points']}")
    print(f"Team 2 final: {results['team2_final_points']}")
    print(f"Total: {results['team1_final_points'] + results['team2_final_points']}")
    
    # Check individual hole results
    hole1 = results['hole_results'][0]
    print(f"\nHole 1 breakdown:")
    print(f"  team1_p1_points: {hole1['team1_p1_points']}")
    print(f"  team1_p2_points: {hole1['team1_p2_points']}")
    print(f"  team2_p1_points: {hole1['team2_p1_points']}")
    print(f"  team2_p2_points: {hole1['team2_p2_points']}")
    print(f"  team1_points: {hole1['team1_points']}")
    print(f"  team2_points: {hole1['team2_points']}")
    
    # Each player should get 0.5 points per hole
    expected_per_player = 0.5
    all_passed = True
    
    if abs(hole1['team1_p1_points'] - expected_per_player) < 0.001:
        print(f"  [PASS] team1_p1 gets {expected_per_player} points (tie)")
    else:
        print(f"  [FAIL] team1_p1 gets {hole1['team1_p1_points']}, expected {expected_per_player}")
        all_passed = False
        
    if abs(hole1['team1_p2_points'] - expected_per_player) < 0.001:
        print(f"  [PASS] team1_p2 gets {expected_per_player} points (tie)")
    else:
        print(f"  [FAIL] team1_p2 gets {hole1['team1_p2_points']}, expected {expected_per_player}")
        all_passed = False
        
    if abs(hole1['team2_p1_points'] - expected_per_player) < 0.001:
        print(f"  [PASS] team2_p1 gets {expected_per_player} points (tie)")
    else:
        print(f"  [FAIL] team2_p1 gets {hole1['team2_p1_points']}, expected {expected_per_player}")
        all_passed = False
        
    if abs(hole1['team2_p2_points'] - expected_per_player) < 0.001:
        print(f"  [PASS] team2_p2 gets {expected_per_player} points (tie)")
    else:
        print(f"  [FAIL] team2_p2 gets {hole1['team2_p2_points']}, expected {expected_per_player}")
        all_passed = False
    
    # Team points per hole should be 2.0 total (1.0 + 1.0) because there are 2 matchups per hole
    if abs(hole1['team1_points'] + hole1['team2_points'] - 2.0) < 0.001:
        print(f"  [PASS] Team points per hole sum to 2.0")
    else:
        print(f"  [FAIL] Team points sum to {hole1['team1_points'] + hole1['team2_points']}, expected 2.0")
        all_passed = False
    
    # Bonus should be split
    if abs(results['team1_bonus'] - 2.5) < 0.001 and abs(results['team2_bonus'] - 2.5) < 0.001:
        print(f"  [PASS] Bonus split: 2.5 each")
    else:
        print(f"  [FAIL] Bonus: Team1={results['team1_bonus']}, Team2={results['team2_bonus']}, expected 2.5 each")
        all_passed = False
    
    # Final total should be 23
    total = results['team1_final_points'] + results['team2_final_points']
    if abs(total - 23.0) < 0.001:
        print(f"  [PASS] Total points = 23")
    else:
        print(f"  [FAIL] Total = {total}, expected 23")
        all_passed = False
    
    return all_passed

if __name__ == "__main__":
    try:
        test1_passed = test_total_points_always_23()
        test2_passed = test_tie_scenarios()
        
        if test1_passed and test2_passed:
            print("\n" + "="*50)
            print("ALL TESTS PASSED!")
            sys.exit(0)
        else:
            print("\n" + "="*50)
            print("SOME TESTS FAILED!")
            sys.exit(1)
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
