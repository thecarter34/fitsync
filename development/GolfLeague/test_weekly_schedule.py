#!/usr/bin/env python3
"""
Test script for weekly schedule generation feature.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from golf_league import DataManager, generate_team_name
import json

def test_weekly_schedule():
    """Test the weekly schedule generation."""
    print("Testing weekly schedule generation...")
    
    # Initialize data manager
    dm = DataManager()
    
    # Clear existing data for clean test
    dm.players = {}
    dm.teams = {}
    dm.seasons = {}
    dm.matches = {}
    dm.scores = {}
    dm.handicap_history = {}
    
    # Create test players
    p1_id = dm.add_player("John Smith", 10.0, phone="555-0101")
    p2_id = dm.add_player("Jane Doe", 12.0, phone="555-0102")
    p3_id = dm.add_player("Bob Johnson", 8.0, phone="555-0103")
    p4_id = dm.add_player("Alice Brown", 15.0, phone="555-0104")
    p5_id = dm.add_player("Charlie Davis", 11.0, phone="555-0105")
    p6_id = dm.add_player("Diana Evans", 9.0, phone="555-0106")
    
    print(f"Created 6 players")
    
    # Create teams
    t1_id = dm.add_team("Team 1", player1_id=p1_id, player2_id=p2_id)
    t2_id = dm.add_team("Team 2", player1_id=p3_id, player2_id=p4_id)
    t3_id = dm.add_team("Team 3", player1_id=p5_id, player2_id=p6_id)
    
    print(f"Created 3 teams")
    print(f"Team 1 handicap: {dm.get_team_handicap(t1_id):.1f}")
    print(f"Team 2 handicap: {dm.get_team_handicap(t2_id):.1f}")
    print(f"Team 3 handicap: {dm.get_team_handicap(t3_id):.1f}")
    
    # Create season
    season_id = dm.create_season("Test Season 2026")
    dm.add_team_to_season(season_id, t1_id)
    dm.add_team_to_season(season_id, t2_id)
    dm.add_team_to_season(season_id, t3_id)
    
    season = dm.get_season(season_id)
    print(f"Season created with {len(season['team_ids'])} teams")
    
    # Test 1: Generate Week 1 schedule
    print("\n--- Test 1: Generate Week 1 ---")
    week1_matchups = dm.generate_weekly_schedule(season_id, 1)
    print(f"Generated {len(week1_matchups)} matchups for Week 1")
    for t1, t2 in week1_matchups:
        team1 = dm.get_team(t1)
        team2 = dm.get_team(t2)
        print(f"  {team1['name']} vs {team2['name']}")
    
    # Add Week 1 matches
    for t1, t2 in week1_matchups:
        dm.add_match(season_id, 1, t1, t2)
    print(f"Added {len(week1_matchups)} matches to database")
    
    # Test 2: Generate Week 2 schedule (should not repeat matchups)
    print("\n--- Test 2: Generate Week 2 ---")
    week2_matchups = dm.generate_weekly_schedule(season_id, 2)
    print(f"Generated {len(week2_matchups)} matchups for Week 2")
    for t1, t2 in week2_matchups:
        team1 = dm.get_team(t1)
        team2 = dm.get_team(t2)
        print(f"  {team1['name']} vs {team2['name']}")
    
    # Add Week 2 matches
    for t1, t2 in week2_matchups:
        dm.add_match(season_id, 2, t1, t2)
    print(f"Added {len(week2_matchups)} matches to database")
    
    # Test 3: Generate Week 3 schedule (should have 1 matchup left for 3 teams)
    print("\n--- Test 3: Generate Week 3 ---")
    week3_matchups = dm.generate_weekly_schedule(season_id, 3)
    print(f"Generated {len(week3_matchups)} matchups for Week 3")
    for t1, t2 in week3_matchups:
        team1 = dm.get_team(t1)
        team2 = dm.get_team(t2)
        print(f"  {team1['name']} vs {team2['name']}")
    
    # Add Week 3 matches
    for t1, t2 in week3_matchups:
        dm.add_match(season_id, 3, t1, t2)
    print(f"Added {len(week3_matchups)} matches to database")
    
    # Verify all matches in database
    all_matches = dm.get_matches_for_season(season_id)
    print(f"\nTotal matches in database: {len(all_matches)}")
    for match in all_matches:
        team1 = dm.get_team(match["team1_id"])
        team2 = dm.get_team(match["team2_id"])
        print(f"  Week {match['week_number']}: {team1['name']} vs {team2['name']}")
    
    # Test 4: Test with handicap changes
    print("\n--- Test 4: Handicap changes ---")
    # Update a player's handicap
    dm.update_player(p1_id, handicap=14.0)
    print(f"Updated {dm.get_player(p1_id)['name']} handicap to 14.0")
    
    # Get team handicap after update
    new_hcp = dm.get_team_handicap(t1_id)
    print(f"Team 1 new handicap: {new_hcp:.1f}")
    
    # Generate another week (week 4) - should use current handicaps
    week4_matchups = dm.generate_weekly_schedule(season_id, 4)
    print(f"Generated {len(week4_matchups)} matchups for Week 4")
    for t1, t2 in week4_matchups:
        team1 = dm.get_team(t1)
        team2 = dm.get_team(t2)
        h1 = dm.get_team_handicap(t1)
        h2 = dm.get_team_handicap(t2)
        print(f"  {team1['name']} (HCP: {h1:.1f}) vs {team2['name']} (HCP: {h2:.1f})")
    
    print("\nAll tests completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_weekly_schedule()
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
