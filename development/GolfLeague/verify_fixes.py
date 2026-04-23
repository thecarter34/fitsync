#!/usr/bin/env python3
"""Verify both fixes: season_setup generate button and schedule tab display-only"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_season_setup_generate():
    """Test that the season setup generate button works with correct API format"""
    print("=" * 60)
    print("Testing Season Setup 'Generate Full Schedule' button fix...")
    print("=" * 60)

    # Create season
    resp = requests.post(f"{BASE_URL}/api/seasons", json={'name': 'Verify Season'})
    season = resp.json()
    season_id = season['id']
    print(f"[OK] Created season: {season_id}")

    # Create players and teams
    player_ids = []
    for i in range(1, 5):
        resp = requests.post(f"{BASE_URL}/api/players", json={'name': f'P{i}', 'handicap': i*5})
        player_ids.append(resp.json()['id'])

    team_ids = []
    for i in range(0, 4, 2):
        resp = requests.post(f"{BASE_URL}/api/teams", json={
            'name': f'Team {i//2+1}',
            'player1_id': player_ids[i],
            'player2_id': player_ids[i+1]
        })
        team_ids.append(resp.json()['id'])

    # Add teams to season
    for tid in team_ids:
        requests.post(f"{BASE_URL}/api/seasons/{season_id}/teams/{tid}")

    print(f"[OK] Added {len(team_ids)} teams to season")

    # Simulate what the season_setup.html generateFullSchedule() does
    # (season_id as query param, team_ids as JSON array in body)
    resp = requests.post(f"{BASE_URL}/api/schedule/generate?season_id={season_id}", json=team_ids)

    if resp.status_code == 200:
        result = resp.json()
        print(f"[OK] Schedule generated successfully: {len(result['schedule'])} matches")
        print("[OK] Season Setup button works correctly!")
        return True
    else:
        print(f"✗ FAILED: {resp.status_code} - {resp.text}")
        return False

def test_schedule_tab_removed_generator():
    """Verify schedule.html no longer has generateFullSchedule function"""
    print("\n" + "=" * 60)
    print("Testing Schedule tab (should be display-only)...")
    print("=" * 60)

    resp = requests.get(f"{BASE_URL}/schedule")
    if resp.status_code != 200:
        print("✗ Could not fetch schedule page")
        return False

    html = resp.text

    # Check that the button is removed
    if 'onclick="generateFullSchedule()"' in html:
        print("[FAIL] generateFullSchedule button still present in schedule.html")
        return False

    # Check that the function is removed
    if 'async function generateFullSchedule()' in html:
        print("[FAIL] generateFullSchedule function still defined in schedule.html")
        return False

    # Check that the message is updated
    if 'Schedule is generated in the Season Setup tab' in html:
        print("[OK] Schedule tab is now display-only")
        return True
    elif 'Generate a full round-robin schedule' in html:
        print("[FAIL] Old instruction text still present")
        return False
    else:
        print("[?] Could not verify message, but button/function removed")
        return True

if __name__ == "__main__":
    try:
        test1 = test_season_setup_generate()
        test2 = test_schedule_tab_removed_generator()

        print("\n" + "=" * 60)
        if test1 and test2:
            print("\n[SUCCESS] All fixes verified!")
            exit(0)
        else:
            print("\n[FAILURE] Some tests failed")
            exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
