from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from stats_generator import generate_stats_image, generate_stats_pdf, share_file

class StatsPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        self.stats_label = Label(text="Stats will be displayed here.", font_size=24)
        self.layout.add_widget(self.stats_label)

        button_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.2))
        button_layout.add_widget(Button(text="Download Image", on_press=self.save_as_image))
        button_layout.add_widget(Button(text="Download PDF", on_press=self.save_as_pdf))
        button_layout.add_widget(Button(text="Share Image", on_press=self.share_as_image))
        button_layout.add_widget(Button(text="Share PDF", on_press=self.share_as_pdf))
        button_layout.add_widget(Button(text="Back", on_press=self.go_back))

        self.layout.add_widget(button_layout)
        self.add_widget(self.layout)

    def update_stats(self, stats):
        stats_text = "\n".join([f"{key}: {stats[key][0]} - {stats[key][1]}" for key in stats])
        self.stats_label.text = f"Match Statistics:\n{stats_text}"

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
