from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from stats_generator import generate_stats_image, generate_stats_pdf, share_file

class StatsPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Stats display label
        self.stats_label = Label(text="Stats will be displayed here.", font_size=24)
        self.layout.add_widget(self.stats_label)

        # Buttons layout
        button_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.2))
        button_layout.add_widget(Button(text="Download Image", on_press=self.save_as_image))
        button_layout.add_widget(Button(text="Download PDF", on_press=self.save_as_pdf))
        button_layout.add_widget(Button(text="Share Image", on_press=self.share_as_image))
        button_layout.add_widget(Button(text="Share PDF", on_press=self.share_as_pdf))
        button_layout.add_widget(Button(text="Back", on_press=self.go_back))

        self.layout.add_widget(button_layout)
        self.add_widget(self.layout)

    def update_stats(self, stats):
        print(f"RECEIVED IN STATS PAGE: {stats}")  # Debugging print

        if not stats:  # If stats is empty, print warning
            print("WARNING: stats is empty!")
        """ Ensures all required stats are available before displaying """
        
        # Ensure all keys exist in stats
        default_stats = {
            "Ace": [0, 0],
            "Winner": [0, 0],
            "Double Fault": [0, 0],
            "Volley": [0, 0]
        }
        
        for key in default_stats:
            if key not in stats:
                stats[key] = default_stats[key]  # Fill missing keys with default values

        total_points_won = sum([stats[key][0] for key in stats if key != "Double Fault"])
        total_points_lost = sum([stats[key][1] for key in stats]) + stats["Double Fault"][0]
        total_points_played = total_points_won + total_points_lost

        win_percentage = (total_points_won / total_points_played * 100) if total_points_played > 0 else 0
        ace_percentage = (stats["Ace"][0] / total_points_won * 100) if total_points_won > 0 else 0
        winner_percentage = (stats["Winner"][0] / total_points_won * 100) if total_points_won > 0 else 0
        double_fault_percentage = (stats["Double Fault"][0] / total_points_played * 100) if total_points_played > 0 else 0

        self.stats_label.text = (
            f"Match Statistics:\n\n"
            f"Total Points Won: {total_points_won}\n"
            f"Total Points Lost: {total_points_lost}\n"
            f"Win Percentage: {win_percentage:.2f}%\n\n"
            f"Aces: {stats['Ace'][0]} ({ace_percentage:.2f}%)\n"
            f"Winners: {stats['Winner'][0]} ({winner_percentage:.2f}%)\n"
            f"Double Faults: {stats['Double Fault'][0]} ({double_fault_percentage:.2f}%)\n\n"
            f"Volleys Won: {stats['Volley'][0]}\n"
            f"Volleys Lost: {stats['Volley'][1]}\n"
        )


    def save_as_image(self, instance):
        img_path = generate_stats_image(self.stats_label.text)
        print(f"Image saved at {img_path}")

    def save_as_pdf(self, instance):
        pdf_path = generate_stats_pdf(self.stats_label.text)
        print(f"PDF saved at {pdf_path}")

    def share_as_image(self, instance):
        img_path = generate_stats_image(self.stats_label.text)
        share_file(img_path)

    def share_as_pdf(self, instance):
        pdf_path = generate_stats_pdf(self.stats_label.text)
        share_file(pdf_path)

    def go_back(self, instance):
        self.manager.current = "main"
