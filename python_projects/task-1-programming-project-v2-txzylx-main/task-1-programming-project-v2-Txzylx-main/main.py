# READ PLS
# This was an extremely hard project for me, therefore it comes with multiple faults. Its not a perfect game, it doesnt have many
# logic of a real poker game, but it runs and it uses all the coding knowledge I have. If i had more knowledge i could make this better
# but i just used my knowledge of lists, functions and loops to make this. 
# 
# For marked sections AI has been used to edit lines of code
# Youtube Tutorials have been used to give ideas
# https://www.youtube.com/watch?v=uwgRf51YUGY
# https://www.youtube.com/watch?v=h7HkazD7Ro8
# https://www.youtube.com/watch?v=dmvvEDSfQeM



# ALL AI USE REFERENCED



# AI Assistance: ChatGPT

# Prompt used: "How do i make the game exit?"

# Date: May 2nd 2026

# Modifications: Added sys library



# AI Assistance: ChatGPT

# Prompt used: "Sort this list out"

# Date: April 2026

# Modifications: Sorted the cards list
 


# AI Assistance: ChatGPT

# Prompt used: "How do i check if 5 numbers are consecutive

# Date: May 2nd 2026

# Modifications: Added "if values == list(range(values[0], values[0] + 5)):""



# AI Assistance: ChatGPT

# Prompt used: "How do i sort 5 numbers

# Date: May 2nd 2026

# Modifications: Added values.sort



# AI Assistance: ChatGPT

# Prompt used: Make me a list of all the suits and an emoji for each one

# Date: May 3rd 2026

# Modifications: Added list of suits and their corresponding emojis



# AI Assistance: ChatGPT

# Prompt used: "Make me ascii art for cards - add empty zones for variables that i will add in"

# Date: April 2026

# Modifications: Added ascii art for cards

# AI Assistance: ChatGPT

# Prompt used: "How do i print all ascii art next to each other?

# Date: April 2026

# Modifications: added "for line_number in range(len(ascii_cards[0])):""

import random # random library
import sys # this is for when the user folds to exit the game
cards = [ ## ai used for readability
    '2 of Spades', '3 of Spades', '4 of Spades', '5 of Spades',
    '6 of Spades', '7 of Spades', '8 of Spades', '9 of Spades', '10 of Spades',
    'Jack of Spades', 'Queen of Spades', 'King of Spades', 'Ace of Spades',

    '2 of Diamonds', '3 of Diamonds', '4 of Diamonds', '5 of Diamonds',
    '6 of Diamonds', '7 of Diamonds', '8 of Diamonds', '9 of Diamonds', '10 of Diamonds',
    'Jack of Diamonds', 'Queen of Diamonds', 'King of Diamonds', 'Ace of Diamonds',

    '2 of Clubs', '3 of Clubs', '4 of Clubs', '5 of Clubs',
    '6 of Clubs', '7 of Clubs', '8 of Clubs', '9 of Clubs', '10 of Clubs',
    'Jack of Clubs', 'Queen of Clubs', 'King of Clubs', 'Ace of Clubs',

    '2 of Hearts', '3 of Hearts', '4 of Hearts', '5 of Hearts',
    '6 of Hearts', '7 of Hearts', '8 of Hearts', '9 of Hearts', '10 of Hearts',
    'Jack of Hearts', 'Queen of Hearts', 'King of Hearts', 'Ace of Hearts'
]
def pairfinder(cards): # code to check if a bot has a pair
    ranks = []
    for card in cards:
        rank = card.split(" of ")[0] # this gets the rank, 0 is the index BEFORE of
        ranks.append(rank)
    rank_counts = {}
    
    for rank in ranks:
        if rank in rank_counts: # if this rank has been seen before then add 1 to count
            rank_counts[rank] += 1
        else:
            rank_counts[rank] = 1 # if its the first time its being seen set count to 1. 

    if 2 in rank_counts.values(): # if theres 2 counts of one rank that means there is a pair
        return True #returns true if there is a pair
    else:
        return False # returns false if there is no pair

def threeofakindfinder(cards): # same concept but instead of 2 of the same rank there must be 3 to return true
        ranks = []
        for card in cards:
            rank = card.split(" of ")[0]
            ranks.append(rank)
        rank_counts = {}

        for rank in ranks:
            if rank in rank_counts:
                rank_counts[rank] += 1
            else:
                rank_counts[rank] = 1

        if 3 in rank_counts.values():
            return True
        else:
            return False
        
def fullhouse(cards): # finds if there is a full house in a bots deck (3 of a kind + pair)
    ranks = []
    for card in cards:
        rank = card.split(" of ")[0] # gets rank (index before 0)
        ranks.append(rank) # appends rank to the empty ranks list
    rank_counts = {} # rank count set to 0
    
    for rank in ranks:# loop through all ranks
        if rank in rank_counts: 
            rank_counts[rank] += 1 #add one to count if the rank has been seen already
        else:
            rank_counts[rank] = 1 #else set the rank count to 1

    has_three = 3 in rank_counts.values() # the 3 of a kind is 3 in rank counts
    has_pair = 2 in rank_counts.values() # the pair

    if has_three and has_pair: # if there is a three of a kind and a pair it returns true for a full house
        return True
    else:
        return False
    
def flush(cards): # code for if a bot has a flush
    suits = [] # empty suits list

    for card in cards: # loops through cards
        suit = card.split(" of ")[1] # gets the 1 index (AFTER the of) to get the suit
        suits.append(suit) # appends the suit to the suits list
    suit_counts = {} # empty count of suits

    for suit in suits:
        if suit in suit_counts:
            suit_counts[suit] += 1 # if something appears multiple times add it 
        else:
            suit_counts[suit] = 1 # if its the first time set val to 1
            
    for count in suit_counts.values(): 
        if count >= 5: # if there is 5 or more of a suit then there is a flush
            return True

    return False # if no flush

def straight(cards): # code for if a bot has a straight
    if len(cards) < 5: # makes it so that in the early rounds its automatically false as a straight is not possible
        return False

    
    rank_values = { # sets a value to each rank
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "Jack": 11,
        "Queen": 12,
        "King": 13,
        "Ace": 14
    }
    values = [] # empty value list
    for card in cards: # loops through cards 
        rank = card.split(" of ")[0] # gets the rank of a card
        values.append(rank_values[rank]) # appends the value to the value list
    values.sort() # AI used for this line: sorts values in order

    if values == list(range(values[0], values[0] + 5)): # ai used for logic of this line, checks if 5 cards are consecutive (I had no idea how to do it)
        return True
    else: 
        return False
    

#### My old code im leaving it to show the process of making my functions
       
    # original threeofakind - leaving here so i can edit my new code
# def three_of_a_kind_finder(): #edited pairfinder code
   # for player in player_cards:
     #   cards = player_cards[player]
      #  rank1 = cards[0][:2].strip()
      #  rank2 = cards[1][:2].strip()
      #  rank3 = cards[2][:2].strip()
       # if rank1 == rank2:
       #     if rank2 == rank3:
        #        if player == "usercards": 
         #           print(f"{user} has a three of a kind") 
          #          continue #skips loop for the user so they dont raise automatically - ai used to find solution for this problem
 
          #      amountraise = random.randint(0, 60) / 100
          #      player_number = player.split("_")[1]
          #      money = player_values[f"player{player_number}val"]
           #     player_name = f"Player {player_number}"
           #     raisenumber = amountraise * money
            #    print(f"{player_name} raised {raisenumber}")


# original full house - also leaving to edit code
#def full_house(): 
    #for player in player_cards:
      #  cards = player_cards[player]
      #  ranks = []

       # for card in cards:
       #     rank = card[::2].strip
        #    ranks.append(rank)
        
      #  rank_counts = {}
       # for rank in ranks:
        #    if rank in rank_counts:
        #       rank_counts[rank] += 1
         #   else:
         #       rank_counts[rank] = 1
        
      #  has_three = 3 in rank_counts.values()
      #  has_pair = 2 in rank_counts.values()

       # if has_three and has_pair:
         #   if player == "usercards":
         #       print(f"{user} has a full house")
           #     continue          
         #   amountraise = random.randint(0, 60) / 100
         #   player_number = player.split("_")[1]
          #  money = player_values[f"player{player_number}val"]
          #  player_name = f"Player {player_number}"
          ##  raisenumber = amountraise * money
         #   print(f"{player_name} has a full house")
          #  print(f"{player_name} raised {raisenumber}")            
      
# def flush(): original flush code
    #for player in player_cards:
     #   cards = player_cards[player]
     #   suits = []

      #  for card in cards:
         #   suit = card.split(" of ")[1]
        #    suits.append(suit)

       # if len(set(suits)) == 1: #ai used for this line, removes duplicates - original line was "if suits[0] == suits[1] == suits[2] == suits[3] == suits[4]""
        #    if player == "usercards":
            #    print(f"{user} has a flush")
             #   continue
        
           # player_number = player.split("_")[1]
           # money = player_values[f"player{player_number}val"]
           # player_name = f"Player {player_number}"
           # print(f"{player_name} has a flush")
           # amountraise = random.randint(40, 100) / 100
          #  raisenumber = amountraise * money
          #  print(f"{player_name} raised {raisenumber}")


# def straight(): original straight code
    #rank_values = { #converts string to integers
      #  "2": 2, 
      #  "3": 3,
     #   "4": 4,
      #  "5": 5,
      #  "6": 6,
      #  "7": 7,
      #  "8": 8,
       # "9": 9,
      #  "10": 10,
       # "Jack": 11,
       # "Queen": 12,
       # "King": 13,
       # "Ace": 14
    
  #  for player in player_cards:
      #  cards = player_cards[player]

       # values = []

       # for card in cards:
        #    rank = card.split(" of ")[0]
         #   values.append(rank_values[rank])

      #  values.sort()

      #  if values[0] + values[1] + values[2] + values[3] + values[4] == values[4] + 4:
        #    if player == "usercards":
            #    print(f"{user} has a straight")
             #   continue
         #   player_number = player.split("_")[1]
         #   money = player_values[f"player{player_number}val"]
          #  player_name = f"Player {player_number}"  
          #  print(f"{player_name} has a straight")
           # amountraise = random.randint(40, 100) / 100
           # raisenumber = amountraise * money
           # print(f"{player_name} raised {raisenumber}")

def hand_rank(cards): # ranks of each hand
    if fullhouse(cards):
        return 6 # highest rank
    elif flush(cards):
        return 5 # 2nd highest
    elif straight(cards):
        return 4 #3rd highest
    elif threeofakindfinder(cards):
        return 3 #4th highest
    elif pairfinder(cards):
        return 2 #5th highest
    else:
        return 1 #6th highest

def find_winner(pot): # finds the winner of the game
    best_score = 0 #empty score
    winner = None # no winner currently 
    for player in active_players:
        if player == "user": # if the player is the user
            cards = player_cards["usercards"] #then get the cards for the user
            name = "You"
        else:
            cards = player_cards[f"player_{player}"] # this is for the bots
            name = f"Player {player}"
        score = hand_rank(cards) # gets the score for each hand
        if score > best_score: # if a players score is greater than the best score
            best_score = score # then set the best score to that score
            winner = name # the winner is the player who wins
    print(f"{winner} wins the pot of {pot}") # prints the winner and how much money

def cardasciiconverter(card): #splits cards up to their suits and their rank
    rank = card.split(" of ")[0] #0 is the rank
    suit = card.split(" of ")[1] #1 is the suit

    suit_symbols = { # AI used to make this list
        "Spades": "♠",
        "Hearts": "♥",
        "Diamonds": "♦",
        "Clubs": "♣"

    }

    rank_symbols = { #turns all the face cards into a letter instead of the full word
        "Jack": "J",
        "Queen": "Q",
        "King": "K",
        "Ace": "A"
    }

    display_rank = rank_symbols.get(rank, rank) # displays converted face cards and original numbers
    suit_symbol = suit_symbols[suit] #returns emoji from suit


    return [ #AI used to make this ascii art
        "┌─────────┐",
        f"│{display_rank:<2}       │",
        "│         │",
        f"│    {suit_symbol}    │",
        "│         │",
        f"│       {display_rank:>2}│",
        "└─────────┘"
    ]


def print_cards_ascii(hand): # prints the ascii version of cards
    ascii_cards = [cardasciiconverter(card) for card in hand] #converts each card into ascii and stores it in a new variable

# AI used to help make this section better
    for line_number in range(len(ascii_cards[0])): # loops each line of the ascii
        for card in ascii_cards: # loops through each card
            print(card[line_number], end="  ") #print the line of each card side by side
        print() # moves to the next line after all cards have been printed
actions1 = ['check', 'check', 'raise', 'fold'] 
actions2 = ['call', 'call', 'call', 'raise', 'fold', 'fold'] # highr chances of calling and raising than folding


def draw_card(): # draw card function
    card = random.choice(cards) # random card from card list
    cards.remove(card) # removes it from list so no dupes
    return card

def get_hand(): # your hand is 2 cards
    return draw_card(), draw_card()

player_cards = { # each players cards - list is empty for now
    "usercards": [],
    "player_2": [],
    "player_3": [],
    "player_4": [],
    "player_5": [],
    "player_6": []
}

player_values = { # players value - everyones value is set to 0 right now
    "userval": 0,
    "player2val": 0,
    "player3val": 0,
    "player4val": 0,
    "player5val": 0,
    "player6val": 0,
}
active_players = ["user", 2, 3, 4, 5, 6] # all players still in the game

players = ['Player 2', 'Player 3', 'Player 4', 'Player 5', 'Player 6'] # all players 








# remove card after being added later 


    # pot = raiseuser
    # print(f"Pot: {pot}")

def botsturn(player_number, pot, actions): # playernumber is which bots turn it is, pot is the value of the pot currently, and actions is the list of possible actions
    player = f"player_{player_number}" # gets current bots number
    player_name = f"Player {player_number}" #displays the name
    money = player_values[f"player{player_number}val"] # how much money this bot has
    cards = player_cards[player] # this bots cards

    if fullhouse(cards):
        amountraise = random.randint(60, 100) / 100 # the strongest hand has the biggest raise
        raisenumber = amountraise * money # raises buy amountraise multiplied by their money 

    elif flush(cards): 
        amountraise = random.randint(50, 100) / 100
        raisenumber = amountraise * money

    elif straight(cards):
        amountraise = random.randint(40, 100) / 100
        raisenumber = amountraise * money

    elif threeofakindfinder(cards):
        amountraise = random.randint(30, 60) / 100
        raisenumber = amountraise * money

    elif pairfinder(cards):
        amountraise = random.randint(10, 25) / 100
        raisenumber = amountraise * money
    
    else:
        choice = random.choice(actions) #picks a random action

        if choice == "raise": # the choice is raise
            amountraise = random.randint(0, 25) / 100 # same logic as previous
            raisenumber = amountraise * money

        elif choice == "fold": 
            print(f"{player_name} folds!")
            if player_number in active_players: # if this player folds 
                active_players.remove(player_number) # remove them from the active players list
            print(f"Pot = {pot}") # print value of pot
            return pot # return value of pot
        
        elif choice == "check": 
            print(f"{player_name} check!")
            print(f"Pot = {pot}")
            return pot
        
        elif choice == "call":
            print(f"{player_name} calls!")
            print(f"Pot = {pot}")
            return pot
    
    print(f"{player_name} raised {raisenumber:.0f}") #raises and makes 0 sig figs, rounds to nearest whole number
    pot += raisenumber # adds raisenumber to pot value
    player_values[f"player{player_number}val"] -= raisenumber
    print(f"Pot = {pot:.0f}") # 0 sig figs again

    return pot






def round1():
    pot = 0
    player_cards["usercards"].extend(get_hand()) #adds each users hand to their cards
    player_cards["player_2"].extend(get_hand())
    player_cards["player_3"].extend(get_hand())
    player_cards["player_4"].extend(get_hand())
    player_cards["player_5"].extend(get_hand())
    player_cards["player_6"].extend(get_hand())

    user = input("Enter your username: ") # asks user for their username
    print(f"Welcome to Texas Hold 'Em, {user}") 

    amount = int(input("How much money should everyone start with? ")) 

    for value in player_values: # goes thru every value in player vals
        player_values[value] = amount # set each players val to starting amt
    
    print("Your cards are:") # shows cards

    print_cards_ascii(player_cards["usercards"]) # prints ascii of the users cards

    userchoice = input("What do you want to do? (Raise, Check, Fold): ").lower()

    if userchoice == "raise": # all the choices of what to do and what happens if you do them
        raiseuser = int(input(f"How much do you want to raise? (0 - {amount}): "))
        print(f"{user} raised {raiseuser}!")
        pot += raiseuser
        player_values["userval"] -= raiseuser
        print(f"Pot = {pot}")
        bot_actions = actions2

    elif userchoice == "check":
        print(f"{user} checks!")
        print(f"Pot = {pot}")
        bot_actions = actions1

    elif userchoice == "fold":
        print(f"{user} folds!")
        print("Thank you for playing!")
        sys.exit()

    else:
        print("Invalid choice")
        return
    
    for player_number in active_players: # loops all active players
        if player_number == "user":
            continue # ignore the user and continue

        pot = botsturn(player_number, pot, bot_actions) # calls botsturn function and returns updated pot to store it

    return pot

def burnasciier(hand): # the ascii art for the burned ascii - ai used to make this
    ascii_cards = []
    for card in hand:
        ascii_cards.append(cardasciiconverter(card))

    empty_card = [
        "┌─────────┐",
        "│         │",
        "│         │",
        "│         │",
        "│         │",
        "│         │",
        "└─────────┘" 
    ]

    for line_number in range(len(ascii_cards[0])): # loops each line of the ascii so that multiple cards can be lined up next to each other
        for card in ascii_cards:
            print(card[line_number], end=" ")
        print()
    
def round2(pot):
    print("Burning first card")
    burncard = draw_card()
    tablecards = [] # empty table cards list

    for i in range(3): # loops 3 times
        tablecards.append(draw_card()) # appends a drawn card to the table

    for player in player_cards: # loops each player in player cards
        for card in tablecards: # same for cards in table cards
            player_cards[player].append(card) # appends the cards on the table to playercards so that the pair and flush etc functions can work,

    print("") # makes a new empty line 

    print("Your cards:") # prints your cards in ascii
    print_cards_ascii(player_cards["usercards"][:2]) # the first 2 cards are the user cards , rest are table

    print("\nTable cards:") # new line and shows the table cards
    print_cards_ascii(tablecards) # prints the ascii of the table cards


    print(f"Pot = {pot}") # pots value
    userchoice = input("What do you want to do? (Raise, check, Fold:)").lower()

    if userchoice == "raise":
        raiseuser = int(input("How much do you want to raise?: "))

        print(f"You raised {raiseuser}!")

        pot += raiseuser

        player_values["userval"] -= raiseuser

        print(f"Pot = {pot}")

        bot_actions = actions2

    elif userchoice == "check":

        print("You check!")

        print(f"Pot = {pot}")

        bot_actions = actions1

    elif userchoice == "fold":

        print("You fold!")

        print("Thank you for playing!")

        sys.exit() # uses sys library to stop game

        bot_actions = actions1
    else:
        print("Not an option") # if they dont pick an action returns not an option
        return pot
    
    for player_number in active_players:

        if player_number == "user":
            continue

        pot = botsturn(player_number, pot, bot_actions) 
    
    return pot

def round3(pot): # essentially the same as round 2
    print("Burning first card")
    burncard = draw_card()

    turncard = draw_card()
    for player in player_cards:
        player_cards[player].append(turncard)
    print("Your cards:")
    print_cards_ascii(player_cards["usercards"][:2])

    print("\nTable cards:")
    print_cards_ascii(player_cards["usercards"][2:6]) # 2 - 6 as there is now 4 cards on the table 
    print(f"\nPot = {pot}")

    userchoice = input("What do you want to do? (Raise, check, Fold:)").lower()

    if userchoice == "raise":
        raiseuser = int(input("How much do you want to raise?: "))
        print(f"You raised {raiseuser}!")
        pot += raiseuser
        player_values["userval"] -= raiseuser
        print(f"Pot = {pot}")
        bot_actions = actions2

    elif userchoice == "check":
        print("You check!")
        print(f"Pot = {pot}")
        bot_actions = actions1
        
    elif userchoice == "fold":
        print("You fold!")
        print("Thank you for playing!")
        sys.exit()

        bot_actions = actions1
    else:
        print("Not an option")
        return pot
    for player_number in active_players:
        if player_number == "user":
            continue

        pot = botsturn(player_number, pot, bot_actions)
    
    return pot

def round4(pot): # same again
    print("Burning first card")
    burncard = draw_card()

    turncard = draw_card()
    for player in player_cards:
        player_cards[player].append(turncard)
    print("Your cards:")
    print_cards_ascii(player_cards["usercards"][:2])

    print("\nTable cards:")
    print_cards_ascii(player_cards["usercards"][2:7]) # 7 this time as there are 5 cards
    print(f"\nPot = {pot}")

    userchoice = input("What do you want to do? (Raise, check, Fold:)").lower()

    if userchoice == "raise":
        raiseuser = int(input("How much do you want to raise?: "))
        print(f"You raised {raiseuser}!")
        pot += raiseuser
        player_values["userval"] -= raiseuser
        print(f"Pot = {pot}")
        bot_actions = actions2

    elif userchoice == "check":
        print("You check!")
        print(f"Pot = {pot}")
        bot_actions = actions1

    elif userchoice == "fold":
        print("You fold!")
        print("Thank you for playing!")
        sys.exit()

        bot_actions = actions1
    else:
        print("Not an option")
        return pot
    
    for player_number in active_players:
        if player_number == "user":
            continue

        pot = botsturn(player_number, pot, bot_actions)
    return pot


def main(): # main code
    pot = round1() #each round in order
    pot = round2(pot) # I had an error where i couldnt bring a variable from a different function to a new function, i used AI to fix this. (This line and the line above)
    pot = round3(pot) 
    pot = round4(pot)
    find_winner(pot)

main() # main code called












# Just for documentation: original round 1 code before remaking
  #shuffling deck and dealing
    #card1, card2 = get_hand()
    #card3, card4 = get_hand()
    #card5, card6 = get_hand()
    #card7, card8 = get_hand()
    #card9, card10 = get_hand()
    #card11, card12 = get_hand()
    # adding cards to list
    #player_cards["usercards"].extend([card1, card2])
    #player_cards["player_2"].extend([card3, card4])
    #player_cards["player_3"].extend([card5, card6])
    #player_cards["player_4"].extend([card7, card8])
    #player_cards["player_5"].extend([card9, card10])
    #player_cards["player_6"].extend([card11, card12])
    #user = input("Enter your username: ")
    #players.append(user)

    #print(f"Welcome to Texas Hold 'Em, {user}")

    #amount = int(input("How much money should everyone start with? "))

    #for value in player_values:
     #   player_values[value] += amount
   # print(f"{user} starts!")
   # print("Your cards are:")
  #  print_cards_ascii([card1, card2])
    # pairfinder(user)
    #print(player_cards["player_2"]) # delete these later
    #print(player_cards["player_3"])
    #print(player_cards["player_4"])
    #print(player_cards["player_5"])
    #print(player_cards["player_6"])

# user turn round 1




  #  pot = 0
 #   userchoice = input("What do you want to do? (Raise, Check, Fold): ").lower()
   # if userchoice == "raise":
  #      raiseuser = int(input(f"How much do you want to raise? (0 - {amount})"))
    #    print(f"{user} raised {raiseuser}!")
    #    pot += raiseuser
    #    print(f"Pot = {pot}")

   # elif userchoice == "check":
   #     print(f"{user} checks!")
  #      print("Pot = 0")
  #  elif userchoice == "fold":
  #      print(f"{user} folds!")   
   #     print("Pot = 0")
 

# player 2 turn in round 1
    #pairfinder(players['player2'])





   # if userchoice == 'check' or userchoice == 'fold':
   #     p2choice = random.choice(actions1)
    #    if p2choice == "raise":
      #      amountraise = random.randint(40, 100) / 100
      #      money = player_values["player2val"]
      #      raisenumber = amountraise * money
      #      pot += raisenumber
#
      #      print(f"Player 2  raised {raisenumber}!")

      #      print(f"Pot = {pot}")

            # player 3 if player 1 doesnt raise and player 2 raises
       #     if p2choice == 'raise':
          #      p3choice = random.choice(actions1)
          #      if p3choice == "raise":
                 #   amountraise = random.randint(40, 100) / 100
                 #   money = player_values["player3val"]
                #    raisenumber = amountraise * (player_values["player3val"] - pot)
                #    pot += raisenumber

                #    print(f"Player 3  raised {raisenumber}!")
                 #   print(f"Pot = {pot}")
                    # player 4 if player 1 doesnt raise and player 2 raises and player 3 raises
                  #  if p3choice == 'raise':
                    #    p4choice = random.choice(actions1)
                     #   if p4choice == "raise":
                        #    amountraise = random.randint(40, 100) / 100
                        #    money = player_values["player4val"]
                       #     raisenumber = amountraise * (player_values["player4val"] - pot)
                        #    pot += raisenumber

                         #   print(f"Player 4  raised {raisenumber}!")
                         #   print(f"Pot = {pot}")
                       # elif p4choice == ("fold"):
                        #    print("Player 4 folds!")
                        #    print(f"Pot = {pot}")

            
                      #  elif p4choice == ("check"):
                        #    print("Player 4 checks!")
                         #   print(f"Pot = {pot}")


              #  elif p3choice == ("fold"):
                #    print("Player 3 folds!")
                #    print(f"Pot = {pot}")

            
             #   elif p3choice == ("check"):
              #      print("Player 3 checks!")
              #      print(f"Pot = {pot}")


      #  elif p2choice == ("fold"):
      #      print("Player 2 folds!")
            
     #   elif p2choice == ("check"):
     #       print("Player 2 checks!")
    # code for if the user has raised





 #   if userchoice == 'raise':
     #   choice = random.choice(actions2)
      #  if choice == "raise":
        #    amountraise = random.randint(0, 25) / 100
       #     money = player_values["player2val"]
        #    raisenumber = amountraise * (money - pot) + pot

          #  print(f"Player 2  raised {raisenumber}!")
        #    pot += raisenumber
        #    print(f"Pot = {pot}")

     #   elif choice == ("fold"):
     #       print("Player 2 folds!")
       #     print(f"Pot = {pot}")

    #    elif choice == ("call"):                  
     #       print("Player 2 calls!")
     #       pot = pot * 2
    #       print(f"Pot = {pot}")










