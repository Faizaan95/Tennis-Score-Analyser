from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from stats_generator import generate_stats_image
import logging
from stats_generator import collect_stats
from score_manager import get_score_display

# Configure logging (creates a log file for errors)
logging.basicConfig(
    filename="app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class StatsPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.previous_screen = "main"  # default fallback
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        
        

        # Stats display label
        self.stats_label = Label(text="Stats will be displayed here.", font_size=24)
        self.layout.add_widget(self.stats_label)

        # Buttons layout
        button_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.2))
        button_layout.add_widget(Button(text="Download Image", on_press=self.save_as_image))
        button_layout.add_widget(Button(text="Back", on_press=self.go_back))

        self.layout.add_widget(button_layout)
        self.add_widget(self.layout)

    def update_stats(self, data):
        match_stats = data.get("match_stats", {})
        score_summary = data.get("score_summary", {})

        stats = collect_stats(match_stats)  # Compute derived stats
        
        self.is_player1_serving = False

        # Extract score data
        player_score = score_summary.get("player_score", 0)
        opponent_score = score_summary.get("opponent_score", 0)
        game_score = score_summary.get("game_score", [0, 0])
        set_score = score_summary.get("set_score", [0, 0])
        is_serving_p1 = score_summary.get("is_player1_serving", False)

        # Format score
        score_text = get_score_display(
            player_score, opponent_score, game_score, set_score, is_serving_p1, show_server=False
        )

        self.stats_label.text = (
            f"{score_text}\n\n"
            f"Match Statistics:\n\n"
            f"Total Points Won: {stats['Total Points Won']}\n"
            f"Total Points Lost: {stats['Total Points Lost']}\n"
            f"Win Percentage: {stats['Win Percentage']:.2f}%\n\n"

            f"Aces (First Serve): {stats['Aces (First Serve)'][0]} | {stats['Aces (First Serve)'][1]}\n"
            f"Aces (Second Serve): {stats['Aces (Second Serve)'][0]} | {stats['Aces (Second Serve)'][1]}\n"

            f"Winners (First Serve): {stats['Winners (First Serve)'][0]} | {stats['Winners (First Serve)'][1]}\n"
            f"Winners (Second Serve): {stats['Winners (Second Serve)'][0]} | {stats['Winners (Second Serve)'][1]}\n\n"

            f"Errors (Player): {match_stats.get('Errors', [0, 0])[0]}\n"
            f"Opponent Winners: {match_stats.get('Opponent Winners', [0, 0])[1]}\n\n"

            f"Double Faults: {stats['Double Faults'][0]}"
        )
        
                # Optional breakdown
        SHOW_BREAKDOWN = False

        if SHOW_BREAKDOWN:
            breakdown_text = "\nDetailed Breakdown:\n"
            for key in sorted(match_stats.keys()):
                if any(term in key for term in ["Forehand", "Backhand", "Volley", "Smash", "Dropshot", "Lob"]):
                    breakdown_text += f"{key}: {match_stats[key][0]} | {match_stats[key][1]}\n"
            self.stats_label.text += "\n" + breakdown_text




    def save_as_image(self, instance):  # Add 'instance' parameter
        img_path = generate_stats_image(self.stats_label)  # or whatever your stats container is
        if img_path:
            print(f"Image saved at {img_path}")
        else:
            print("Failed to save image")



    def go_back(self, instance):
        self.manager.current = self.previous_screen
