#!/usr/bin/env python3
"""Test bulk delete functionality for Players and Teams"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_players_bulk_delete():
    """Test bulk delete for players"""
    print("=" * 60)
    print("Testing Players Bulk Delete...")
    print("=" * 60)

    # Create players
    player_ids = []
    for i in range(1, 6):
        resp = requests.post(f"{BASE_URL}/api/players", json={'name': f'Test Player {i}', 'handicap': i*5})
        player_ids.append(resp.json()['id'])
    print(f"[OK] Created {len(player_ids)} players")

    # Get all players
    resp = requests.get(f"{BASE_URL}/api/players")
    all_players = resp.json()
    initial_count = len(all_players)
    print(f"[OK] Total players before delete: {initial_count}")

    # Delete 3 players
    to_delete = player_ids[:3]
    print(f"[INFO] Deleting {len(to_delete)} players...")

    promises = [requests.delete(f"{BASE_URL}/api/players/{pid}") for pid in to_delete]
    for p in promises:
        p.raise_for_status()

    print(f"[OK] Deleted {len(to_delete)} players")

    # Verify count
    resp = requests.get(f"{BASE_URL}/api/players")
    remaining = resp.json()
    expected = initial_count - len(to_delete)

    if len(remaining) != expected:
        print(f"[FAIL] Expected {expected} players, got {len(remaining)}")
        return False

    print(f"[OK] Player count decreased from {initial_count} to {len(remaining)}")

    # Verify deleted players are gone
    for pid in to_delete:
        if any(p['id'] == pid for p in remaining):
            print(f"[FAIL] Deleted player {pid} still exists")
            return False

    print(f"[OK] All deleted players confirmed absent")

    print("\n" + "=" * 60)
    print("[SUCCESS] Players bulk delete works correctly!")
    print("=" * 60)
    return True

def test_teams_bulk_delete():
    """Test bulk delete for teams"""
    print("\n" + "=" * 60)
    print("Testing Teams Bulk Delete...")
    print("=" * 60)

    # Create players first
    player_ids = []
    for i in range(1, 7):
        resp = requests.post(f"{BASE_URL}/api/players", json={'name': f'Team Test Player {i}', 'handicap': i*5})
        player_ids.append(resp.json()['id'])

    # Create teams
    team_ids = []
    for i in range(0, 6, 2):
        resp = requests.post(f"{BASE_URL}/api/teams", json={
            'name': f'Test Team {i//2+1}',
            'player1_id': player_ids[i],
            'player2_id': player_ids[i+1]
        })
        team_ids.append(resp.json()['id'])
    print(f"[OK] Created {len(team_ids)} teams")

    # Get all teams
    resp = requests.get(f"{BASE_URL}/api/teams")
    all_teams = resp.json()
    initial_count = len(all_teams)
    print(f"[OK] Total teams before delete: {initial_count}")

    # Delete 2 teams
    to_delete = team_ids[:2]
    print(f"[INFO] Deleting {len(to_delete)} teams...")

    promises = [requests.delete(f"{BASE_URL}/api/teams/{tid}") for tid in to_delete]
    for p in promises:
        p.raise_for_status()

    print(f"[OK] Deleted {len(to_delete)} teams")

    # Verify count
    resp = requests.get(f"{BASE_URL}/api/teams")
    remaining = resp.json()
    expected = initial_count - len(to_delete)

    if len(remaining) != expected:
        print(f"[FAIL] Expected {expected} teams, got {len(remaining)}")
        return False

    print(f"[OK] Team count decreased from {initial_count} to {len(remaining)}")

    # Verify deleted teams are gone
    for tid in to_delete:
        if any(t['id'] == tid for t in remaining):
            print(f"[FAIL] Deleted team {tid} still exists")
            return False

    print(f"[OK] All deleted teams confirmed absent")

    print("\n" + "=" * 60)
    print("[SUCCESS] Teams bulk delete works correctly!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        test1 = test_players_bulk_delete()
        test2 = test_teams_bulk_delete()

        print("\n" + "=" * 60)
        if test1 and test2:
            print("[SUCCESS] All bulk delete tests passed!")
            exit(0)
        else:
            print("[FAILURE] Some tests failed")
            exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
