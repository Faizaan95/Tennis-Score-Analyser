import os
import json
import logging
from datetime import datetime
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.filechooser import FileChooserListView
from kivy.utils import platform
import csv

# Logging
logging.basicConfig(
    filename="app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def End_Match(instance):
    content = BoxLayout(orientation="vertical", spacing=10, padding=10)
    name_input = TextInput(hint_text="Enter match/folder name", multiline=False)
    content.add_widget(name_input)

    # Manual path switch
    row = BoxLayout(size_hint_y=None, height="40dp", spacing=10)
    row.add_widget(Label(text="Choose location manually"))
    custom_switch = Switch(active=False)
    row.add_widget(custom_switch)
    content.add_widget(row)

    def on_confirm(btn):
        folder_name = name_input.text.strip() or "Player"
        popup.dismiss()
        if custom_switch.active:
            open_path_chooser(instance, folder_name)
        else:
            finalize_match(instance, folder_name)

    confirm_btn = Button(text="Save Match", size_hint_y=None, height=40)
    confirm_btn.bind(on_press=on_confirm)
    content.add_widget(confirm_btn)

    popup = Popup(title="Save Match", content=content, size_hint=(0.85, 0.5))
    popup.open()

def open_path_chooser(instance, folder_name):
    layout = BoxLayout(orientation="vertical")
    chooser = FileChooserListView(path='/', dirselect=True)
    layout.add_widget(chooser)

    save_btn = Button(text="Save Here", size_hint_y=None, height=40)
    layout.add_widget(save_btn)

    popup = Popup(title="Choose Folder", content=layout, size_hint=(0.9, 0.9))

    def on_choose(_):
        popup.dismiss()
        finalize_match(instance, folder_name, custom_base=chooser.path)

    save_btn.bind(on_press=on_choose)
    popup.open()

def get_save_folder(folder_name, custom_base=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name_full = f"{folder_name}_{timestamp}"

    if custom_base:
        base = custom_base
    elif platform == "android":
        try:
            from android.permissions import request_permissions, Permission
            from android.storage import primary_external_storage_path
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
            base = os.path.join(primary_external_storage_path(), "Download", "TennisApp")
        except Exception as e:
            print("⚠️ Android path fallback:", e)
            base = "/sdcard/Download/TennisApp"
    else:
        base = os.path.expanduser("~/Downloads/TennisApp")

    final = os.path.join(base, folder_name_full)
    os.makedirs(final, exist_ok=True)
    print(f"📁 Saving to: {final}")
    return final

def finalize_match(instance, folder_name, custom_base=None):
    try:
        base_folder = get_save_folder(folder_name, custom_base)
        
        # ✅ Patch: Ensure all expected stat keys exist
        required_keys = [
            "First Serve Winners", "Second Serve Winners",
            "First Serve Aces", "Second Serve Aces",
            "Double Faults", "Winners", "Errors",
            "Aces","First Serve Forehand Winners",  
            "First Serves In",               
            "Second Serves In" 
        ]
        for key in required_keys:
            if key not in instance.stats:
                instance.stats[key] = [0, 0]
        
        match_data = {
            "player_score": instance.player_score,
            "opponent_score": instance.opponent_score,
            "game_score": instance.game_score,
            "set_score": instance.set_score,
            "set_history": instance.set_history,
            "stats": instance.stats,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save JSON
        json_path = os.path.join(base_folder, "match_stats.json")
        with open(json_path, "w") as f:
            json.dump(match_data, f, indent=4)
        print(f"✅ JSON saved at {json_path}")

        # Save TXT
        txt_path = os.path.join(base_folder, "match_summary.txt")
        with open(txt_path, "w") as f:
            f.write(f"Match Summary - {folder_name}\n")
            f.write(f"Date: {match_data['timestamp']}\n\n")
            f.write(f"Final Score:\n  Player: {instance.player_score}\n  Opponent: {instance.opponent_score}\n\n")
            f.write(f"Set Score: {instance.set_score}\n")
            f.write(f"Set History: {', '.join(match_data['set_history'])}\n")
            f.write(f"Game Score: {instance.game_score}\n\n")
            f.write("Statistics:\n")
            for k, v in instance.stats.items():
                f.write(f"  {k}: {v}\n")
        print(f"✅ TXT Summary saved at {txt_path}")

        # Save CSV
        csv_path = os.path.join(base_folder, "match_stats.csv")
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Stat", "Player", "Opponent"])
            for stat, values in instance.stats.items():
                player_val = values[0] if isinstance(values, list) else values
                opponent_val = values[1] if isinstance(values, list) else ""
                writer.writerow([stat, player_val, opponent_val])
        print(f"✅ CSV saved at {csv_path}")

        # Reset match data
        instance.player_score = 0
        instance.opponent_score = 0
        instance.game_score = [0, 0]
        instance.set_score = [0, 0]
        instance.tiebreaker_active = False
        instance.is_player1_serving = True
        instance.stats = {}
        instance.set_history = []
        instance.history.clear()

        if hasattr(instance, "reset_match"):
            instance.reset_match()
        

        instance.update_live_stats()
        instance.manager.current = "home"
        print("✅ Match reset and returned to home.")

        # Show confirmation popup
        show_save_success_popup(base_folder)

    except Exception as e:
        logging.error(f"❌ Error in finalize_match: {e}")
        print(f"❌ Failed to finalize match: {e}")
        show_error_popup(str(e))

def show_save_success_popup(save_path):
    content = BoxLayout(orientation='vertical', spacing=10, padding=10)
    content.add_widget(Label(text="Match saved "))
    btn = Button(text="OK", size_hint_y=None, height=40)
    content.add_widget(btn)
    popup = Popup(title="Success", content=content, size_hint=(0.9, 0.5))
    btn.bind(on_press=popup.dismiss)
    popup.open()

def show_error_popup(message):
    content = BoxLayout(orientation='vertical', spacing=10, padding=10)
    content.add_widget(Label(text=message))
    btn = Button(text="OK", size_hint_y=None, height=40)
    content.add_widget(btn)
    popup = Popup(title="Error", content=content, size_hint=(0.8, 0.4))
    btn.bind(on_press=popup.dismiss)
    popup.open()
