from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from score_manager import process_score_update  # ✅ Correct import
import logging

# Configure logging (creates a log file for errors)
logging.basicConfig(
    filename="app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DEBUG_MODE = True  # Set to False to disable debug print statements


def switch_server(instance, _):
    """ Manually switch the server. """
    try:
        assert instance is not None, "Instance is None in switch_server()"

        instance.is_player1_serving = not instance.is_player1_serving
        instance.score_label.text = instance.get_score_display()
    
    except Exception as e:
        logging.error(f"Error in switch_server: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in switch_server: {e}")


def show_serve_prompt(instance, result):
    """ Ask for First Serve, Second Serve, or Double Fault before selecting Shot Type. """
    try:
        assert instance is not None, "Instance is None in show_serve_prompt()"
        assert result in ["Won", "Lost"], f"Invalid result: {result}"

        serve_options = ["First Serve", "Second Serve"]
        if result == "Lost":
            serve_options.append("Double Fault")

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        for serve in serve_options:
            btn = Button(
                text=serve,
                on_press=lambda btn, serve=serve: process_serve_selection(instance, serve, result)
            )
            popup_layout.add_widget(btn)

        instance.popup = Popup(title="Select Serve Type", content=popup_layout, size_hint=(0.5, 0.5))
        instance.popup.open()

    except Exception as e:
        logging.error(f"Error in show_serve_prompt: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in show_serve_prompt: {e}")


def process_serve_selection(instance, serve, result):
    """ Store serve type and proceed to shot selection or award point for double fault. """
    try:
        assert instance is not None, "Instance is None in process_serve_selection()"
        assert serve is not None, "Serve type is None"
        assert result in ["Won", "Lost"], f"Invalid result: {result}"

        instance.selected_serve = serve
        instance.popup.dismiss()

        if serve == "Double Fault":
            process_score_update(instance, serve, "Double Fault", result)  # ✅ Fixed
        else:
            show_shot_type_prompt(instance, serve, result)

    except Exception as e:
        logging.error(f"Error in process_serve_selection: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in process_serve_selection: {e}")


def show_shot_type_prompt(instance, serve, result):
    """ Ask for Shot Type after Serve selection. """
    try:
        assert instance is not None, "Instance is None in show_shot_type_prompt()"
        assert serve is not None, "Serve type is None"
        assert result in ["Won", "Lost"], f"Invalid result: {result}"

        instance.popup.dismiss()  # Close previous popup

        # Determine valid shot types based on serve/receive situation
        if instance.is_player1_serving:
            shot_types = ["Volley", "Winner", "Ace"] if result == "Won" else ["Volley", "Winner", "Ace"]
        else:
            shot_types = ["Volley", "Winner"] if result == "Won" else ["Ace", "Volley", "Winner"]

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        for shot in shot_types:
            btn = Button(text=shot, on_press=lambda btn, shot=shot: process_score_update(instance, serve, shot, result))  # ✅ Fixed
            popup_layout.add_widget(btn)

        instance.popup = Popup(title="Select Shot Type", content=popup_layout, size_hint=(0.5, 0.5))
        instance.popup.open()

    except Exception as e:
        logging.error(f"Error in show_shot_type_prompt: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in show_shot_type_prompt: {e}")
