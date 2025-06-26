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
from kivy.uix.gridlayout import GridLayout


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
        self.set_history = []  
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
        
        

        # Score label
        self.score_label = Label(
            text=get_score_display(self.player_score, self.opponent_score, self.game_score, self.set_score, self.is_player1_serving),
            markup=True,
            font_size=36,
            size_hint=(1, 1.8)
        )
        button_style = {
            "font_size": 22,
            "background_color": (164/255.0, 196/255.0, 255/255.0, 1),
            "color": (1, 1, 1, 1),
            "markup": True
        }

        main_layout.add_widget(self.score_label)
        
        main_layout.add_widget(Button(
            text="Back to Home",
            size_hint=(1, 0.3),
            on_press=lambda btn: self.go_to_home(),
            **button_style
        ))

        # Buttons layout
        self.button_layout = GridLayout(cols=2, spacing=10, size_hint=(1, 0.4))

        

        self.button_layout.add_widget(Button(text="[b]Won[/b]", on_press=lambda btn: show_serve_prompt(self, "Won"), **button_style))
        self.button_layout.add_widget(Button(text="[b]Lost[/b]", on_press=lambda btn: show_serve_prompt(self, "Lost"), **button_style))
        self.button_layout.add_widget(Button(text="[b]Undo[/b]", on_press=lambda btn: undo_last_action(self), **button_style))
        self.button_layout.add_widget(Button(text="[b]Switch Server[/b]", on_press=lambda btn: switch_server(self, btn), **button_style))
        self.button_layout.add_widget(Button(text="[b]Match Stats[/b]", on_press=self.go_to_stats_page, **button_style))
        self.button_layout.add_widget(Button(text="[b]End Match[/b]", on_press=lambda btn: end_match_popup(self), **button_style))

        
        
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
        total_points_won = (
            self.stats.get('Aces', [0,0])[0] +
            self.stats.get('Winners', [0,0])[0] +
            self.stats.get('Errors', [0,0])[1]  # Fixed: Changed from 'Opponent Errors' to 'Errors'[1]
        )

        return (
            f"Double Faults: {self.stats['Double Faults'][0]}    "
            f"Total Points Won: {total_points_won}"
        )

    def update_live_stats(self):
        # Use the same calculation logic as collect_stats() for consistency
        total_points_won = (
            self.stats.get('Winners', [0,0])[0] +
            self.stats.get('Errors', [0,0])[1] +  # Opponent errors
            self.stats.get('Aces', [0,0])[0]
        )

        self.live_stats_label.text = (
            f"Double Faults: {self.stats['Double Faults'][0]}    "
            f"Total Points Won: {total_points_won}"
        )
    
    def reset_match(self):
        self.player_score = 0
        self.opponent_score = 0
        self.game_score = [0, 0]
        self.set_score = [0, 0]
        self.tiebreaker_active = False
        self.is_player1_serving = True
        self.stats = {
                "First Serve Winners": [0, 0],
                "Second Serve Winners": [0, 0],
                "First Serve Aces": [0, 0],
                "Second Serve Aces": [0, 0],
                "First Serve Volleys": [0, 0],
                "Second Serve Volleys": [0, 0],
                "Double Faults": [0, 0],
                "Winners": [0, 0],
                "Errors": [0, 0],
                "Opponent Errors": [0, 0],
                "Opponent Winners": [0, 0],
                "Aces": [0, 0]
            }
        self.history.clear()
        self.refresh_score_display()
        self.update_live_stats()




    
    def refresh_score_display(self):
        self.score_label.text = get_score_display(
            self.player_score,
            self.opponent_score,
            self.game_score,
            self.set_score,
            self.is_player1_serving
        )


    def on_pre_enter(self, *args):
        self.refresh_score_display()
        self.update_live_stats()
        
        
    def go_to_home(self):
            self.manager.current = "home"