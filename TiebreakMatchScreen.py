from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import logging

from serve_manager import show_serve_prompt, switch_server
from score_manager import get_score_display, undo_last_action
from end_match import End_Match as end_match_popup

# Logging
logging.basicConfig(
    filename="app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class TiebreakMatchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ➕ Game State Initialization
        self.player_score = 0
        self.opponent_score = 0
        self.game_score = [0, 0]
        self.set_score = [0, 0]
        self.tiebreaker_active = True
        self.is_player1_serving = True
        self.selected_serve = None
        self.history = []

        self.stats = {
            "First Serve Winners": [0, 0],
            "Second Serve Winners": [0, 0],
            "First Serve Aces": [0, 0],
            "Second Serve Aces": [0, 0],
            "First Serve Volleys": [0, 0],
            "Second Serve Volleys": [0, 0],
            "Double Faults": [0, 0]
        }

        # Layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.score_label = Label(
            text=self.get_score_text(),
            font_size=28
        )
        main_layout.add_widget(self.score_label)
        
        main_layout.add_widget(Button(
            text="Back to Home",
            size_hint=(1, 0.1),
            on_press=lambda btn: self.go_to_home()
        ))

        # ➕ Buttons
        button_layout = BoxLayout(size_hint=(1, 0.2))
        button_layout.add_widget(Button(text="Won", on_press=lambda btn: show_serve_prompt(self, "Won")))
        button_layout.add_widget(Button(text="Lost", on_press=lambda btn: show_serve_prompt(self, "Lost")))
        button_layout.add_widget(Button(text="Undo", on_press=lambda btn: undo_last_action(self)))
        button_layout.add_widget(Button(text="Switch Server", on_press=lambda btn: switch_server(self, btn)))
        button_layout.add_widget(Button(text="Match Stats", on_press=self.go_to_stats_page))
        button_layout.add_widget(Button(text="End Match", on_press=lambda btn: end_match_popup(self)))

        main_layout.add_widget(button_layout)

        # ➕ Live Stats Label
        self.live_stats_label = Label(
            text=self.get_live_stats_text(),
            font_size=20,
            size_hint=(1, 0.1)
        )
        main_layout.add_widget(self.live_stats_label)

        self.add_widget(main_layout)

    def go_to_stats_page(self, instance):
        stats_screen = self.manager.get_screen("stats")
        stats_screen.previous_screen = "tiebreak_match"
        stats_screen.update_stats(self.stats)
        self.manager.current = "stats"


    def get_live_stats_text(self):
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
        total_points_won = (
            self.stats['First Serve Winners'][0] + self.stats['Second Serve Winners'][0] +
            self.stats['First Serve Aces'][0] + self.stats['Second Serve Aces'][0] +
            self.stats['First Serve Volleys'][0] + self.stats['Second Serve Volleys'][0]
        )

        self.live_stats_label.text = (
            f"Double Faults: {self.stats['Double Faults'][0]}    "
            f"Total Points Won: {total_points_won}"
        )
    def get_score_text(self):
        server_dot_p1 = "• " if self.is_player1_serving else ""
        server_dot_p2 = "• " if not self.is_player1_serving else ""
        return f"{server_dot_p1}Player 1: {self.player_score} - Player 2: {self.opponent_score}{server_dot_p2}"
    
    def go_to_home(self):
        self.manager.current = "home"