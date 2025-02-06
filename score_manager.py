def update_score(player_score, opponent_score, game_score, set_score, result, tiebreaker_active, reason=None, stats=None):
    if stats is None:
        stats = {"Aces": [0, 0], "Winners": [0, 0], "Double Fault": [0, 0], "Volleys Won": [0, 0]}

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
            stats["Double Fault"][1] += 1  # Increase opponent's double fault count

    return player_score, opponent_score, game_score, set_score, tiebreaker_active, stats



def calculate_tennis_score(player, opponent, game_score, set_score, is_player, tiebreaker_active):
    tennis_points = [0, 15, 30, 40]

    # Tiebreaker logic
    if tiebreaker_active:
        player += 1  # Increment tiebreaker score for the selected player

        if player >= 7 and (player - opponent) >= 2:  # Win by 2 rule
            set_score[0 if is_player else 1] += 1  # Award the set
            game_score = [0, 0]  # Reset game scores
            player, opponent = 0, 0  # Reset points
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
