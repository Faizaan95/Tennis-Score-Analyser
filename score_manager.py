import logging
import copy  # ✅ Import deepcopy

# Configure logging
logging.basicConfig(
    filename="app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def update_score(player_score, opponent_score, game_score, set_score, result, tiebreaker_active, reason=None, stats=None, is_dedicated_tiebreaker=False):
    if stats is None:
        stats = {"Ace": [0, 0], "Winner": [0, 0], "Double Fault": [0, 0], "Volley": [0, 0]}

    if result == "Won":
        player_score, opponent_score, game_score, set_score, tiebreaker_active = calculate_tennis_score(
            player_score, opponent_score, game_score, set_score, True, tiebreaker_active, is_dedicated_tiebreaker
        )
    elif result == "Lost":
        opponent_score, player_score, game_score, set_score, tiebreaker_active = calculate_tennis_score(
            opponent_score, player_score, game_score, set_score, False, tiebreaker_active, is_dedicated_tiebreaker
        )

        if reason == "Double Fault":
            if "Double Fault" in stats:
                stats["Double Fault"][1] += 1

    return player_score, opponent_score, game_score, set_score, tiebreaker_active, stats


def process_score_update(instance, serve, point_type, result):
    """ Processes score updates and updates the stats page. """

    # Check if this is a dedicated tiebreaker screen
    is_dedicated_tiebreaker = hasattr(instance, 'name') and instance.name == 'tiebreak_match'

    # Backup for undo
    instance.history.append((
        instance.player_score,
        instance.opponent_score,
        instance.game_score[:],
        instance.set_score[:],
        instance.tiebreaker_active,
        copy.deepcopy(instance.stats),
        instance.is_player1_serving
    ))

    # Stats update
    if serve == "Double Fault" and result == "Lost":
        instance.stats["Double Faults"][0 if instance.is_player1_serving else 1] += 1
        print("🏷️ Tracking key: Double Faults")
    else:
        key = f"{serve} {point_type}s"
        if key not in instance.stats:
            instance.stats[key] = [0, 0]
        instance.stats[key][0 if result == "Won" else 1] += 1
        print(f"🏷️ Tracking key: {key}")

    prev_game_score = instance.game_score[:]

    # Score update
    instance.player_score, instance.opponent_score, instance.game_score, instance.set_score, instance.tiebreaker_active, instance.stats = update_score(
        instance.player_score, instance.opponent_score, instance.game_score, instance.set_score,
        result, instance.tiebreaker_active, serve if point_type == "Double Fault" else None, instance.stats, is_dedicated_tiebreaker
    )

    # Server switch logic
    if instance.game_score != prev_game_score and not instance.tiebreaker_active:
        instance.is_player1_serving = not instance.is_player1_serving

    # Update score label
    if hasattr(instance, 'get_score_text'):
        instance.score_label.text = instance.get_score_text()
    else:
        instance.score_label.text = get_score_display(
            instance.player_score, instance.opponent_score,
            instance.game_score, instance.set_score,
            instance.is_player1_serving
        )

    instance.update_live_stats()

    # Live update stats page
    try:
        stats_screen = instance.manager.get_screen("stats")
        if stats_screen:
            stats_screen.update_stats({
                "match_stats": instance.stats,
                "score_summary": {
                    "player_score": instance.player_score,
                    "opponent_score": instance.opponent_score,
                    "game_score": instance.game_score,
                    "set_score": instance.set_score,
                    "tiebreaker_active": instance.tiebreaker_active,
                    "is_player1_serving": instance.is_player1_serving
                }
            })
    except Exception as e:
        logging.error(f"Error updating stats screen after score update: {e}")

    # Dismiss popup if any
    try:
        if hasattr(instance, 'popup') and instance.popup:
            instance.popup.dismiss()
    except Exception:
        pass


def calculate_tennis_score(player, opponent, game_score, set_score, is_player, tiebreaker_active, is_dedicated_tiebreaker=False):
    tennis_points = [0, 15, 30, 40]

    if tiebreaker_active:
        player += 1
        
        # For dedicated tiebreaker screen, don't end the tiebreaker - just keep counting
        if is_dedicated_tiebreaker:
            return player, opponent, game_score, set_score, tiebreaker_active
        
        # For regular matches, end tiebreaker when someone reaches 7+ with 2+ point lead
        if player >= 7 and (player - opponent) >= 2:
            set_score[0 if is_player else 1] += 1
            game_score = [0, 0]
            player, opponent = 0, 0
            tiebreaker_active = False
        return player, opponent, game_score, set_score, tiebreaker_active

    if isinstance(player, int) and player < 40:
        player = tennis_points[tennis_points.index(player) + 1]
    elif player == 40:
        if opponent in [0, 15, 30]:
            player = "Game"
        elif opponent == 40:
            player = "Adv"
        else:
            player, opponent = 40, 40
    elif player == "Adv":
        player = "Game"

    if player == "Game":
        game_score[0 if is_player else 1] += 1
        player, opponent = 0, 0
        if game_score[0 if is_player else 1] == 6 and game_score[1 if is_player else 0] == 6:
            tiebreaker_active = True
        elif game_score[0 if is_player else 1] >= 6 and abs(game_score[0] - game_score[1]) >= 2:
            set_score[0 if is_player else 1] += 1
            game_score = [0, 0]

    return player, opponent, game_score, set_score, tiebreaker_active


def get_score_display(player_score, opponent_score, game_score, set_score, is_player1_serving, show_server=True):
    if show_server:
        server_dot_p1 = "• " if is_player1_serving else ""
        server_dot_p2 = "• " if not is_player1_serving else ""
    else:
        server_dot_p1 = ""
        server_dot_p2 = ""

    return (f"{server_dot_p1}Player 1: {player_score} - Opponent: {opponent_score} {server_dot_p2}\n"
            f"Games: {game_score[0]} - {game_score[1]}\n"
            f"Sets: {set_score[0]} - {set_score[1]}")



def undo_last_action(instance):
    """ Reverts the last recorded game state. """
    try:
        print("🔄 Undo button pressed!")

        if instance.history:
            (
                instance.player_score,
                instance.opponent_score,
                instance.game_score,
                instance.set_score,
                instance.tiebreaker_active,
                instance.stats,
                instance.is_player1_serving
            ) = instance.history.pop()

            print(f"✅ Undo successful! New state: {instance.player_score}, {instance.opponent_score}, {instance.game_score}, {instance.set_score}")

            if hasattr(instance, 'get_score_text'):
                instance.score_label.text = instance.get_score_text()
            else:
                instance.score_label.text = get_score_display(
                    instance.player_score, instance.opponent_score,
                    instance.game_score, instance.set_score,
                    instance.is_player1_serving
                )

            instance.update_live_stats()

            stats_screen = instance.manager.get_screen("stats")
            if stats_screen:
                stats_screen.update_stats({
                    "match_stats": instance.stats,
                    "score_summary": {
                        "player_score": instance.player_score,
                        "opponent_score": instance.opponent_score,
                        "game_score": instance.game_score,
                        "set_score": instance.set_score,
                        "tiebreaker_active": instance.tiebreaker_active,
                        "is_player1_serving": instance.is_player1_serving
                    }
                })
                print("✅ Stats page updated successfully after undo.")
            else:
                print("⚠ ERROR: Could not find stats screen!")
        else:
            print("⚠ No history to undo!")

    except Exception as e:
        logging.error(f"Error in undo_last_action: {e}")
        print(f"⚠ Error: {e}")