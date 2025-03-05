import os
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from reportlab.pdfgen import canvas
from kivy.utils import platform
import logging

# Configure logging (creates a log file for errors)
logging.basicConfig(
    filename="app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Import Android-specific modules only if running on Android
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
    width, height = Window.size
    texture = Texture.create(size=(width, height))
    Window.screenshot(name=img_path)
    print(f"Stats saved as {img_path}")
    return img_path  # Return path for sharing

def generate_stats_pdf(stats_text):
    pdf_path = "stats.pdf"
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, stats_text)
    c.save()
    print(f"Stats saved as {pdf_path}")
    return pdf_path  # Return path for sharing

def share_file(file_path, mime_type="application/pdf"):
    """ Shares a file via Android's sharing system. """
    if platform == "android" and SharedStorage:
        file_uri = SharedStorage().copy_to_shared(file_path, mime_type)
        intent = Intent(Intent.ACTION_SEND)
        intent.setType(mime_type)
        intent.putExtra(Intent.EXTRA_STREAM, Uri.parse(file_uri))
        chooser = Intent.createChooser(intent, "Share via")
        PythonActivity.mActivity.startActivity(chooser)
    else:
        print(f"Sharing not supported on this platform. File saved at {file_path}")

def collect_stats(match_stats):
    """ Returns both basic and advanced tennis match stats. """
    
    print(f"RECEIVED IN collect_stats(): {match_stats}")  

    if not match_stats:
        print("WARNING: match_stats is empty!")

    # Ensure all keys exist in stats dictionary
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
        if key not in match_stats:
            match_stats[key] = default_stats[key]  # Fill missing keys with defaults

    # Calculate total points won/lost
    total_points_won = (
        match_stats["First Serve Winners"][0] + match_stats["Second Serve Winners"][0] +
        match_stats["First Serve Aces"][0] + match_stats["Second Serve Aces"][0] +
        match_stats["First Serve Volleys"][0] + match_stats["Second Serve Volleys"][0]
    )
    total_points_lost = (
        match_stats["First Serve Winners"][1] + match_stats["Second Serve Winners"][1] +
        match_stats["First Serve Aces"][1] + match_stats["Second Serve Aces"][1] +
        match_stats["First Serve Volleys"][1] + match_stats["Second Serve Volleys"][1]
    ) + match_stats["Double Faults"][0]  # Double faults count as lost points

    total_points_played = total_points_won + total_points_lost

    # Avoid division by zero
    win_percentage = (total_points_won / total_points_played * 100) if total_points_played > 0 else 0
    ace_percentage = ((match_stats["First Serve Aces"][0] + match_stats["Second Serve Aces"][0]) / total_points_won * 100) if total_points_won > 0 else 0
    winner_percentage = ((match_stats["First Serve Winners"][0] + match_stats["Second Serve Winners"][0]) / total_points_won * 100) if total_points_won > 0 else 0
    double_fault_percentage = (match_stats["Double Faults"][0] / total_points_played * 100) if total_points_played > 0 else 0

    stats = {
        "Total Points Won": total_points_won,
        "Total Points Lost": total_points_lost,
        "Win Percentage": round(win_percentage, 2),
        "Aces (First Serve)": match_stats["First Serve Aces"],
        "Aces (Second Serve)": match_stats["Second Serve Aces"],
        "Winners (First Serve)": match_stats["First Serve Winners"],
        "Winners (Second Serve)": match_stats["Second Serve Winners"],
        "Volleys (First Serve)": match_stats["First Serve Volleys"],
        "Volleys (Second Serve)": match_stats["Second Serve Volleys"],
        "Double Faults": match_stats["Double Faults"],
        "Ace Percentage": round(ace_percentage, 2),
        "Winner Percentage": round(winner_percentage, 2),
        "Double Fault Percentage": round(double_fault_percentage, 2)
    }

    print(f"PROCESSED IN collect_stats(): {stats}")  
    return stats
