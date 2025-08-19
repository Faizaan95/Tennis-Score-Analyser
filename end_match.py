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
from stats_generator import collect_stats

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
        
        # 1) Keep a copy of the raw stats 
        raw_stats = instance.stats.copy()

        # 2) Generate clean, aggregated stats
        clean_stats = collect_stats(raw_stats)
        
        # 3) Start with clean aggregated stats
        instance.stats = clean_stats.copy()
        
        # 4) Add back the detailed shot-by-shot stats that aren't redundant
        for key, value in raw_stats.items():
            # Skip if this key is already in our clean stats (avoid duplicates)
            if key not in instance.stats:
                # Only add detailed shot stats (they contain specific shot types)
                detailed_stat_keywords = ['Forehand', 'Backhand', 'Volley', 'Smash', 'Lob', 'Dropshot', 'Overhead',
                                            'Winner', 'Error', 'Ace', 'Double Fault'  # Add these
                                            ]
                if any(keyword in key for keyword in detailed_stat_keywords):
                    instance.stats[key] = value


        # ✅ Build match data with clean stats only
        match_data = {
            "player_score": instance.player_score,
            "opponent_score": instance.opponent_score,
            "game_score": instance.game_score,
            "set_score": instance.set_score,
            "set_history": instance.set_history,
            "stats": instance.stats,  # Now contains only clean, aggregated stats
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save JSON
        json_path = os.path.join(base_folder, "match_stats.json")
        with open(json_path, "w") as f:
            json.dump(match_data, f, indent=4)
        print(f"✅ JSON saved at {json_path}")

        # Save TXT with clean formatting
        txt_path = os.path.join(base_folder, "match_summary.txt")
        with open(txt_path, "w") as f:
            f.write(f"Match Summary - {folder_name}\n")
            f.write(f"Date: {match_data['timestamp']}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Final Score:\n")
            f.write(f"  Player: {instance.player_score}\n")
            f.write(f"  Opponent: {instance.opponent_score}\n\n")
            
            f.write(f"Set Score: {instance.set_score}\n")
            f.write(f"Set History: {', '.join(match_data['set_history']) if match_data['set_history'] else 'None'}\n")
            f.write(f"Game Score: {instance.game_score}\n\n")
            
            f.write("Match Statistics:\n")
            f.write("-" * 30 + "\n")
            
            # Organize stats in a logical order - AGGREGATED STATS FIRST
            key_order = [
                "Total Points Won", "Total Points Lost", "Win Percentage",
                "Aces", "First Serve Aces", "Second Serve Aces", 
                "Double Faults", "First Serves In", "Second Serves In",
                "Winners", "First Serve Winners", "Second Serve Winners",
                "Errors", "Ace Percentage", "Winner Percentage", "Double Fault Percentage","Error Percentage"
            ]
            
            f.write("SUMMARY STATS:\n")
            for key in key_order:
                if key in instance.stats:
                    value = instance.stats[key]
                    if isinstance(value, list):
                        f.write(f"  {key}: Player {value[0]} | Opponent {value[1]}\n")
                    else:
                        f.write(f"  {key}: {value}\n")
            
            # Function to automatically abbreviate stat names
            def abbreviate_stat(stat_name):
                """Automatically abbreviate long stat names using pattern matching."""
                abbreviations = {
                    "Player": "P", "Opponent": "Opp",
                    "Serving": "Srvng", "Return": "Rtrn", 
                    "First": "1st", "Second": "2nd",
                    "Forehand": "FH", "Backhand": "BH",
                    "Smash": "Sm", "Winners": "Win", "Errors": "Err",
                    "Points": "Pts","Volley": "Vol", "Serve": "Srv"
                }
                
                # Apply abbreviations
                result = stat_name
                for full, abbrev in abbreviations.items():
                    result = result.replace(full, abbrev)
                
                return result
            
            # Add detailed shot-by-shot stats with automatic abbreviations
            f.write(f"\nDETAILED SHOT STATS:\n")
            for key, value in instance.stats.items():
                if key not in key_order:  # These are the detailed stats
                    # Automatically abbreviate the stat name
                    display_key = abbreviate_stat(key)
                    if isinstance(value, list):
                        f.write(f"  {display_key}: P{value[0]} | O{value[1]}\n")
                    else:
                        f.write(f"  {display_key}: {value}\n")
                        
        print(f"✅ TXT Summary saved at {txt_path}")

        # Save CSV with clean formatting
        csv_path = os.path.join(base_folder, "match_stats.csv")
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Statistic", "Player", "Opponent"])
            
            for stat, values in instance.stats.items():
                if isinstance(values, list) and len(values) >= 2:
                    writer.writerow([stat, values[0], values[1]])
                elif isinstance(values, list) and len(values) == 1:
                    writer.writerow([stat, values[0], ""])
                else:
                    writer.writerow([stat, values, ""])
                    
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
    content.add_widget(Label(text="Match saved successfully!"))
    content.add_widget(Label(text=f"Location: {save_path}", text_size=(None, None)))
    btn = Button(text="OK", size_hint_y=None, height=40)
    content.add_widget(btn)
    popup = Popup(title="Success", content=content, size_hint=(0.9, 0.6))
    btn.bind(on_press=popup.dismiss)
    popup.open()

def show_error_popup(message):
    content = BoxLayout(orientation='vertical', spacing=10, padding=10)
    content.add_widget(Label(text=f"Error: {message}"))
    btn = Button(text="OK", size_hint_y=None, height=40)
    content.add_widget(btn)
    popup = Popup(title="Error", content=content, size_hint=(0.8, 0.4))
    btn.bind(on_press=popup.dismiss)
    popup.open()