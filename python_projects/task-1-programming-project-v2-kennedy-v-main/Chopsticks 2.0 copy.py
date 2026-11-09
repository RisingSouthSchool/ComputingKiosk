import math

killword = "terminate"
force_error = 0 # used in tadem with terimante function#
P1_left_score = 1 # replaced fingers for score and remove hand from variable name to simplify code #
P1_right_score = 1
P2_left_score = 1
P2_right_score = 1
player_turn = 1

def terminate_code():
    print("")
    print("Preparing Termination...")
    print("...")
    print("Preperations Complete!")
    print("")
    shutdown

def close_game():
    print("")
    print("Closing Game...")
    print("...")
    shutdown()

def shutdown():
    print("The game will now shut down Via Forced Error.")
    print("Executing Forced Error...")
    print("...")
    print("Have A Nice Day!")
    print("")
    print(force_error.lower) # Will force an error, stopping the code. #

def confirm_game_start(killword):
    start_game = input("Would you like to play chopsticks?(Y/N): ")
    while True:
        if start_game == "Y" or start_game == "y":
            print("")
            print("Starting game.")
            game_loop(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score, player_turn)
            break
        elif start_game == "N" or start_game == "n":
            print("Understood. Feel free to start game when your ready.")
            start_game = input("Would you like to play chopsticks?(Y/N): ")
        elif start_game == killword:
            terminate_code()
            break
        else:
            print(f"ERROR: {start_game} is not a valid input or command.")
            print("Please enter a valid input or command.")
            start_game = input("Would you like to play chopsticks?(Y/N): ")

def game_loop(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score, player_turn):
    game_state(P1_left_score, P1_right_score, P2_left_score, P2_right_score)
    while True:
        if player_turn == 1:
            P1_turn(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score, player_turn)
            player_turn = player_turn + 1

        elif player_turn == 2:
            P2_turn(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score, player_turn)
            player_turn = player_turn - 1

        else:
            print("TURN ORDER ERROR!")
            print("Ending and shutting down current game.")
            print("Please see a coder for repairs if this error contines to occurr.")
            print("Code shutt down. Have a nice day.")
            break

def game_state(P1_left_score, P1_right_score, P2_left_score, P2_right_score):
    print("")
    print(f"Player 1's lefthand score is {P1_left_score}")
    print(f"Player 1's right hand score is {P1_right_score}")
    print("")
    print(f"Player 2's left hand score is {P2_left_score}")
    print(f"Player 2's right hand score is {P2_right_score}")
    print("")

def P1_turn(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score,player_turn):
    while True:
        print("What would you like to do player 1?")
        action = input("Attack(A), Balance(B) or Surrender(S)? ")
        if action == "Attack" or action == "A" or action == "attack" or action == "a":
            action_word = "Attack" # Used to tell player their action (Attack) is in confrim_action istead of what they inputed (A) #
            confirm_P1_action(action_word)
            P1_atack_P2(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score)
            break
        elif action == "Balance" or action == "B" or action == "balance" or action == "b":
            action_word = "Balance"
            confirm_P1_action(action_word)
            P1_balance(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score)
            break
        elif action == "Surrender" or action == "S" or action == "surrender" or action == "s":
            action_word = "Surrender"
            confirm_P1_action(action_word)
            P1_surrender()
            break
        elif action == killword:
            terminate_code()
            break
        else:
            print("")
            print(f"ERROR: {action} is not a valid input or command.")
            print("Please enter a valid input or command.")
            action = input("Attack(A), Swap(S) or Surrender(G)? ")

def P2_turn(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score, player_turn):
    while True:
        print("What would you like to do player 1?")
        action = input("Attack(A), Balance(B) or Surrender(S)? ")
        if action == "Attack" or action == "A" or action == "attack" or action == "a":
            action_word = "Attack"
            confirm_P2_action(action_word)
            P2_atack_P1(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score)
            break
        elif action == "Balance" or action == "B" or action == "balance" or action == "b":
            action_word = "Balance"
            confirm_P2_action(action_word)
            P2_balance(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score)
            break
        elif action == "Surrender" or action == "S" or action == "surrender" or action == "s":
            action_word = "Surrender"
            confirm_P2_action(action_word)
            P2_surrender()
            break
        elif action == killword:
            terminate_code()
            break
        else:
            print("")
            print(f"ERROR: {action} is not a valid input or command.")
            print("Please enter a valid input or command.")
            action = input("Attack(A), Swap(S) or Surrender(G)? ")

def confirm_P1_action(action_word):
    while True:
        print("")
        confirm = input(f"Confirm action {action_word}?(Y/N): ")
        print("")
        if confirm == "Y" or confirm == "y" or confirm == "Confirm" or confirm == "confirm":
            confirm = "N/A" # To cancel previously cancel moves from being confirm wehn canceling again #
            break
        elif confirm == "N" or confirm == "n":
            confirm = "N/A" # To cancel previously cancel moves from being confirm wehn canceling again #
            game_state(P1_left_score, P1_right_score, P2_left_score, P2_right_score)
            P1_turn(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score,player_turn)
            break
        elif confirm == killword:
            terminate_code()
            break
        else:
            print("")
            print(f"ERROR: {confirm} is not a valid input or command.")
            print("Please enter a valid input or command.")
            confirm = input(f"Confirm action {action_word}?(Y/N)")

def confirm_P2_action(action_word):
    while True:
        print("")
        confirm = input(f"Confirm action {action_word}?(Y/N): ")
        print("")
        if confirm == "Y" or confirm == "y" or confirm == "Confirm" or confirm == "confirm":
            confirm = "N/A"
            break
        elif confirm == "N" or confirm == "n":
            confirm = "N/A"
            game_state(P1_left_score, P1_right_score, P2_left_score, P2_right_score)
            P1_turn(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score,player_turn)
            break
        elif confirm == killword:
            terminate_code()
            break
        else:
            print("")
            print(f"ERROR: {confirm} is not a valid input or command.")
            print("Please enter a valid input or command.")
            confirm = input(f"Confirm action {action_word}?(Y/N)")

def P1_atack_P2(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score,action_word):
    game_state(P1_left_score, P1_right_score, P2_left_score, P2_right_score)
    print("Which Hand Would You Like to Attack With?")
    P1_attacking_hand = input(f"Left Hand(L):{P1_left_score} Or Right Hand(R):{P1_left_score}? ")
    action_word = P1_attacking_hand
    confirm_P1_action(action_word)
    while True:
        if P1_attacking_hand == "Left Hand" or P1_attacking_hand == "L" or P1_attacking_hand == "Left" or P1_attacking_hand == "left Hand" or P1_attacking_hand == "l" or P1_attacking_hand == "left":
            attacking_value = P1_left_score
            break
        elif P1_attacking_hand == "Right Hand" or P1_attacking_hand == "R" or P1_attacking_hand == "Right" or P1_attacking_hand == "right Hand" or P1_attacking_hand == "r" or P1_attacking_hand == "right":
            attacking_value = P1_right_score
            break
        elif P1_attacking_hand == killword:
            terminate_code()
            break
        else:
            print("")
            print(f"ERROR: {P1_attacking_hand} is not a valid input or command.")
            print("Please enter a valid input or command.")
            print("")
            print("Which Hand Would You Like to Attack With?")
            P1_attacking_hand = input(f"Left Hand(L):{P1_left_score} Or Right Hand(R):{P1_left_score}? ")
            action_word = P1_attacking_hand
            confirm_P1_action(action_word)
    

def P1_balance(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score):
    game_state(P1_left_score, P1_right_score, P2_left_score, P2_right_score)
    print("Balancing Player 1's left and right hand scores...")
    total_score = P1_left_score + P1_right_score
    print("Balancing...")
    print("...")
    if P1_right_score > P1_left_score:
        P1_right_score = math.ceil(total_score/2) # We round one hand up and the other down to avoid loosing or increasing score #
        print("Balancing...")
        print("...")
        P1_left_score = math.floor(total_score/2)
    else:
        P1_left_score = math.ceil(total_score/2)
        print("Balancing...")
        print("...")
        P1_right_score = math.floor(total_score/2)
    print("Score Balanced!")
    print("")
    print(P1_left_score)
    print(P1_right_score)
    game_state(P1_left_score, P1_right_score, P2_left_score, P2_right_score)
    total_score = 0 # Set total_value back to zero incase of caring over any scores #

def P2_atack_P1(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score):
    game_state(P1_left_score, P1_right_score, P2_left_score, P2_right_score)


def P2_balance(killword, P1_left_score, P1_right_score, P2_left_score, P2_right_score):
    print("Balancing Player 1's left and right hand scores...")
    total_score = P2_left_score + P2_right_score
    print("Balancing...")
    print("...")
    if P2_right_score > P2_left_score:
        P2_right_score = math.ceil(total_score/2)
        print("Balancing...")
        print("...")
        P2_left_score = math.floor(total_score/2)
    else:
        P2_left_score = math.ceil(total_score/2)
        print("Balancing...")
        print("...")
        P2_right_score = math.floor(total_score/2)
    print("Score Balanced!")
    print("")
    print(P2_left_score)
    print(P2_right_score)
    game_state(P1_left_score, P1_right_score, P2_left_score, P2_right_score)
    total_score = 0

def P1_surrender():
    print("Player 1 surrenders!")
    print("Player 2 Wins!")
    print("Now Commencing Auto Shutdown...")
    close_game()

def P2_surrender():
    print("Player 2 surrenders!")
    print("Player 1 Wins!")
    print("")
    print("Now Commencing Auto Shutdown...")
    close_game()
    
confirm_game_start(killword)