#!/usr/bin/env python3
"""
Comprehensive Tennis Stats Testing Suite
Tests every possible combination of serve, shot, and outcome scenarios.
"""

import sys
import json
import logging
from collections import defaultdict

# Mock instance class for testing
class MockTennisInstance:
    def __init__(self):
        self.stats = {}
        self.is_player1_serving = True
        
    def set_serving(self, player_serving):
        self.is_player1_serving = player_serving

# Copy your functions here (you'll need to paste them)
DEBUG_MODE = True


def update_match_statistics(instance, serve, point_type, result):
    
    player_serving = getattr(instance, "is_player1_serving", True)

    try:
        if DEBUG_MODE:
            print(f"📊 STATS CALL: serve='{serve}', point_type='{point_type}', result='{result}', player_serving={player_serving}")

        # Handle Double Fault specifically
        if serve == "Double Fault":
            if "Double Faults" not in instance.stats:
                instance.stats["Double Faults"] = [0, 0]
            
            # Whoever was serving made the double fault
            if player_serving:
                instance.stats["Double Faults"][0] += 1  # Player double fault
            else:
                instance.stats["Double Faults"][1] += 1  # Opponent double fault
            
            if DEBUG_MODE:
                who_faulted = "Player" if player_serving else "Opponent"
                print(f"📊 Tracked: {who_faulted} Double Fault")
            return

        # Handle Ace properly
        if (serve in ["First Serve", "Second Serve"] and point_type == "Ace"):
            
            # Track total aces
            if "Aces" not in instance.stats:
                instance.stats["Aces"] = [0, 0]
            instance.stats["Aces"][0 if player_serving else 1] += 1

            # Track serve-specific aces
            ace_key = f"{serve} Aces"
            if ace_key not in instance.stats:
                instance.stats[ace_key] = [0, 0]
            instance.stats[ace_key][0 if player_serving else 1] += 1
            
            # Track serves in for aces
            serve_in_key = f"{serve}s In"
            if serve_in_key not in instance.stats:
                instance.stats[serve_in_key] = [0, 0]
            instance.stats[serve_in_key][0 if player_serving else 1] += 1
            
            if DEBUG_MODE:
                print(f"📊 Tracked: Ace on {serve} by {'Player' if player_serving else 'Opponent'}")
            return

        # Track serves in (for all serves that aren't double faults)
        if serve in ["First Serve", "Second Serve"]:
            serve_in_key = f"{serve}s In"
            if serve_in_key not in instance.stats:
                instance.stats[serve_in_key] = [0, 0]
            instance.stats[serve_in_key][0 if player_serving else 1] += 1

        # Parse point_type for shot analysis
        point_parts = point_type.split()
        
        if len(point_parts) >= 2:
            # Handle different point_type formats
            if "Error" in point_type:
                # For errors, the last word is always "Error"
                outcome = "Error"
                shot_type = " ".join(point_parts[:-1])  # Everything except "Error"
            elif "Winner" in point_type:
                # For winners, the last word is always "Winner" 
                outcome = "Winner"
                shot_type = " ".join(point_parts[:-1])  # Everything except "Winner"
            else:
                # Default parsing
                shot_type, outcome = point_parts[0], point_parts[1]
                
            if DEBUG_MODE:
                print(f"🔍 Parsed: shot_type='{shot_type}', outcome='{outcome}'")
            
            # Create clean stat names based on who is serving
            serving_prefix = "Player Serving" if player_serving else "Opponent Serving"
            
            # Handle "Opponent Error" correctly
            if outcome == "Opponent" and len(point_parts) >= 3 and point_parts[2] == "Error":
                shot_key = f"{serving_prefix} {serve} {shot_type} Opponent Errors"
                if shot_key not in instance.stats:
                    instance.stats[shot_key] = [0, 0]
                
                if result == "Won":
                    instance.stats[shot_key][0 if player_serving else 1] += 1
                
                # Track in aggregate errors
                instance.stats.setdefault("Errors", [0,0])[1 if player_serving else 0] += 1
                
                if DEBUG_MODE:
                    print(f"📊 Tracked: {shot_key}")
                return
            
            # Track aggregate winners and errors
            if result == "Won":
                if "Winner" in outcome:
                    instance.stats.setdefault("Winners", [0,0])[0] += 1
                elif "Error" in outcome:
                    instance.stats.setdefault("Errors", [0,0])[1] += 1
                    
            elif result == "Lost":
                if "Winner" in outcome:
                    instance.stats.setdefault("Winners", [0,0])[1] += 1
                elif "Error" in outcome:
                    instance.stats.setdefault("Errors", [0,0])[0] += 1

            # Track detailed shot stats - CORRECTED LOGIC
            if serve in ["First Serve", "Second Serve"]:
                shot_key = f"{serving_prefix} {serve} {point_type}s"
                if shot_key not in instance.stats:
                    instance.stats[shot_key] = [0, 0]
                
                if DEBUG_MODE:
                    print(f"🔍 Processing detailed stat: {shot_key}")
                    print(f"🔍 point_type='{point_type}', outcome='{outcome}', result='{result}'")
                
                # CORRECTED LOGIC: Attribute the action to whoever performed it
                if "Winner" in outcome:
                    # For winners: whoever won the point performed the winning shot
                    if result == "Won":
                        # Player won = player hit the winner
                        instance.stats[shot_key][0] += 1  
                    else:  # result == "Lost"
                        # Player lost = opponent hit the winner  
                        instance.stats[shot_key][1] += 1
                        
                elif "Error" in outcome:
                    # For errors: whoever lost the point made the error
                    if result == "Won":
                        # Player won = opponent made the error
                        instance.stats[shot_key][1] += 1
                    else:  # result == "Lost"
                        # Player lost = player made the error
                        instance.stats[shot_key][0] += 1
                        
                else:
                    # Default case: attribute to the serving player
                    instance.stats[shot_key][0 if player_serving else 1] += 1
                
                # Handle serve winners separately
                if "Winner" in outcome:
                    winner_key = f"{serve} Winners"
                    instance.stats.setdefault(winner_key, [0,0])
                    if result == "Won":
                        instance.stats[winner_key][0] += 1  # Player hit winner
                    else:
                        instance.stats[winner_key][1] += 1  # Opponent hit winner

    except Exception as e:
        logging.error(f"Error updating match statistics: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error updating statistics: {e}")

    if DEBUG_MODE:
        print(f"📈 Current Stats: {instance.stats}")
def collect_stats(match_stats):
    """Processes all match statistics without double counting, correctly assigning points for errors."""

    if DEBUG_MODE:
        print(f"RECEIVED IN collect_stats(): {match_stats}")

    if not match_stats:
        print("WARNING: match_stats is empty!")
        return {}

    # Initialize point totals
    player_points_won = 0
    opponent_points_won = 0

    # Initialize detailed stats
    player_total_aces = 0
    opponent_total_aces = 0
    player_first_serve_aces = 0
    player_second_serve_aces = 0
    opponent_first_serve_aces = 0
    opponent_second_serve_aces = 0
    player_double_faults = 0
    opponent_double_faults = 0
    player_total_winners = 0
    opponent_total_winners = 0
    player_total_errors = 0
    opponent_total_errors = 0
    player_first_serves_in = 0
    opponent_first_serves_in = 0
    player_second_serves_in = 0
    opponent_second_serves_in = 0
    player_first_serve_winners = 0
    opponent_first_serve_winners = 0
    player_second_serve_winners = 0
    opponent_second_serve_winners = 0

    if DEBUG_MODE:
        print("=== COMPREHENSIVE STATS PROCESSING ===")

    for key, val in match_stats.items():
        if not isinstance(val, list) or len(val) < 2:
            continue

        player_count = val[0]
        opponent_count = val[1]

        if DEBUG_MODE and (player_count > 0 or opponent_count > 0):
            print(f"Processing: {key} = [Player: {player_count}, Opponent: {opponent_count}]")

        # Aces
        if key == "Aces":
            player_total_aces = player_count
            opponent_total_aces = opponent_count
            player_points_won += player_count
            opponent_points_won += opponent_count

        elif key == "First Serve Aces":
            player_first_serve_aces = player_count
            opponent_first_serve_aces = opponent_count

        elif key == "Second Serve Aces":
            player_second_serve_aces = player_count
            opponent_second_serve_aces = opponent_count

        # Double Faults
        elif key == "Double Faults":
            player_double_faults = player_count
            opponent_double_faults = opponent_count
            opponent_points_won += player_count
            player_points_won += opponent_count

        # Winners
        elif key == "Winners":
            player_total_winners = player_count
            opponent_total_winners = opponent_count
            player_points_won += player_count      # ADD THIS LINE
            opponent_points_won += opponent_count

        # Opponent Errors → forced errors that give points to player
        elif "Opponent Error" in key:
            player_points_won += opponent_count    # Opponent errors give player points
            opponent_points_won += player_count    # Player errors give opponent points

        # Serves In
        elif key == "First Serves In":
            player_first_serves_in = player_count
            opponent_first_serves_in = opponent_count

        elif key == "Second Serves In":
            player_second_serves_in = player_count
            opponent_second_serves_in = opponent_count

                # First Serve Winners (aggregate)
        elif key == "First Serve Winners":
            player_first_serve_winners = player_count
            opponent_first_serve_winners = opponent_count
            # Don't add to points here - they're already counted in "Winners"

        

        elif key == "Second Serve Winners":
            player_second_serve_winners = player_count
            opponent_second_serve_winners = opponent_count
            # Don't add to points here - they're already counted in "Winners"

        

                # Any kind of error (aggregate or detailed), except Opponent Errors & Double Faults
        elif "Error" in key and "Opponent Error" not in key and key != "Double Faults":
            
            # For aggregate "Errors" - only track counts, don't count points (avoid double counting)
            if key == "Errors":
                player_total_errors += player_count  # Player made these errors
                opponent_total_errors += opponent_count  # Opponent made these errors
                # DON'T count points here - they're already counted in detailed stats
                
            # For detailed error stats (e.g., "Player Serving First Serve Forehand Errors")
            else:
                # Count points only for detailed error stats
                opponent_points_won += player_count  # Player errors → opponent points
                player_points_won += opponent_count  # Opponent errors → player points
                

    return {
        "Total Points Won": player_points_won,
        "Total Points Lost": opponent_points_won,
        "Aces": [player_total_aces, opponent_total_aces],
        "Double Faults": [player_double_faults, opponent_double_faults],
        "Winners": [player_total_winners, opponent_total_winners],
        "Errors": [player_total_errors, opponent_total_errors]
    }

# Test scenarios
TEST_SCENARIOS = [
    # Format: (server, serve, point_type, result, expected_player_points, expected_opponent_points, description)
    
    # PLAYER SERVING SCENARIOS
    ("player", "First Serve", "Ace", "Won", 1, 0, "Player serving ace"),
    ("player", "Second Serve", "Ace", "Won", 1, 0, "Player serving 2nd serve ace"),
    ("player", "First Serve", "Forehand Winner", "Won", 1, 0, "Player serving forehand winner"),
    ("player", "Second Serve", "Backhand Winner", "Won", 1, 0, "Player serving backhand winner"),
    ("player", "First Serve", "Forehand Error", "Lost", 0, 1, "Player serving forehand error"),
    ("player", "Second Serve", "Backhand Error", "Lost", 0, 1, "Player serving backhand error"),
    ("player", "First Serve", "Forehand Opponent Error", "Won", 1, 0, "Player serving, opponent return error"),
    ("player", "Second Serve", "Backhand Opponent Error", "Won", 1, 0, "Player serving, opponent return error"),
    ("player", "Double Fault", "Double Fault", "Lost", 0, 1, "Player double fault"),
    
    # OPPONENT SERVING SCENARIOS  
    ("opponent", "First Serve", "Ace", "Lost", 0, 1, "Opponent serving ace"),
    ("opponent", "Second Serve", "Ace", "Lost", 0, 1, "Opponent serving 2nd serve ace"),
    ("opponent", "First Serve", "Return Forehand Winner", "Won", 1, 0, "Opponent serving, player return winner"),
    ("opponent", "Second Serve", "Return Backhand Winner", "Won", 1, 0, "Opponent serving, player return winner"),
    ("opponent", "First Serve", "Return Forehand Error", "Lost", 0, 1, "Opponent serving, player return error"),
    ("opponent", "Second Serve", "Return Backhand Error", "Lost", 0, 1, "Opponent serving, player return error"),
    ("opponent", "First Serve", "Forehand Opponent Error", "Won", 1, 0, "Opponent serving, opponent error on shot"),
    ("opponent", "Second Serve", "Backhand Opponent Error", "Won", 1, 0, "Opponent serving, opponent error on shot"),
    ("opponent", "Double Fault", "Double Fault", "Won", 1, 0, "Opponent double fault"),
    
    # RALLY SCENARIOS
    ("player", "First Serve", "Volley Winner", "Won", 1, 0, "Player serving, volley winner"),
    ("player", "First Serve", "Smash Winner", "Won", 1, 0, "Player serving, smash winner"),
    ("player", "First Serve", "Dropshot Winner", "Won", 1, 0, "Player serving, dropshot winner"),
    ("opponent", "First Serve", "Volley Error", "Lost", 0, 1, "Opponent serving, player volley error"),
    ("opponent", "First Serve", "Lob Error", "Lost", 0, 1, "Opponent serving, player lob error"),
]

def run_comprehensive_test():
    """Run all test scenarios and validate results."""
    
    print("🎾 COMPREHENSIVE TENNIS STATS TESTING SUITE")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for i, scenario in enumerate(TEST_SCENARIOS):
        server, serve, point_type, result, expected_player_pts, expected_opponent_pts, description = scenario
        
        print(f"\n📋 TEST {i+1}: {description}")
        print(f"   Input: server={server}, serve={serve}, point_type={point_type}, result={result}")
        print(f"   Expected: Player={expected_player_pts}, Opponent={expected_opponent_pts}")
        
        # Create fresh instance
        instance = MockTennisInstance()
        instance.set_serving(server == "player")
        
        # Run the stat update
        update_match_statistics(instance, serve, point_type, result)
        
        # Process stats
        processed_stats = collect_stats(instance.stats)
        
        actual_player_pts = processed_stats.get("Total Points Won", 0)
        actual_opponent_pts = processed_stats.get("Total Points Lost", 0)
        
        # Validate
        if actual_player_pts == expected_player_pts and actual_opponent_pts == expected_opponent_pts:
            print(f"   ✅ PASSED: Player={actual_player_pts}, Opponent={actual_opponent_pts}")
            passed_tests += 1
        else:
            print(f"   ❌ FAILED: Got Player={actual_player_pts}, Opponent={actual_opponent_pts}")
            failed_tests.append({
                'test': i+1,
                'description': description,
                'expected': (expected_player_pts, expected_opponent_pts),
                'actual': (actual_player_pts, actual_opponent_pts),
                'raw_stats': instance.stats
            })
        
        total_tests += 1
        
        # Show raw stats for debugging
        if instance.stats:
            print(f"   📊 Raw stats: {json.dumps(instance.stats, indent=2)}")
    
    # Summary
    print(f"\n🏆 TEST SUMMARY")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Show failed tests
    if failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for failure in failed_tests:
            print(f"  Test {failure['test']}: {failure['description']}")
            print(f"    Expected: {failure['expected']}, Got: {failure['actual']}")
            print(f"    Raw stats: {failure['raw_stats']}")
    
    return len(failed_tests) == 0

def run_aggregate_test():
    """Test multiple scenarios in one match to ensure no double counting."""
    
    print(f"\n🔄 AGGREGATE TEST: Multiple points in one match")
    print("=" * 50)
    
    instance = MockTennisInstance()
    
    # Simulate a series of points
    scenarios = [
        ("player", "First Serve", "Ace", "Won"),                    # +1 player
        ("player", "Second Serve", "Forehand Error", "Lost"),       # +1 opponent  
        ("opponent", "First Serve", "Return Forehand Winner", "Won"), # +1 player
        ("opponent", "Second Serve", "Return Backhand Error", "Lost"), # +1 opponent
        ("player", "Double Fault", "Double Fault", "Lost"),         # +1 opponent
        ("opponent", "Double Fault", "Double Fault", "Won"),        # +1 player
    ]
    
    expected_player_total = 3  # ace + return winner + opponent double fault
    expected_opponent_total = 3  # player error + player return error + player double fault
    
    for server, serve, point_type, result in scenarios:
        instance.set_serving(server == "player")
        update_match_statistics(instance, serve, point_type, result)
    
    processed_stats = collect_stats(instance.stats)
    actual_player = processed_stats.get("Total Points Won", 0)
    actual_opponent = processed_stats.get("Total Points Lost", 0)
    
    print(f"Expected totals: Player={expected_player_total}, Opponent={expected_opponent_total}")
    print(f"Actual totals: Player={actual_player}, Opponent={actual_opponent}")
    
    if actual_player == expected_player_total and actual_opponent == expected_opponent_total:
        print("✅ AGGREGATE TEST PASSED")
        return True
    else:
        print("❌ AGGREGATE TEST FAILED")
        print(f"Raw stats: {json.dumps(instance.stats, indent=2)}")
        return False

if __name__ == "__main__":
    print("Starting comprehensive tennis stats testing...")
    
    # Run individual scenario tests
    individual_passed = run_comprehensive_test()
    
    # Run aggregate test
    aggregate_passed = run_aggregate_test()
    
    if individual_passed and aggregate_passed:
        print(f"\n🎉 ALL TESTS PASSED! Your stats system is working correctly.")
    else:
        print(f"\n⚠️  SOME TESTS FAILED. Review the output above to fix issues.")
    
    print(f"\nTo run this tester:")
    print(f"1. Copy your current update_match_statistics and collect_stats functions")
    print(f"2. Paste them into this script (replace the placeholder functions)")
    print(f"3. Run: python tennis_stats_tester.py")