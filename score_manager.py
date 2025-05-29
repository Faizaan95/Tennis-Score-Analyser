import logging
import copy  # ✅ Import deepcopy


# Configure logging (creates a log file for errors)
logging.basicConfig(
    filename="app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)



def update_score(player_score, opponent_score, game_score, set_score, result, tiebreaker_active, reason=None, stats=None):
    if stats is None:  # Only reset stats if it's completely empty
        stats = {"Ace": [0, 0], "Winner": [0, 0], "Double Fault": [0, 0], "Volley": [0, 0]}

    if result == "Won":  
        player_score, opponent_score, game_score, set_score, tiebreaker_active = calculate_tennis_score(
            player_score, opponent_score, game_score, set_score, True, tiebreaker_active
        )
    elif result == "Lost":  
        opponent_score, player_score, game_score, set_score, tiebreaker_active = calculate_tennis_score(
            opponent_score, player_score, game_score, set_score, False, tiebreaker_active
        )

        # Check if the loss was due to a double fault
        if reason == "Double Fault":
            if "Double Fault" in stats:  # Ensure key exists before updating
                stats["Double Fault"][1] += 1  

    return player_score, opponent_score, game_score, set_score, tiebreaker_active, stats

def process_score_update(instance, serve, point_type, result):
    """ Processes score updates and calls the core score update logic. """

    # 🔹 Use deepcopy() to fully copy stats (fixes the undo issue!)
    instance.history.append((
        instance.player_score,
        instance.opponent_score,
        instance.game_score[:],  # ✅ Copy list to prevent reference issues
        instance.set_score[:],  
        instance.tiebreaker_active,
        copy.deepcopy(instance.stats),  # ✅ Use deepcopy() for stats
        instance.is_player1_serving
    ))

    # Only track double faults when the player who served loses the point
    if serve == "Double Fault" and result == "Lost":
        instance.stats["Double Faults"][0 if instance.is_player1_serving else 1] += 1
    else:
        key = f"{serve} {point_type}s"  # Example: "First Serve Winners"
        if key not in instance.stats:
            instance.stats[key] = [0, 0]
        instance.stats[key][0 if result == "Won" else 1] += 1

    print(f"🏷️ Tracking key: {key}")

    # Store previous game score before updating
    prev_game_score = instance.game_score[:]

    # Call `update_score()`
    instance.player_score, instance.opponent_score, instance.game_score, instance.set_score, instance.tiebreaker_active, instance.stats = update_score(
        instance.player_score, instance.opponent_score, instance.game_score, instance.set_score, result, instance.tiebreaker_active, None, instance.stats
    )

    # Switch server if a full game was won/lost
    if instance.game_score != prev_game_score and not instance.tiebreaker_active:
        instance.is_player1_serving = not instance.is_player1_serving  

    # Update UI elements
    # Prefer screen-defined score formatting if available
    if hasattr(instance, 'get_score_text'):
        instance.score_label.text = instance.get_score_text()
    else:
        instance.score_label.text = get_score_display(
            instance.player_score, instance.opponent_score,
            instance.game_score, instance.set_score,
            instance.is_player1_serving
        )

    instance.update_live_stats()  # Refresh the live stats after updating the score


    # Close any open popups safely
    try:
        if hasattr(instance, 'popup') and instance.popup:
            instance.popup.dismiss()
    except Exception:
        pass  # Prevents errors if popup dismissal fails

def calculate_tennis_score(player, opponent, game_score, set_score, is_player, tiebreaker_active):
    tennis_points = [0, 15, 30, 40]

    # Tiebreaker logic
    if tiebreaker_active:
        player += 1  # Increment tiebreaker score for the selected player

        if player >= 7 and (player - opponent) >= 2:  # Win by 2 rule
            set_score[0 if is_player else 1] += 1  # Start new set at 1-0
            game_score = [0, 0]  # Reset game scores
            player, opponent = 0, 0  # Reset point scores
            tiebreaker_active = False  # End tiebreaker

        return player, opponent, game_score, set_score, tiebreaker_active



    # Normal point progression
    if isinstance(player, int) and player < 40:
        player = tennis_points[tennis_points.index(player) + 1]

    elif player == 40:
        if opponent in [0, 15, 30]:  # Opponent has a normal score
            player = "Game"
        elif opponent == 40:
            player = "Adv" if not is_player else "Adv" # Ensure string consistency  
        else:
            player,opponent = 40,40

    elif player == "Adv":
        if is_player:  # If player wins, he gets game
            player = "Game"
           
        elif not is_player: #If opponent wins , opponent gets game
            player = "Game"  
    

    # Game win
    if player == "Game":
        game_score[0 if is_player else 1] += 1
        player, opponent = 0, 0  

        # Check for set win (normal case)
        if game_score[0 if is_player else 1] == 6 and game_score[1 if is_player else 0] == 6:
            tiebreaker_active = True  # Activate tiebreaker at 6-6
        elif game_score[0 if is_player else 1] >= 6 and abs(game_score[0] - game_score[1]) >= 2:
            set_score[0 if is_player else 1] += 1
            game_score = [0, 0]  # Reset game scores

    return player, opponent, game_score, set_score, tiebreaker_active


def get_score_text(player_score, opponent_score, game_score, set_score, tiebreaker_active):
    if tiebreaker_active:
        return f"Tiebreaker: {player_score} - {opponent_score}\nSets: {set_score[0]} - {set_score[1]}"
    return f"Score: {player_score} - {opponent_score}\nGames: {game_score[0]} - {game_score[1]}\nSets: {set_score[0]} - {set_score[1]}"


def get_score_display(player_score, opponent_score, game_score, set_score, is_player1_serving):
    """ Returns formatted score text with server indicator. """
    server_dot_p1 = "• " if is_player1_serving else ""
    server_dot_p2 = "• " if not is_player1_serving else ""

    return (f"{server_dot_p1}Player 1: {player_score} - Opponent: {opponent_score} {server_dot_p2}\n"
            f"Games: {game_score[0]} - {game_score[1]}\n"
            f"Sets: {set_score[0]} - {set_score[1]}")


def undo_last_action(instance):
    """ Reverts the last recorded game state. """
    try:
        print("🔄 Undo button pressed!")  

        if instance.history:
            print(f"📜 History before undo: {instance.history}")  

            (
                instance.player_score,
                instance.opponent_score,
                instance.game_score,
                instance.set_score,
                instance.tiebreaker_active,
                instance.stats,  # ✅ Now fully restored thanks to deepcopy()
                instance.is_player1_serving
            ) = instance.history.pop()

            print(f"✅ Undo successful! New state: {instance.player_score}, {instance.opponent_score}, {instance.game_score}, {instance.set_score}")  

            # Update Score Display
            try:
                # Let each screen define how to display score
                if hasattr(instance, 'get_score_text'):
                    instance.score_label.text = instance.get_score_text()
                else:
                    instance.score_label.text = get_score_display(
                        instance.player_score, instance.opponent_score,
                        instance.game_score, instance.set_score,
                        instance.is_player1_serving
                    )
            except Exception as e:
                logging.error(f"Error updating score display: {e}")
            
            instance.update_live_stats()  # Refresh the live stats after undoing


            # ✅ Ensure stats are updated properly in the stats page
            stats_screen = instance.manager.get_screen("stats")
            if stats_screen:
                print("🔄 Calling update_stats() now!")  
                stats_screen.update_stats(instance.stats)  # ✅ Stats will now update correctly!
                print("✅ Stats page updated successfully after undo.")

            else:
                print("⚠ ERROR: Could not find stats screen!")

        else:
            print("⚠ No history to undo!")  

    except Exception as e:
        logging.error(f"Error in undo_last_action: {e}")
        print(f"⚠ Error: {e}")  
