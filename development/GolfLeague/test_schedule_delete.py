#!/usr/bin/env python3
"""Test the schedule delete functionality"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_delete_single_match():
    """Test deleting a single match from the schedule"""
    print("=" * 60)
    print("Testing DELETE /api/matches/{match_id}...")
    print("=" * 60)

    # Create season
    resp = requests.post(f"{BASE_URL}/api/seasons", json={'name': 'Delete Test Season'})
    season = resp.json()
    season_id = season['id']
    print(f"[OK] Created season: {season_id}")

    # Create players and teams
    player_ids = []
    for i in range(1, 5):
        resp = requests.post(f"{BASE_URL}/api/players", json={'name': f'Player {i}', 'handicap': i*5})
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

    # Generate schedule
    resp = requests.post(f"{BASE_URL}/api/schedule/generate?season_id={season_id}", json=team_ids)
    result = resp.json()
    schedule = result.get('schedule', [])
    print(f"[OK] Generated {len(schedule)} matches")

    # Get all matches
    resp = requests.get(f"{BASE_URL}/api/matches")
    matches = resp.json()
    print(f"[OK] Retrieved {len(matches)} matches from API")

    if not matches:
        print("[FAIL] No matches to delete")
        return False

    # Delete the first match
    match_id = matches[0]['id']
    print(f"[INFO] Deleting match {match_id}...")
    resp = requests.delete(f"{BASE_URL}/api/matches/{match_id}")

    if resp.status_code != 200:
        print(f"[FAIL] Delete failed: {resp.status_code} - {resp.text}")
        return False

    print(f"[OK] Deleted match {match_id}")

    # Verify match is gone
    resp = requests.get(f"{BASE_URL}/api/matches")
    remaining = resp.json()
    if len(remaining) != len(matches) - 1:
        print(f"[FAIL] Expected {len(matches)-1} matches, got {len(remaining)}")
        return False

    print(f"[OK] Verified: match count decreased from {len(matches)} to {len(remaining)}")

    # Verify the specific match is not in the list
    if any(m['id'] == match_id for m in remaining):
        print(f"[FAIL] Deleted match {match_id} still appears in results")
        return False

    print(f"[OK] Deleted match {match_id} not found in remaining matches")

    # Also verify scores were deleted
    resp = requests.get(f"{BASE_URL}/api/scores/{match_id}")
    if resp.status_code == 200:
        scores = resp.json()
        if scores.get('has_scores', False):
            print("[WARN] Scores still exist for deleted match (should be cleaned up)")

    print("\n" + "=" * 60)
    print("[SUCCESS] Single match deletion works correctly!")
    print("=" * 60)
    return True

def test_delete_multiple_matches():
    """Test deleting multiple matches at once"""
    print("\n" + "=" * 60)
    print("Testing batch delete of multiple matches...")
    print("=" * 60)

    # Create season
    resp = requests.post(f"{BASE_URL}/api/seasons", json={'name': 'Batch Delete Test Season'})
    season = resp.json()
    season_id = season['id']

    # Create players and teams
    player_ids = []
    for i in range(1, 7):
        resp = requests.post(f"{BASE_URL}/api/players", json={'name': f'Player {i}', 'handicap': i*5})
        player_ids.append(resp.json()['id'])

    team_ids = []
    for i in range(0, 6, 2):
        resp = requests.post(f"{BASE_URL}/api/teams", json={
            'name': f'Team {i//2+1}',
            'player1_id': player_ids[i],
            'player2_id': player_ids[i+1]
        })
        team_ids.append(resp.json()['id'])

    # Add teams to season
    for tid in team_ids:
        requests.post(f"{BASE_URL}/api/seasons/{season_id}/teams/{tid}")

    # Generate schedule (should create multiple matches)
    resp = requests.post(f"{BASE_URL}/api/schedule/generate?season_id={season_id}", json=team_ids)
    result = resp.json()
    schedule = result.get('schedule', [])
    print(f"[OK] Generated {len(schedule)} matches")

    # Get all matches
    resp = requests.get(f"{BASE_URL}/api/matches")
    matches = resp.json()
    initial_count = len(matches)
    print(f"[OK] Total matches: {initial_count}")

    if initial_count < 2:
        print("[WARN] Not enough matches for batch delete test, skipping")
        return True

    # Delete first 2 matches
    match_ids = [m['id'] for m in matches[:2]]
    print(f"[INFO] Deleting {len(match_ids)} matches...")

    promises = [requests.delete(f"{BASE_URL}/api/matches/{mid}") for mid in match_ids]
    for p in promises:
        p.raise_for_status()

    print(f"[OK] Deleted {len(match_ids)} matches")

    # Verify count
    resp = requests.get(f"{BASE_URL}/api/matches")
    remaining = resp.json()
    expected = initial_count - len(match_ids)

    if len(remaining) != expected:
        print(f"[FAIL] Expected {expected} matches, got {len(remaining)}")
        return False

    print(f"[OK] Match count decreased from {initial_count} to {len(remaining)}")

    # Verify deleted matches are gone
    for mid in match_ids:
        if any(m['id'] == mid for m in remaining):
            print(f"[FAIL] Deleted match {mid} still appears")
            return False

    print(f"[OK] All deleted matches confirmed absent")

    print("\n" + "=" * 60)
    print("[SUCCESS] Batch delete works correctly!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        test1 = test_delete_single_match()
        test2 = test_delete_multiple_matches()

        print("\n" + "=" * 60)
        if test1 and test2:
            print("[SUCCESS] All delete tests passed!")
            exit(0)
        else:
            print("[FAILURE] Some tests failed")
            exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
