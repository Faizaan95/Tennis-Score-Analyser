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
        player_score, opponent_score, game_score, set_score, tiebreaker_active,set_completed,game_score_before_reset  = calculate_tennis_score(
            player_score, opponent_score, game_score, set_score, True, tiebreaker_active, is_dedicated_tiebreaker
        )
    elif result == "Lost":
        opponent_score, player_score, game_score, set_score, tiebreaker_active,set_completed,game_score_before_reset = calculate_tennis_score(
            opponent_score, player_score, game_score, set_score, False, tiebreaker_active, is_dedicated_tiebreaker
        )

        # Handle double fault stats in the legacy function
        if reason == "Double Fault":
            if "Double Fault" in stats:
                stats["Double Fault"][1] += 1

    return player_score, opponent_score, game_score, set_score, tiebreaker_active, stats,set_completed,game_score_before_reset


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

       

        # Process statistics based on serve and point type
        update_match_statistics(instance, serve, point_type, result)

        # Store previous game score for server switching
        prev_game_score = instance.game_score[:]

        # Update tennis score using the existing function
        

        instance.player_score, instance.opponent_score, instance.game_score, instance.set_score, instance.tiebreaker_active, instance.stats,set_completed,game_score_before_reset = update_score(
            instance.player_score, instance.opponent_score, instance.game_score, instance.set_score,
            result, instance.tiebreaker_active, serve if point_type == "Double Fault" else None, instance.stats, is_dedicated_tiebreaker
        )

        if set_completed and game_score_before_reset and hasattr(instance, "set_history"):
            instance.set_history.append(f"{game_score_before_reset[0]}-{game_score_before_reset[1]}")
            if DEBUG_MODE:
                print("📝 Set history updated:", instance.set_history)



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
            import traceback
            print(f"📊 STATS CALL: serve='{serve}', point_type='{point_type}', result='{result}'")
            print(f"📊 CALL STACK: {traceback.format_stack()[-3:-1]}")  # Show where this was called from


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

            # Add specific serve ace tracking
            if serve in ["First Serve", "Second Serve"]:
                ace_key = f"{serve} Aces"
                if ace_key not in instance.stats:
                    instance.stats[ace_key] = [0, 0]
                instance.stats[ace_key][0] += 1
                
                # Track serves in for aces (only once)
                serve_in_key = f"{serve}s In"
                if serve_in_key not in instance.stats:
                    instance.stats[serve_in_key] = [0, 0]
                instance.stats[serve_in_key][0] += 1
                
                if DEBUG_MODE:
                    print(f"📊 Tracked: {ace_key} and {serve_in_key}")

            if DEBUG_MODE:
                print("📊 Tracked: Aces")
            return

        # Track serves in (only for non-ace, non-double fault serves)
        if serve in ["First Serve", "Second Serve"] and point_type != "Double Fault":
            serve_in_key = f"{serve}s In"
            if serve_in_key not in instance.stats:
                instance.stats[serve_in_key] = [0, 0]
            
            if result == "Won":
                instance.stats[serve_in_key][0] += 1
            else:
                instance.stats[serve_in_key][1] += 1

        # Parse the point_type to extract shot and outcome
        point_parts = point_type.split()
        
        if len(point_parts) >= 2:
            shot_type, outcome = point_parts[0], point_parts[1]
            
            # Track winners and errors
            if result == "Won":
                if "Winner" in outcome:
                    # Player winner
                    instance.stats.setdefault("Winners", [0,0])[0] += 1
                    if serve in ["First Serve", "Second Serve"]:
                        instance.stats.setdefault(f"{serve} Winners", [0,0])[0] += 1
                    if DEBUG_MODE:
                        print("📊 Tracked: Player Winner")

                elif "Error" in outcome or "Error" in point_type:
                    instance.stats.setdefault("Errors", [0, 0])[1] += 1  # Opponent made an error
                    if DEBUG_MODE:
                        print("📊 Tracked: Opponent Error → Player Wins")

            elif result == "Lost":
                if "Winner" in outcome:
                    # Opponent hit a winner
                    instance.stats.setdefault("Winners", [0,0])[1] += 1
                    if serve in ["First Serve", "Second Serve"]:
                        instance.stats.setdefault(f"{serve} Winners", [0,0])[1] += 1
                    if DEBUG_MODE:
                        print("📊 Tracked: Opponent Winner")

                elif "Error" in outcome:
                    instance.stats.setdefault("Errors", [0, 0])[0] += 1  # Player made an error
                    if DEBUG_MODE:
                        print("📊 Tracked: Player Error → Point Lost")

            # Track specific shot types on serves
            if serve in ["First Serve", "Second Serve"]:
                serve_shot_key = f"{serve} {point_type}s"
                if serve_shot_key not in instance.stats:
                    instance.stats[serve_shot_key] = [0, 0]
                
                if "Error" in outcome and result == "Lost":
                    instance.stats[serve_shot_key][0] += 1  # Player error
                elif "Error" in outcome and result == "Won":
                    instance.stats[serve_shot_key][1] += 1  # Opponent error
                else:
                    instance.stats[serve_shot_key][0 if result == "Won" else 1] += 1


    except Exception as e:
        logging.error(f"Error updating match statistics: {e}")
        if DEBUG_MODE:
            print(f"⚠ Error updating statistics: {e}")

    if DEBUG_MODE:
        print(f"📈 Current Stats: {instance.stats}")
        
def calculate_tennis_score(player, opponent, game_score, set_score, is_player, tiebreaker_active, is_dedicated_tiebreaker=False):
    """Calculate tennis score progression."""
    tennis_points = [0, 15, 30, 40]
    
    set_completed = False
    game_score_before_reset = None 

    if tiebreaker_active:
        player += 1

        if is_dedicated_tiebreaker:
            return player, opponent, game_score, set_score, tiebreaker_active, set_completed, game_score_before_reset

        if player >= 7 and (player - opponent) >= 2:
            set_score[0 if is_player else 1] += 1
            game_score = [0, 0]
            player, opponent = 0, 0
            tiebreaker_active = False
            set_completed = True

        return player, opponent, game_score, set_score, tiebreaker_active, set_completed, game_score_before_reset

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
        # Increment game first
        game_score[0 if is_player else 1] += 1

        # Check if this caused a set completion
        if game_score[0 if is_player else 1] >= 6 and abs(game_score[0] - game_score[1]) >= 2:
            # Capture the completed set before reset
            set_completed = True
            game_score_before_reset = game_score[:]
            set_score[0 if is_player else 1] += 1
            game_score = [0, 0]
        

        # Check for tiebreaker only if set wasn't completed
        elif game_score[0] == 6 and game_score[1] == 6:
            tiebreaker_active = True

        # Reset points
        player, opponent = 0, 0


    return player, opponent, game_score, set_score, tiebreaker_active,set_completed,game_score_before_reset


def get_score_display(player_score, opponent_score, game_score, set_score, is_player1_serving, show_server=True):
    """Generate score display string with markup."""
    if show_server:
        server_dot_p1 = "[color=ffaa00]•[/color] " if is_player1_serving else ""
        server_dot_p2 = " [color=ffaa00]•[/color]" if not is_player1_serving else ""
    else:
        server_dot_p1 = ""
        server_dot_p2 = ""

        

    return (
        f"{server_dot_p1}[color=#cdbf17][b]Player[/b]: [color=ffffff]{player_score} - [color=#cdbf17][b]Opponent[/b]"
        f"[color=#cdbf17]: [color=ffffff]{opponent_score}[color=ffffff]{server_dot_p2}\n"
        f"[color=#cdbf17][b]Games[/b]: [color=ffffff]{game_score[0]} - {game_score[1]}[/color]\n"
        f"[color=#cdbf17][b]Sets[/b]: [color=ffffff]{set_score[0]} - {set_score[1]}[/color]"
    )

def get_tiebreak_score_display(player_score, opponent_score, is_player1_serving, show_server=True):
    """Generate a custom score display for tiebreakers with markup."""
    server_dot_p1 = "[color=ffaa00]•[/color] " if is_player1_serving and show_server else ""
    server_dot_p2 = " [color=ffaa00]•[/color]" if not is_player1_serving and show_server else ""

    return (
        f"{server_dot_p1}[color=#cdbf17][b]Player[/b]: [color=ffffff]{player_score} "
        f"- [color=#cdbf17][b]Opponent[/b]: [color=ffffff]{opponent_score}{server_dot_p2}"
    )


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