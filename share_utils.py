# share_utils.py
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.utils import platform
import os
import json
from datetime import datetime
from kivy.graphics import Color, Rectangle

try:
    from android.storage import primary_external_storage_path
    ANDROID = True
except ImportError:
    ANDROID = False



def generate_stats_image(stats_widget):
    # 🕒 Timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 📂 Choose output directory
    if ANDROID:
        downloads_dir = primary_external_storage_path() + "/Download"
    else:
        downloads_dir = "."  # Save to current directory on desktop

    img_path = f"{downloads_dir}/stats_{timestamp}.png"

    # 🖤 Add black background if not already present
    if not hasattr(stats_widget, 'bg_rect'):
        with stats_widget.canvas.before:
            Color(0, 0, 0, 1)
            stats_widget.bg_rect = Rectangle(pos=stats_widget.pos, size=stats_widget.size)

    # 🧭 Update background position and size
    stats_widget.bg_rect.pos = stats_widget.pos
    stats_widget.bg_rect.size = stats_widget.size

    try:
        # 📸 Export widget to PNG
        stats_widget.export_to_png(img_path)
        print(f"✅ Stats image saved: {img_path}")
        return img_path

    except Exception as e:
        print(f"❌ Error saving stats image: {e}")
        return None





def finalize_match_data(instance, match_name):
    try:
        # 🔸 Step 1: Create folder in shared location (if Android)
        base_dir = os.path.expanduser("~")
        folder_name = match_name.replace(" ", "_")
        full_path = os.path.join(base_dir, "TennisMatches", folder_name)

        os.makedirs(full_path, exist_ok=True)

        # 🔸 Step 2: Build JSON data
        data = {
            "player_score": instance.player_score,
            "opponent_score": instance.opponent_score,
            "game_score": instance.game_score,
            "set_score": instance.set_score,
            "tiebreaker_active": instance.tiebreaker_active,
            "is_player1_serving": instance.is_player1_serving,
            "stats": instance.stats,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        json_path = os.path.join(full_path, "match_data.json")
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

        print(f"✅ Match JSON saved to {json_path}")
        return full_path  # useful for next steps

    except Exception as e:
        print(f"❌ Error saving match data: {e}")