#!/usr/bin/env python3
"""
Test script for decoupled data_manager and scoring_engine modules.
This verifies that the core logic works independently of Tkinter.
"""

import sys
import traceback

def test_imports():
    """Test that modules can be imported."""
    print("Testing imports...")
    try:
        from data_manager import DataManager, DEFAULT_STROKE_INDEX, HOLE_PARS
        from scoring_engine import ScoringEngine
        print("[PASS] Modules imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        traceback.print_exc()
        return False

def test_data_manager_init():
    """Test DataManager initialization."""
    print("\nTesting DataManager initialization...")
    try:
        from data_manager import DataManager, DEFAULT_STROKE_INDEX, HOLE_PARS
        dm = DataManager()
        print("[PASS] DataManager initialized")
        print(f"  - Loaded {len(dm.players)} players")
        print(f"  - Loaded {len(dm.teams)} teams")
        print(f"  - Loaded {len(dm.matches)} matches")
        print(f"  - Stroke index: {dm.course_settings.get('stroke_index', DEFAULT_STROKE_INDEX)}")
        print(f"  - Hole pars: {dm.course_settings.get('hole_pars', HOLE_PARS)}")
        return True
    except Exception as e:
        print(f"[FAIL] DataManager initialization failed: {e}")
        traceback.print_exc()
        return False

def test_scoring_engine():
    """Test ScoringEngine with sample data."""
    print("\nTesting ScoringEngine...")
    try:
        from data_manager import DataManager
        from scoring_engine import ScoringEngine

        dm = DataManager()
        se = ScoringEngine(dm)

        # Check if we have a match to test with
        if not dm.matches:
            print("[WARN] No matches in data - skipping scoring test")
            return True

        # Get first match
        match_id = list(dm.matches.keys())[0]
        match = dm.matches[match_id]
        print(f"  Testing with match: {match_id}")

        # Get teams
        team1 = dm.get_team(match["team1_id"])
        team2 = dm.get_team(match["team2_id"])

        if not team1 or not team2:
            print("[WARN] Teams not found - skipping scoring test")
            return True

        # Create sample gross scores (all pars for simplicity)
        team1_p1_gross = {h: 4 for h in range(1, 10)}
        team1_p2_gross = {h: 4 for h in range(1, 10)}
        team2_p1_gross = {h: 4 for h in range(1, 10)}
        team2_p2_gross = {h: 4 for h in range(1, 10)}

        # Calculate scores
        results = se.calculate_match_scores(
            match_id,
            team1_p1_gross, team1_p2_gross,
            team2_p1_gross, team2_p2_gross
        )

        if not results:
            print("[FAIL] ScoringEngine returned empty results")
            return False

        print(f"[PASS] ScoringEngine calculated successfully")
        print(f"  - Team1 final points: {results.get('team1_final_points', 0)}")
        print(f"  - Team2 final points: {results.get('team2_final_points', 0)}")
        print(f"  - Winner: {results.get('winner', 'unknown')}")
        print(f"  - Hole results: {len(results.get('hole_results', []))} holes")
        return True

    except Exception as e:
        print(f"[FAIL] ScoringEngine test failed: {e}")
        traceback.print_exc()
        return False

def test_stroke_index_logic():
    """Test Hickory Hills stroke index logic."""
    print("\nTesting stroke index logic...")
    try:
        from data_manager import DEFAULT_STROKE_INDEX

        # Verify the stroke index order
        expected = [3, 8, 1, 6, 9, 4, 7, 2, 5]
        if DEFAULT_STROKE_INDEX == expected:
            print(f"[PASS] Stroke index matches Hickory Hills: {DEFAULT_STROKE_INDEX}")
            return True
        else:
            print(f"[FAIL] Stroke index mismatch!")
            print(f"  Expected: {expected}")
            print(f"  Got: {DEFAULT_STROKE_INDEX}")
            return False
    except Exception as e:
        print(f"[FAIL] Stroke index test failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("PHASE 1: Testing Decoupled Modules")
    print("=" * 60)

    results = []
    results.append(("Imports", test_imports()))
    results.append(("DataManager Init", test_data_manager_init()))
    results.append(("Stroke Index Logic", test_stroke_index_logic()))
    results.append(("ScoringEngine", test_scoring_engine()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {name}")

    all_passed = all(r[1] for r in results)
    if all_passed:
        print("\n[SUCCESS] All tests passed! Phase 1 complete.")
        return 0
    else:
        print("\n[ERROR] Some tests failed. Please review.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
