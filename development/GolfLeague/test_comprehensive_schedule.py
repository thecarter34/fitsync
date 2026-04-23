#!/usr/bin/env python3
"""Comprehensive test of schedule generation with 6 teams"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_six_teams():
    print("Testing schedule generation with 6 teams...")
    
    # Create season
    resp = requests.post(f"{BASE_URL}/api/seasons", json={'name': '6-Team Season'})
    season = resp.json()
    season_id = season['id']
    print(f"Season ID: {season_id}")
    
    # Create 12 players with varying handicaps
    player_ids = []
    for i in range(1, 13):
        resp = requests.post(f"{BASE_URL}/api/players", json={'name': f'Player {i}', 'handicap': i*2})
        player_ids.append(resp.json()['id'])
    print(f"Created {len(player_ids)} players")
    
    # Create 6 teams
    team_ids = []
    for i in range(0, 12, 2):
        resp = requests.post(f"{BASE_URL}/api/teams", json={
            'name': f'Team {i//2+1}',
            'player1_id': player_ids[i],
            'player2_id': player_ids[i+1]
        })
        team_ids.append(resp.json()['id'])
    print(f"Created {len(team_ids)} teams")
    
    # Add teams to season
    for tid in team_ids:
        requests.post(f"{BASE_URL}/api/seasons/{season_id}/teams/{tid}")
    
    # Generate full schedule
    resp = requests.post(f"{BASE_URL}/api/schedule/generate?season_id={season_id}", json=team_ids)
    
    if resp.status_code != 200:
        print(f"ERROR: {resp.status_code} - {resp.text}")
        return False
    
    result = resp.json()
    schedule = result.get('schedule', [])
    print(f"\nGenerated {len(schedule)} matches")
    
    # Count matches per team
    team_match_count = {tid: 0 for tid in team_ids}
    for match in schedule:
        team_match_count[match['team1_id']] += 1
        team_match_count[match['team2_id']] += 1
    
    print("\nMatches per team:")
    for tid, count in sorted(team_match_count.items()):
        print(f"  {tid}: {count}")
    
    # Expected: each team plays 5 matches (against each of the other 5 teams)
    expected_per_team = len(team_ids) - 1
    all_correct = all(count == expected_per_team for count in team_match_count.values())
    
    # Check total unique matchups
    unique_matchups = set()
    for match in schedule:
        unique_matchups.add(frozenset([match['team1_id'], match['team2_id']]))
    
    expected_total = (len(team_ids) * (len(team_ids) - 1)) // 2
    print(f"\nExpected total matches: {expected_total}")
    print(f"Actual total matches: {len(unique_matchups)}")
    print(f"Expected per team: {expected_per_team}")
    
    if all_correct and len(unique_matchups) == expected_total:
        print("\n[SUCCESS] Schedule generation is correct!")
        return True
    else:
        print("\n[FAILURE] Schedule generation has issues")
        return False

if __name__ == "__main__":
    try:
        success = test_six_teams()
        exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
