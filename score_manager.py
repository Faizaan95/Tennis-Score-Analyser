import logging



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

    # Only track double faults when the player who served loses the point
    if serve == "Double Fault" and result == "Lost":
        instance.stats["Double Faults"][0 if instance.is_player1_serving else 1] += 1
    else:
        key = f"{serve} {point_type}s"  # Example: "First Serve Winners"
        if key in instance.stats:
            instance.stats[key][0 if result == "Won" else 1] += 1  

    # Store previous game score before updating
    prev_game_score = instance.game_score[:]

    # Call `update_score()` from score_manager.py
    instance.player_score, instance.opponent_score, instance.game_score, instance.set_score, instance.tiebreaker_active, instance.stats = update_score(
        instance.player_score, instance.opponent_score, instance.game_score, instance.set_score, result, instance.tiebreaker_active, None, instance.stats
    )

    # Switch server if a full game was won/lost
    if instance.game_score != prev_game_score and not instance.tiebreaker_active:
        instance.is_player1_serving = not instance.is_player1_serving  

    # Update UI elements
    instance.score_label.text = get_score_display(
    instance.player_score, instance.opponent_score, instance.game_score, instance.set_score, instance.is_player1_serving
    )
    instance.live_stats_label.text = instance.get_live_stats_text()

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
