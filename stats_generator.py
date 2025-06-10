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




def collect_stats(match_stats):
    print(f"RECEIVED IN collect_stats(): {match_stats}")  

    if not match_stats:
        print("WARNING: match_stats is empty!")

    # Ensure essential aggregate keys exist
    essential_keys = [
        "Winners", "Errors", "Double Faults", "Opponent Errors", "Opponent Winners", "Aces"
    ]
    for key in essential_keys:
        if key not in match_stats:
            match_stats[key] = [0, 0]

    # --- Aggregating First/Second Serve Winners ---
    first_serve_winners = [0, 0]
    second_serve_winners = [0, 0]
    first_serve_volleys = [0, 0]
    second_serve_volleys = [0, 0]
    first_serve_aces = match_stats.get("First Serve Aces", [0, 0])
    second_serve_aces = match_stats.get("Second Serve Aces", [0, 0])

    for key, val in match_stats.items():
        if key.startswith("First Serve") and "Winner" in key:
            first_serve_winners[0] += val[0]
            first_serve_winners[1] += val[1]
        if key.startswith("Second Serve") and "Winner" in key:
            second_serve_winners[0] += val[0]
            second_serve_winners[1] += val[1]
        if key.startswith("First Serve") and "Volley" in key:
            first_serve_volleys[0] += val[0]
            first_serve_volleys[1] += val[1]
        if key.startswith("Second Serve") and "Volley" in key:
            second_serve_volleys[0] += val[0]
            second_serve_volleys[1] += val[1]

    total_points_won = (
        match_stats["Winners"][0] +
        match_stats["Opponent Errors"][1] +
        match_stats["Aces"][0]
    )

    total_points_lost = (
        match_stats["Errors"][0] +
        match_stats["Opponent Winners"][1] +
        match_stats["Double Faults"][0]
    )

    total_points_played = total_points_won + total_points_lost

    # Percentages
    win_percentage = (total_points_won / total_points_played * 100) if total_points_played else 0
    ace_percentage = (match_stats["Aces"][0] / total_points_won * 100) if total_points_won else 0
    winner_percentage = (match_stats["Winners"][0] / total_points_won * 100) if total_points_won else 0
    double_fault_percentage = (match_stats["Double Faults"][0] / total_points_played * 100) if total_points_played else 0

    stats =  {
        "Total Points Won": total_points_won,
        "Total Points Lost": total_points_lost,
        "Win Percentage": round(win_percentage, 2),
        "Aces (First Serve)": first_serve_aces,
        "Aces (Second Serve)": second_serve_aces,
        "Winners (First Serve)": first_serve_winners,
        "Winners (Second Serve)": second_serve_winners,
        "Volleys (First Serve)": first_serve_volleys,
        "Volleys (Second Serve)": second_serve_volleys,
        "Double Faults": match_stats["Double Faults"],
        "Ace Percentage": round(ace_percentage, 2),
        "Winner Percentage": round(winner_percentage, 2),
        "Double Fault Percentage": round(double_fault_percentage, 2)
    }

    print(f"PROCESSED IN collect_stats(): {stats}")  
    return stats
