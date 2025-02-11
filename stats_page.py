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
        """ Updates the stats display with advanced statistics calculations. """
        total_points_won = sum([stats[key][0] for key in stats if key != "Double Fault"])  # Exclude double faults
        total_points_lost = sum([stats[key][1] for key in stats]) + stats["Double Fault"][0]  # Only add double faults to lost points
        total_points_played = total_points_won + total_points_lost

        # Avoid division by zero
        win_percentage = (total_points_won / total_points_played * 100) if total_points_played > 0 else 0
        ace_percentage = (stats["Ace"][0] / total_points_won * 100) if total_points_won > 0 else 0
        winner_percentage = (stats["Winner"][0] / total_points_won * 100) if total_points_won > 0 else 0
        double_fault_percentage = (stats["Double Fault"][0] / total_points_played * 100) if total_points_played > 0 else 0

        stats_text = (
            f"🏆 **Match Statistics:**\n\n"
            f"🎾 **Total Points Won:** {total_points_won}\n"
            f"❌ **Total Points Lost:** {total_points_lost}\n"
            f"📊 **Win Percentage:** {win_percentage:.2f}%\n\n"
            f"🔥 **Aces:** {stats['Ace'][0]} ({ace_percentage:.2f}%)\n"
            f"🎯 **Winners:** {stats['Winner'][0]} ({winner_percentage:.2f}%)\n"
            f"⚠️ **Double Faults:** {stats['Double Fault'][0]} ({double_fault_percentage:.2f}%)\n\n"
            f"🏓 **Volleys Won:** {stats['Volley'][0]}\n"
            f"🏓 **Volleys Lost:** {stats['Volley'][1]}\n"
        )

        self.stats_label.text = stats_text


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
