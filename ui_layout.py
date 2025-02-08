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
        self.stats = {"Volley": [0, 0], "Winner": [0, 0], "Ace": [0, 0], "Double Fault": [0, 0]}  # Point type
        self.history = []  # Stores multiple past states for undo actions

        # Layout 
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Score display
        self.score_label = Label(text=get_score_text(self.player_score, self.opponent_score, self.game_score, self.set_score, self.tiebreaker_active), font_size=24)
        main_layout.add_widget(self.score_label)

        # Buttons layout
        self.button_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.2))
        self.button_layout.add_widget(Button(text="Won", on_press=lambda btn: self.show_prompt("Won")))
        self.button_layout.add_widget(Button(text="Lost", on_press=lambda btn: self.show_prompt("Lost")))
        self.button_layout.add_widget(Button(text="Undo", on_press=self.undo_last_action))
        self.button_layout.add_widget(Button(text="Generate Graph", on_press=self.generate_graph))
        self.button_layout.add_widget(Button(text="Generate Stats", on_press=self.go_to_stats_page))
        main_layout.add_widget(self.button_layout)

        # Live stats label
        self.live_stats_label = Label(text=self.get_live_stats_text(), font_size=20, size_hint=(1, 0.1))
        main_layout.add_widget(self.live_stats_label)  # Added live stats at the bottom

        self.add_widget(main_layout)

    def show_prompt(self, result):
        options = ["Volley", "Winner", "Ace", "Double Fault"]
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        for option in options:
            btn = Button(text=option, on_press=lambda btn, option=option: self.update_score(option, result))
            popup_layout.add_widget(btn)

        self.popup = Popup(title="Select Point Type", content=popup_layout, size_hint=(0.5, 0.5))
        self.popup.open()

    def update_score(self, point_type, result):
        """ Updates the score and stats based on the selected point type and result. """
        
        self.history.append((
            self.player_score,
            self.opponent_score,
            self.game_score[:],  # Copy list
            self.set_score[:],  # Copy list
            self.tiebreaker_active,
            {k: v[:] for k, v in self.stats.items()}  # Deep copy dictionary
        ))
        if result == "Lost" and point_type == "Double Fault":
            reason = "Double Fault"  # Mark as a double fault loss
        else:
            reason = None  

        # Update stats (track for opponent if it's a double fault)
        if point_type == "Double Fault":
            if result == "Won":  # Player won the point → Opponent made a double fault
                self.stats["Double Fault"][1] += 1  # Increase **opponent's** double fault count
            elif  result == "Lost":  # Player won the point → Opponent made a double fault
                self.stats["Double Fault"][0] += 1
                self.stats["Double Fault"][1] += -1 #opponents count was going up as well without this line of code 
        else:
            self.stats[point_type][0 if result == "Won" else 1] += 1  # Update stats normally


        # Update score
        self.player_score, self.opponent_score, self.game_score, self.set_score, self.tiebreaker_active, self.stats = update_score(
            self.player_score, self.opponent_score, self.game_score, self.set_score, result, self.tiebreaker_active, reason, self.stats
        )

        # Update UI
        self.score_label.text = get_score_text(self.player_score, self.opponent_score, self.game_score, self.set_score, self.tiebreaker_active)
        self.live_stats_label.text = self.get_live_stats_text()  # Update live stats
        self.popup.dismiss()

        # Handle tiebreaker
        if self.tiebreaker_active:
            self.show_tiebreaker_prompt()

    def show_tiebreaker_prompt(self):
        """ Handles tiebreaker UI. """
        self.tiebreaker_popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.tiebreaker_label = Label(text=f"Tiebreaker Score: {self.player_score} - {self.opponent_score}")
        self.tiebreaker_popup_layout.add_widget(self.tiebreaker_label)

        player_btn = Button(text="Player Point", on_press=lambda btn: self.update_tiebreaker(True))
        opponent_btn = Button(text="Opponent Point", on_press=lambda btn: self.update_tiebreaker(False))

        self.tiebreaker_popup_layout.add_widget(player_btn)
        self.tiebreaker_popup_layout.add_widget(opponent_btn)

        self.tiebreaker_popup = Popup(title="Tiebreaker", content=self.tiebreaker_popup_layout, size_hint=(0.5, 0.3))
        self.tiebreaker_popup.open()

    def update_tiebreaker(self, player_won):
        """ Updates tiebreaker score. """
        self.player_score, self.opponent_score, self.game_score, self.set_score, self.tiebreaker_active = update_score(
            self.player_score, self.opponent_score, self.game_score, self.set_score, "Won" if player_won else "Lost", self.tiebreaker_active
        )
        self.score_label.text = get_score_text(self.player_score, self.opponent_score, self.game_score, self.set_score, self.tiebreaker_active)

        self.tiebreaker_label.text = f"Tiebreaker Score: {self.player_score} - {self.opponent_score}"

        if not self.tiebreaker_active:  
            self.tiebreaker_popup.dismiss()

    def generate_graph(self, instance):
        """ Generates the score progression graph. """
        generate_graph()

    def go_to_stats_page(self, instance):
        """ Navigates to the stats page and passes updated stats. """
        stats_screen = self.manager.get_screen("stats")
        stats_screen.update_stats(self.stats)  # Pass stats to the stats page
        self.manager.current = "stats"

    def get_live_stats_text(self):
        """ Returns formatted text displaying live stats summary. """
        return (
            f"Volley: {self.stats['Volley'][0]} | {self.stats['Volley'][1]}    "
            f"Winner: {self.stats['Winner'][0]} | {self.stats['Winner'][1]}    "
            f"Ace: {self.stats['Ace'][0]} | {self.stats['Ace'][1]}    "
            f"Double Fault: {self.stats['Double Fault'][0]} | {self.stats['Double Fault'][1]}"
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

    def go_to_stats_page(self, instance):
        """ Navigates to the stats page and passes updated stats. """
        stats_screen = self.manager.get_screen("stats")
        stats_screen.update_stats(self.stats)  # Pass stats to the stats page
        self.manager.current = "stats"