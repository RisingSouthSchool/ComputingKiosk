#!/usr/bin/env python3
import sqlite3
import time #imports time for readability

def get_connection():
    conn = sqlite3.connect('WorldCup2026.db') #connects sqlite3 to database
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

#important information before viewing database

print()
print("Hello, Welcome to my 2026 World Cup database!")
print("In this database, goals and assists are represented")
print("as '⚽️' and '🅰️' respectively.")
print("If the score does not match the goalscorers, an own goal was scored")
print("If the number of assisters do not match the number of goals scored,")
print("then the goal was either a penalty, freekick or a deflection.")
print("Therefore by FIFA's definition of an assist, it is not counted.")
print("Enjoy!")


penalty_winners = { ("Netherlands", "Morocco"): ("Morocco", "3-2"), #dictionary for penalty winners in the round of 32 and round of 16
                   ("Germany", "Paraguay"): ("Paraguay", "4-3"),
                   ("Australia", "Egypt"): ("Egypt", "4-2"),
                   ("Switzerland", "Colombia"): ("Switzerland", "4-3") }


def view_group_matches(GroupID): #passes GroupID as a parameter
    conn = get_connection()
    cursor = conn.cursor()
    print()
    print(f"Here are the matches in Group {GroupID}")
    print("Note: If the score does not match the goalscorers, an own goal was scored")
    time.sleep(3)

    cursor.execute("""SELECT Matches.MatchID, t1.TeamName, Matches.TeamScore1, Matches.TeamScore2, t2.TeamName, Stadiums.StadiumName
    FROM Matches
    JOIN Teams t1 ON t1.TeamID = Matches.TeamID1
    JOIN Teams t2 ON t2.TeamID = Matches.TeamID2
    JOIN Stadiums ON Stadiums.StadiumID = Matches.StadiumID
    JOIN Groups ON t1.TeamID = Groups.TeamID
    WHERE Matches.Stage = 'Group Stage'
    AND Groups.GroupID = ? """, (GroupID,)) #allows for the matches of the chosen GroupID to be chosen
    for row in cursor.fetchall():
        print()
        print(row[1:]) #doesn't print MatchID
        cursor.execute("""
    SELECT Players.PlayerName, Teams.TeamName, MatchEvents.Goals, MatchEvents.Assists
    FROM MatchEvents
    JOIN Players ON Players.PlayerID = MatchEvents.PlayerID
    JOIN Teams ON Teams.TeamID = Players.TeamID
    WHERE MatchEvents.MatchID = ? """, (row[0],))
        events = cursor.fetchall() #defines the query as events
        goals1 = []
        goals2 = []
        assists1 = []
        assists2 = []
        for event in events:
            PlayerName, TeamName, Goals, Assists = event #breaks the event up
            if Goals > 0: #checks if goals is bigger than 0
                if TeamName == row[1]: #checks if team is in row 2 (team1)
                    for Goal in range(Goals): #allows for players with multiple goals to be added
                        goals1.append(PlayerName) #adds goal
                if TeamName == row[4]:
                    for Goal in range(Goals):
                        goals2.append(PlayerName)

            if Assists > 0:
                if TeamName == row[1]:
                    for Assist in range(Assists):
                        assists1.append(PlayerName)
                if TeamName == row[4]:
                    for Assist in range(Assists):
                        assists2.append(PlayerName) #same system as goals

        for goalscorer in goals1:
            print(goalscorer + "⚽️") #prints the goalscorers name and an emoji for readability
            time.sleep(0.5) #wait 0.5 seconds
        for goalscorer in goals2:
            print(" " * 25 + goalscorer + "⚽️") #adds 25 spaces for users to understand the goals are from team2
            time.sleep(0.5)
        for assister in assists1:
            print(assister + "🅰️")
            time.sleep(0.5)
        for assister in assists2:
            print(" " * 25 + assister + "🅰️")
            time.sleep(0.5) #same logic applied

        time.sleep(5)


    print()
    while True:
        print()
        print("1. Return To Groups") #one option
        print()

        choice = input("Choose an option: ")
        if choice == "1":
            break

        else:
            print("Not a valid option, Try Again.") #checks for validation

def view_groups():
    conn = get_connection()
    cursor = conn.cursor()
    GroupID = "A" #as group A is the first group, GroupID starts with "A"

    while True:
        print(f"Group {GroupID} | Points | Qualified")

        cursor.execute("""
            SELECT Teams.TeamName, Groups.Points, Groups.Qualified
            FROM Groups
            JOIN Teams ON Groups.TeamID = Teams.TeamID
            WHERE Groups.GroupID = ?
            ORDER BY Groups.Points DESC;""", (GroupID,)) #selects group

        for row in cursor.fetchall():
            print(row)

        print()
        print("1. Previous Group")
        print("2. Next Group")
        print("3. View Matches in this group")
        print("4. Return to Main Menu")
        print()

        choice = input("Choose an option: ")

        if choice == "1":
            if GroupID > "A":
                GroupID = chr(ord(GroupID) - 1) #converts the letter to unicode minus one to go back and converts it back to letter form
            else:
                print("You are already at Group A.") #Group A is the first group

        elif choice == "2":
            if GroupID < "L":
                GroupID = chr(ord(GroupID) + 1) #converts the letter to unicode adds one to go back and converts it back to letter form
            else:
                print("You are already at Group L.") #Group L is the last group
        elif choice == "3":
            view_group_matches(GroupID) #calls function with selected GroupID
        elif choice == "4":
            break

        else:
            print("Not a valid option, try again.") #validation

        print()

    conn.close()


def view_knockouts():
    conn = get_connection()
    cursor = conn.cursor()
    while True:
        print()
        print("1. Round of 32")
        print("2. Round of 16")
        print("3. Quarter-finals")
        print("4. Semi-finals")
        print("5. Third-place Play-off")
        print("6. Final")
        print("7. Return to Main Menu")
        print() #options

        choice = input("Choose an option: ")

        if choice == "1":
            print()
            cursor.execute("""SELECT Matches.MatchID, t1.TeamName, Matches.TeamScore1, Matches.TeamScore2, t2.TeamName, Stadiums.StadiumName FROM Matches
                            JOIN Teams t1 ON t1.TeamID = Matches.TeamID1
                            JOIN Teams t2 ON t2.TeamID = Matches.TeamID2
                            JOIN Stadiums ON Stadiums.StadiumID = Matches.StadiumID
                            WHERE Matches.Stage = 'Round of 32';""") #same as view_groups() only for round of 32
            for row in cursor.fetchall():
                print()
                print("-" * 60)
                print()
                print(row[1:])
                if row[2] == row[3]: #checks if the two teams score values are equal eg: 0 and 0
                    teams = (row[1], row[4]) #defines the two teams as teams
                    if teams in penalty_winners: #checks if the teams are in penalty_winners dictionary
                        winner, penalty_score = penalty_winners[teams] #defines winner, penalty score
                        print(f"{winner} won on penalties ({penalty_score})") #the winner is printed using the dictionary and the score is also printed
                cursor.execute("""
                    SELECT Players.PlayerName, Teams.TeamName, MatchEvents.Goals, MatchEvents.Assists
                    FROM MatchEvents
                    JOIN Players ON Players.PlayerID = MatchEvents.PlayerID
                    JOIN Teams ON Teams.TeamID = Players.TeamID
                    WHERE MatchEvents.MatchID = ? """, (row[0],)) #same as view_groups()
                events = cursor.fetchall()
                goals1 = []
                goals2 = []
                assists1 = []
                assists2 = []
                for event in events:
                    PlayerName, TeamName, Goals, Assists = event
                    if Goals > 0:
                        if TeamName == row[1]:
                            for Goal in range(Goals):
                                goals1.append(PlayerName)
                        if TeamName == row[4]:
                            for Goal in range(Goals):
                                goals2.append(PlayerName) #same as view_groups()

                    if Assists > 0:
                        if TeamName == row[1]:
                            for Assist in range(Assists):
                                    assists1.append(PlayerName)
                        if TeamName == row[4]:
                            for Assist in range(Assists):
                                assists2.append(PlayerName) #same as view_groups()

                for goalscorer in goals1:
                    print(goalscorer + "⚽️")
                    time.sleep(0.5)
                for goalscorer in goals2:
                    print(" " * 25 + goalscorer + "⚽️")
                    time.sleep(0.5)
                for assister in assists1:
                    print(assister + "🅰️")
                    time.sleep(0.5)
                for assister in assists2:
                    print(" " * 25 + assister + "🅰️") #same as view_groups()
                    time.sleep(0.5)

                time.sleep(3)

        elif choice == "2": #chosen value of 2 = view round of 16
            print()
            print()
            cursor.execute("""SELECT Matches.MatchID, t1.TeamName, Matches.TeamScore1, Matches.TeamScore2, t2.TeamName, Stadiums.StadiumName FROM Matches
                            JOIN Teams t1 ON t1.TeamID = Matches.TeamID1
                            JOIN Teams t2 ON t2.TeamID = Matches.TeamID2
                            JOIN Stadiums ON Stadiums.StadiumID = Matches.StadiumID
                            WHERE Matches.Stage = 'Round of 16';""") #same as view_groups() only for round of 16
            for row in cursor.fetchall():
                print()
                print("-" * 60)
                print()
                print(row[1:])
                if row[2] == row[3]:
                    teams = (row[1], row[4])
                    if teams in penalty_winners:
                        winner, penalty_score = penalty_winners[teams]
                        print(f"{winner} won on penalties ({penalty_score})") #again checks the teams if the scores are even and displays the result
                cursor.execute("""
                    SELECT Players.PlayerName, Teams.TeamName, MatchEvents.Goals, MatchEvents.Assists
                    FROM MatchEvents
                    JOIN Players ON Players.PlayerID = MatchEvents.PlayerID
                    JOIN Teams ON Teams.TeamID = Players.TeamID
                    WHERE MatchEvents.MatchID = ? """, (row[0],))
                events = cursor.fetchall()
                goals1 = []
                goals2 = []
                assists1 = []
                assists2 = []
                for event in events:
                    PlayerName, TeamName, Goals, Assists = event
                    if Goals > 0:
                        if TeamName == row[1]:
                            for Goal in range(Goals):
                                goals1.append(PlayerName)
                        if TeamName == row[4]:
                            for Goal in range(Goals):
                                goals2.append(PlayerName)

                    if Assists > 0:
                        if TeamName == row[1]:
                            for Assist in range(Assists):
                                    assists1.append(PlayerName) #same as view_groups()
                        if TeamName == row[4]:
                            for Assist in range(Assists):
                                assists2.append(PlayerName)

                for goalscorer in goals1:
                    print(goalscorer + "⚽️")
                    time.sleep(0.5)
                for goalscorer in goals2:
                    print(" " * 25 + goalscorer + "⚽️")
                    time.sleep(0.5)
                for assister in assists1:
                    print(assister + "🅰️")
                    time.sleep(0.5)
                for assister in assists2:
                    print(" " * 25 + assister + "🅰️") #same as view_groups()
                    time.sleep(0.5)

                time.sleep(3)
        elif choice == "3":
            print()
            print()
            cursor.execute("""SELECT Matches.MatchID, t1.TeamName, Matches.TeamScore1, Matches.TeamScore2, t2.TeamName, Stadiums.StadiumName FROM Matches
                            JOIN Teams t1 ON t1.TeamID = Matches.TeamID1
                            JOIN Teams t2 ON t2.TeamID = Matches.TeamID2
                            JOIN Stadiums ON Stadiums.StadiumID = Matches.StadiumID
                            WHERE Matches.Stage = 'Quarter Finals';""") #same as view_groups() except quarter finals
            for row in cursor.fetchall():
                print()
                print("-" * 60)
                print()
                print(row[1:])
                cursor.execute("""
                    SELECT Players.PlayerName, Teams.TeamName, MatchEvents.Goals, MatchEvents.Assists
                    FROM MatchEvents
                    JOIN Players ON Players.PlayerID = MatchEvents.PlayerID
                    JOIN Teams ON Teams.TeamID = Players.TeamID
                    WHERE MatchEvents.MatchID = ? """, (row[0],)) #same as view_groups()
                events = cursor.fetchall()
                goals1 = []
                goals2 = []
                assists1 = []
                assists2 = []
                for event in events:
                    PlayerName, TeamName, Goals, Assists = event
                    if Goals > 0:
                        if TeamName == row[1]:
                            for Goal in range(Goals):
                                goals1.append(PlayerName)
                        if TeamName == row[4]: #same as view_groups()
                            for Goal in range(Goals):
                                goals2.append(PlayerName)

                    if Assists > 0:
                        if TeamName == row[1]:
                            for Assist in range(Assists):
                                    assists1.append(PlayerName)
                        if TeamName == row[4]:
                            for Assist in range(Assists):
                                assists2.append(PlayerName) #same as view_groups()

                for goalscorer in goals1:
                    print(goalscorer + "⚽️")
                    time.sleep(0.5)
                for goalscorer in goals2:
                    print(" " * 25 + goalscorer + "⚽️")
                    time.sleep(0.5)
                for assister in assists1:
                    print(assister + "🅰️")
                    time.sleep(0.5)
                for assister in assists2:
                    print(" " * 25 + assister + "🅰️") #same as view_groups()
                    time.sleep(0.5)

                time.sleep(3)

        elif choice == "4":
            print()
            print()
            cursor.execute("""SELECT Matches.MatchID, t1.TeamName, Matches.TeamScore1, Matches.TeamScore2, t2.TeamName, Stadiums.StadiumName FROM Matches
                            JOIN Teams t1 ON t1.TeamID = Matches.TeamID1
                            JOIN Teams t2 ON t2.TeamID = Matches.TeamID2
                            JOIN Stadiums ON Stadiums.StadiumID = Matches.StadiumID
                            WHERE Matches.Stage = 'Semi Finals';""") #same as view_groups() except for semi finals
            for row in cursor.fetchall():
                print()
                print(row[1:])
                cursor.execute("""
                    SELECT Players.PlayerName, Teams.TeamName, MatchEvents.Goals, MatchEvents.Assists
                    FROM MatchEvents
                    JOIN Players ON Players.PlayerID = MatchEvents.PlayerID
                    JOIN Teams ON Teams.TeamID = Players.TeamID
                    WHERE MatchEvents.MatchID = ? """, (row[0],)) #same as view_groups()
                events = cursor.fetchall()
                goals1 = []
                goals2 = []
                assists1 = []
                assists2 = []
                for event in events:
                    PlayerName, TeamName, Goals, Assists = event
                    if Goals > 0:
                        if TeamName == row[1]:
                            for Goal in range(Goals):
                                goals1.append(PlayerName)
                        if TeamName == row[4]:
                            for Goal in range(Goals): #same as view_groups()
                                goals2.append(PlayerName)

                    if Assists > 0:
                        if TeamName == row[1]:
                            for Assist in range(Assists): #same as view_groups()
                                    assists1.append(PlayerName)
                        if TeamName == row[4]:
                            for Assist in range(Assists):
                                assists2.append(PlayerName)

                for goalscorer in goals1:
                    print(goalscorer + "⚽️")
                    time.sleep(0.5)
                for goalscorer in goals2:
                    print(" " * 25 + goalscorer + "⚽️")
                    time.sleep(0.5) #same as view_groups()
                for assister in assists1:
                    print(assister + "🅰️")
                    time.sleep(0.5)
                for assister in assists2:
                    print(" " * 25 + assister + "🅰️") #same as view_groups()
                    time.sleep(0.5)

                time.sleep(3)
        elif choice == "5":
            print()
            cursor.execute("""SELECT Matches.MatchID, t1.TeamName, Matches.TeamScore1, Matches.TeamScore2, t2.TeamName, Stadiums.StadiumName FROM Matches
                            JOIN Teams t1 ON t1.TeamID = Matches.TeamID1
                            JOIN Teams t2 ON t2.TeamID = Matches.TeamID2
                            JOIN Stadiums ON Stadiums.StadiumID = Matches.StadiumID
                            WHERE Matches.Stage = 'Third Place';""") #same as view_groups() except for third place
            for row in cursor.fetchall():
                print()
                print("Many people miss out on the third place match, due to the teams 'not trying'. Certainly in this fixture,")
                print("the only thing that was on display was the attack, a recording breaking 10 goals scored between them.")
                print("England ultimately won that game in this highest scoring fixture in FIFA World Cup history.")
                print() #rough description of the match as it is only 1 match
                print(row[1:])
                cursor.execute("""
                    SELECT Players.PlayerName, Teams.TeamName, MatchEvents.Goals, MatchEvents.Assists
                    FROM MatchEvents
                    JOIN Players ON Players.PlayerID = MatchEvents.PlayerID
                    JOIN Teams ON Teams.TeamID = Players.TeamID
                    WHERE MatchEvents.MatchID = ? """, (row[0],)) #same as view_groups()
                events = cursor.fetchall()
                goals1 = []
                goals2 = []
                assists1 = []
                assists2 = []
                for event in events:
                    PlayerName, TeamName, Goals, Assists = event
                    if Goals > 0:
                        if TeamName == row[1]:
                            for Goal in range(Goals):
                                goals1.append(PlayerName)
                        if TeamName == row[4]:
                            for Goal in range(Goals):
                                goals2.append(PlayerName) #same as view_groups()

                    if Assists > 0:
                        if TeamName == row[1]:
                            for Assist in range(Assists):
                                    assists1.append(PlayerName)
                        if TeamName == row[4]:
                            for Assist in range(Assists):
                                assists2.append(PlayerName) #same as view_groups()

                for goalscorer in goals1:
                    print(goalscorer + "⚽️")
                    time.sleep(0.5)
                for goalscorer in goals2:
                    print(" " * 25 + goalscorer + "⚽️")
                    time.sleep(0.5)
                for assister in assists1:
                    print(assister + "🅰️")
                    time.sleep(0.5)
                for assister in assists2:
                    print(" " * 25 + assister + "🅰️")
                    time.sleep(0.5)

                time.sleep(3) #same as view_groups()
        elif choice == "6":
            print()
            cursor.execute("""SELECT Matches.MatchID, t1.TeamName, Matches.TeamScore1, Matches.TeamScore2, t2.TeamName, Stadiums.StadiumName FROM Matches
                                JOIN Teams t1 ON t1.TeamID = Matches.TeamID1
                                JOIN Teams t2 ON t2.TeamID = Matches.TeamID2
                                JOIN Stadiums ON Stadiums.StadiumID = Matches.StadiumID
                                WHERE Matches.Stage = 'Final';""") #same as view_groups() but for the Final
            for row in cursor.fetchall():
                print()
                print("The final of the biggest competition in the world, the most watched event ever.")
                print("Spain and Argentina, felt like a passing of the torch from the greatest player ever,")
                print("Lionel Messi, to the young prodigee taking the world by storm, Lamine Yamal.")
                print("This game ended in Spain lifting the World Cup Trophy after an extra time winner.")
                print() #brief description of the match
                print(row[1:])
                cursor.execute("""
                    SELECT Players.PlayerName, Teams.TeamName, MatchEvents.Goals, MatchEvents.Assists
                    FROM MatchEvents
                    JOIN Players ON Players.PlayerID = MatchEvents.PlayerID
                    JOIN Teams ON Teams.TeamID = Players.TeamID
                    WHERE MatchEvents.MatchID = ? """, (row[0],)) #same as view_groups()
                events = cursor.fetchall()
                goals1 = []
                goals2 = []
                assists1 = []
                assists2 = []
                for event in events:
                    PlayerName, TeamName, Goals, Assists = event
                    if Goals > 0:
                        if TeamName == row[1]:
                            for Goal in range(Goals):
                                goals1.append(PlayerName)
                        if TeamName == row[4]:
                            for Goal in range(Goals):
                                goals2.append(PlayerName) #same as view_groups()

                    if Assists > 0:
                        if TeamName == row[1]:
                            for Assist in range(Assists):
                                    assists1.append(PlayerName)
                        if TeamName == row[4]:
                            for Assist in range(Assists):
                                assists2.append(PlayerName)

                for goalscorer in goals1:
                    print(goalscorer + "⚽️")
                    time.sleep(0.5) #same as view_groups()
                for goalscorer in goals2:
                    print(" " * 25 + goalscorer + "⚽️")
                    time.sleep(0.5)
                for assister in assists1:
                    print(assister + "🅰️")
                    time.sleep(0.5)
                for assister in assists2:
                    print(" " * 25 + assister + "🅰️")
                    time.sleep(0.5)

                time.sleep(3)
        elif choice == "7":
            break #exits function goes to main menu
        else:
            print("Not a valid option, try again.") #validates if user doesn't type a valid option

    conn.close()

def view_stat_leaders():
     conn = get_connection()
     cursor = conn.cursor()
     while True:
         print()
         print("1. Sort by Goals")
         print("2. Sort by Assists")
         print("3. Sort by G+A")
         print("4. Return to Main Menu")
         print()
         choice = input("Choose on option: ") #options
         print()
         if choice == "1":
            print("Player | Goals")
            cursor.execute("""SELECT Players.PlayerName, SUM(MatchEvents.Goals) AS Goals FROM Players
                      JOIN MatchEvents ON Players.PlayerID = MatchEvents.PlayerID
                      GROUP BY Players.PlayerName
                      ORDER BY Goals DESC
                      LIMIT 10;""") #shows the top ten players with the most goals
            for row in cursor.fetchall():
                print(row)

         elif choice == "2":
            print("Player |  Assists") #differentiate the columns
            cursor.execute("""SELECT Players.PlayerName, SUM(MatchEvents.Assists) AS Assists FROM Players
                                   JOIN MatchEvents ON Players.PlayerID = MatchEvents.PlayerID
                                   GROUP BY Players.PlayerName
                                   ORDER BY Assists DESC
                                   LIMIT 10;""") #shows the top ten players with the most assists
            for row in cursor.fetchall():
                print(row)
         elif choice == "3":
            print("Player | G+A | Goals | Assists")
            cursor.execute("""SELECT Players.PlayerName, SUM(MatchEvents.Assists) + SUM(MatchEvents.Goals) AS "G+A", SUM(MatchEvents.Goals) AS Goals, SUM(MatchEvents.Assists) AS Assists FROM Players
                                   JOIN MatchEvents ON Players.PlayerID = MatchEvents.PlayerID
                                   GROUP BY Players.PlayerName
                                   ORDER BY "G+A" DESC
                                   LIMIT 10;""") #shows the top ten players with the most goals and assists combined
            for row in cursor.fetchall():
                print(row)
         elif choice == "4":
             break #returns to main menu
         else:
             print("Not a valid option, try again") #validates user input

     conn.close()


def team_search():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TeamName FROM Teams") #selects all the teams
    TeamNames = [row[0] for row in cursor.fetchall()] #pulls name out of tuple
    while True:
            TeamName = input("Enter a team's name: ").title() #allows for text to be capitalized
            if TeamName not in TeamNames: #checks if the user input is not ateam in the world cup
                print("Team not found, try again")
                print()
            else:
                cursor.execute("""SELECT RoundAchieved FROM Teams WHERE TeamName = ?""", (TeamName,)) #selects the round achieved for the chosen team
                RoundAchieved = cursor.fetchall()
                print(f"This is {TeamName}'s run in the World Cup 2026.")
                print(f"{TeamName} achieved the result of the {RoundAchieved}") #shows the team names result
                print("This is their matches down below.")
                print()
                cursor.execute("""SELECT Matches.MatchID, t1.TeamName, Matches.TeamScore1, Matches.TeamScore2, t2.TeamName, Matches.Stage, Stadiums.StadiumName FROM Matches
                                JOIN Teams t1 ON t1.TeamID = Matches.TeamID1
                                JOIN Teams t2 ON t2.TeamID = Matches.TeamID2
                                JOIN Stadiums ON Stadiums.StadiumID = Matches.StadiumID
                                WHERE t1.TeamName = ? OR t2.TeamName =?""", (TeamName, TeamName))
                for row in cursor.fetchall(): #same as view_groups() however the WHERE statement has been changed to accommodate the possibility of the team to be in either teamname1 or teamname2
                    print(row[1:]) #doesnt print the first row (matchID)
                break #exits function
    conn.close()

def player_search():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT PlayerName FROM Players") #selects all the players
    PlayerNames = [row[0] for row in cursor.fetchall()] #pulls out name from tuple
    while True:
        PlayerName = input("Enter a player's name: ").title() #capitalizes player
        if PlayerName not in PlayerNames: #checks if user input not in playernames
            print("Player not found, try again")
            print()
        else:
            cursor.execute("""SELECT SUM(MatchEvents.Goals), SUM(MatchEvents.Assists) FROM MatchEvents JOIN Players ON MatchEvents.PlayerID = Players.PlayerID WHERE PlayerName =?""", (PlayerName,))
            Stats = cursor.fetchall() #selects the players stat data (number of goals and assists)
            print()
            cursor.execute("SELECT PlayerID FROM Players WHERE PlayerName = ?", (PlayerName,))
            PlayerID = cursor.fetchone()[0] #returns first row of the query and removes the first column of the tuple eg: "(1,)" becomes "1"
            cursor.execute("SELECT Teams.TeamName FROM Teams JOIN Players ON Players.TeamID = Teams.TeamID WHERE PlayerID =?", (PlayerID,)) #users playerID to select their teamname
            TeamName = cursor.fetchone()[0] #same thing as playerid logic
            print(f"{PlayerName} had {Stats[0][0]} goals and {Stats[0][1]} assists across the World Cup 2026, playing for {TeamName}") #shows only the number not the row or item
            print() #prints the stats of the players splitting the goals and assists for readability
            cursor.execute("""SELECT Matches.MatchID, MatchEvents.Goals, MatchEvents.Assists, t1.TeamName, Matches.TeamScore1, Matches.TeamScore2, t2.TeamName, Matches.Stage, Stadiums.StadiumName FROM Matches
                                JOIN Teams t1 ON t1.TeamID = Matches.TeamID1
                                JOIN Teams t2 ON t2.TeamID = Matches.TeamID2
                                JOIN Stadiums ON Stadiums.StadiumID = Matches.StadiumID
                                JOIN MatchEvents ON MatchEvents.MatchID = Matches.MatchID
                                WHERE MatchEvents.PlayerID = ? AND (MatchEvents.Goals > 0 OR MatchEvents.Assists > 0)""", (PlayerID,))
            PlayerMatches = cursor.fetchall() #selects the players stats in every match they played in for which they recorded a goal or an assist atleast once
            for row in PlayerMatches:
                print(row[3:]) #doesnt print the first 4 columns
                print(f"{PlayerName} scored {row[1]} goals and got {row[2]} assists in this match.") #displays the stats underneath every match
                print()
                time.sleep(2) #waits 2 seconds
            break #exits function
    conn.close()

def view_stadiums():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT Stadiums.StadiumName, Stadiums.HostCity, Stadiums.Country, t1.TeamName, Matches.TeamScore1, Matches.TeamScore2, t2.TeamName, Matches.Stage
                        FROM Stadiums
                        JOIN Matches ON Matches.StadiumID = Stadiums.StadiumID
                        JOIN Teams t1 ON t1.TeamID = Matches.TeamID1
                        JOIN Teams t2 ON t2.TeamID = Matches.TeamID2
                        ORDER BY Stadiums.StadiumName""") #selects the stadium details and the matches they hosted, orders them in stadium name
    current_stadium = None #allows the current stadium to be none
    for row in cursor.fetchall():
        if row[0] != current_stadium: #which it always it going to be because it is bigger than none
            print()
            print(f"{row[0]} in {row[1]}, {row[2]} hosted these games:") #grabs the stadium details and allows for user to view the stadium name and where it is (city and country)
            print()
            current_stadium = row[0] #updated
            time.sleep(3) #displays one by one for readability

        print(row[3:]) #removes first 4 lines only displaying the match events
    conn.close()

#main menu
while True:
    print()
    print("1. View the Groups")
    print("2. View The Knockout Stages")
    print("3. View the Stat Leaders")
    print("4. View the Stadiums")
    print("5. Search Teams")
    print("6. Search Players")
    print("7. Important Information")
    print("8. Exit")
    print() #all options for the main menu
    choice = input("Choose an option: ")
    print()

    if choice == "1":
        view_groups()
        print()
    elif choice == "2":
        view_knockouts()
        print()
    elif choice == "3":
        view_stat_leaders()
    elif choice == "4":
        view_stadiums()
    elif choice == "5":
        team_search()
    elif choice == "6":
        player_search() #each option calls the function
    elif choice == "7":
        print()
        print("In this database, goals and assists are represented")
        print("as '⚽️' and '🅰️' respectively.")
        print("If the score does not match the goalscorers, an own goal was scored")
        print("If the number of assisters do not match the number of goals scored,")
        print("then the goal was either a penalty, freekick or a deflection.")
        print("Therefore by FIFA's definition of an assist, it is not counted.") #information incase user didn't read the start
        print("Enjoy!")
    elif choice == "8":
        break #exits program
    else:
        print("Not a valid option, try again") #validates user input
