from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from end_match import End_Match as end_match_popup
from serve_manager import show_serve_prompt,switch_server
import logging
from score_manager import get_score_display  # ✅ Import the function
from score_manager import undo_last_action



# Configure logging (creates a log file for errors)
logging.basicConfig(
    filename="app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Main screen
class TennisScoreLayout(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Variables
        self.player_score = 0
        self.opponent_score = 0
        self.game_score = [0, 0]
        self.set_score = [0, 0]
        self.tiebreaker_active = False
        self.is_player1_serving = True  # Player 1 starts as the server
        self.selected_serve = None  # Store selected serve type
        

        # Track advanced stats
        self.stats = {
            "First Serve Winners": [0, 0],
            "Second Serve Winners": [0, 0],
            "First Serve Aces": [0, 0],
            "Second Serve Aces": [0, 0],
            "First Serve Volleys": [0, 0],
            "Second Serve Volleys": [0, 0],
            "Double Faults": [0, 0]
        }
        
        self.history = []

        # Layout
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        
        

        # Score display with server indicator
        self.score_label = Label(
            text=get_score_display(self.player_score, self.opponent_score, self.game_score, self.set_score, self.is_player1_serving),
            font_size=24
        )
        main_layout.add_widget(self.score_label)
        
        main_layout.add_widget(Button(
            text="Back to Home",
            size_hint=(1, 0.1),
            on_press=lambda btn: self.go_to_home()
        ))

        # Buttons layout
        self.button_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.2))
        self.button_layout.add_widget(Button(text="Won", on_press=lambda btn: show_serve_prompt(self, "Won")))  # ✅ Fixed
        self.button_layout.add_widget(Button(text="Lost", on_press=lambda btn: show_serve_prompt(self, "Lost")))  # ✅ Fixed
        self.button_layout.add_widget(Button(text="Undo", on_press=lambda btn: undo_last_action(self)))
        self.button_layout.add_widget(Button(text="Switch Server", on_press=lambda btn: switch_server(self, btn)))  # ✅ Call the external function
        self.button_layout.add_widget(Button(text="Match Stats", on_press=self.go_to_stats_page))
        self.button_layout.add_widget(Button(text="End Match", on_press=lambda btn: end_match_popup(self)))

        
        
        main_layout.add_widget(self.button_layout)

        # Live stats label
        self.live_stats_label = Label(text=self.get_live_stats_text(), font_size=20, size_hint=(1, 0.1))
        main_layout.add_widget(self.live_stats_label)

        self.add_widget(main_layout)


    

    def go_to_stats_page(self, instance):
        stats_screen = self.manager.get_screen("stats")
        stats_screen.previous_screen = "main"
        
        stats_screen.update_stats({
            "match_stats": self.stats,
            "score_summary": {
                "player_score": self.player_score,
                "opponent_score": self.opponent_score,
                "game_score": self.game_score,
                "set_score": self.set_score,
                "tiebreaker_active": self.tiebreaker_active,
                "is_player1_serving": self.is_player1_serving
            }
        })

        self.manager.current = "stats"

    def get_live_stats_text(self):
        """ Returns formatted text displaying live stats summary. """
        
        total_points_won = (
            self.stats['First Serve Winners'][0] + self.stats['Second Serve Winners'][0] +
            self.stats['First Serve Aces'][0] + self.stats['Second Serve Aces'][0] +
            self.stats['First Serve Volleys'][0] + self.stats['Second Serve Volleys'][0]
        )

        return (
            
            f"Double Faults: {self.stats['Double Faults'][0]}    "
            f"Total Points Won: {total_points_won}"
        )



    def update_live_stats(self):
        """Updates the live stats label dynamically."""
        
        total_points_won = (
            self.stats['First Serve Winners'][0] + self.stats['Second Serve Winners'][0] +
            self.stats['First Serve Aces'][0] + self.stats['Second Serve Aces'][0] +
            self.stats['First Serve Volleys'][0] + self.stats['Second Serve Volleys'][0]
        )
        
        self.live_stats_label.text = (
            f"Double Faults: {self.stats['Double Faults'][0]}    "
            f"Total Points Won: {total_points_won}"
        )


    

    def go_to_home(self):
            self.manager.current = "home"