#!/usr/bin/env python3
"""Test round-robin schedule generation with various team counts"""

from data_manager import DataManager

def test_round_robin_even():
    """Test with even number of teams (4 teams)"""
    dm = DataManager()
    team_ids = [f"T{i}" for i in range(1, 5)]  # T1, T2, T3, T4
    
    schedule = dm.generate_schedule("test_season", team_ids)
    
    print("Even teams (4):")
    print(f"  Total matches: {len(schedule)}")
    
    # Check that each team plays exactly 3 matches (once against each other team)
    team_matches = {tid: 0 for tid in team_ids}
    for match in schedule:
        team_matches[match['team1_id']] += 1
        team_matches[match['team2_id']] += 1
    
    for tid, count in team_matches.items():
        print(f"  {tid}: {count} matches")
        assert count == 3, f"Team {tid} should play 3 matches, got {count}"
    
    # Check that all unique matchups are present
    expected_matchups = set()
    for t1, t2 in __import__('itertools').combinations(team_ids, 2):
        expected_matchups.add((t1, t2))
        expected_matchups.add((t2, t1))
    
    actual_matchups = set()
    for match in schedule:
        actual_matchups.add((match['team1_id'], match['team2_id']))
    
    assert len(actual_matchups) == 6, f"Should have 6 unique matchups, got {len(actual_matchups)}"
    print("  [PASS] All assertions passed\n")

def test_round_robin_odd():
    """Test with odd number of teams (5 teams)"""
    dm = DataManager()
    team_ids = [f"T{i}" for i in range(1, 6)]  # T1, T2, T3, T4, T5
    
    schedule = dm.generate_schedule("test_season", team_ids)
    
    print("Odd teams (5):")
    print(f"  Total matches: {len(schedule)}")
    
    # Check that each team plays exactly 4 matches (once against each other team)
    team_matches = {tid: 0 for tid in team_ids}
    for match in schedule:
        team_matches[match['team1_id']] += 1
        team_matches[match['team2_id']] += 1
    
    for tid, count in team_matches.items():
        print(f"  {tid}: {count} matches")
        assert count == 4, f"Team {tid} should play 4 matches, got {count}"
    
    # Check that all unique matchups are present (order-independent)
    expected_matchups = set()
    for t1, t2 in __import__('itertools').combinations(team_ids, 2):
        expected_matchups.add(frozenset([t1, t2]))
    
    actual_matchups = set()
    for match in schedule:
        actual_matchups.add(frozenset([match['team1_id'], match['team2_id']]))
    
    assert len(actual_matchups) == 10, f"Should have 10 unique matchups, got {len(actual_matchups)}"
    assert actual_matchups == expected_matchups, "All matchups should be present"
    print("  [PASS] All assertions passed\n")

def test_round_robin_single_matchup():
    """Test with only 2 teams (minimum)"""
    dm = DataManager()
    team_ids = ["T1", "T2"]
    
    schedule = dm.generate_schedule("test_season", team_ids)
    
    print("Two teams:")
    print(f"  Total matches: {len(schedule)}")
    
    assert len(schedule) == 1, f"Should have 1 match, got {len(schedule)}"
    assert schedule[0]['team1_id'] == "T1" and schedule[0]['team2_id'] == "T2"
    print("  [PASS] All assertions passed\n")

def test_round_robin_three_teams():
    """Test with 3 teams"""
    dm = DataManager()
    team_ids = ["T1", "T2", "T3"]
    
    schedule = dm.generate_schedule("test_season", team_ids)
    
    print("Three teams:")
    print(f"  Total matches: {len(schedule)}")
    
    # Should have 3 matches (T1-T2, T1-T3, T2-T3)
    assert len(schedule) == 3, f"Should have 3 matches, got {len(schedule)}"
    
    team_matches = {tid: 0 for tid in team_ids}
    for match in schedule:
        team_matches[match['team1_id']] += 1
        team_matches[match['team2_id']] += 1
    
    for tid, count in team_matches.items():
        assert count == 2, f"Team {tid} should play 2 matches, got {count}"
    
    print("  [PASS] All assertions passed\n")

if __name__ == "__main__":
    test_round_robin_even()
    test_round_robin_odd()
    test_round_robin_single_matchup()
    test_round_robin_three_teams()
    print("[SUCCESS] All round-robin tests passed!")
