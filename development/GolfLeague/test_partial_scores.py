"""
Test to verify that partial scores only calculate completed holes.
"""
import sys
sys.path.insert(0, '.')

from data_manager import DataManager
from scoring_engine import ScoringEngine

def test_partial_scores():
    """Test that only holes with scores are included in results."""
    dm = DataManager()
    se = ScoringEngine(dm)

    # Get a match (use the first one available)
    matches = list(dm.matches.values())
    if not matches:
        print("No matches found. Creating test match...")
        # Need to create test data
        return

    match = matches[0]
    match_id = match['id']

    # Simulate partial scores - only holes 1, 2, 3 have scores
    team1_p1_scores = {1: 4, 2: 5, 3: 4}  # Only 3 holes
    team1_p2_scores = {1: 5, 2: 4, 3: 5}
    team2_p1_scores = {1: 4, 2: 4, 3: 4}
    team2_p2_scores = {1: 5, 2: 5, 3: 4}

    results = se.calculate_match_scores(
        match_id,
        team1_p1_scores,
        team1_p2_scores,
        team2_p1_scores,
        team2_p2_scores
    )

    print(f"Total hole results: {len(results['hole_results'])}")
    print(f"Holes included: {[h['hole'] for h in results['hole_results']]}")

    # Should only have 3 holes
    assert len(results['hole_results']) == 3, f"Expected 3 holes, got {len(results['hole_results'])}"

    # Check that only holes 1, 2, 3 are present
    hole_numbers = [h['hole'] for h in results['hole_results']]
    assert hole_numbers == [1, 2, 3], f"Expected [1, 2, 3], got {hole_numbers}"

    # Totals should only reflect completed holes
    assert results['team1_hole_points'] <= 3.0 * 2.0, "Team1 points should only be for 3 holes"
    assert results['team2_hole_points'] <= 3.0 * 2.0, "Team2 points should only be for 3 holes"

    # Bonus should be 0 for incomplete rounds
    assert results['team1_bonus'] == 0.0, f"Team1 bonus should be 0 for partial round, got {results['team1_bonus']}"
    assert results['team2_bonus'] == 0.0, f"Team2 bonus should be 0 for partial round, got {results['team2_bonus']}"

    print("[PASS] Partial scores test passed!")

    # Test with no scores
    results_empty = se.calculate_match_scores(
        match_id,
        {}, {}, {}, {}
    )
    print(f"\nNo scores test: hole_results length = {len(results_empty['hole_results'])}")
    assert len(results_empty['hole_results']) == 0, "Should have no hole results"
    assert results_empty['winner'] == "tie", f"Winner should be 'tie', got {results_empty['winner']}"
    assert results_empty['team1_final_points'] == 0.0, "Final points should be 0"
    print("[PASS] No scores test passed!")

    # Test with all 9 holes
    all_holes_scores = {
        i: 4 for i in range(1, 10)
    }
    results_full = se.calculate_match_scores(
        match_id,
        all_holes_scores,
        all_holes_scores,
        all_holes_scores,
        all_holes_scores
    )
    print(f"\nFull scores test: hole_results length = {len(results_full['hole_results'])}")
    assert len(results_full['hole_results']) == 9, "Should have all 9 holes"
    
    # Full round should have bonus points (total bonus = 5.0)
    total_bonus = results_full['team1_bonus'] + results_full['team2_bonus']
    assert total_bonus == 5.0, f"Full round should have 5 bonus points total, got {total_bonus}"
    
    print("[PASS] Full scores test passed!")

if __name__ == '__main__':
    test_partial_scores()
