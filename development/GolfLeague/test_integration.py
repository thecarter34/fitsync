#!/usr/bin/env python
"""Integration test for team name generation and team numbering."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from golf_league import DataManager, generate_team_name

print("=== Testing DataManager with auto-generated team names ===\n")

# Create a fresh DataManager
dm = DataManager()

# Clear existing data for clean test
dm.teams = {}
dm.players = {}

# Add test players
p1_id = dm.add_player("Bill Blackburn", 5.0)
p2_id = dm.add_player("Dave Degrasse", 8.0)
p3_id = dm.add_player("Craig Fladten", 4.0)
p4_id = dm.add_player("Matt Fladten", 0.0)

print(f"Added players:")
print(f"  - Bill Blackburn (ID: {p1_id})")
print(f"  - Dave Degrasse (ID: {p2_id})")
print(f"  - Craig Fladten (ID: {p3_id})")
print(f"  - Matt Fladten (ID: {p4_id})")

# Test 1: Auto-generate team name (no name provided)
team1_id = dm.add_team(player1_id=p1_id, player2_id=p2_id)
team1 = dm.get_team(team1_id)
expected_name1 = "Blackburn-Degrasse"
print(f"\nTest 1 - Auto-generated team name:")
print(f"  Expected: {expected_name1}")
print(f"  Actual:   {team1['name']}")
print(f"  Result:   {'PASS' if team1['name'] == expected_name1 else 'FAIL'}")

# Test 2: Custom team name (name provided)
team2_id = dm.add_team(name="Custom Team", player1_id=p3_id, player2_id=p4_id)
team2 = dm.get_team(team2_id)
print(f"\nTest 2 - Custom team name:")
print(f"  Expected: 'Custom Team'")
print(f"  Actual:   '{team2['name']}'")
print(f"  Result:   {'PASS' if team2['name'] == 'Custom Team' else 'FAIL'}")

# Test 3: Get all teams and verify team numbers
print(f"\nTest 3 - Team listing with numbers:")
teams = dm.get_teams()
for idx, team in enumerate(teams, 1):
    p1 = dm.get_player(team["player1_id"])
    p2 = dm.get_player(team["player2_id"])
    print(f"  Team {idx}: {team['name']} - Players: {p1['name']}, {p2['name']}")

print("\nAll tests completed!")
