

import random
from assignroles import assign_roles
from voting import voting
from intermission import intermission
import os
import time

player_names = []

while True:
    try:
        number_of_players = int(input("How many players are playing? "))
        print()
        if number_of_players < 3 or number_of_players > 30:
            print("Number of players must be between 3-30")
            print()
            continue
        break


    except ValueError:
        print("Try again with a number please")
#while loop showing how many players are playing and try exception handling

for i in range(number_of_players):
                name = input(f"Player {i+1}, what is your name? ").title()
                while name in player_names:
                    print()
                    print(name, "cannot be used twice")
                    print()
                    name = input(f"Player {i+1}, what is your name? ").title()
                print("")
                print("Player", i+1, "=", name)
                print("")
                player_names.append(name)
        #loops through players and inputs a name and assigns the users chosen name as their player name
while True:
        try:
            number_of_imposters = int(input("How many imposters do you want for your game? "))
            if number_of_imposters >= number_of_players - number_of_imposters:
                print("Number of imposters must be less than number of civilians or players")
                print()
                continue
            break
        except ValueError:
                print("Try again with a number please")
#while loop to figure out how many imposters there will be playing
#based on the number of players, the loop will confirm the minimum and maximum number of imposters are allowed 

print("Number of imposters set to as", number_of_imposters)

roles = assign_roles(player_names, number_of_imposters)

print("Everyone sit in a circle")
print(random.choice(player_names), "starts first")
#allows for the game to begin by allowing a random player to start first
time.sleep(5)

intermission()

voting(player_names, roles)
