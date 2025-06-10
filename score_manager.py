# score_manager.py
import logging
import copy

# Configure logging
logging.basicConfig(
    filename="app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DEBUG_MODE = True

def update_score(player_score, opponent_score, game_score, set_score, result, tiebreaker_active, reason=None, stats=None, is_dedicated_tiebreaker=False):
    """Update tennis score based on point result."""
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

        # Handle double fault stats in the legacy function
        if reason == "Double Fault":
            if "Double Fault" in stats:
                stats["Double Fault"][1] += 1

    return player_score, opponent_score, game_score, set_score, tiebreaker_active, stats


def process_score_update(instance, serve, point_type, result):
    """Process score updates and update the stats properly."""
    try:
        if DEBUG_MODE:
            print(f"🎾 Processing: serve='{serve}', point_type='{point_type}', result='{result}'")

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

        # Initialize stats if needed
        if not hasattr(instance, 'stats') or instance.stats is None:
            instance.stats = {}

        # Process statistics based on serve and point type
        update_match_statistics(instance, serve, point_type, result)

        # Store previous game score for server switching
        prev_game_score = instance.game_score[:]

        # Update tennis score using the existing function
        instance.player_score, instance.opponent_score, instance.game_score, instance.set_score, instance.tiebreaker_active, instance.stats = update_score(
            instance.player_score, instance.opponent_score, instance.game_score, instance.set_score,
            result, instance.tiebreaker_active, serve if point_type == "Double Fault" else None, instance.stats, is_dedicated_tiebreaker
        )

        # Server switch logic (only when game is completed and not in tiebreaker)
        if instance.game_score != prev_game_score and not instance.tiebreaker_active:
            instance.is_player1_serving = not instance.is_player1_serving
            if DEBUG_MODE:
                serving_player = "Player 1" if instance.is_player1_serving else "Player 2"
                print(f"🔄 Server switched to: {serving_player}")

        # Update score display
        if hasattr(instance, 'get_score_text'):
            instance.score_label.text = instance.get_score_text()
        else:
            instance.score_label.text = get_score_display(
                instance.player_score, instance.opponent_score,
                instance.game_score, instance.set_score,
                instance.is_player1_serving
            )

        # Update live stats if available
        if hasattr(instance, 'update_live_stats'):
            instance.update_live_stats()

        # Update stats screen
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
                if DEBUG_MODE:
                    print("✅ Stats screen updated successfully")
        except Exception as e:
            logging.error(f"Error updating stats screen after score update: {e}")

        # Dismiss popup if any
        try:
            if hasattr(instance, 'popup') and instance.popup:
                instance.popup.dismiss()
        except Exception:
            pass

        if DEBUG_MODE:
            print(f"✅ Score updated successfully: {instance.player_score}-{instance.opponent_score}")

    except Exception as e:
        logging.error(f"Error in process_score_update: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error in process_score_update: {e}")


def update_match_statistics(instance, serve, point_type, result):
    """Update match statistics based on the point played."""
    try:
        if DEBUG_MODE:
            print(f"📊 Updating stats: serve='{serve}', point_type='{point_type}', result='{result}'")

        # Handle Double Fault specifically
        if serve == "Double Fault" and result == "Lost":
            if "Double Faults" not in instance.stats:
                instance.stats["Double Faults"] = [0, 0]
            instance.stats["Double Faults"][0] += 1  # Player's double fault
            if DEBUG_MODE:
                print("📊 Tracked: Double Faults")
            return

        # Handle Ace
        if point_type == "Ace" and result == "Won":
            if "Aces" not in instance.stats:
                instance.stats["Aces"] = [0, 0]
            instance.stats["Aces"][0] += 1

            # Add this block:
            if serve in ["First Serve", "Second Serve"]:
                ace_key = f"{serve} Aces"
                if ace_key not in instance.stats:
                    instance.stats[ace_key] = [0, 0]
                instance.stats[ace_key][0] += 1
                if DEBUG_MODE:
                    print(f"📊 Tracked: {ace_key}")

            if DEBUG_MODE:
                print("📊 Tracked: Aces")
            return

        # Parse the point_type to extract shot and outcome
        # Expected formats: "Forehand Winner", "Backhand Error", "Volley Winner", etc.
        point_parts = point_type.split()
        
        if len(point_parts) >= 2:
            shot_type = point_parts[0]  # e.g., "Forehand", "Backhand", "Volley"
            outcome = point_parts[1]    # e.g., "Winner", "Error", "Opponent"
            
            # Create appropriate stat keys
            if result == "Won":
                if "Winner" in point_type:
                    # Track as winner
                    stat_key = f"{shot_type} Winners"
                    if stat_key not in instance.stats:
                        instance.stats[stat_key] = [0, 0]
                    instance.stats[stat_key][0] += 1
                    
                    # Also track general winners
                    if "Winners" not in instance.stats:
                        instance.stats["Winners"] = [0, 0]
                    instance.stats["Winners"][0] += 1
                    
                    if DEBUG_MODE:
                        print(f"📊 Tracked: {stat_key} and Winners")
                        
                elif "Opponent Error" in point_type:
                    # Track as opponent error (point won due to opponent's mistake)
                    if "Opponent Errors" not in instance.stats:
                        instance.stats["Opponent Errors"] = [0, 0]
                    instance.stats["Opponent Errors"][1] += 1  # Opponent's error
                    
                    if DEBUG_MODE:
                        print("📊 Tracked: Opponent Errors")
                        
            elif result == "Lost":
                if "Error" in point_type:
                    # Track as player's error
                    stat_key = f"{shot_type} Errors"
                    if stat_key not in instance.stats:
                        instance.stats[stat_key] = [0, 0]
                    instance.stats[stat_key][0] += 1
                    
                    # Also track general errors
                    if "Errors" not in instance.stats:
                        instance.stats["Errors"] = [0, 0]
                    instance.stats["Errors"][0] += 1
                    
                    if DEBUG_MODE:
                        print(f"📊 Tracked: {stat_key} and Errors")
                        
                elif "Winner" in point_type:
                    # Track as opponent winner
                    if "Opponent Winners" not in instance.stats:
                        instance.stats["Opponent Winners"] = [0, 0]
                    instance.stats["Opponent Winners"][1] += 1  # Opponent's winner
                    
                    if DEBUG_MODE:
                        print("📊 Tracked: Opponent Winners")

            if serve in ["First Serve", "Second Serve"]:
                serve_key = f"{serve} {point_type}s"
                if serve_key not in instance.stats:
                    instance.stats[serve_key] = [0, 0]
                instance.stats[serve_key][0 if result == "Won" else 1] += 1

                if DEBUG_MODE:
                    print(f"📊 Tracked: {serve_key}")

            # Legacy tracking for backward compatibility (only if it's not a duplicate)
            key = f"{serve} {point_type}s"
            if key != serve_key:  # 👈 avoid double-increment
                if key not in instance.stats:
                    instance.stats[key] = [0, 0]
                instance.stats[key][0 if result == "Won" else 1] += 1

                if DEBUG_MODE:
                    print(f"📊 Legacy tracked: {key}")


    except Exception as e:
        logging.error(f"Error updating match statistics: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error updating statistics: {e}")

    if DEBUG_MODE:
        print(f"📈 Current Stats: {instance.stats}")

def calculate_tennis_score(player, opponent, game_score, set_score, is_player, tiebreaker_active, is_dedicated_tiebreaker=False):
    """Calculate tennis score progression."""
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

    # Regular game scoring
    if isinstance(player, int) and player < 40:
        player = tennis_points[tennis_points.index(player) + 1]
    elif player == 40:
        if opponent in [0, 15, 30]:
            player = "Game"
        elif opponent == 40:
            player = "Adv"
        else:  # opponent == "Adv"
            player, opponent = 40, 40
    elif player == "Adv":
        player = "Game"

    # Handle game completion
    if player == "Game":
        game_score[0 if is_player else 1] += 1
        player, opponent = 0, 0
        # Check for tiebreaker condition
        if game_score[0] == 6 and game_score[1] == 6:
            tiebreaker_active = True
        # Check for set completion
        elif game_score[0 if is_player else 1] >= 6 and abs(game_score[0] - game_score[1]) >= 2:
            set_score[0 if is_player else 1] += 1
            game_score = [0, 0]

    return player, opponent, game_score, set_score, tiebreaker_active


def get_score_display(player_score, opponent_score, game_score, set_score, is_player1_serving, show_server=True):
    """Generate score display string."""
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
    """Revert the last recorded game state."""
    try:
        if DEBUG_MODE:
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

            if DEBUG_MODE:
                print(f"✅ Undo successful! New state: {instance.player_score}, {instance.opponent_score}, {instance.game_score}, {instance.set_score}")

            if hasattr(instance, 'get_score_text'):
                instance.score_label.text = instance.get_score_text()
            else:
                instance.score_label.text = get_score_display(
                    instance.player_score, instance.opponent_score,
                    instance.game_score, instance.set_score,
                    instance.is_player1_serving
                )

            if hasattr(instance, 'update_live_stats'):
                instance.update_live_stats()

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
                    if DEBUG_MODE:
                        print("✅ Stats page updated successfully after undo.")
            except Exception as e:
                logging.error(f"Error updating stats screen during undo: {e}")
                if DEBUG_MODE:
                    print(f"⚠ ERROR: Could not update stats screen: {e}")
        else:
            if DEBUG_MODE:
                print("⚠ No history to undo!")

    except Exception as e:
        logging.error(f"Error in undo_last_action: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error: {e}")