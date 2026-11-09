#!/usr/bin/env python3
import sqlite3 #import the sqlite library to.the python file

conn = sqlite3.connect("ArtistTracker.db") #connects python to the database
conn.execute("PRAGMA foreign_keys = ON") #turns foreign keys on in the file
cursor = conn.cursor()

def view_artists(): #function to view all artists in the database
    cursor.execute("SELECT * FROM Artist") #Selects every artist
    artists = cursor.fetchall()

    for artist in artists: #loops for each artist
        print(artist) #prints each artist

def view_tracks(): #function to view all tracks
#selects track ID, track name, album name and duration
#gets this info FROM the track table
#joins the album table to display the album that each track is in
    cursor.execute("""
        SELECT Track.TrackID, Track.TrackName,
            Album.AlbumName, Track.Duration
        FROM Track
        INNER JOIN Album
        ON Track.AlbumID = Album.AlbumID
    """)

    tracks = cursor.fetchall() # gets every track

    for track in tracks: #loops each track
        print(track) #prints each track in the loop

def search_artist(): #searches the artist database
    name = input("Enter artist name: ") #input to search an artist
#selects the track name and the contribution of an artist from the track table.
#Joins the collaboration table, and the artist table. Has a like function so if their is a partial match it will show up
    cursor.execute("""
        SELECT Track.TrackName, Collaboration.Contribution
        FROM Track
        INNER JOIN Collaboration
        ON Track.TrackID = Collaboration.TrackID
        INNER JOIN Artist
        ON Collaboration.ArtistID = Artist.ArtistID
        WHERE Artist.ArtistName LIKE ?
    """, ("%" + name + "%",))

    results = cursor.fetchall() #fetches all results
    if len(results) == 0: #if there is no letter typed, the code will print that there is nothing
        print("No tracks found.")
    else: #if there is a value, it will print the track name
        for track in results:
            print(track)
def update_artist(): #function to update an artists genre
    while True:
        login = input("Restricted Access! Enter Username: ")

        if login == "Admin":
            password = input("What is your password? ")
            if password == "Password1":
                print("User accepted")
            artist_id = int(input("Enter artist ID: ")) #asks the user to end the artist id
            new_genre = input("Enter updated genre: ") #asks the user to enter the new genre
            #updates the genre in the artist table
            #uses the artist ID to find which artist to update
            #question marks are placeholders for the user inputs
            cursor.execute("""
                UPDATE Artist
                SET Genre = ?
                WHERE ArtistID = ?
            """, (new_genre, artist_id))

            conn.commit() #saves changes to the database
            if cursor.rowcount > 0: #checks if any rows were updated
                print("Artist updated successfully!") #print success message
            else: #if no rows were updated
                print("Artist not found.") # error message

            break
        else:
            print("Invalid username!")

def search_genre(): #search genre function
    genre = input("Enter genre: ") #user inputs the genre they want to see
    #selects distinct track and artist from the track table, joins collaboration table onto the track table.
    cursor.execute("""
        SELECT DISTINCT Track.TrackName, Artist.ArtistName
        FROM Track
        INNER JOIN Collaboration
        ON Track.TrackID = Collaboration.TrackID
        INNER JOIN Artist
        ON Collaboration.ArtistID = Artist.ArtistID
        WHERE Artist.Genre LIKE ?
    """, ("%" + genre + "%",))
    results = cursor.fetchall() #get all results
    for track in results: #print every track results
        print(track)

def count_tracks(): #function to count the number of tracks per person
    cursor.execute("""
        SELECT Artist.ArtistName,
            COUNT(DISTINCT Collaboration.TrackID)
        FROM Artist
        LEFT JOIN Collaboration
        ON Artist.ArtistID = Collaboration.ArtistID
        GROUP BY Artist.ArtistID, Artist.ArtistName
    """)
    results = cursor.fetchall() #gets every result

    for artist in results:
        print(artist) #prints every artist

def sort_tracks():
    cursor.execute("""
        SELECT TrackName, Duration
        FROM Track
        ORDER BY Duration DESC
    """)
    results = cursor.fetchall()
    for track in results:
        print(track)

def popular_artists(): #function to find artists with more than three tracks
    #selects each artist and counts the number of distinct tracks they have, has to be distinct to not count dupe collab tracks
    #orders by most tracks to least
    cursor.execute("""
        SELECT Artist.ArtistName,
            COUNT(DISTINCT Collaboration.TrackID) AS TotalTracks
        FROM Artist
        INNER JOIN Collaboration
        ON Artist.ArtistID = Collaboration.ArtistID
        GROUP BY Artist.ArtistID, Artist.ArtistName
        HAVING COUNT(DISTINCT Collaboration.TrackID) > 3
        ORDER BY TotalTracks DESC
    """)
    results = cursor.fetchall()
    for artist in results:
        print(artist)

def add_artist(): #function to add artist

   while True:
        login = input("Restricted Access! Enter Username: ")

        if login == "Admin":
            password = input("What is your password? ")
            if password == "Password1":
                print("User accepted")
                artist_id = int(input("Enter artist ID: ")) #add the ID of the artist you want to add
                name = input("Enter artist name: ") #add the name of the artist you want to add
                nationality = input("Enter nationality: ") #add the nationality of the artist you want to add
                genre = input("Enter genre: ") #add the grene of the artist you want to add

                try: #try add an artist, insert the values added
                    cursor.execute("""
                        INSERT INTO Artist
                        (ArtistID, ArtistName, Nationality, Genre)
                        VALUES (?, ?, ?, ?)
                    """, (artist_id, name, nationality, genre))

                    conn.commit() #saves changes to database
                    print("Artist added successfully!") #if it works there will be a confirmation statement

                except ValueError:
                    print("Artist ID has to be a number!")

                except sqlite3.IntegrityError: #if there is an integrity error, (breaks a rule) an error message will show up
                    print("Error: ArtistID already exists!") #error message
            else:
                print("Incorrect password")

        else:
            print("Invalid username!")

def add_track(): #function to add tracks
   while True:
        login = input("Restricted Access! Enter Username: ")

        if login == "Admin":
            password = input("What is your password? ")
            if password == "Password1":
                print("User accepted")
                Track_ID = int(input("Enter track ID: ")) #asks for track id
                Track_Name = input("Enter track name: ") #asks for the track name
                Album_ID = int(input("Enter album ID: ")) #asks which album the track is part of
                Duration = input("Enter track duration: ") #asks for the duration
                Release_Date = input("Enter release date (DD-MM-YYYY): ") #asks for release date

                try: #tries to insert the new track into db
                    cursor.execute("""
                        INSERT INTO Track
                        (TrackID, TrackName, AlbumID, Duration, ReleaseDate)
                        VALUES (?, ?, ?, ?, ?)
                    """, (Track_ID, Track_Name, Album_ID, Duration, Release_Date))
                    conn.commit() #saves changes to the db
                    print("Track added successfuly!") #prints the success message

                except sqlite3.IntegrityError: #checks if any of the db rules break
                    print("Error: Track ID already exists or album id is invalid.")
            else:
                print("Incorrect password")

        else:
            print("Invalid username!")


def delete_artist(): #function to delete an artist from the database

   while True:
        login = input("Restricted Access! Enter Username: ")

        if login == "Admin":
            password = input("What is your password? ")
            if password == "Password1":
                print("User accepted")
                artist_id = int(input("Enter artist ID to delete: ")) #enter the id of the artist that you want to delete
                try: #try to delete if there are no errors.
                    cursor.execute("""
                        DELETE FROM Artist
                        WHERE ArtistID = ?
                    """, (artist_id,))
                    conn.commit()
                    if cursor.rowcount > 0:
                        print("Artist deleted successfully!") #if it works print a success message
                    else:
                        print("Artist not found.") #if the database doesnt have the value for that id, print an error message



                except sqlite3.IntegrityError: #checks if any of the db rules break
                    print("Error: Track ID already exists or album id is invalid.")
            else:
                print("Incorrect password")

        else:
            print("Invalid username!")











while True: #this will happen when the database starts


        print("ARTIST DATABASE") #pretty much a UI layout for the user to interact with
        print("1. View all artists") #the different options for the user to pick
        print("2. View all tracks")
        print("3. Search tracks by artist")
        print("4. Add artist")
        print("5. Delete artist")
        print("6. Update Artist Info")
        print("7. Search tracks by genre")
        print("8. Count tracks per artist")
        print("9. Sort tracks by duration")
        print("10. Show artists with many tracks")
        print("11. Add track")
        print("12. Exit")
        print("")



        choice = input("Enter choice: ") #tells the user to pick a choice
        try:
            if choice == "1": #the results for the different choices, each one does a different function
                view_artists()

            elif choice == "2":
                view_tracks()

            elif choice == "3":
                search_artist()

            elif choice == "4":
                add_artist()

            elif choice == "5":
                delete_artist()


            elif choice == "6":
                update_artist()

            elif choice == "11":
                add_track()

            elif choice == "7":
                search_genre()

            elif choice == "8":
                count_tracks()

            elif choice == "9":
                sort_tracks()

            elif choice == "10":
                popular_artists()

            elif choice == "12":
                print("Goodbye")
                break

            else:
                print("Invalid choice.") #if there is a number other than these itll error.
        except ValueError:
            print("Error: Please enter valid number.")



conn.close() #closes the database connection



