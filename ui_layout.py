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

        # Layout 
        main_layout = BoxLayout(orientation="horizontal", spacing=10, padding=10)
        self.score_layout = BoxLayout(orientation="vertical", size_hint=(0.7, 1))
        self.score_label = Label(text=get_score_text(self.player_score, self.opponent_score, self.game_score, self.set_score, self.tiebreaker_active), font_size=24)
        self.score_layout.add_widget(self.score_label)
        
        # Buttons
        self.button_layout = BoxLayout(orientation="vertical", size_hint=(0.3, 1))
        self.button_layout.add_widget(Button(text="Won", on_press=lambda btn: self.show_prompt("Won")))
        self.button_layout.add_widget(Button(text="Lost", on_press=lambda btn: self.show_prompt("Lost")))
        self.button_layout.add_widget(Button(text="Generate Graph", on_press=self.generate_graph))
        self.button_layout.add_widget(Button(text="Generate Stats", on_press=self.go_to_stats_page))
        
        main_layout.add_widget(self.score_layout)
        main_layout.add_widget(self.button_layout)
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
