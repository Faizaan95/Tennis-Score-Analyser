import os
from share_utils import generate_stats_image
from kivy.core.image import Image as CoreImage
import logging

# Configure logging (creates a log file for errors)
logging.basicConfig(
    filename="app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DEBUG_MODE = True


# FULLY CORRECTED version that properly interprets the data structure
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
                
                if DEBUG_MODE:
                    print(f"🔢 Detailed Error Points: Player {player_count} → Opponent points, Opponent {opponent_count} → Player points from '{key}'")
    # Final totals
    total_points_played = player_points_won + opponent_points_won
    win_percentage = (player_points_won / total_points_played * 100) if total_points_played else 0
    ace_percentage = (player_total_aces / player_points_won * 100) if player_points_won else 0
    winner_percentage = (player_total_winners / player_points_won * 100) if player_points_won else 0
    double_fault_percentage = (player_double_faults / total_points_played * 100) if total_points_played else 0
    error_percentage = (player_total_errors / total_points_played * 100) if total_points_played else 0

    stats = {
        "Total Points Won": player_points_won,
        "Total Points Lost": total_points_played - player_points_won,
        "Win Percentage": round(win_percentage, 2),

        # Serving Stats
        "Aces": [player_total_aces, opponent_total_aces],
        "First Serve Aces": [player_first_serve_aces, opponent_first_serve_aces],
        "Second Serve Aces": [player_second_serve_aces, opponent_second_serve_aces],
        "Double Faults": [player_double_faults, opponent_double_faults],
        "First Serves In": [player_first_serves_in, opponent_first_serves_in],
        "Second Serves In": [player_second_serves_in, opponent_second_serves_in],

        # Shot Making Stats
        "Winners": [player_total_winners, opponent_total_winners],
        "First Serve Winners": [player_first_serve_winners, opponent_first_serve_winners],
        "Second Serve Winners": [player_second_serve_winners, opponent_second_serve_winners],
        "Errors": [player_total_errors, opponent_total_errors],

        # Percentages
        "Ace Percentage": round(ace_percentage, 2),
        "Winner Percentage": round(winner_percentage, 2),
        "Double Fault Percentage": round(double_fault_percentage, 2),
        "Error Percentage": round(error_percentage, 2),
    }

    if DEBUG_MODE:
        print(f"FINAL PROCESSED STATS: {stats}")
        print(f"  player_points_won = {player_points_won}")
        print(f"  opponent_points_won = {opponent_points_won}")

    return stats
