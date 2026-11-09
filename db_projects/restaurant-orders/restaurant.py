#!/usr/bin/env python3
import datetime
from cs50 import SQL

db = SQL("sqlite:///restaurant.db")

try:
    # 1. Ensure a Restaurant exists
    restaurants = db.execute("SELECT RestaurantID FROM Restaurant LIMIT 1")
    if not restaurants:
        print("[Database Sync] No restaurant found. Automatically creating default restaurant...")
        db.execute(
            "INSERT INTO Restaurant (Restaurant_Name, Address, Phone_Number) VALUES (?, ?, ?)",
            "Authentic Italian Pizza", "246 Rainbow St", "123-456"
        )
        restaurants = db.execute("SELECT RestaurantID FROM Restaurant LIMIT 1")

    # 2. Ensure a Customer exists
    RESTAURANT_ID = restaurants[0]["RestaurantID"]

except Exception as start_error:
    print(f"[Database Error] Could not auto-initalize restaurant: {start_error}")
    RESTAURANT_ID = 1


    ##This is the player account registration so it adds, the players own names

print("\n---WELCOME TO THE RESTAURANT ACCOUNT REGISTRATION!---")

while True:
    party_input = input("Welcome! how many people are dining today? ")
    if party_input.isdigit() and int(party_input) > 0:
        party_size = int(party_input)
        break
    print("Please enter a valid number of people.")

guests = []


for p in range(party_size):
    print(f"\n--- Registering Guest {p + 1} ---")
    while True:
        first_name = input("Enter your first name: ").strip().capitalize()
        last_name = input("Enter your last name: ").strip().capitalize()
        if first_name and last_name:
            break
        print("Error: Names cannot be left blank, retry.")

    phone_number = input("Enter phone number (or press enter to skip): ").strip()
    if not phone_number:
        phone_number = "N/A"

    try:
        existing_customer = db.execute(
            "SELECT CustomerID FROM Customer WHERE First_Name = ? AND Last_Name = ?",
            first_name, last_name
        )
        if len(existing_customer) > 0:
            cust_id = existing_customer[0]["CustomerID"]
            print(f"Welcome Back, {first_name}!")
        else:
            cust_id = db.execute(
                "INSERT INTO Customer(First_Name, Last_Name, Phone_Number) VALUES(?, ?, ?)",
                first_name, last_name, phone_number
            )
            print(f"Welcome {first_name}! Your account was successfully created congratulations!")
    except Exception as e:
        print(f"Database error: {e}")
        cust_id = 1

    guests.append({
        "id": cust_id,
        "first_name": first_name,
        "last_name": last_name,
        "balance": 0,
        "cart": []
    })


#
print("WELCOME TO THE RESTAURANT CUSTOMER!")

# questions for the user to answer

def ask_question(question, correct_answer):
   print("\n" + question)
   user_answer =  input("Your answer: ")


   if user_answer.strip().replace(".", "").lower() == correct_answer.lower():
       print("Correct! You have earned 10 dollars Congratulations!")
       return 10
   else:
       print(f"Wrong! The Correct answer was!: {correct_answer}.")
       return 0



questions = [
   "What day comes after Monday?",
   "What is five multiplied by five?",
   "What do you call a cow without legs?",
   "What is Data?",
   "How many sides does a triangle. have?"
]




answers = [
   "Tuesday",
   "twenty five",
   "Ground Beef",
   "Raw unproccessed information",
   "3"
]


print("\n--- WELCOME TO THE QUIZ! YOU CAN EARN YOUR CASH HERE! ---")
for guest in guests:
    print(f"\n {guest['first_name']}, it is your turn to earn money!")
    for i in range(5):
        print(f"\nQuestion {i + 1}:")
        cash_earned  = ask_question(questions[i], answers[i])
        guest["balance"] += cash_earned
        print(f"{guest['first_name']}'s Current Balance: ${guest['balance']:.2f}")
    print(f"Quiz is over for {guest['first_name']} Total Earned: ${guest['balance']:.2f}\n")



# Makes sure that prices are presented from ascending order in the menu.

menu_rows = db.execute("""
    SELECT Menu.MenuID, Menu.Menu_Item, Menu.price, Food.Food_Description
    FROM Menu
    INNER JOIN Food ON Menu.FoodID = Food.FoodID
    ORDER BY Menu.price ASC
""")

## THIS MAKES IT INTO A MULTI ITEM THING
cart = []

# This makes sure if the user inserts a menu id number that is in the menu.

def get_valid_menu_choice(menu_rows):
 "Validates that the user enters a number that currently exists on the menu."
 while True:
     choice = input("Enter the ID number of the food you want to eat (c for checkout or q for quit): ")

     if choice.lower() == "q":
         return "q"

     if choice.lower() =="c":
         return "c"

     if not choice.isdigit():
         print("ERROR: Please enter a valid number.")
         continue

     choice = int(choice)

     valid_ids = [row["MenuID"] for row in menu_rows]

     if choice not in valid_ids:
         print("Error: That ID is not on the menu try again please!")
         continue

     return choice

 # receipt given to the user

def print_receipt(customer_id, cart):
    """Displays a complete invoice summary layout for the customer."""
    # Simple Year 11 historical data tracking block
    try:
        stats = db.execute("""
            SELECT SUM(Menu.price) AS lifetime_total
            FROM Order_Items
            INNER JOIN Menu ON Order_Items.MenuID = Menu.MenuID
            INNER JOIN Orders ON Order_Items.OrderID = Orders.OrderID
            WHERE Orders.CustomerID = ?
        """, customer_id)

        if stats and stats[0]["lifetime_total"]:
            print(f"Your historical lifetime spending at this restaurant is approximately: ${stats[0]['lifetime_total']:.2f}")
    except Exception as e:
        print(f"Could not fetch historical stats: {e}")

    query = "SELECT First_Name, Last_Name, Phone_Number FROM Customer WHERE CustomerID = ?"

    try:
        result = db.execute(query, customer_id)

        if result:
            first_name = result[0]['First_Name']
            last_name = result[0]['Last_Name']
            phone = result[0]['Phone_Number']

            # Simple linear loop for calculating totals matching Year 11 structures
            total_bill = 0
            for item in cart:
                total_bill += item["price"]

            time_rules = {
                "Margherita Pizza": 10,
                "Spaghetti Carabona": 20,
                "Tiramisu": 12,
                "Garlic Bread": 5,
                "Fettucina Alfredo": 22
            }

            total_prep_time = 0
            for item in cart:
                item_name = item["name"]
                if item_name in time_rules:
                    total_prep_time += time_rules[item_name]

            print(f"\n--- YOUR RECEIPT ---")
            print(f"Customer: {first_name} {last_name}")
            print(f"Phone Number: {phone}")
            print(f"Total items ordered today: {len(cart)}")
            print(f"Amount Charged: ${total_bill:.2f}")
            print(f"Estimated waiting time: {total_prep_time} minutes")
            print(f"--------------------\n")
    except Exception as e:
        print(f"Error generating receipt: {e}")

for guest in guests:
    print(f"\n======================================================")
    print(f"WELCOME! THIS IS THE MENU SELECTION FOR: {guest['first_name'].upper()}")
    print(f"\n======================================================")
    print("Feel free to choose from our options! (or type q to exit!)")

    while True:
        for row in menu_rows:
            item_id = row["MenuID"]
            name = row["Menu_Item"]
            item_price = row["price"]
            desc = row["Food_Description"]
            print(f"{item_id}. {name} - ${item_price:.2f} ({desc})")

        print("")
        choice = get_valid_menu_choice(menu_rows)

        if choice == "q":
            print(f"\nOrder Cancelled for  {guest['first_name']}.")
            guest["cart"] = []
            break
        if choice == "c":
            if len(guest["cart"]) > 0:
                print(f"\n--- Proceeding to Checkout for {guest['first_name']} ---")
                break# This now safely exits the menu loop to begin checkout processing
            else:
                print(f"\nError: Your cart is empty! Add food before checking out.")
                continue

        # Simple standard loop matching SCSA Year 11 linear search matching
        for row in menu_rows:
            if row["MenuID"] == choice:
                bought_id = row["MenuID"]
                bought_name = row["Menu_Item"]
                bought_price = row["price"]

                guest["cart"].append({"id": bought_id, "name": bought_name, "price": bought_price})
                print(f"\nSuccessfully Added {bought_name} to {guest['first_name']}'s cart!")

                # Calculating total using a standard iteration loop
                running_total = 0
                for item in guest["cart"]:
                    running_total += item["price"]
                print(f"Current Cart Total: ${running_total:.2f}")


            # OUTSIDE THE WHILE LOOP (Shifted left to run only once at checkout)
    if len(guest["cart"]) > 0:
        final_total = 0
        for item in guest["cart"]:
            final_total += item["price"]

        print(f"\n{guest['first_name']}'s final bill comes to: ${final_total:.2f}")
        print(f"{guest['first_name']}'s current wallet balance is: ${guest['balance']:.2f}")

        if guest["balance"] >= final_total:
            guest["balance"] -= final_total
            print(f"\nPurchase Successful for {guest['first_name']}!")

                    # Indented correctly to run ONLY when the balance check passes
            time_now = datetime.datetime.now().strftime("%H:%M:%S")
            date_now = datetime.datetime.now().strftime("%Y-%m-%d")

            try:
                new_order_id = db.execute(
                    "INSERT INTO Orders (Order_Time, Order_Date, RestaurantID, CustomerID) VALUES (?, ?, ?, ?)",
                    time_now, date_now, RESTAURANT_ID, guest["id"]
                )

                for item in guest["cart"]:
                    db.execute(
                        "INSERT OR IGNORE INTO Order_Items (OrderID, MenuID, Quantity) VALUES (?, ?, ?)",
                        new_order_id, item["id"], 1
                    )


                print(f"Database tracking synced for {guest['first_name']}!")
            except Exception as database_error:
                    print(f"\n[Database Error] Could not save order: {database_error}")
        else:
                print(f"\nTransaction Declined for {guest['first_name']}. Total is ${final_total:.2f} but you only have ${guest['balance']:.2f}.")
                guest["cart"] = []

    else:
        print(f"\nNo items ordered by {guest['first_name']} Today.")


print(f"\n=================================================")
print(f"      FINAL RESTAURANT INVOICES ARE COMPLETE!      ")
print(f"\n=================================================")

for current_guest in guests:
    print_receipt(current_guest["id"], current_guest["cart"])

# ADD A CANCEL ORDER OPTION
# Add an option that multiple people can join or not (for example if you have or friends or family)
# Fix the phone number registration
#Add combos, as per original version of the code


