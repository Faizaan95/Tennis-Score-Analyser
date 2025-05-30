from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from stats_generator import generate_stats_image, generate_stats_pdf, share_file
import logging
from stats_generator import collect_stats
# Configure logging (creates a log file for errors)
logging.basicConfig(
    filename="app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class StatsPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.previous_screen = "main"  # default fallback
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

    def update_stats(self, raw_stats):
        
        stats = collect_stats(raw_stats) 
        print(f"RECEIVED IN STATS PAGE: {stats}")  # Debugging print

        if not stats:
            print("WARNING: stats is empty!")

        """ Ensures all required stats are available before displaying """
        default_stats = {
            "First Serve Winners": [0, 0],
            "Second Serve Winners": [0, 0],
            "First Serve Aces": [0, 0],
            "Second Serve Aces": [0, 0],
            "First Serve Volleys": [0, 0],
            "Second Serve Volleys": [0, 0],
            "Double Faults": [0, 0]
        }

        for key in default_stats:
            if key not in stats:
                stats[key] = default_stats[key]  # Fill missing keys with default values

        # Calculate total points
        total_points_won = (
            stats["First Serve Winners"][0] + stats["Second Serve Winners"][0] +
            stats["First Serve Aces"][0] + stats["Second Serve Aces"][0] +
            stats["First Serve Volleys"][0] + stats["Second Serve Volleys"][0]
        )
        total_points_lost = (
            stats["First Serve Winners"][1] + stats["Second Serve Winners"][1] +
            stats["First Serve Aces"][1] + stats["Second Serve Aces"][1] +
            stats["First Serve Volleys"][1] + stats["Second Serve Volleys"][1]
        ) + stats["Double Faults"][0]  # Double faults count as lost points
        total_points_played = total_points_won + total_points_lost

        # Avoid division by zero
        win_percentage = (total_points_won / total_points_played * 100) if total_points_played > 0 else 0

        # Update UI with formatted stats
        self.stats_label.text = (
            f"Match Statistics:\n\n"
            f"Total Points Won: {stats['Total Points Won']}\n"
            f"Total Points Lost: {stats['Total Points Lost']}\n"
            f"Win Percentage: {stats['Win Percentage']:.2f}%\n\n"

            f"Aces (First Serve): {stats['Aces (First Serve)'][0]} | {stats['Aces (First Serve)'][1]}\n"
            f"Aces (Second Serve): {stats['Aces (Second Serve)'][0]} | {stats['Aces (Second Serve)'][1]}\n"

            f"Winners (First Serve): {stats['Winners (First Serve)'][0]} | {stats['Winners (First Serve)'][1]}\n"
            f"Winners (Second Serve): {stats['Winners (Second Serve)'][0]} | {stats['Winners (Second Serve)'][1]}\n"

            f"Volleys (First Serve): {stats['Volleys (First Serve)'][0]} | {stats['Volleys (First Serve)'][1]}\n"
            f"Volleys (Second Serve): {stats['Volleys (Second Serve)'][0]} | {stats['Volleys (Second Serve)'][1]}\n\n"

            f"Double Faults: {stats['Double Faults'][0]}"
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
        self.manager.current = self.previous_screen
