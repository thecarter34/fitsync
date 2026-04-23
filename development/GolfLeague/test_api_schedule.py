#!/usr/bin/env python3
"""Test the schedule generation API"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_schedule_generation():
    print("Testing schedule generation API...")

    # Create a season
    resp = requests.post(f"{BASE_URL}/api/seasons", json={'name': 'Test Season 2026'})
    if resp.status_code != 200:
        print(f"Failed to create season: {resp.text}")
        return False
    season = resp.json()
    season_id = season['id']
    print(f"Created season: {season_id}")

    # Create 4 players
    players = []
    for name, handicap in [("Player A", 5.0), ("Player B", 8.0), ("Player C", 12.0), ("Player D", 18.0)]:
        resp = requests.post(f"{BASE_URL}/api/players", json={'name': name, 'handicap': handicap})
        if resp.status_code == 200:
            players.append(resp.json())
        else:
            print(f"Failed to create player {name}: {resp.text}")
            return False
    print(f"Created {len(players)} players")

    # Create 2 teams
    resp = requests.post(f"{BASE_URL}/api/teams", json={
        'name': 'Team 1',
        'player1_id': players[0]['id'],
        'player2_id': players[3]['id']
    })
    if resp.status_code != 200:
        print(f"Failed to create team 1: {resp.text}")
        return False
    team1 = resp.json()

    resp = requests.post(f"{BASE_URL}/api/teams", json={
        'name': 'Team 2',
        'player1_id': players[1]['id'],
        'player2_id': players[2]['id']
    })
    if resp.status_code != 200:
        print(f"Failed to create team 2: {resp.text}")
        return False
    team2 = resp.json()
    print(f"Created teams: {team1['id']}, {team2['id']}")

    # Add teams to season
    requests.post(f"{BASE_URL}/api/seasons/{season_id}/teams/{team1['id']}")
    requests.post(f"{BASE_URL}/api/seasons/{season_id}/teams/{team2['id']}")
    print("Added teams to season")

    # Generate full schedule (season_id as query param, team_ids in body)
    resp = requests.post(f"{BASE_URL}/api/schedule/generate?season_id={season_id}",
                         json=[team1['id'], team2['id']])

    if resp.status_code == 200:
        result = resp.json()
        print(f"\nSchedule generated successfully!")
        print(f"Message: {result.get('message', 'No message')}")
        print(f"Number of matches: {len(result.get('schedule', []))}")
        for match in result.get('schedule', []):
            print(f"  Week {match['week']}: {match['team1_id']} vs {match['team2_id']}")
        return True
    else:
        print(f"\nFailed to generate schedule: {resp.status_code}")
        print(f"Error: {resp.text}")
        return False

if __name__ == "__main__":
    try:
        success = test_schedule_generation()
        if success:
            print("\n[SUCCESS] All tests passed!")
            exit(0)
        else:
            print("\n[FAILURE] Test failed")
            exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
