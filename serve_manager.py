from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from score_manager import process_score_update  # ✅ Correct import
import logging
from score_manager import get_score_display  # Ensure this is imported

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
# Configure logging (creates a log file for errors)
logging.basicConfig(
    filename="app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DEBUG_MODE = True  # Set to False to disable debug print statements


from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window

def create_custom_popup(title_text, content):
    """ Creates a styled popup with a custom title. """

    # Custom title label
    title_label = Label(
        text=title_text,
        font_size='15sp',        # ✅ Bigger title font
        bold=True,               # ✅ Bold text
        color=(1, 1, 1, 1),      # ✅ White text color
        size_hint_y=None,
        height=25
    )

    # Title container with background color
    title_container = BoxLayout(orientation='vertical', size_hint_y=None, height=60)
    title_container.add_widget(title_label)

    # Combine title and content
    layout = BoxLayout(orientation='vertical')
    layout.add_widget(title_container)
    layout.add_widget(content)

    popup = Popup(
        title='',  # Hide default title
        content=layout,
        size_hint=(0.9, 0.4)
    )
    return popup


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
        title = "Which serve was used?"
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)


            # ✅ Create a vertically scrollable layout with proper spacing and size_hint
        grid = GridLayout(cols=1, spacing=15, size_hint_y=None, padding=20)
        grid.bind(minimum_height=grid.setter('height'))  # Important for ScrollView to work

        for serve_type in serve_options:
            btn = Button(
                text=serve_type,
                font_size=70,            # ✅ Larger font for mobile
                size_hint_y=None,        # ✅ Fixed height to make buttons easier to tap
                height=80,               # ✅ Touch-friendly button height
                on_press=lambda btn, serve_type=serve_type: process_serve_selection(instance, serve_type, result)
            )
            grid.add_widget(btn)

        # ✅ Wrap the layout in a ScrollView for mobile usability
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(grid)
        
        popup = create_custom_popup(title, scroll)
        instance.popup = popup
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
                # Player was receiving, can't win with an Ace
                options = ["Winner", "Opponent Error"]
                title = "How did the player win the point?"
            else:
                # Player was serving, can win with Ace
                options = ["Ace", "Winner", "Opponent Error"]
                title = "How did the player win the point?"

        else:  # result == "Lost"
            if not instance.is_player1_serving:
                # Player was receiving, opponent was serving - opponent could have hit an Ace
                options = ["Ace", "Winner", "Error"]
                title = "How did the player lose the point?"
            else:
                # Player was serving, opponent was receiving - no Ace possible
                options = ["Winner", "Error"]
                title = "How did the player lose the point?"

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # ✅ Create a vertically scrollable layout with proper spacing and size_hint
        grid = GridLayout(cols=1, spacing=15, size_hint_y=None, padding=20)
        grid.bind(minimum_height=grid.setter('height'))  # Important for ScrollView to work

        for shot_type in options:
            btn = Button(
                text=shot_type,
                font_size=70,            # ✅ Larger font for mobile
                size_hint_y=None,        # ✅ Fixed height to make buttons easier to tap
                height=80,               # ✅ Touch-friendly button height
                on_press=lambda btn, shot_type=shot_type: process_shot_type_selection(instance, serve, shot_type, result)
            )
            grid.add_widget(btn)

        # ✅ Wrap the layout in a ScrollView for mobile usability
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(grid)
        
        popup = create_custom_popup(title, scroll)
        instance.popup = popup
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
    """ FIXED: Ask for the specific shot type used, properly handling Opponent Error. """
    try:
        # Default shot options
        shot_options = ["Forehand", "Backhand", "Volley", "Smash", "Dropshot", "Lob"]

        # Add "Serve" as an option for serving scenarios
        if shot_type == "Opponent Error" and instance.is_player1_serving:
            shot_options.insert(0, "Serve")
        
            
            
        if not instance.is_player1_serving and (
            (result == "Lost" and shot_type == "Error") or
            (result not in ("Lost", "Winner"))
        ):
            shot_options.insert(0, "Return Forehand")
            shot_options.insert(1, "Return Backhand")
            
            
        if instance.is_player1_serving and (
            (result == "Lost" and shot_type == "Winner") or
            (result not in ("Won", "Error"))
        ):
            shot_options.insert(0, "Return Forehand")
            shot_options.insert(1, "Return Backhand")



        grid = GridLayout(cols=1, spacing=15, size_hint_y=None, padding=20)
        grid.bind(minimum_height=grid.setter('height'))

        for detail in shot_options:
            btn = Button(
                text=detail,
                font_size=70,
                size_hint_y=None,
                height=80,
                on_press=lambda btn, detail=detail: finalize_shot_selection(instance, serve, detail, shot_type, result)
            )
            grid.add_widget(btn)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(grid)

        # Title adjustment
        if result == "Lost" and shot_type == "Error":
            title = "With which shot did the error occur?"
        elif shot_type == "Opponent Error":
            title = "Which shot was hit that forced the opponent's error?"
        else:
            title = "With which shot did you/opponent win the point?"

        popup = create_custom_popup(title, scroll)
        instance.popup = popup
        instance.popup.open()

    except Exception as e:
        logging.error(f"Error in show_detailed_shot_prompt: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in show_detailed_shot_prompt: {e}")


def finalize_shot_selection(instance, serve, shot_detail, shot_type, result):
    """ FIXED: Properly format the point_type and call process_score_update. """
    try:
        instance.popup.dismiss()
        
        # Format the point_type correctly
        if shot_type == "Opponent Error":
            point_type = f"{shot_detail} Opponent Error"
        else:
            point_type = f"{shot_detail} {shot_type}"
        
        if DEBUG_MODE:
            print(f"🎯 Final shot selection: serve='{serve}', point_type='{point_type}', result='{result}'")
        
        process_score_update(instance, serve, point_type, result)

    except Exception as e:
        logging.error(f"Error in finalize_shot_selection: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in finalize_shot_selection: {e}")