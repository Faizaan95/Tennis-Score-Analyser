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
    """CORRECTED: Processes all match statistics without double counting."""

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
            if DEBUG_MODE:
                print(f"🔢 Aces: +{player_count} player, +{opponent_count} opponent")

        # Serve-specific aces
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
            if DEBUG_MODE:
                print(f"🔢 Double Faults: +{opponent_count} player, +{player_count} opponent")

        # Winners
        elif key == "Winners":
            player_total_winners = player_count
            opponent_total_winners = opponent_count
            # No point counting here — specific shots already handle it

        # Errors
        elif key == "Errors":
            player_total_errors = player_count
            opponent_total_errors = opponent_count

        # Serves In
        elif key == "First Serves In":
            player_first_serves_in = player_count
            opponent_first_serves_in = opponent_count

        elif key == "Second Serves In":
            player_second_serves_in = player_count
            opponent_second_serves_in = opponent_count

        # First Serve Winners
        elif (
            "First Serve" in key and "Winner" in key
            and key != "First Serve Winners"  # Avoid double-counting
        ):

            player_first_serve_winners += player_count
            opponent_first_serve_winners += opponent_count
            player_points_won += player_count
            opponent_points_won += opponent_count
            if DEBUG_MODE:
                print(f"🔢 Serve Winner (1st): +{player_count} player, +{opponent_count} opponent from '{key}'")

        # Second Serve Winners
        elif (
            "Second Serve" in key and "Winner" in key
            and key != "Second Serve Winners"  # Avoid double-counting
        ):

            player_second_serve_winners += player_count
            opponent_second_serve_winners += opponent_count
            player_points_won += player_count
            opponent_points_won += opponent_count
            if DEBUG_MODE:
                print(f"🔢 Serve Winner (2nd): +{player_count} player, +{opponent_count} opponent from '{key}'")

        # Other Winners (non-serve)
        elif (
            "Winner" in key
            and "First Serve" not in key
            and "Second Serve" not in key
        ):
            player_points_won += player_count
            opponent_points_won += opponent_count
            if DEBUG_MODE:
                print(f"🔢 Groundstroke/Other Winner: +{player_count} player, +{opponent_count} opponent from '{key}'")

        # Other Errors (non-DF)
        elif "Error" in key and key != "Double Faults":
            opponent_points_won += player_count
            player_points_won += opponent_count
            if DEBUG_MODE:
                print(f"🔢 Error: +{opponent_count} player, +{player_count} opponent from '{key}'")

    total_points_played = player_points_won + opponent_points_won

    if DEBUG_MODE:
        print(f"\n=== FINAL TOTALS ===")
        print(f"Points Won by Player: {player_points_won}")
        print(f"Points Won by Opponent: {opponent_points_won}")
        print(f"First Serve Winners - Player: {player_first_serve_winners}, Opponent: {opponent_first_serve_winners}")
        print(f"Second Serve Winners - Player: {player_second_serve_winners}, Opponent: {opponent_second_serve_winners}")
        print(f"Total Points Played: {total_points_played}")
        print("=== END TOTALS ===\n")

    # Percentages
    win_percentage = (player_points_won / total_points_played * 100) if total_points_played else 0
    ace_percentage = (player_total_aces / player_points_won * 100) if player_points_won else 0
    winner_percentage = (player_total_winners / player_points_won * 100) if player_points_won else 0
    double_fault_percentage = (player_double_faults / total_points_played * 100) if total_points_played else 0

    stats = {
        "Total Points Won": player_points_won,
        "Total Points Lost": opponent_points_won,
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
    }

    if DEBUG_MODE:
        print(f"FINAL PROCESSED STATS: {stats}")

    return stats


# ALSO, here's the issue with your update_match_statistics function:
# The ace detection is wrong. You need to fix this in your score_manager.py:

def update_match_statistics_FIXED(instance, serve, point_type, result):
    """Update match statistics based on the point played."""
    
    player_serving = getattr(instance, "is_player1_serving", True)

    try:
        if DEBUG_MODE:
            import traceback
            print(f"📊 STATS CALL: serve='{serve}', point_type='{point_type}', result='{result}'")

        # Handle Double Fault specifically
        if serve == "Double Fault" and result == "Lost":
            if "Double Faults" not in instance.stats:
                instance.stats["Double Faults"] = [0, 0]
            instance.stats["Double Faults"][0] += 1
            if DEBUG_MODE:
                print("📊 Tracked: Double Faults")
            return

        # *** FIX: Handle Ace properly ***
        # Check if this is an ace (unreturnable serve)
        if (serve in ["First Serve", "Second Serve"] and 
            point_type == "Ace" and result == "Won"):
            
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
                print(f"📊 Tracked: Ace on {serve}")
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
            shot_type, outcome = point_parts[0], point_parts[1]
            
            # Track aggregate winners and errors
            if result == "Won":
                if "Winner" in outcome and serve not in ["First Serve", "Second Serve"]:
                    instance.stats.setdefault("Winners", [0,0])[0 if player_serving else 1] += 1
                elif "Error" in outcome:
                    instance.stats.setdefault("Errors", [0,0])[1 if player_serving else 0] += 1
                    
            elif result == "Lost":
                if "Winner" in outcome and serve not in ["First Serve", "Second Serve"]:
                    instance.stats.setdefault("Winners", [0,0])[1 if player_serving else 0] += 1
                elif "Error" in outcome:
                    instance.stats.setdefault("Errors", [0,0])[0 if player_serving else 1] += 1

            # Track detailed shot stats
            if serve in ["First Serve", "Second Serve"]:
                serve_shot_key = f"{'Player' if player_serving else 'Opponent'} {serve} {point_type}s"
                if serve_shot_key not in instance.stats:
                    instance.stats[serve_shot_key] = [0, 0]
                
                # The key insight: this tracks WHO made the shot, not who won the point
                if player_serving:
                    if result == "Won":
                        instance.stats[serve_shot_key][0] += 1  # Player made the shot
                    else:
                        instance.stats[serve_shot_key][1] += 1  # Opponent made the shot
                else:
                    if result == "Won":
                        instance.stats[serve_shot_key][1] += 1  # Opponent made the shot  
                    else:
                        instance.stats[serve_shot_key][0] += 1  # Player made the shot

    except Exception as e:
        logging.error(f"Error updating match statistics: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error updating statistics: {e}")

    if DEBUG_MODE:
        print(f"📈 Current Stats: {instance.stats}")