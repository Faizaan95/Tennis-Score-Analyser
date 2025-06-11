import unittest
from score_manager import update_match_statistics

class DummyInstance:
    def __init__(self):
        self.stats = {}

class TestMatchStatLogic(unittest.TestCase):

    def setUp(self):
        self.instance = DummyInstance()

    def test_ace_first_serve(self):
        update_match_statistics(self.instance, "First Serve", "Ace", "Won")
        self.assertEqual(self.instance.stats.get("Aces"), [1, 0])
        self.assertEqual(self.instance.stats.get("First Serve Aces"), [1, 0])

    def test_dropshot_error_by_player(self):
        update_match_statistics(self.instance, "First Serve", "Dropshot Error", "Lost")
        self.assertEqual(self.instance.stats.get("Dropshot Errors"), [1, 0])
        self.assertEqual(self.instance.stats.get("First Serve Dropshot Errors"), [1, 0])

    def test_opponent_winner(self):
        update_match_statistics(self.instance, "Second Serve", "Backhand Winner", "Lost")
        self.assertEqual(self.instance.stats.get("Opponent Winners"), [0, 1])
        self.assertEqual(self.instance.stats.get("Second Serve Backhand Winners"), [0, 1])

    def test_player_winner(self):
        update_match_statistics(self.instance, "Second Serve", "Forehand Winner", "Won")
        self.assertEqual(self.instance.stats.get("Forehand Winners"), [1, 0])
        self.assertEqual(self.instance.stats.get("Winners"), [1, 0])
        self.assertEqual(self.instance.stats.get("Second Serve Forehand Winners"), [1, 0])

    def test_opponent_error(self):
        update_match_statistics(self.instance, "First Serve", "Opponent Error", "Won")
        self.assertEqual(self.instance.stats.get("Opponent Errors"), [0, 1])
        self.assertEqual(self.instance.stats.get("First Serve Opponent Errors"), [1, 0])

    def test_player_error(self):
        update_match_statistics(self.instance, "Second Serve", "Backhand Error", "Lost")
        self.assertEqual(self.instance.stats.get("Backhand Errors"), [1, 0])
        self.assertEqual(self.instance.stats.get("Errors"), [1, 0])
        self.assertEqual(self.instance.stats.get("Second Serve Backhand Errors"), [1, 0])

    def test_double_fault(self):
        update_match_statistics(self.instance, "Double Fault", "Double Fault", "Lost")
        self.assertEqual(self.instance.stats.get("Double Faults"), [1, 0])

    def test_multiple_stats_combined(self):
        update_match_statistics(self.instance, "First Serve", "Forehand Winner", "Won")
        update_match_statistics(self.instance, "First Serve", "Forehand Winner", "Won")
        update_match_statistics(self.instance, "Second Serve", "Backhand Error", "Lost")
        update_match_statistics(self.instance, "First Serve", "Dropshot Error", "Lost")
        update_match_statistics(self.instance, "Second Serve", "Ace", "Won")

        self.assertEqual(self.instance.stats.get("Forehand Winners"), [2, 0])
        self.assertEqual(self.instance.stats.get("Winners"), [2, 0])
        self.assertEqual(self.instance.stats.get("First Serve Forehand Winners"), [2, 0])

        self.assertEqual(self.instance.stats.get("Backhand Errors"), [1, 0])
        self.assertEqual(self.instance.stats.get("Dropshot Errors"), [1, 0])
        self.assertEqual(self.instance.stats.get("Errors"), [2, 0])

        self.assertEqual(self.instance.stats.get("Second Serve Backhand Errors"), [1, 0])
        self.assertEqual(self.instance.stats.get("First Serve Dropshot Errors"), [1, 0])

        self.assertEqual(self.instance.stats.get("Aces"), [1, 0])
        self.assertEqual(self.instance.stats.get("Second Serve Aces"), [1, 0])


if __name__ == "__main__":
    unittest.main()
