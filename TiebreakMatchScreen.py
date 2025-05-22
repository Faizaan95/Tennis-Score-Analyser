from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class TiebreakMatchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = [0, 0]

        layout = BoxLayout(orientation='vertical', spacing=20, padding=20)

        self.score_label = Label(text=self.get_score_text(), font_size=32)
        layout.add_widget(self.score_label)

        button_layout = BoxLayout(orientation='horizontal')
        button_layout.add_widget(Button(text="Player 1 Scores", on_press=lambda x: self.update_score(0)))
        button_layout.add_widget(Button(text="Player 2 Scores", on_press=lambda x: self.update_score(1)))
        layout.add_widget(button_layout)

        layout.add_widget(Button(text="End Tiebreak", on_press=self.end_tiebreak))

        self.add_widget(layout)

    def get_score_text(self):
        return f"{self.score[0]} - {self.score[1]}"

    def update_score(self, player_index):
        self.score[player_index] += 1
        self.score_label.text = self.get_score_text()

    def end_tiebreak(self, instance):
        self.manager.current = "home"