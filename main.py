from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from ui_layout import TennisScoreLayout
from stats_page import StatsPage
from HomeScreen import HomeScreen
from TiebreakMatchScreen import TiebreakMatchScreen

class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(TennisScoreLayout(name="main"))
        sm.add_widget(TiebreakMatchScreen(name="tiebreak_match"))
        sm.add_widget(StatsPage(name="stats"))  # Stats page
        
        sm.current = "home"  # Start from HomeScreen
        
        return sm

if __name__ == "__main__":
    MainApp().run()
