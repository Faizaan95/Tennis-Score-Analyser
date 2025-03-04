from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup

def switch_server(instance, _):
    """ Manually switch the server. """
    instance.is_player1_serving = not instance.is_player1_serving
    instance.score_label.text = instance.get_score_display()


def show_serve_prompt(instance, result):
    """ Ask for First Serve, Second Serve, or Double Fault before selecting Shot Type. """
    if instance.is_player1_serving:
        serve_options = ["First Serve", "Second Serve"] if result == "Won" else ["First Serve", "Second Serve", "Double Fault"]
    else:
        serve_options = ["First Serve", "Second Serve", "Double Fault"] if result == "Won" else ["First Serve", "Second Serve"]

    popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

    for serve in serve_options:
        btn = Button(
            text=serve,
            on_press=lambda btn, serve=serve: process_serve_selection(instance, serve, result)
        )
        popup_layout.add_widget(btn)

    instance.popup = Popup(title="Select Serve Type", content=popup_layout, size_hint=(0.5, 0.5))
    instance.popup.open()

def process_serve_selection(instance, serve, result):
    """ Store serve type and proceed to shot selection or award point for double fault. """
    instance.selected_serve = serve
    instance.popup.dismiss()

    if serve == "Double Fault":
        instance.update_score(serve, "Double Fault", result)
    else:
        show_shot_type_prompt(instance, serve, result)

def show_shot_type_prompt(instance, serve, result):
    """ Ask for Shot Type after Serve selection. """
    instance.popup.dismiss()  # Close previous popup

    # Determine valid shot types based on serve/receive situation
    if instance.is_player1_serving:
        shot_types = ["Volley", "Winner", "Ace"] if result == "Won" else ["Volley", "Winner", "Ace"]
    else:
        shot_types = ["Volley", "Winner"] if result == "Won" else ["Ace", "Volley", "Winner"]

    popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

    for shot in shot_types:
        btn = Button(text=shot, on_press=lambda btn, shot=shot: instance.update_score(serve, shot, result))
        popup_layout.add_widget(btn)

    instance.popup = Popup(title="Select Shot Type", content=popup_layout, size_hint=(0.5, 0.5))
    instance.popup.open()