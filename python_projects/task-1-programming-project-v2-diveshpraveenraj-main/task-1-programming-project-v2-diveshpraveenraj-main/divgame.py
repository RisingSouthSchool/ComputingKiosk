# Game name - Apex Custom Game - BY DIVESH

import random 

def show_menu(money):
    print("\nMoney:", money)
    print("\n1. Shop")
    print("2. Dyno Test")
    print("3. Race") 
    print("4. Exit")

def shop(money,speed, power, turboBrought, tiresBrought):

    print("\nSHOP")
    print("Turbo ($500)")
    print("Tires ($300)")

    option = input("What do you want to buy? ").lower()

    if option == "turbo":

        if turboBrought:
            print("You already bought turbo")

        elif money < 500:
            print("Not enough money for turbo")

        else:
            money -= 500
            speed += 50
            power += 50
            turboBrought = True
            print("Turbo installed!")

    elif option == "tires":

        if tiresBrought:
            print("You already bought tires")

        elif money < 300:
            print("Not enought monet for tires")

        else:
            money -= 300
            speed += 30
            tiresBrought = True
            print("Tires installed!")

    else:
        print("Invalid input")

    return money, speed, power, turboBrought, tiresBrought

def dyno(speed, power):
    
    total = speed + power

    print("\n--- DYNO RESULTS ---")
    print("Speed:", speed)
    print("Power:", power)
    print("Total Score", total)
    

def race(speed,power, money):

    playerScore = speed + power
    opponentScore = random.randint(150,300)

    print("\n--- RACE ---")
    print("Your score:", playerScore)
    print("Opponent score:", opponentScore)

    if playerScore > opponentScore:
        print("You win the race!")
        money += 200
        print("You earned $200!")
    else:
        print("You lost the race")

    print("Money now:", money)

    return money



#MAIN

money = 1000
speed = 100
power = 100

turboBrought = False 
tiresBrought = False

gameOver = False

print("Welcome to Apex Custom Garage")
print("Upgrade your car and test it on the dyno!")

while not gameOver:

    show_menu(money)
    choice = input("Choose an option: ")

    if choice == "1":
        money, speed, power, turboBrought, tiresBrought = shop(money, speed, power, turboBrought, tiresBrought)

    elif choice == "2":
        dyno(speed, power)
    
    elif choice == "3":
        money = race(speed, power, money)

    elif choice == "4":
        gameOver = True
        print("Thanks for playing!")

    else:
        print("Invalid input")

