from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=20, padding=40)

        layout.add_widget(Button(
            text=" Standard Match",
            on_press=self.go_to_standard_match
        ))
        layout.add_widget(Button(
            text=" Tiebreak Match",
            on_press=self.go_to_tiebreak_match
        ))

        self.add_widget(layout)

    def go_to_standard_match(self, instance):
        self.manager.current = "main"

    def go_to_tiebreak_match(self, instance):
        self.manager.current = "tiebreak_match"
