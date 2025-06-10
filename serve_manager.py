from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from score_manager import process_score_update  # ✅ Correct import
import logging
from score_manager import get_score_display  # Ensure this is imported
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

        # 🧠 Prefer custom screen formatting if available
        if hasattr(instance, 'get_score_text'):
            instance.score_label.text = instance.get_score_text()
        else:
            instance.score_label.text = get_score_display(
                instance.player_score,
                instance.opponent_score,
                instance.game_score,
                instance.set_score,
                instance.is_player1_serving
            )

    except Exception as e:
        logging.error(f"Error in switch_server: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in switch_server: {e}")


def show_serve_prompt(instance, result):
    """ Ask for First Serve, Second Serve, or Double Fault before selecting Shot Type. """
    try:
        assert instance is not None, "Instance is None in show_serve_prompt()"
        assert result in ["Won", "Lost"], f"Invalid result: {result}"

        if instance.is_player1_serving:
            # Player 1 serving
            serve_options = ["First Serve", "Second Serve"] if result == "Won" else ["First Serve", "Second Serve", "Double Fault"]
        else:
            # Player 2 serving (Player 1's perspective)
            serve_options = ["First Serve", "Second Serve", "Double Fault"] if result == "Won" else ["First Serve", "Second Serve"]

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        for serve in serve_options:
            btn = Button(
                text=serve,
                on_press=lambda btn, serve=serve: process_serve_selection(instance, serve, result)
            )

            popup_layout.add_widget(btn)

        instance.popup = Popup(title="On which serve did the point occur?", content=popup_layout, size_hint=(0.5, 0.5))
        instance.popup.open()

    except Exception as e:
        logging.error(f"Error in show_serve_prompt: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in show_serve_prompt: {e}")


def process_serve_selection(instance, serve, result):
    """ Handles serve selection, routes to next stage. """
    try:
        assert instance is not None and serve and result in ["Won", "Lost"]
        instance.selected_serve = serve
        instance.popup.dismiss()

        if serve == "Double Fault":
            process_score_update(instance, serve, "Double Fault", result)
        else:
            show_point_result_prompt(instance, serve, result)

    except Exception as e:
        logging.error(f"Error in process_serve_selection: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in process_serve_selection: {e}")


def show_point_result_prompt(instance, serve, result):
    """ Prompt 2: How was the point won or lost. """
    try:
        assert instance is not None, "Instance is None in show_point_result_prompt()"
        assert serve is not None, "Serve type is None"
        assert result in ["Won", "Lost"], f"Invalid result: {result}"

        instance.popup.dismiss()  # Close previous popup

        # Dynamic shot result options
        if result == "Won":
            if not instance.is_player1_serving:
                # Player was returning, can't win with an Ace
                options = ["Winner", "Opponent Error"]
            else:
                options = ["Ace", "Winner", "Opponent Error"]
            title = "How did the player win the point?"

        else:
            options = ["Winner", "Error"]
            title = "How did the player lose the point?"

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        for shot_type in options:
            btn = Button(
                text=shot_type,
                on_press=lambda btn, shot_type=shot_type: process_shot_type_selection(instance, serve, shot_type, result)
            )
            popup_layout.add_widget(btn)

        instance.popup = Popup(title=title, content=popup_layout, size_hint=(0.5, 0.5))
        instance.popup.open()

    except Exception as e:
        logging.error(f"Error in show_point_result_prompt: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in show_point_result_prompt: {e}")



def process_shot_type_selection(instance, serve, shot_type, result):
    """ Decides whether to ask for detailed shot type, or finalize immediately (e.g. Ace). """
    try:
        instance.popup.dismiss()

        if shot_type == "Ace" or shot_type == "Double Fault":
            # Finalize directly
            process_score_update(instance, serve, shot_type, result)
        else:
            # Ask for detailed shot type (Forehand, Backhand, etc.)
            show_detailed_shot_prompt(instance, serve, shot_type, result)

    except Exception as e:
        logging.error(f"Error in process_shot_type_selection: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in process_shot_type_selection: {e}")


def show_detailed_shot_prompt(instance, serve, shot_type, result):
    """ Ask for the specific shot type used (forehand, backhand, etc). """
    try:
        shot_options = ["Forehand", "Backhand", "Volley", "Smash","Dropshot","Lob"]

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        for detail in shot_options:
            btn = Button(
                text=detail,
                on_press=lambda btn, detail=detail: process_score_update(instance, serve, f"{detail} {shot_type}", result)
            )
            popup_layout.add_widget(btn)

        # Determine title dynamically
        if result == "Lost" and shot_type == "Error":
            title = "On which shot did the error occur?"
        else:
            title = "Which shot was used to win the point?" if result == "Won" else "Which shot beat the player?"

        instance.popup = Popup(title=title, content=popup_layout, size_hint=(0.5, 0.5))
        instance.popup.open()


    except Exception as e:
        logging.error(f"Error in show_detailed_shot_prompt: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in show_detailed_shot_prompt: {e}")
