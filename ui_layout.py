from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from score_manager import update_score, get_score_text
from graph_generator import generate_graph
from stats_generator import collect_stats

# Main screen
class TennisScoreLayout(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Variables
        self.player_score = 0
        self.opponent_score = 0
        self.game_score = [0, 0]  # [Player Games, Opponent Games]
        self.set_score = [0, 0]  # [Player Sets, Opponent Sets]
        self.tiebreaker_active = False
        self.is_player1_serving = True  # Player 1 starts as the server

        # Track advanced stats
        self.stats = {
            "First Serve Winners": [0, 0],
            "Second Serve Winners": [0, 0],
            "First Serve Aces": [0, 0],
            "Second Serve Aces": [0, 0],
            "First Serve Volleys": [0, 0],
            "Second Serve Volleys": [0, 0],
            "Double Faults": [0, 0]  # Stays independent
        }
        
        self.history = []  # Stores multiple past states for undo actions

        # Layout
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Score display with server indicator
        self.score_label = Label(text=self.get_score_display(), font_size=24)
        main_layout.add_widget(self.score_label)

        # Buttons layout
        self.button_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.2))
        self.button_layout.add_widget(Button(text="Won", on_press=lambda btn: self.show_serve_prompt("Won")))
        self.button_layout.add_widget(Button(text="Lost", on_press=lambda btn: self.show_serve_prompt("Lost")))
        self.button_layout.add_widget(Button(text="Switch Server", on_press=self.switch_server))
        self.button_layout.add_widget(Button(text="Generate Stats", on_press=self.go_to_stats_page))
        self.button_layout.add_widget(Button(text="End Match", on_press=self.generate_graph))
        
        main_layout.add_widget(self.button_layout)

        # Live stats label
        self.live_stats_label = Label(text=self.get_live_stats_text(), font_size=20, size_hint=(1, 0.1))
        main_layout.add_widget(self.live_stats_label)  # Added live stats at the bottom

        self.add_widget(main_layout)

    def get_score_display(self):
        """ Returns formatted score text with server indicator. """
        server_dot_p1 = "• " if self.is_player1_serving else ""
        server_dot_p2 = "• " if not self.is_player1_serving else ""

        return (f"{server_dot_p1}Player 1: {self.player_score} - {self.opponent_score} {server_dot_p2}\n"
                f"Games: {self.game_score[0]} - {self.game_score[1]}\n"
                f"Sets: {self.set_score[0]} - {self.set_score[1]}")

    def switch_server(self, instance):
        """ Manually switch the server. """
        self.is_player1_serving = not self.is_player1_serving
        self.score_label.text = self.get_score_display()

    def show_serve_prompt(self, result):
        """ Ask for First Serve, Second Serve, or Double Fault before selecting Shot Type. """
        if self.is_player1_serving:
            serve_options = ["First Serve", "Second Serve"] if result == "Won" else ["First Serve", "Second Serve", "Double Fault"]
        else:
            serve_options = ["First Serve", "Second Serve", "Double Fault"] if result == "Won" else ["First Serve", "Second Serve"]

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        for serve in serve_options:
            btn = Button(
                text=serve, 
                on_press=lambda btn, serve=serve: self.update_score(serve, "Double Fault", result) if serve == "Double Fault" else self.show_shot_type_prompt(serve, result)
            )
            popup_layout.add_widget(btn)

        self.popup = Popup(title="Select Serve Type", content=popup_layout, size_hint=(0.5, 0.5))
        self.popup.open()

    def show_shot_type_prompt(self, serve, result):
        """ Ask for Shot Type after Serve selection. """
        
        # Close previous popup
        self.popup.dismiss()

        # 🔹 Determine valid shot types based on serve/receive situation
        if self.is_player1_serving:
            if result == "Won":
                shot_types = ["Volley", "Winner", "Ace"]
            else:
                shot_types = ["Volley", "Winner", "Ace"]
        else:
            if result == "Won":
                shot_types = ["Volley", "Winner"]
            else:
                shot_types = ["Ace", "Volley", "Winner"]

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        for shot in shot_types:
            btn = Button(text=shot, on_press=lambda btn, shot=shot: self.update_score(serve, shot, result))
            popup_layout.add_widget(btn)

        self.popup = Popup(title="Select Shot Type", content=popup_layout, size_hint=(0.5, 0.5))
        self.popup.open()

    def update_score(self, serve, point_type, result):
        """ Updates the score and stats based on serve type, shot type, and result. """

        # Track serve stats
        if serve == "First Serve":
            self.stats["First Serve Won" if result == "Won" else "First Serve Lost"][0 if self.is_player1_serving else 1] += 1
        elif serve == "Second Serve":
            self.stats["Second Serve Won" if result == "Won" else "Second Serve Lost"][0 if self.is_player1_serving else 1] += 1
        elif serve == "Double Fault":
            self.stats["Double Fault"][0 if self.is_player1_serving else 1] += 1

        # Track shot type
        if point_type != "Double Fault":
            self.stats[point_type][0 if result == "Won" else 1] += 1  

        # Store previous game score before updating
        prev_game_score = self.game_score[:]

        # Update score
        self.player_score, self.opponent_score, self.game_score, self.set_score, self.tiebreaker_active, self.stats = update_score(
            self.player_score, self.opponent_score, self.game_score, self.set_score, result, self.tiebreaker_active, None, self.stats
        )

        # 🔹 Switch server if a full game was won/lost
        if self.game_score != prev_game_score and not self.tiebreaker_active:  
            self.is_player1_serving = not self.is_player1_serving  

        # Update UI
        self.score_label.text = self.get_score_display()
        self.live_stats_label.text = self.get_live_stats_text()
        self.popup.dismiss()


    def generate_graph(self, instance):
        """ Generates the score progression graph. """
        generate_graph()

    def go_to_stats_page(self, instance):
        """ Navigates to the stats page and passes updated stats. """
        stats_screen = self.manager.get_screen("stats")
        stats_screen.update_stats(self.stats)  # Pass stats directly
        self.manager.current = "stats"

    def get_live_stats_text(self):
        """ Returns formatted text displaying live stats summary. """
        return (
            f"First Serve Won: {self.stats['First Serve Won'][0]} | {self.stats['First Serve Won'][1]}    "
            f"Second Serve Won: {self.stats['Second Serve Won'][0]} | {self.stats['Second Serve Won'][1]}    "
            f"Double Faults: {self.stats['Double Fault'][0]} | {self.stats['Double Fault'][1]}"
        )

    def undo_last_action(self, instance):
        if self.history:  # Ensure there's a previous state to revert to
            (
                self.player_score,
                self.opponent_score,
                self.game_score,
                self.set_score,
                self.tiebreaker_active,
                self.stats
            ) = self.history.pop()  # Remove and restore the last state

            # Update UI after undo
            self.score_label.text = get_score_text(self.player_score, self.opponent_score, self.game_score, self.set_score, self.tiebreaker_active)

    def generate_graph(self, instance):
        """ Generates the score progression graph. """
        generate_graph()

