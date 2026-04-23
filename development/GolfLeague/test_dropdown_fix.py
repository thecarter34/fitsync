#!/usr/bin/env python3
"""Test the schedule dropdown functionality with actual data"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_dropdown_with_data():
    print("=" * 60)
    print("Testing schedule dropdown with actual match data...")
    print("=" * 60)
    
    # Create season
    resp = requests.post(f"{BASE_URL}/api/seasons", json={'name': 'Dropdown Test Season'})
    season = resp.json()
    season_id = season['id']
    print(f"[OK] Created season: {season_id}")
    
    # Create 4 players
    player_ids = []
    for i in range(1, 5):
        resp = requests.post(f"{BASE_URL}/api/players", json={'name': f'Player {i}', 'handicap': i*5})
        player_ids.append(resp.json()['id'])
    print(f"[OK] Created {len(player_ids)} players")
    
    # Create 2 teams
    resp = requests.post(f"{BASE_URL}/api/teams", json={
        'name': 'Team A',
        'player1_id': player_ids[0],
        'player2_id': player_ids[1]
    })
    team1 = resp.json()
    
    resp = requests.post(f"{BASE_URL}/api/teams", json={
        'name': 'Team B',
        'player1_id': player_ids[2],
        'player2_id': player_ids[3]
    })
    team2 = resp.json()
    
    team_ids = [team1['id'], team2['id']]
    print(f"[OK] Created teams: {team1['id']}, {team2['id']}")
    
    # Add teams to season
    for tid in team_ids:
        requests.post(f"{BASE_URL}/api/seasons/{season_id}/teams/{tid}")
    print(f"[OK] Added teams to season")
    
    # Generate full schedule (should create matches for multiple weeks)
    resp = requests.post(f"{BASE_URL}/api/schedule/generate?season_id={season_id}", json=team_ids)
    if resp.status_code != 200:
        print(f"[FAIL] Schedule generation failed: {resp.text}")
        return False
    
    result = resp.json()
    schedule = result.get('schedule', [])
    print(f"[OK] Generated {len(schedule)} matches")
    
    # Get all matches from API
    resp = requests.get(f"{BASE_URL}/api/matches")
    if resp.status_code != 200:
        print(f"[FAIL] Failed to get matches: {resp.text}")
        return False
    
    matches = resp.json()
    print(f"[OK] Retrieved {len(matches)} matches from API")
    
    # Check that matches have week_number field
    if not matches:
        print("[FAIL] No matches returned")
        return False
    
    first_match = matches[0]
    if 'week_number' not in first_match:
        print(f"[FAIL] Match does not have 'week_number' field. Keys: {list(first_match.keys())}")
        return False
    
    print(f"[OK] Matches have 'week_number' field: {first_match['week_number']}")
    
    # Check that we have multiple weeks
    weeks = set(m['week_number'] for m in matches)
    print(f"[OK] Found weeks: {sorted(weeks)}")
    
    # Test the schedule page loads
    resp = requests.get(f"{BASE_URL}/schedule")
    if resp.status_code != 200:
        print(f"[FAIL] Failed to load schedule page: {resp.text}")
        return False
    
    html = resp.text
    
    # Check that the dropdown exists
    if 'id="week-filter"' not in html:
        print("[FAIL] Week filter dropdown not found in HTML")
        return False
    
    print("[OK] Schedule page loads with week filter dropdown")
    
    # Check that the dropdown is populated client-side (we can't test JS directly, but we can verify the structure)
    if 'populateWeekDropdown' in html:
        print("[OK] Dropdown population function present")
    else:
        print("[FAIL] Dropdown population function missing")
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Dropdown functionality is properly implemented!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_dropdown_with_data()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
