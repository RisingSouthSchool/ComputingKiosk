#!/usr/bin/env python3
import sqlite3
connection = sqlite3.connect("steamdatabase.db")
cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys = ON")


cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    UserID INTEGER PRIMARY KEY,
    UserName TEXT,
    DateOfBirth TEXT,
    CreditCardNumber TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Genre (
    GenreID INTEGER PRIMARY KEY,
    GenreName TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Games (
    GameID INTEGER PRIMARY KEY,
    GameName TEXT,
    GenreID INTEGER,
    GamePrice TEXT,

    FOREIGN KEY (GenreID) REFERENCES Genre(GenreID)
)
    """)

cursor.execute("""
CREATE TABLE IF NOT EXISTS SteamLibrary (
    UserID INTEGER,
    GameID INTEGER,
    HoursPlayed TEXT,

    PRIMARY KEY (UserID, GameID),

    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (GameID) REFERENCES Games(GameID)
)
""")

#
#
#
#

def view_games(): #views and prints all information in the games entity
    query = """
    SELECT * FROM Games;
    """
    print("GameID, GameName, GenreID, Cost:")
    cursor.execute(query)

    for row in cursor.fetchall():
        print(row)

def view_users(): #views and prints all information in the users entity
    query = """
    SELECT * FROM Users;
    """

    print("UserID, UserName, DateOfBirth, CreditCardNumber:")
    cursor.execute(query)

    for row in cursor.fetchall():
        print(row)


def view_genres(): #views and prints all information in the genres entity
    query = """
    SELECT * FROM Genre;
    """

    print("GenreID, GenreName:")
    cursor.execute(query)

    for row in cursor.fetchall():
        print(row)


def view_steamlibrary(): #views and prints all information in the steamlibrary entity
    query = """
    SELECT * FROM SteamLibrary;
    """

    print("UserID, GameID, HoursPlayed:")
    cursor.execute(query)

    for row in cursor.fetchall():
        print(row)

def count_owned_games(): #counts the amount of games owned by each person in the database and displays that number next to their names
    aggregate_query = """
    SELECT Users.UserName, COUNT(*) AS TotalGames
    FROM SteamLibrary
    INNER JOIN Users ON SteamLibrary.UserID = Users.UserID
    GROUP BY Users.UserName
    ORDER BY TotalGames DESC;
    """

    print("UserName, Number of Games Owned:")
    cursor.execute(aggregate_query)

    for row in cursor.fetchall():
        print(row)
        
def update_queries():
    query_update_1 = """
    UPDATE Users
    SET UserName = ?
    WHERE UserID = ?;
    """
    query_update_2 = """
    UPDATE Users
    SET CreditCardNumber = ?
    WHERE UserID = ?;
    """
    query_update_3 = """
    UPDATE Games
    SET GamePrice = ?
    WHERE GameID = ?;
    """
    query_update_4 = """
    UPDATE SteamLibrary
    SET HoursPlayed = ?
    WHERE UserID = ? AND GameID = ?;
    """
    while True:
        print("""
------------------------------------------------
Please Choose an Action:
1. Update User Info (UserName, CreditCardNumber)
2. Update Game Info (Price)
3. Update Steam Library Info (Hours Played)
4. Back
------------------------------------------------
""")
        update_choice = input("Input Number:")

        if update_choice == "1":
            while True:
                print("""
--------------------------
Please Choose an Action:
1. Update UserName
2. Update CreditCardNumber
3. Back
--------------------------
""")
                update_action = input("Input Number:")


                if update_action == "1":
                    print()
                    view_users()
                    print()

                    try:
                        select_id: int = input("Please select the ID of the user whose information you wish to update:")
                        new_username: str = input("Please enter new UserName:")
                        updated_user = (new_username, select_id)

                        confirm_update(query_update_1, updated_user)
                        break
                    except sqlite3.IntegrityError:
                            print()
                            print("Update Failed")

                elif update_action == "2":
                    print()
                    view_users()
                    print()

                    try:
                        select_id: int = input("Please select the ID of the user whose information you wish to update:")
                        new_credit_card_number: str = input("Please enter new CreditCardNumber:")
                        while True:
                            if new_credit_card_number[0] != "4" or len(new_credit_card_number) != 19:
                                print("-------------------------------------")
                                print("Not a valid credit card number")
                                print("-------------------------------------")
                                print("Example of valid credit card number:")
                                print("4000 0000 0000 0000")
                                print()
                                new_credit_card_number: str = input("Please enter new CreditCardNumber:")
                            else:
                                break

                        updated_user = (new_credit_card_number, select_id)

                        confirm_update(query_update_2, updated_user)
                        break
                    except sqlite3.IntegrityError:
                        print()
                        print("Update Failed")

                elif update_action == "3":
                    break

                else:
                    print()
                    print("Please try again")


        elif update_choice == "2":
            print()
            view_games()
            print()

            try:
                select_id: int = input("Please select the ID of the Game you would like to update:")
                new_price: str = input("Please enter new GamePrice:")
                while True:
                    if new_price[0] != "A" or new_price[1] != "$":
                        print("--------------------------------------------------------------------------")
                        print("Must specify Australian currency by entering A$ at the start of GamePrice")
                        print("--------------------------------------------------------------------------")
                        print("Example of a valid price:")
                        print("A$40.98")
                        print()
                        new_price: str = input("Please enter new GamePrice:")
                    else:
                        break
                updated_price = (new_price, select_id)

                confirm_update(query_update_3, updated_price)
                break
            except sqlite3.IntegrityError:
                print()
                print("Update Failed")

        elif update_choice == "3":
            print()
            view_steamlibrary()
            print()

            try:
                select_userid: int = input("Enter the ID of the user whose information you want to update:")
                select_gameid: int = input("Enter the ID of the game you would like to update hours played for:")
                edited_hours: str = input("Enter new HoursPlayed:")

                library_update = (edited_hours, select_userid, select_gameid)

                confirm_update(query_update_4, library_update)
                break
            except sqlite3.IntegrityError:
                print()
                print("Update Failed")

        elif update_choice == "4":
            break

        else:
            print()
            print("Please try again")

def insert_queries():

    query_insert_1 = """
    INSERT INTO Games(GameID, GameName, GenreID, GamePrice)
    VALUES (?, ?, ?, ?);
    """
    query_insert_2 = """
    INSERT INTO Genre(GenreID, GenreName)
    VALUES (?, ?);
    """
    query_insert_3 = """
    INSERT INTO Users(UserID, UserName, DateOfBirth, CreditCardNumber)
    VALUES (?, ?, ?, ?);
    """
    query_insert_4 = """
    INSERT INTO SteamLibrary(UserID, GameID, HoursPlayed)
    VALUES (?, ?, ?);
    """

    while True:
        print("""
-----------------------------
Please Choose an Action:
1. Insert Into Games
2. Insert Into Genres
3. Insert Into Users
4. Insert Into Steam Library
5. Back
-----------------------------
""")
        insert_choice = input("Input Number:")

        if insert_choice == "1":
            print()
            view_games()
            print()
            value_1: int = input("Enter GameID:")
            value_2: str = input("Enter GameName:")
            print()
            view_genres()
            print()
            value_3: int = input("Enter GenreID:")
            value_4: str = input("Enter GamePrice:")
            while True:
                if value_4[0] != "A" or value_4[1] != "$":
                    print("--------------------------------------------------------------------------")
                    print("Must specify Australian currency by entering A$ at the start of GamePrice")
                    print("--------------------------------------------------------------------------")
                    print("Example of a valid price:")
                    print("A$40.98")
                    print()
                    value_4: str = input("Please enter GamePrice:")
                else:
                    break

            value_list = (value_1, value_2, value_3, value_4)

            confirm_insert(query_insert_1, value_list)
            break

        elif insert_choice == "2":
            print()
            view_genres()
            print()
            value_1: int = input("Enter GenreID:")
            value_2: str = input("Enter GenreName:")

            value_list = (value_1, value_2)

            confirm_insert(query_insert_2, value_list)
            break

        elif insert_choice == "3":
            print()
            view_users()
            print()
            value_1: int = input("Enter UserID:")
            value_2: str = input("Enter UserName:")
            value_3: str = input("Enter DateOfBirth:")
            value_4: str = input("Enter CreditCardNumber:")
            while True:
                if value_4[0] != "4" or len(value_4) != 19:
                    print("-------------------------------------")
                    print("Not a valid credit card number")
                    print("-------------------------------------")
                    print("Example of valid credit card number:")
                    print("4000 0000 0000 0000")
                    print()
                    value_4: str = input("Enter CreditCardNumber:")
                else:
                    break
            value_list = (value_1, value_2, value_3, value_4)

            confirm_insert(query_insert_3, value_list)
            break

        elif insert_choice == "4":
            print()
            view_steamlibrary()
            print()
            view_users()
            print()
            value_1: int = input("Enter UserID:")
            print()
            view_games()
            print()
            value_2: int = input("Enter GameID:")
            value_3: str = "0 Hours"

            value_list = (value_1, value_2, value_3)

            confirm_insert(query_insert_4, value_list)
            break

        elif insert_choice == "5":
            break

        else:
            print()
            print("Please try again")

def delete_queries():
    query_delete_1 = """
    DELETE FROM Games
    WHERE GameID = ?;
    """
    query_delete_2 = """
    DELETE FROM Users
    WHERE UserID = ?;
    """
    query_delete_3 = """
    DELETE FROM SteamLibrary
    WHERE UserID = ? AND GameID = ?;
    """
    while True:
        print("""
    ------------------------------
    Please Choose an Action:
    1. Delete From Games
    2. Delete From Users
    3. Delete From Steam Libraries
    4. Back
    ------------------------------
    """)
        delete_choice = input("Input Number:")

        if delete_choice == "1":
            print()
            view_games()
            print()
            try:
                selected_id: int = input("Please select the ID of the game you want to delete:")

                confirm_deletion(query_delete_1, selected_id)
                break
            except sqlite3.IntegrityError:
                print()
                print("Please delete data associated with selected game from Steam libraries")

        elif delete_choice == "2":
            print()
            view_users()
            print()
            try:
                selected_id: int = input("Please select the ID of the user you want to delete:")

                confirm_deletion(query_delete_2, selected_id)
                break
            except sqlite3.IntegrityError:
                print()
                print("Please delete data associated with selected user from Steam libraries")

        elif delete_choice == "3":
            print()
            view_steamlibrary()
            print()
            try:
                selected_userid: int = input("Please select the ID of the user whose information you wish to delete:")
                selected_gameid: int = input("Please select the ID of the game you would like to delete from said user's Steam Library:")
                selected_ids = (selected_userid, selected_gameid)

                confirm_deletion(query_delete_3, selected_ids)
                break
            except sqlite3.IntegrityError:
                print()
                print("Data does not exist")

        elif delete_choice == "4":
            break

        else:
            print()
            print("Please try again")

def more_actions(): #contains insert, delete and update functions and acts as a secondary main function
    query_delete_1 = """
    DELETE FROM Games
    WHERE GameID = ?;
    """
    query_delete_2 = """
    DELETE FROM Users
    WHERE UserID = ?;
    """
    query_delete_3 = """
    DELETE FROM SteamLibrary
    WHERE UserID = ? AND GameID = ?;
    """
    while True:
        print("""
------------------------
Please Choose an Action:
1. Insert Information
2. Delete Information
3. Update Information
4. Back
------------------------
""")
        user_input = input("Input Number: ")

        if user_input == "1":
            insert_queries()

        elif user_input == "2":
            delete_queries()

        elif user_input == "3":
            update_queries()

        elif user_input == "4":
                    break

        else:
            print()
            print("Please try again")

def confirm_update(query_update, updated_user): #asks the user for confirmation, allowing them to reconsider updating information
    confirmation = input("Confirm Insert Y/N:").upper()

    while True:
        if confirmation == "Y":
            cursor.execute(query_update, updated_user)
            connection.commit()
            print()
            print("Update Confirmed")
            break
        elif confirmation == "N":
            print()
            print("Update Cancelled")
            break
        else:
            print()
            print("Invalid Input")
            confirmation = input("Confirm Insert Y/N:").upper()

def confirm_insert(query_insert, value_list): #asks the user for confirmation, allowing them to reconsider inserting information
    confirmation = input("Confirm Insert Y/N:").upper()

    while True:
        if confirmation == "Y":
            cursor.execute(query_insert, value_list)
            connection.commit()
            print()
            print("Insert Confirmed")
            break
        elif confirmation == "N":
            print()
            print("Insert Cancelled")
            break
        else:
            print()
            print("Invalid Input")
            confirmation = input("Confirm Insert Y/N:").upper()

def confirm_deletion(query_delete, selected_id): #asks the user for confirmation, allowing them to reconsider deleting information
    confirmation = input("Confirm Deletion Y/N:").upper()

    while True:
        if confirmation == "Y":
            cursor.execute(query_delete, selected_id)
            connection.commit()
            print()
            print("Deletion Confirmed")
            break
        elif confirmation == "N":
            print()
            print("Deletion Cancelled")
            break
        else:
            print()
            print("Invalid Input")
            confirmation = input("Confirm Deletion Y/N:").upper()

def user_authentication(): #requires the user to input a login to access the database
    while True:
        print()
        user_authentication_1: str = input("Please Enter Email:")
        print()
        user_authentication_2: str = input("Please Enter Password:")

        if user_authentication_1 != "admin@example.com" or user_authentication_2 != "1987":
            print()
            print("Incorrect Login Details")
        else:
            break

def main(): #main function of the database, calls all previous functions and runs the database
    user_authentication()

    print()
    print("Welcome to the Steam Database admin account.")

    while True:
        print("""
-----------------------------
Please Choose an Action:
1. View Games
2. View Users
3. View Genres
4. View Steam Libraries
5. More Actions
6. View Number of Games Owned
7. Exit
-----------------------------
""")
        # user_input = integer_checker()
        user_input = input("Input Number:")


        if user_input == "1":
            print()
            view_games()
            print()
        elif user_input == "2":
            print()
            view_users()
        elif user_input == "3":
            print()
            view_genres()
        elif user_input == "4":
            print()
            view_steamlibrary()
        elif user_input == "5":
            more_actions()
        elif user_input == "6":
            count_owned_games()
        elif user_input == "7":
            print()
            print("Goodbye")
            print()
            connection.close()
            break
        else:
            print()
            print("Please try again")

main()
