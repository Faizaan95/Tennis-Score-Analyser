import unittest
import sys
import os

# Add the parent directory to the path to import your modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from score_manager import update_match_statistics
except ImportError:
    print("Warning: Could not import update_match_statistics. Make sure score_manager.py is in the same directory.")

class DummyInstance:
    def __init__(self):
        self.stats = {}

class TestMatchStatLogic(unittest.TestCase):

    def setUp(self):
        self.instance = DummyInstance()

    def test_ace_first_serve(self):
        """Test that aces are tracked correctly"""
        update_match_statistics(self.instance, "First Serve", "Ace", "Won")
        
        # Check aggregate ace tracking
        self.assertEqual(self.instance.stats.get("Aces"), [1, 0])
        # Check serve-specific ace tracking
        self.assertEqual(self.instance.stats.get("First Serve Aces"), [1, 0])
        # Aces should count as serves in
        self.assertEqual(self.instance.stats.get("First Serves In"), [1, 0])

    def test_ace_second_serve(self):
        """Test second serve aces"""
        update_match_statistics(self.instance, "Second Serve", "Ace", "Won")
        
        self.assertEqual(self.instance.stats.get("Aces"), [1, 0])
        self.assertEqual(self.instance.stats.get("Second Serve Aces"), [1, 0])
        self.assertEqual(self.instance.stats.get("Second Serves In"), [1, 0])

    def test_double_fault(self):
        """Test double fault tracking"""
        update_match_statistics(self.instance, "Double Fault", "Double Fault", "Lost")
        
        self.assertEqual(self.instance.stats.get("Double Faults"), [1, 0])
        # Double faults should not count as serves in
        self.assertNotIn("Second Serves In", self.instance.stats)

    def test_player_winner_first_serve(self):
        """Test player winner on first serve"""
        update_match_statistics(self.instance, "First Serve", "Forehand Winner", "Won")
        
        # Check aggregate winner tracking
        self.assertEqual(self.instance.stats.get("Winners"), [1, 0])
        # Check serve-specific winner tracking
        self.assertEqual(self.instance.stats.get("First Serve Winners"), [1, 0])
        # Check specific shot tracking
        self.assertEqual(self.instance.stats.get("First Serve Forehand Winners"), [1, 0])
        # Should count as serve in
        self.assertEqual(self.instance.stats.get("First Serves In"), [1, 0])

    def test_player_winner_second_serve(self):
        """Test player winner on second serve"""
        update_match_statistics(self.instance, "Second Serve", "Backhand Winner", "Won")
        
        self.assertEqual(self.instance.stats.get("Winners"), [1, 0])
        self.assertEqual(self.instance.stats.get("Second Serve Winners"), [1, 0])
        self.assertEqual(self.instance.stats.get("Second Serve Backhand Winners"), [1, 0])
        self.assertEqual(self.instance.stats.get("Second Serves In"), [1, 0])

    def test_opponent_winner_first_serve(self):
        """Test when opponent hits a winner"""
        update_match_statistics(self.instance, "First Serve", "Forehand Winner", "Lost")
        
        # Opponent winner should be tracked in Winners[1]
        self.assertEqual(self.instance.stats.get("Winners"), [0, 1])
        self.assertEqual(self.instance.stats.get("First Serve Winners"), [0, 1])
        self.assertEqual(self.instance.stats.get("First Serve Forehand Winners"), [0, 1])
        # Should still count as serve in (serve was good, opponent just hit a winner)
        self.assertEqual(self.instance.stats.get("First Serves In"), [0, 1])

    def test_player_error_first_serve(self):
        """Test when player makes an error"""
        update_match_statistics(self.instance, "First Serve", "Backhand Error", "Lost")
        
        # Player error should be tracked in Errors[0]
        self.assertEqual(self.instance.stats.get("Errors"), [1, 0])
        self.assertEqual(self.instance.stats.get("First Serve Backhand Errors"), [1, 0])
        # Should count as serve in (serve was good, player just made an error)
        self.assertEqual(self.instance.stats.get("First Serves In"), [0, 1])

    def test_opponent_error_second_serve(self):
        """Test when opponent makes an error (player wins)"""
        update_match_statistics(self.instance, "Second Serve", "Serve Opponent Error", "Won")
        
        # Opponent error should be tracked in Errors[1]
        self.assertEqual(self.instance.stats.get("Errors"), [0, 1])
        self.assertEqual(self.instance.stats.get("Second Serve Serve Opponent Errors"), [1, 0])
        # Should count as serve in
        self.assertEqual(self.instance.stats.get("Second Serves In"), [1, 0])

    def test_volley_winner_first_serve(self):
        """Test volley winner tracking"""
        update_match_statistics(self.instance, "First Serve", "Volley Winner", "Won")
        
        self.assertEqual(self.instance.stats.get("Winners"), [1, 0])
        self.assertEqual(self.instance.stats.get("First Serve Winners"), [1, 0])
        self.assertEqual(self.instance.stats.get("First Serve Volley Winners"), [1, 0])
        self.assertEqual(self.instance.stats.get("First Serves In"), [1, 0])

    def test_multiple_points_accumulation(self):
        """Test that multiple points accumulate correctly"""
        # First serve ace
        update_match_statistics(self.instance, "First Serve", "Ace", "Won")
        # Second serve winner
        update_match_statistics(self.instance, "Second Serve", "Forehand Winner", "Won")
        # Player error
        update_match_statistics(self.instance, "First Serve", "Backhand Error", "Lost")
        # Opponent error
        update_match_statistics(self.instance, "Second Serve", "Serve Opponent Error", "Won")
        # Double fault
        update_match_statistics(self.instance, "Double Fault", "Double Fault", "Lost")

        # Check accumulated totals
        self.assertEqual(self.instance.stats.get("Aces"), [1, 0])  # 1 ace
        self.assertEqual(self.instance.stats.get("Winners"), [1, 0])  # 1 winner (not counting ace)
        self.assertEqual(self.instance.stats.get("Errors"), [1, 1])  # 1 player error, 1 opponent error
        self.assertEqual(self.instance.stats.get("Double Faults"), [1, 0])  # 1 double fault
        
        # Check serve accuracy
        self.assertEqual(self.instance.stats.get("First Serves In"), [1, 1])  # 1 won, 1 lost
        self.assertEqual(self.instance.stats.get("Second Serves In"), [2, 0])  # 2 won, 0 lost

    def test_serve_specific_tracking(self):
        """Test that serve-specific stats are tracked correctly"""

        # Player wins point with a forehand winner on first serve
        update_match_statistics(self.instance, "First Serve", "Forehand Winner", "Won")
        self.assertEqual(self.instance.stats.get("First Serve Forehand Winners"), [1, 0])
        self.assertEqual(self.instance.stats.get("Winners"), [1, 0])
        self.assertEqual(self.instance.stats.get("First Serves In"), [1, 0])

        # Player wins point with a backhand winner on first serve
        update_match_statistics(self.instance, "First Serve", "Backhand Winner", "Won")
        self.assertEqual(self.instance.stats.get("First Serve Backhand Winners"), [1, 0])
        self.assertEqual(self.instance.stats.get("Winners"), [2, 0])
        self.assertEqual(self.instance.stats.get("First Serves In"), [2, 0])

        # Player loses point due to volley error on first serve
        update_match_statistics(self.instance, "First Serve", "Volley Error", "Lost")
        self.assertEqual(self.instance.stats.get("First Serve Volley Errors"), [1, 0])
        self.assertEqual(self.instance.stats.get("Errors"), [1, 0])
        self.assertEqual(self.instance.stats.get("First Serves In"), [2, 1])  # 3rd serve was also "in"


    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Same shot type multiple times
        for _ in range(5):
            update_match_statistics(self.instance, "Second Serve", "Forehand Winner", "Won")
        
        self.assertEqual(self.instance.stats.get("Winners"), [5, 0])
        self.assertEqual(self.instance.stats.get("Second Serve Winners"), [5, 0])
        self.assertEqual(self.instance.stats.get("Second Serve Forehand Winners"), [5, 0])
        self.assertEqual(self.instance.stats.get("Second Serves In"), [5, 0])

    def test_different_error_types(self):
        """Test different types of errors are tracked"""
        update_match_statistics(self.instance, "First Serve", "Forehand Error", "Lost")
        update_match_statistics(self.instance, "Second Serve", "Backhand Error", "Lost")
        update_match_statistics(self.instance, "First Serve", "Volley Error", "Lost")
        
        # All should contribute to general error count
        self.assertEqual(self.instance.stats.get("Errors"), [3, 0])
        
        # Check specific error tracking
        self.assertEqual(self.instance.stats.get("First Serve Forehand Errors"), [1, 0])
        self.assertEqual(self.instance.stats.get("Second Serve Backhand Errors"), [1, 0])
        self.assertEqual(self.instance.stats.get("First Serve Volley Errors"), [1, 0])

    def test_opponent_scenarios(self):
        """Test various opponent scenarios"""
        # Opponent winners
        update_match_statistics(self.instance, "First Serve", "Forehand Winner", "Lost")
        update_match_statistics(self.instance, "Second Serve", "Backhand Winner", "Lost")
        
        # Opponent errors
        update_match_statistics(self.instance, "First Serve", "Serve Opponent Error", "Won")
        update_match_statistics(self.instance, "Second Serve", "Return Opponent Error", "Won")
        
        # Check opponent winner tracking
        self.assertEqual(self.instance.stats.get("Winners"), [0, 2])  # 0 player, 2 opponent
        
        # Check opponent error tracking  
        self.assertEqual(self.instance.stats.get("Errors"), [0, 2])  # 0 player, 2 opponent

    def print_all_stats(self):
        """Helper method to print all stats for debugging"""
        print("\n=== ALL STATISTICS ===")
        for key, value in sorted(self.instance.stats.items()):
            print(f"{key}: {value}")
        print("=====================\n")

    def run_comprehensive_test(self):
        """Run a comprehensive test simulating a real game scenario"""
        print("\n=== COMPREHENSIVE GAME SIMULATION ===")
        
        # Point 1: First serve ace
        update_match_statistics(self.instance, "First Serve", "Ace", "Won")
        print("Point 1: First serve ace")
        
        # Point 2: Second serve winner
        update_match_statistics(self.instance, "Second Serve", "Forehand Winner", "Won")
        print("Point 2: Second serve forehand winner")
        
        # Point 3: Player makes error
        update_match_statistics(self.instance, "First Serve", "Backhand Error", "Lost")
        print("Point 3: First serve, player backhand error")
        
        # Point 4: Opponent winner
        update_match_statistics(self.instance, "Second Serve", "Forehand Winner", "Lost")
        print("Point 4: Second serve, opponent forehand winner")
        
        # Point 5: Double fault
        update_match_statistics(self.instance, "Double Fault", "Double Fault", "Lost")
        print("Point 5: Double fault")
        
        # Point 6: Opponent error
        update_match_statistics(self.instance, "First Serve", "Serve Opponent Error", "Won")
        print("Point 6: First serve, opponent error")
        
        self.print_all_stats()
        
        # Verify expected totals
        expected_totals = {
            "Total Aces": 1,
            "Total Winners (Player)": 1,
            "Total Winners (Opponent)": 1, 
            "Total Errors (Player)": 1,
            "Total Errors (Opponent)": 1,
            "Total Double Faults": 1,
            "Total Points Won": 3,  # Ace + Winner + Opponent Error
            "Total Points Lost": 3   # Player Error + Opponent Winner + Double Fault
        }
        
        print("=== VERIFICATION ===")
        actual_aces = self.instance.stats.get("Aces", [0, 0])[0]
        actual_player_winners = self.instance.stats.get("Winners", [0, 0])[0]
        actual_opponent_winners = self.instance.stats.get("Winners", [0, 0])[1]
        actual_player_errors = self.instance.stats.get("Errors", [0, 0])[0]
        actual_opponent_errors = self.instance.stats.get("Errors", [0, 0])[1]
        actual_double_faults = self.instance.stats.get("Double Faults", [0, 0])[0]
        
        print(f"Aces: Expected {expected_totals['Total Aces']}, Got {actual_aces}")
        print(f"Player Winners: Expected {expected_totals['Total Winners (Player)']}, Got {actual_player_winners}")
        print(f"Opponent Winners: Expected {expected_totals['Total Winners (Opponent)']}, Got {actual_opponent_winners}")
        print(f"Player Errors: Expected {expected_totals['Total Errors (Player)']}, Got {actual_player_errors}")
        print(f"Opponent Errors: Expected {expected_totals['Total Errors (Opponent)']}, Got {actual_opponent_errors}")
        print(f"Double Faults: Expected {expected_totals['Total Double Faults']}, Got {actual_double_faults}")
        
        # Calculate total points
        total_won = actual_aces + actual_player_winners + actual_opponent_errors
        total_lost = actual_player_errors + actual_opponent_winners + actual_double_faults
        
        print(f"Total Points Won: Expected {expected_totals['Total Points Won']}, Got {total_won}")
        print(f"Total Points Lost: Expected {expected_totals['Total Points Lost']}, Got {total_lost}")
        
        return all([
            actual_aces == expected_totals['Total Aces'],
            actual_player_winners == expected_totals['Total Winners (Player)'],
            actual_opponent_winners == expected_totals['Total Winners (Opponent)'],
            actual_player_errors == expected_totals['Total Errors (Player)'],
            actual_opponent_errors == expected_totals['Total Errors (Opponent)'],
            actual_double_faults == expected_totals['Total Double Faults'],
            total_won == expected_totals['Total Points Won'],
            total_lost == expected_totals['Total Points Lost']
        ])

if __name__ == "__main__":
    # Run the comprehensive test first
    test_instance = TestMatchStatLogic()
    test_instance.setUp()
    
    print("Running comprehensive game simulation...")
    success = test_instance.run_comprehensive_test()
    
    if success:
        print("✅ Comprehensive test PASSED!")
    else:
        print("❌ Comprehensive test FAILED!")
    
    print("\nRunning unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)