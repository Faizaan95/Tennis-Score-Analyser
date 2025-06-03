# share_utils.py
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from reportlab.pdfgen import canvas
from kivy.utils import platform
import os
import json
from datetime import datetime

# Android-specific
if platform == "android":
    from androidstorage4kivy import SharedStorage
    from jnius import autoclass
    Intent = autoclass("android.content.Intent")
    Uri = autoclass("android.net.Uri")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
else:
    SharedStorage = None  # Prevents crashes on non-Android devices

def generate_stats_image(stats_text):
    img_path = "stats.png"
    Window.screenshot(name=img_path)
    print(f"Stats saved as {img_path}")
    return img_path

def generate_stats_pdf(stats_text):
    pdf_path = "stats.pdf"
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, stats_text)
    c.save()
    print(f"Stats saved as {pdf_path}")
    return pdf_path

def share_file(file_path, mime_type="application/pdf"):
    if platform == "android" and SharedStorage:
        file_uri = SharedStorage().copy_to_shared(file_path, mime_type)
        intent = Intent(Intent.ACTION_SEND)
        intent.setType(mime_type)
        intent.putExtra(Intent.EXTRA_STREAM, Uri.parse(file_uri))
        chooser = Intent.createChooser(intent, "Share via")
        PythonActivity.mActivity.startActivity(chooser)
    else:
        print(f"Sharing not supported on this platform. File saved at {file_path}")

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