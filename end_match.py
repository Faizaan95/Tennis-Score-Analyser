import os
import json
import logging
from datetime import datetime
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.utils import platform
from reportlab.pdfgen import canvas
from share_utils import share_file

# Logging
logging.basicConfig(filename="app_errors.log", level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def End_Match(instance):
    """ Prompts user for folder name and then finalizes match saving. """
    content = BoxLayout(orientation='vertical', spacing=10, padding=10)
    name_input = TextInput(hint_text="Enter player/folder name", multiline=False)
    content.add_widget(name_input)

    def on_confirm(btn):
        player_folder = name_input.text.strip() or "Player"
        popup.dismiss()
        finalize_match(instance, player_folder)  # ✅ Use the passed instance here

    confirm_button = Button(text="Save Match")
    confirm_button.bind(on_press=on_confirm)
    content.add_widget(confirm_button)

    popup = Popup(title="Name the Match Folder", content=content,
                  size_hint=(0.8, 0.4))
    popup.open()

def finalize_match(instance, folder_name):
    """ Finalizes match: saves JSON + PDF + optional share. """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_folder = f"match_data/{folder_name}_{timestamp}"
        os.makedirs(base_folder, exist_ok=True)

        # 1. ✅ Save JSON
        json_path = os.path.join(base_folder, "match_stats.json")
        with open(json_path, "w") as f:
            json.dump(instance.stats, f, indent=4)
        print(f"✅ JSON saved at {json_path}")

        # 2. ✅ Save PDF
        pdf_path = os.path.join(base_folder, "match_summary.pdf")
        c = canvas.Canvas(pdf_path)
        y = 800
        c.drawString(100, y, f"Match Summary - {folder_name}")
        y -= 30
        for k, v in instance.stats.items():
            c.drawString(100, y, f"{k}: {v}")
            y -= 20
        c.save()
        print(f"✅ PDF saved at {pdf_path}")

        # 3. ✅ Optional: Share (only PDF or JSON on Android)
        if platform == "android":
            share_file(pdf_path, mime_type="application/pdf")
            # Or use: share_file(json_path, mime_type="application/json")

        # 4. ✅ Reset match state
        instance.player_score = 0
        instance.opponent_score = 0
        instance.game_score = [0, 0]
        instance.set_score = [0, 0]
        instance.tiebreaker_active = False
        instance.stats = {
            "First Serve Winners": [0, 0],
            "Second Serve Winners": [0, 0],
            "First Serve Aces": [0, 0],
            "Second Serve Aces": [0, 0],
            "First Serve Volleys": [0, 0],
            "Second Serve Volleys": [0, 0],
            "Double Faults": [0, 0]
        }
        instance.history.clear()
        instance.score_label.text = "Match Ended. Start a new match!"
        instance.update_live_stats()
        instance.manager.current = "home"
        print("✅ Match reset and returned to home.")

    except Exception as e:
        logging.error(f"❌ Error in finalize_match: {e}")
        print(f"❌ Failed to finalize match: {e}")

