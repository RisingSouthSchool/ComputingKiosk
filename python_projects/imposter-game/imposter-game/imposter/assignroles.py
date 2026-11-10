import random
import os
from topics import topics

# AI Assistance: ChatGPT
# Prompt used: "How to differentiate the categories from the words"
# Date: April 2026
# Modifications: Added the "keys" and taught me about how to use keys in a dictionary

def assign_roles(player_names, number_of_imposters):

    roles = {}
    imposters = random.sample(player_names, number_of_imposters)
    #allocates the imposters randomly
    categories = list(topics.keys())
    #identifies the topics in the code 
    chosen_topic = random.choice(categories)
    #chooses the topic randomly
    word_list  = topics[chosen_topic]
    #identifies the words based on the chosen topic
    chosen_word = random.choice(word_list)
    #chooses the word randomly
    
    for player in player_names:
        if player in imposters:
            roles[player] = "imposter"
        else:
            roles[player] = "civilian"
    #allocates the players as their roles either imposter or civilian
    roleconfirm = input("Ready to see roles for players? (type y to confirm) ")
    print()
    while roleconfirm != "y":
        print()
        print("Invalid Input")
        roleconfirm = input("Ready to see roles for players? (type y to confirm) ")
        #prints invalid input until valid input is typed
    else:
        for i in range(len(player_names)):
            name = player_names[i]
            print()
            rolesreveal = input(f"Hello {name} Ready to reveal role? (type y to confirm) ")
            while rolesreveal != "y":
                print()
                print("Invalid Input")
                rolesreveal = input(f"Hello {name} Ready to reveal role? (type y to confirm) ")
            print()
            print("Your role is", roles[name])
            if roles[name] == "imposter":
                print("Category/Hint is", chosen_topic)
                print("Teammates are", imposters, "Good luck!")
                print()
            if roles[name] == "civilian":
                print("Word is", chosen_word)
                print("Work together as civilians to eliminate the imposters!")
                print()
    #ensures confirmation of player and then displays their role and word and extra information to play the game

            if i != len(player_names) - 1:
                check = input("Ready to move on to the next person? (type y to confirm) ")
                while check != "y":
                    print()
                    print("Invalid Input")
                    check = input("Ready to move on to the next person? (type y to confirm) ")
                
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Screen has been cleared!")
                print()

            else:
                input("Press anything to finish: ")

                os.system('cls' if os.name == 'nt' else 'clear')
                print("Screen has been cleared!")
                print()
    #prevents cheaters to ensure that the person's screen has been cleared for the other person to check their role
    return roles