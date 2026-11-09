#!/usr/bin/env python3
import sqlite3
from database_setup import create_tables
from pathlib import Path

create_tables() #creates the database using by executing my sql code in a different file within my folder

database_path = Path(__file__).with_name("pedalboard.db")

connection = sqlite3.connect(database_path, timeout=10) #the timeout and database path is due to errors which created multiple connections to the same database, breaking the code
cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

def check_input_integer(prompt): #validates user input whenever an integer is inputted
    while True:
        try:
            choice = int(input(prompt))

            if choice <= 0:
                print("Number must be greater than 0. ")

            else:
                return choice

        except ValueError:
            print("Please Enter an integer")


def view_count(): #count the total pedals used in each song stored in the database

    query = """
    SELECT Song.SongTitle, COUNT(Song_Pedal_Setting.PedalID)
    FROM Song
    LEFT JOIN Song_Pedal_Setting
    ON Song.SongID = Song_Pedal_Setting.SongID
    GROUP BY Song.SongID, Song.SongTitle
    ORDER BY Song.SongTitle ASC;
    """

    print("Song Title & Pedal Count: ")
    cursor.execute(query)

    rows = cursor.fetchall()
    for row in rows:
        print(row)

def view_band_information(): #views and prints all the band information stored in the database
    query = """
    SELECT *
    FROM Band;
    """

    cursor.execute(query)

    rows = cursor.fetchall()
    for row in rows:
        print(row)

def view_songs(): #views and prints all the song information stored in the database
    query = """
    SELECT SongTitle, SongID
    FROM Song
    ORDER BY SongID ASC;
    """
    cursor.execute(query)

    rows = cursor.fetchall()
    for row in rows:
        print(row)


def view_pedal_inventory(): #views and prints all the pedal information stored in the database
    query = """
    SELECT *
    FROM pedal;
    """
    cursor.execute(query)

    rows = cursor.fetchall()
    for row in rows:
        print(row)


def view_pedal_chain(): #views and prints the pedal name, chain order, preset and setting corresponding to the songID entered
    query = """
    SELECT Pedal.PedalName,
    Song_Pedal_Setting.ChainOrder,
    Song_Pedal_Setting.KnobPreset
    FROM Song_Pedal_Setting
    INNER JOIN Pedal
    ON Song_Pedal_Setting.PedalID = Pedal.PedalID
    WHERE Song_Pedal_Setting.SongID = ?
    ORDER BY Song_Pedal_Setting.ChainOrder;
    """

    choice_two = input("Please enter SongID, or View SongIDs (1): ").strip().upper()

    if choice_two == "1":
        print()
        view_songs()

        choice_two = input("Now enter the SongID: ").strip().upper()
        print()

    print("Pedal, Chain Position, Settings: ")
    cursor.execute(query, (choice_two,))
    rows = cursor.fetchall()

    for row in rows:
        print(row)


def insert_new_band(): #allows the user to insert a new band into the 'Band' table
        try:
            query = """
            INSERT INTO Band(BandID, BandName, Genre, ContactEmail)
            VALUES (?, ?, ?, ?);
            """

            print("Please input the following information: ")

            print("BandID format - '00' (i.e: 01)")
            BandID = input("Please enter your BandID: ")
            print()

            print("BandName format - String of text (i.e: Sam's Band)")
            BandName = input("Please enter your BandName ")
            print()

            print("Genre format - String of text (i.e: Shoegaze)")
            Genre = input("Please enter your band's genre: ")
            print()

            print("Contact email format - String of text (i.e band@example.com)")
            ContactEmail = input("Please enter your contact email: ")
            print()

            band_data = (BandID, BandName, Genre, ContactEmail)

            cursor.execute(query, band_data)
            connection.commit()
            print("Data successfully commited!")

        except sqlite3.IntegrityError:
            print("An error has occured, please confirm your parameters are correct, possibly BandID already exists?")

def insert_new_pedal(): #allows the user to insert a new pedal into the 'Pedal' table
        query = """
        INSERT INTO Pedal(PedalID, PedalName, Manufacturer, Type)
        VALUES (?, ?, ?, ?);
        """

        try:
            print("Please input the following information: ")

            print("PedalID format - 'P000' (i.e: P001)")
            PedalID = input("Please enter your PedalID: ")
            print()

            print("PedalName format - String of text (Names vary)")
            PedalName = input("Please enter your pedal's name: ")
            print()

            print("Manufacturer format - String of text (i.e: Boss)")
            Manufacturer = input("Please enter your pedal's manufacturer: ")
            print()

            print("Type format - String of text (i.e Distortion)")
            Type = input("Please enter the type of pedal: ")
            print()

            pedal_data = (PedalID, PedalName, Manufacturer, Type)

            cursor.execute(query, pedal_data)
            connection.commit()
            print("Data successfully commited!")

        except sqlite3.IntegrityError:
            print("There is an integrity error, please confirm your parameters are correct, possibly an ID already exists?")

def insert_new_song(): #allows the user to insert a new song into the 'Song' table
        try:
            query = """
            INSERT INTO Song(SongID, SongTitle, TempoBPM, TimeSignature, BandID)
            VALUES (?, ?, ?, ?, ?);
            """

            print("Please input the following information: ")

            print("SongID format - string of text (i.e: SONG001)")
            SongID = input("Please enter your SongID: ").upper()
            print()

            print("SongTitle format - string of text (i.e: Enter Sandman)")
            SongTitle = input("Please enter your song's name: ")
            print()

            print("TempoBPM format - Integer (i.e: 123)")
            TempoBPM = check_input_integer("Please enter the song's tempo: ")
            print()

            print("Time signature format - string of text (i.e 4/4)")
            TimeSignature = input("Please enter the song's time signature: ")
            print()

            print("BandID format - string of text (i.e 01)")
            BandID = input("Please enter the band's ID: ")
            print()


            song_data = (SongID, SongTitle, TempoBPM, TimeSignature, BandID)

            cursor.execute(query, song_data)
            connection.commit()
            print("Data successfully commited!")

        except sqlite3.IntegrityError:
            print("An error has occurred, please ensure your parameters are correct, maybe SongID already exists?")

def insert_new_chain(): #allows the user to add one additional pedal to the pedal chain for a song
        try:
            query = """
            INSERT INTO Song_Pedal_Setting(SongID, PedalID, ChainOrder, KnobPreset)
            VALUES (?, ?, ?, ?);
            """

            print("Please input the following information: ")

            print("SongID format - string of text (i.e: SONG001)")
            SongID = input("Please enter your SongID: ").upper()
            print()

            print("PedalID format - string of text (i.e: P001)")
            PedalID = input("Please enter your pedal's ID: ")
            print()

            print("Chain Order format - Integer (i.e: 2)")
            ChainOrder = check_input_integer("Enter the pedal's chain position: ")
            print()

            print("Knob preset format - string of text (i.e Gain: 4, Tone 5:)")
            KnobPreset = input("Please enter the pedal's knob preset: ")
            print()


            song_pedal_setting_data = (SongID, PedalID, ChainOrder, KnobPreset)

            cursor.execute(query, song_pedal_setting_data)
            connection.commit()
            print("Data successfully commited!")

        except sqlite3.IntegrityError:
            print("An error has occured, please ensure your parameters are correct, possibly IDs dont exist?")



def delete_record(): #validates user's access, then allows user to delete information stored in the database based off of an ID entered
    while True:
        print("Hint: 3x + 47 = 248")
        choice = check_input_integer("Action: ")

        if choice == 67:
            print("Access Granted")
            break

        else:
            print("Incorrect code, try again")


    print("""
What record would you like to delete?:
1: Band Details
2: Pedal Details
3: Song Details
4: Pedal Chain Details""")

    choice_two = check_input_integer("Action: ")
    print()

    if choice_two == 1: #query for band deletion
        query = """
    DELETE FROM Band
    WHERE BandID = ?;
    """

        try:
            band_id = input("Enter the BandID of the band you wish to delete: ")
            cursor.execute(query, (band_id,))

            if cursor.rowcount > 0: #if the delete statement affected atleast ONE table, proceed (prevents false successful deletion messages)
                connection.commit()
                print(f"Successfully deleted band {band_id}")

            else:
                print("No band relating to this bandID, please enter a valid BandID. ")

        except sqlite3.IntegrityError:
            print("Please delete songs associated with this band before deleting the record")

    elif choice_two == 2: #query for pedal deletion
        query = """
    DELETE FROM Pedal
    WHERE PedalID = ?;
    """

        try:
            pedal_id = input("Enter the PedalID of the pedal you wish to delete: ").strip().upper()
            cursor.execute(query, (pedal_id,))

            if cursor.rowcount > 0:
                connection.commit()
                print(f"Successfully deleted pedal {pedal_id}")

            else:
                print("No pedal relating to this pedal ID, please enter a valid pedal ID. ")

        except sqlite3.IntegrityError:
            connection.rollback()
            print("Please delete the Chain Settings relating to this pedal first")


    elif choice_two == 3: #query for song deletion
        query = """
    DELETE FROM Song
    WHERE SongID = ?;
    """

        try:
            song_id = input("Enter the SongID of the song you wish to delete: ").strip().upper()
            cursor.execute(query, (song_id,))

            if cursor.rowcount > 0:
                connection.commit()
                print(f"Successfully deleted song {song_id}")

            else:
                print("No song relating to this song ID, please enter a valid song ID. ")


        except sqlite3.IntegrityError:
            connection.rollback()
            print("Please delete the Chain Settings relating to this song first")


    elif choice_two == 4: #query for chain deletion
        query = """
    DELETE FROM Song_Pedal_Setting
    WHERE SongID = ?;
    """

        try:
            song_id = input("Enter the SongID of the song you wish to delete: ").strip().upper()
            cursor.execute(query, (song_id,))

            if cursor.rowcount > 0:
                connection.commit()
                print(f"Successfully deleted {song_id}")

            else:
                print("No song relates to this song ID, please enter a valid songID.")

        except sqlite3.IntegrityError:
            print("Please delete the Chain Settings relating to this song first")


    else:
        print("Invalid action")


def update_record(): #update function, allows the user to update stored information in a table by prompting the user to enter the new information based off of the ID entered.
    print("""
What record would you like to update?:
1: Band Details
2: Pedal Details
3: Song Details
4: Pedal Chain Details""")

    choice = check_input_integer("Action: ")
    print()

    if choice == 1: #query for band updates
        query = """
    UPDATE Band
    SET BandName = ?, Genre = ?, ContactEmail = ?
    WHERE BandID = ?;
    """

        band_id = input("Input the BandID for the band you wish to make changes to: ")
        BandName = input("Enter the bandname: ")
        Genre = input("Enter the Genre: ")
        ContactEmail = input("Input ContactEmail: ")

        cursor.execute(query, (BandName, Genre, ContactEmail, band_id))
        connection.commit()
        print("Changes saved!")


    elif choice == 2: #query for pedal updates
        query = """
    UPDATE Pedal
    SET PedalName = ?, Manufacturer = ?, Type = ?
    WHERE PedalID = ?;
    """

        pedal_id = input("Input the PedalID for the Pedal you wish to make changes to: ")
        PedalName = input("Enter the Pedal's Name: ")
        Manufacturer = input("Enter the Pedal's manufacturer: ")
        Type = input("Input the Pedal's Type: ")

        cursor.execute(query, (PedalName, Manufacturer, Type, pedal_id))
        connection.commit()
        print("Changes saved!")


    elif choice == 3: #query for song updates
        query = """
    UPDATE Song
    SET SongTitle = ?, TempoBPM = ?, TimeSignature = ?, BandID = ?
    WHERE SongID = ?;
    """

        song_id = input("Input the SongID for the song you wish to make changes to: ").upper()
        SongTitle = input("Enter the Song's Title: ")
        TempoBPM = check_input_integer("Enter the song's Tempo: ")
        TimeSignature = input("Enter the song's Time Signature: ")
        BandID = input("Enter the Band's ID that created the song: ").strip()

        cursor.execute(query, (SongTitle, TempoBPM, TimeSignature, BandID, song_id))
        connection.commit()
        print("Changes saved!")


    elif choice == 4: #query for pedal chain updates
        query = """
    UPDATE Song_Pedal_Setting
    SET ChainOrder = ?, KnobPreset = ?
    WHERE SongID = ? AND PedalID = ?;
    """

        SongID = input("Input the SongID for the Song you wish to make changes to: ").upper()
        PedalID = input("Enter the Pedal's ID which corresponds to the song: ").upper()
        ChainOrder = check_input_integer("Enter the pedal's chain order: ")
        KnobPreset = input("Input the Pedal's knob preset: ")

        cursor.execute(query, (ChainOrder, KnobPreset, SongID, PedalID))
        connection.commit()
        print("Changes saved!")

    else:
        print("Please enter a valid action")

def main(): #main function, how the user interacts with database, based on user action, main executed the corresponding function. Main infinitely loops until user exits.
    print()
    print("Welcome to the Pedalboard Database for Guitarists and Musicians.")
    while True:
        print("""
------------------------------
1: View Pedal Chain for Song
2: View Pedal Inventory
3: View Band Information
4: View All Songs
5: Insert New Band
6: Insert New Pedal
7: Insert New Song
8: Insert New Pedal Chain
9: Delete Record:
10: Update Record:
11: View Pedal Count for Songs
12: Exit
------------------------------
        """)

        choice = check_input_integer("Action: ")
        print()

        if choice == 1:
            view_pedal_chain()

        elif choice == 2:
            view_pedal_inventory()

        elif choice == 3:
            view_band_information()

        elif choice == 4:
            view_songs()

        elif choice == 5:
            insert_new_band()

        elif choice == 6:
            insert_new_pedal()

        elif choice == 7:
            insert_new_song()

        elif choice == 8:
            insert_new_chain()

        elif choice == 9:
            delete_record()

        elif choice == 10:
            update_record()

        elif choice == 11:
            view_count()

        elif choice == 12:
            print("Goodbye, thank you for choosing DB Soloutions \n")
            break

        else:
            print("Enter a valid action")


main()
connection.commit()
connection.close()
