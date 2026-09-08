# AI Assistance: ChatGPT 
# Prompt used: "how do i build a deck of 52 standard cards in python for my blackjack project"
# Date: 15 April 2026

# AI Assistance: ChatGPT 
# Prompt used: "how hard is it to make it so the print hand statement doesnt just print a tuple and make it print just like 6♥, 7♠ etc"
# Date: 2 May 2026


import random
import sys

values = {
    "A": 11,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9":  9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10
}

suits = ['♥', '♦', '♣', '♠']
ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

deck = [(rank, suit) for suit in suits for rank in ranks] 

#  Teacher comment --> essentially this, builds a 2d array. Shorthand shows AI assistance, Sascha needs to demonstrate that he understands this
# for suit in suits:
#     for rank in ranks:
#         deck.append((rank, suit))
double_deck = deck * 2

def deal_card():
    """draws card from deck, removes the card from double_deck"""
    card = random.choice(double_deck )
    double_deck.remove(card)
    return card

player_win = False
playerfunds = 250.0
min_bet = 25
bet_size = 0

def start_game():
    """imports user's bet and validates input, prints players hand neatly"""
    global bet_size
    global playerfunds
    global min_bet

    while True:
        try:
            bet_size = float(input(f"(Type '1' to Quit!) (Minimum Bet Size: $25) (Your Funds: ${playerfunds}) Bet Size: "))
            print()

            if bet_size == 1:
                quitgame()

            elif bet_size > playerfunds:
                print("You're too broke for that!")
                
            elif bet_size < min_bet:
                print("You gotta spend a little more than that")
                
            else:
                break

        except ValueError:
            print("Enter a number")
            print()

    print(f"Player: {player_hand[0][0] + player_hand[0][1]} {player_hand[1][0] + player_hand[1][1]}")
    print(f"Dealer: {dealer_hand[0][0] + dealer_hand[0][1]} ??")
    print()
    

def calculate_hand(hand):
    """calculates score of hand passed through function, returning the total"""
    total = 0
    ace_count = 0

    for card in hand:
        rank = card[0]
        total = total + values[rank]

        if rank == "A":
            ace_count = ace_count + 1
    
    while total > 21 and ace_count > 0:
        total = total - 10
        ace_count = ace_count - 1

    return total


def player_action():
    """inputs the user's action and validates it"""

    while True:
        try:
            
            action = int(input("Hit (1), Stand (2): "))
            
            if action == 1:
                player_hand.append(deal_card())
                print(f"You drew {player_hand[-1][0]}{player_hand[-1][1]}")
                print("Hand:", "  ".join(card[0] + card[1] for card in player_hand))
                print()
                
                if validate_score(player_hand) == False:
                    return "bust"
                
            elif action == 2:
                #stand
                print(f"You Stood: Final Hand: {calculate_hand(player_hand)} ")
                print()
                
                return "stand"
                
            else:
                print("Enter a valid action")

        except ValueError:
            print("Enter a valid action")


def validate_score(player_hand):
    """if players hand is greater than 21 they lose the game and their funds, prints message. If else, continue"""
    global bet_size
    global playerfunds

    if calculate_hand(player_hand) > 21:
        print("You bust!")
        playerfunds = playerfunds - bet_size

        print(f"You lost ${bet_size}")
        print(f"Total Funds: ${playerfunds}")
        print()

        return False
    return True
        
def dealer_actions():
    """dealer ai to draw cards until score >= 17, prints dealer's hand"""
    global player_win

    dtotal = calculate_hand(dealer_hand)

    print("Dealer Hand: ")
    print("Hand:", "  ".join(card[0] + card[1] for card in dealer_hand))
    print()

    while dtotal < 17:
        dealer_hand.append(deal_card())
        dtotal = calculate_hand(dealer_hand)
        print("Dealer:", " ".join(card[0] + card[1] for card in dealer_hand))

        if dtotal > 21: 
            print("Dealer Bust")
            print()
            return "dealer_bust"

def player_win_check():
    """if player win is true, double their bet size and add it to funds, print win message"""
    global bet_size
    global playerfunds

    if player_win == True:
        print(f"You won {bet_size}!")
        
        playerfunds = playerfunds + bet_size
        print(f"Total Funds ${playerfunds}!")
        print()


def win_calculator(dealer_hand, player_hand):
    """compares dealer's hand and user's hand and calculates the result of the round"""
    global player_win
    global playerfunds

    player_total = calculate_hand(player_hand)
    dealer_total = calculate_hand(dealer_hand)

    if player_total > dealer_total and player_total < 22:
        player_win = True
        player_win_check()

    elif player_total < dealer_total and dealer_total < 22:
        print("Dealer won!")
        print()

        playerfunds = playerfunds - bet_size
        print(f"You lost ${bet_size}!")
        print(f"Total Funds: ${playerfunds}")
  
    elif player_total == dealer_total:
        print("Draw, Bet returned")
        print(f"Total Funds: ${playerfunds}")

def quitgame():
    """quit the game and print total funds """
    global playerfunds

    print(f"Final Funds: {playerfunds}")
    sys.exit("Game over!")
    

def main():
    "main game loop, while user has funds available, game runs"
    global player_hand
    global dealer_hand
    global playerfunds
    global min_bet
    global player_win
    global maxfunds

    print("Welcome to Sascha's version of blackjack. The rules mimic that of real life blackjack, the only exception being " \
    "that you can't split and double down. Your bet size is doubled if you win. Enjoy!")
    print()
    print()

    while playerfunds >= min_bet:

        player_hand = [deal_card(), deal_card()]
        dealer_hand = [deal_card(), deal_card()]

        start_game()

        result = player_action()

        if result == "bust":
            print("Dealer Hand:", " ".join(card[0] + card[1] for card in dealer_hand))
            print("New round! Goodluck!!")
            print()
            continue 
        
        dealer_result = dealer_actions()

        if dealer_result == "dealer_bust":
            player_win = True
            player_win_check()
            print("New round! Goodluck!!")
            print()
            continue

        win_calculator(dealer_hand, player_hand)
        player_win = False
        
        print("New Round! Goodluck!!")
        print()
        
    print("You're BROKE! Thanks for losing")


main() 