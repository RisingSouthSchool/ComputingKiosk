import random, sys, time

actions = ["rock", "paper", "scissors", "quit",]
comp_actions = ["rock", "paper", "scissors"]

def main():
    
    round = 1

    print("Welcome to Rock Paper Scissors by Eli McManus!")

    while True:

        print("")
        print(f"Round {round}")

        player_action = start_game()
        comp_choice = computer_choice()

        outcome(player_action, comp_choice)

        time.sleep(1)

        round = round + 1

def start_game():

    print("Actions = 'rock' 'paper' 'scissors' or 'quit'")
    action = input("Enter a move: ").lower()

    while validate_user_input(action):
        action = input("Enter a move: ").lower()
    
    if action == "quit":
        print("See you later!")
        sys.exit()

    return action

def computer_choice():

    c_choice = random.choice(comp_actions)
    return c_choice

def validate_user_input(action_function):

    if action_function not in actions:
        print("Please enter a valid command.")
        print()
        return True
    
    else:
        return False

def outcome(player_input, computer_output):

    countdown(5)

    if player_input == computer_output:
        print("It's a draw!")
        time.sleep(0.5)
        print(f"Your opponent chose {computer_output}!")

    elif player_input == "rock" and computer_output == "scissors":
        print("You win!")
        time.sleep(0.5)
        print(f"Your opponent chose {computer_output}!")

    elif player_input == "paper" and computer_output == "rock":
        print("You win!")
        time.sleep(0.5)
        print(f"Your opponent chose {computer_output}!")

    elif player_input == "scissors" and computer_output == "paper":
        print("You win!")
        time.sleep(0.5)
        print(f"Your opponent chose {computer_output}!")
    else:
        print("You lose!")
        time.sleep(0.5)
        print(f"Your opponent chose {computer_output}!")

def countdown(seconds): 

    while seconds > 0:
        print(f"Outcome pending: {seconds:02d}", end="\r")
        time.sleep(1)
        seconds -= 1
    print("Outcome decided         ")

    time.sleep(0.5)
    suspense = "..."
    for char in suspense:
        print(char, end='', flush=True)
        time.sleep(0.7)

main()