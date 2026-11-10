# Apex Custom Garage

money = 1000
speed = 100
power = 100

turboBought = False
tiresBought = False

gameOver = False


print("=== Welcome to Apex Custom Garage ===")
print("Upgrade your car and test it on the dyno!")


while gameOver == False:

    print("\n1. Shop")
    print("2. Dyno Test")
    print("3. Exit")

    choice = input("Choose an option: ")

    # SHOP
    if choice == "1":

        print("\n--- SHOP ---")
        print("Turbo ($500)")
        print("Tires ($300)")

        option = input("What do you want to buy? ").lower()

        # TURBO
        if option == "turbo":

            if money >= 500 and turboBought == False:
                money = money - 500
                speed = speed + 50
                power = power + 50
                turboBought = True
                print("Turbo installed!")
            else:
                print("Can't buy turbo")

        # TIRES
        elif option == "tires":

            if money >= 300 and tiresBought == False:
                money = money - 300
                speed = speed + 30
                tiresBought = True
                print("Tires installed!")
            else:
                print("Can't buy tires")

        else:
            print("Invalid part")

    # DYNO
    elif choice == "2":

        total = speed + power

        print("\n--- DYNO RESULTS ---")
        print("Speed:", speed)
        print("Power:", power)
        print("Total Score:", total)

    # EXIT
    elif choice == "3":
        gameOver = True
        print("Thanks for playing!")

    else:
        print("Invalid input")
