"""
Test that simulates browser behavior with partial scores.
"""
import sys
sys.path.insert(0, '.')

from data_manager import DataManager
from scoring_engine import ScoringEngine

def test_browser_scenario():
    """Simulate what happens when user fills only 4 holes (all 4 players must have scores)."""
    dm = DataManager()
    se = ScoringEngine(dm)

    matches = list(dm.matches.values())
    if not matches:
        print("No matches found")
        return

    match = matches[0]
    match_id = match['id']

    # Scenario: User fills scores for holes 1, 2, 3, 4
    # All 4 players have scores for these 4 holes
    # The other 5 holes (5-9) have no scores (empty in browser, but sent as 0)
    team1_p1_scores = {1: 4, 2: 5, 3: 4, 4: 5}  # 4 holes
    team1_p2_scores = {1: 5, 2: 4, 3: 5, 4: 4}
    team2_p1_scores = {1: 4, 2: 4, 3: 4, 4: 5}
    team2_p2_scores = {1: 5, 2: 5, 3: 4, 4: 4}

    results = se.calculate_match_scores(
        match_id,
        team1_p1_scores,
        team1_p2_scores,
        team2_p1_scores,
        team2_p2_scores
    )

    print(f"Holes in results: {[h['hole'] for h in results['hole_results']]}")
    print(f"Number of hole results: {len(results['hole_results'])}")
    print(f"Team1 final points: {results['team1_final_points']}")
    print(f"Team2 final points: {results['team2_final_points']}")
    print(f"Team1 bonus: {results['team1_bonus']}")
    print(f"Team2 bonus: {results['team2_bonus']}")

    # Should only have 4 holes
    assert len(results['hole_results']) == 4, f"Expected 4 holes, got {len(results['hole_results'])}"

    # Bonus should be 0 (not all 9 holes completed)
    assert results['team1_bonus'] == 0.0, f"Expected 0 bonus, got {results['team1_bonus']}"
    assert results['team2_bonus'] == 0.0, f"Expected 0 bonus, got {results['team2_bonus']}"

    # Max possible points for 4 holes = 4 holes * 2 points per hole = 8
    assert results['team1_final_points'] <= 8.0, f"Team1 points too high: {results['team1_final_points']}"
    assert results['team2_final_points'] <= 8.0, f"Team2 points too high: {results['team2_final_points']}"

    print("[PASS] Browser simulation test passed!")

if __name__ == '__main__':
    test_browser_scenario()
