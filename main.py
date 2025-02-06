from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from ui_layout import TennisScoreLayout
from stats_page import StatsPage

class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TennisScoreLayout(name="main"))  # Main score tracking screen
        sm.add_widget(StatsPage(name="stats"))  # Stats page
        return sm

if __name__ == "__main__":
    MainApp().run()
