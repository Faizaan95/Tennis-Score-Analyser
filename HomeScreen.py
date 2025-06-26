from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=20, padding=40)


        button_style = {
            "font_size": 50,
            "background_color": (164/255.0, 196/255.0, 255/255.0, 1),
            "color": (1, 1, 1, 1),
            "markup": True
        }
        
        layout.add_widget(Button(
            text=" [b]Standard Match[/b]",
            on_press=self.go_to_standard_match,
            **button_style
        ))
        layout.add_widget(Button(
            text=" [b]Tiebreak Match[/b]",
            on_press=self.go_to_tiebreak_match,
            **button_style
        ))

        self.add_widget(layout)

    def go_to_standard_match(self, instance):
        self.manager.current = "main"

    def go_to_tiebreak_match(self, instance):
        self.manager.current = "tiebreak_match"
