import time
import os
from intermission import intermission
# AI Assistance: GitHub ChatGPT
# Prompt used: "How do I do I make it so that when a tie happens they can choose to either vote or play again?"
# Date: April 2026
# Modifications: Added the options on what happens if it is a tie and how to move on with that.  

def voting(player_names, roles):
    
    eliminated = ""
    votes_for_players = {}
    max_votes = -1
    top_players = []
    
    os.system('cls' if os.name == 'nt' else 'clear')

    while len(player_names) > 2:
        eliminated = ""
        votes_for_players = {}
        max_votes = -1
        top_players = []
        #variables resetted every round of voting
        

        voting = input("Do you want to start voting? (type y to confirm) ")
        while voting != "y":
            print("Invalid Input")
            voting = input("Do you want to start voting? (type y to confirm) ")
        else:
            print("Excellent")
            for player in player_names:
                voted_player = input(f"Who do you vote for {player}: ").title()
                while voted_player not in player_names or player == voted_player:
                    print("Invalid Input")
                    voted_player = input(f"Who do you vote for {player}: ").title()
#for loop, loops through players and inputs their vote for the player they want to choose
                else:
                    if voted_player not in votes_for_players:
                        votes_for_players[voted_player] = 0
                    
                    votes_for_players[voted_player] += 1
                    print(votes_for_players)
    #adds the players vote to the tally of votes for the player voted
        for player in votes_for_players:

            if votes_for_players[player] > max_votes:
                max_votes = votes_for_players[player]
                top_players = [player]
        #this occurs if the voting ends with one person who has more voted than everyone else
        #adds player to the list of top_players (only one player)
            elif votes_for_players[player] == max_votes:
                top_players.append(player)
    #this occurs if the voting happens in a tie adds the player to the list of players with the same amount of votes 
        if len(top_players) == 1:
            print()
            print(f"{top_players[0]} is eliminated")
            eliminated = top_players[0]
            player_names.remove(eliminated)

            imposters_alive = sum(1 for player in player_names if roles[player] == "imposter")
            #counts the amount of imposters alive
            civilians_alive = len(player_names) - imposters_alive
            #counts the civlians alive
            
            if imposters_alive == 0:
                print(f"Civilians Win! There were {imposters_alive} imposters, and {civilians_alive} civlians!")
                print(roles)
                break
            #civilians win when there are no imposters alive meaning civilains successfully eliminated all imposters
                
            if imposters_alive >= civilians_alive:
                print(f"Imposters Win! There were {imposters_alive} imposters, and {civilians_alive} civlians!")
                print(roles)       
                break
            #imposters win when the number of civilians are less than the number of imposters alive
            print("Remaining Players:", player_names)
            print()
            print(eliminated, "was...", roles[eliminated])
            if roles[eliminated] == "civilian":
                print("Remaining Imposters:", imposters_alive)
                print()
                intermission()
                time.sleep(1)
                continue
            if roles[eliminated] == "imposter":
                if imposters_alive > 0:
                    print("Remaining Imposters:", imposters_alive)
                    print()
                    intermission()
                    time.sleep(1)
                    continue
                #shows the players important information regarding the voting and the game
                #shows if the eliminated person was imposter or civilian and displays the imposter alive
            
        else:
            print("We have a tie!")
            print(top_players, "have tied with", max_votes, "votes each!")
            tiebreaker = input("You can either vote again or play another round (press v/p)")
            #inputs user for the option to vote again or play another round when there is a tie
        
            while tiebreaker != "v" and tiebreaker != "p":
                print("Invalid Input")
                tiebreaker = input("You can either vote again or play another round (press v/p)")
            if tiebreaker == "v":
                eliminated = ""
                votes_for_players = {}
                max_votes = -1
                top_players = []
                continue
    #if the option to vote again the loop would restart and the variables would be resetted
            if tiebreaker == "p":
                intermission()
                time.sleep(1)
                continue
    #if the option to play another round was picked the intermission would happen and then the loop would restart
    
    
    print("Thank you for playing!")