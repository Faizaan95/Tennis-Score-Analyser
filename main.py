from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from ui_layout import TennisScoreLayout
from stats_page import StatsPage
from HomeScreen import HomeScreen
from TiebreakMatchScreen import TiebreakMatchScreen
from kivy.utils import platform

class MainApp(App):
    def build(self):
        # ✅ Ask for storage permissions safely within build()
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(TennisScoreLayout(name="main"))
        sm.add_widget(TiebreakMatchScreen(name="tiebreak_match"))
        sm.add_widget(StatsPage(name="stats"))
        sm.current = "home"
        return sm

if __name__ == "__main__":
    MainApp().run()
