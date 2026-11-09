#!/usr/bin/env python3
import sqlite3
import random
from datetime import date

def main(): #runs the main functions and closes the database when finished
  for i in range(99):  # create space for code usage
    print("")
  disclaimer() # run the disclaimer
  login_menu() # run login_menu
  for i in range(99): # bury all usage of the code under blank print statements
    print("")
  print("Thank you for using this database.") # thank the user for using the database
  print("We hope you have a nice day.")
  conn = get_connection()
  conn.close() # close the database

def get_connection(): # repeatable function to simlify a connection to database and allowing foregin keys to work
  conn = sqlite3.connect('database.db')
  conn.execute("PRAGMA foreign_keys = ON")
  return conn

def disclaimer():
  print("")
  print("This is a Test for our database.")
  print("Due to this the data is limited.")
  print("And only few actions can be done.")
  print("Thank you for understanding.")
  print("")

def define_error(error_number): # A dictionary of error messages that can be repeatedly used
    if error_number == 1:
      print("")
      print("Invalid value type.")
      print("Was expecting an integer.")
      return
    elif error_number == 2:
      print("")
      print("Invalid value type.")
      print("Was expecting a float.")
      return
    elif error_number == 3:
      print("")
      print("Invalid Value Size")
      print("Was Expecting a Smaller Value")
      return
    elif error_number == 4:
      print("")
      print("Invalid Value Size")
      print("Was Expecting a Larger Value")
      return
    elif error_number == 5:
      print("")
      print("Failed to Log In")
      print("Incorrect Password or Accountname.")
      print("Try Logging In Again: 1")
      print("Return to Menu: 2")
      return
    elif error_number == 6:
      print("")
      print("Failed to Create AccountName.")
      print("An Account With This Name Already Exists.")
      print("Try Again: 1")
      print("Return to Menu: 2")
      return
    elif error_number == 7:
      print("")
      print("Failed to Confirm Password")
      print("Try Again: 1")
      print("Return to Menu: 2")
      return
    elif error_number == 8:
      print("")
      print("Failed to Find User")
      print("Try Again: 1")
      print("Return to Menu: 2")
      return
    elif error_number == 9:
      print("")
      print("Failed to Enter Name of User")
      print("A User Already has this First & Last Name")
      print("Try Again: 1")
      print("Return to Menu: 2")
      return
    elif error_number == 9:
      print("")
      print("Invalid value type.")
      print("Was expecting a string.")
      return

def login_menu(): # menu to log into the database
  while True:
    print("")
    print("Login: 1.")
    print("Sign Up: 2.")
    print("Quit: 0.")
    choice = get_choice()
    if choice == 1:
      login_account()
    elif choice == 2:
     sign_up()
    elif choice == 0:
      return
    elif choice >= 4:
      define_error(4)
    elif choice <= -1:
      define_error(3)

def get_choice(): # a repeatable function to get a users choice
  while True:
    try:
      print("")
      choice = int(input("Select Option: "))
      print(f"Selected option {choice}")
      print("")
      return choice
    except ValueError:
      define_error(1)

def login_account(): # function to log into an existing account
  while True:
    account = add_accountname()
    password = add_password()
    accountID = verify_account(account,password) # We check if the accounts exist #
    if accountID == -1: # if they dont
      define_error(5) # call an error/ failure message & ask if they want to try again
      while True:
        choice = get_choice()
        if choice <= 0:
          define_error(3)
        elif choice >= 3:
          define_error(4)
        elif choice == 2: # if they dont, we return to login menu
          return
        else: #other wise loop back to start
          break
    else:
      break
  main_menu(accountID) #if account exists, send them to the main database menu


def verify_account(account,password): # a repeatable function that checks if an account exits using AccountName and Password
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT AccountName FROM Accounts WHERE AccountName = ?", (account,)) #Give us the name of an account that has the inputted accountname
  rows = cursor.fetchall()
  checknotblank = [] # a list we use to,
  if rows == checknotblank: # check if the result isnt blank
    return -1
  cursor.execute("SELECT Password FROM Accounts WHERE Password = ?", (password,))
  rows = cursor.fetchall()
  if rows == checknotblank:
    return -1
  cursor.execute("SELECT AccountName, Password FROM Accounts WHERE AccountName = ? AND Password = ?", (account,password)) #Give us the password of an account that has the inputted password
  rows = cursor.fetchall()
  cleanup1 = str(rows) #Here we have to clean up,
  cleanup2 = cleanup1.replace("[('","")
  cleanup3 = cleanup2.replace("')]","")
  check = cleanup3.replace("'","")
  if check != account + ", " + password: # so we can check if the account mathces the password or/& vis versa
    return -1
  cursor.execute("SELECT AccountID FROM Accounts WHERE AccountName = ? AND Password = ?", (account,password)) #Give us the accountID of the account that has both the inputed accountname and password
  rows = cursor.fetchall()
  cleanup1 = str(rows)
  cleanup2 = cleanup1.replace("[(","")
  cleanup3 = cleanup2.replace(",)]","")
  accountID = int(cleanup3) #turn the resulting varible into a integer
  return accountID # return the result

def sign_up(): # a function used to sign up a new account & link it to a user
 accountID = new_account()
 if accountID == -1:
  return
 else:
  main_menu(accountID)

def new_account(): # This function uses the repeatable functions that create new accounts and users. After doing this it then logs the user in with the new account.
  conn = get_connection()
  cursor = conn.cursor()
  print("Before we Create Your New Account.") # prompt use if they also mant to make a new user.
  print("Are You Signing Up as an Existing User?: 1")
  print("Or Would You Like to Sign Up as a New User?: 2")
  while True:
    choice = get_choice()
    if choice == 1: #if they want to use an existing user
      email = add_email() #they enter their email
      passkey = str(input("Enter Accounts Passkey: ")) # and passkey
      userID = verify_user(email,passkey) #so we can check if theirs a user that has this
      if userID == -1: # if not
        define_error(8) # we tell them this use dosnt exist
        newchoice = get_choice() # and ask if they want to try again
        if choice <= 0:
          define_error(3)
        elif newchoice >= 3:
          define_error(4)
        elif newchoice == 2:
          return -1
      else: # other wise
        break # we let them make the new account
    elif choice == 2: # if they want to make a new user
      userID = add_user() # we let them do so
      if userID == -1: # if any issue arise
        return -1 # we return false
      else: # otherwise
        break # we let tme make a new account
    elif choice <= 0:
      define_error(3)
    elif choice >= 3:
      define_error(4)
    else:
      break
  accountID = add_account() # they make the account
  if accountID == -1: # and return them if theirs any issues
    return -1
  cursor.execute("UPDATE Accounts SET UserID = ? WHERE AccountID = ?", (userID,accountID)) # otherwise we link the use to the new account
  conn.commit() # and commit it.
  return accountID

def verify_user(email,passkey): # a repeatable function that checks if an user exits using email and Passkey
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT Email FROM Users WHERE Email = ?", (email,)) #Give us the email of an user that has the inputted email
  rows = cursor.fetchall()
  checknotblank = [] # a list we use to,
  if rows == checknotblank: # check if the result isn't blank
    return -1
  cursor.execute("SELECT PassKey FROM Users WHERE PassKey = ?", (passkey,))
  rows = cursor.fetchall()
  if rows == checknotblank:
    return -1
  cursor.execute("SELECT Email, PassKey FROM Users WHERE Email = ? AND PassKey = ?", (email,passkey)) # Give us both the email & passkey of a user that has the inputted email and passkey.
  rows = cursor.fetchall()
  cleanup1 = str(rows) #Here we have to clean up the result,
  cleanup2 = cleanup1.replace("[('","")
  cleanup3 = cleanup2.replace("')]","")
  check = cleanup3.replace("'","")
  if check != email + ", " + passkey: # so we can check if the email matches the passkey or/& vis versa
    return -1
  cursor.execute("SELECT UserID FROM Users WHERE Email = ? AND PassKey = ?", (email,passkey)) #Give us the accountID of the account that has both the inputted account name and password
  rows = cursor.fetchall()
  cleanup1 = str(rows)
  cleanup2 = cleanup1.replace("[(","")
  cleanup3 = cleanup2.replace(",)]","")
  userID = int(cleanup3) #turn the resulting varible into a integer
  return userID # return the result

def add_user(): #repeatable function to add a new user to database
  conn = get_connection()
  cursor = conn.cursor()
  checkisblank = []
  print("")
  while True:
    firstname = get_firstname() # first name of new user
    lastname = get_lastname() # last name of new user
    cursor.execute("SELECT FirstName, LastName FROM Users WHERE FirstName = ? AND LastName = ?", (firstname,lastname))
    rows = cursor.fetchall()
    if rows != checkisblank: # we check someone dosnt already have the same first and last name
      define_error(9) # if they already is a user with this name, we call an error
      choice = get_choice() # and aske if they want to try again
      if choice <= 0:
        define_error(3)
      elif choice >= 3:
        define_error(4)
      elif choice == 2:
        return -1
    else: # otherwise
      break # we let the move on
  email = add_email() # we aske for their email
  while True:
    passkey = f"{random.randint(0,9999):04d}" # we create a random passkey
    cursor.execute("SELECT PassKey FROM Users WHERE PassKey = ?", (passkey,))
    rows = cursor.fetchall() # make sure their isnt an account with this passkey
    if rows == checkisblank: # if their isnt
      break # We let them move on
  cursor.execute("INSERT INTO Users(FirstName,LastName,Email,PassKey) VALUES(?,?,?,?)", (firstname,lastname,email,passkey)) # we create the user
  conn.commit()
  cursor.execute("SELECT UserID FROM Users WHERE PassKey = ?", (passkey,)) # we find the users ID using their passkey
  rows = cursor.fetchall()
  cleanup1 = str(rows)
  cleanup2 = cleanup1.replace("[(","")
  cleanup3 = cleanup2.replace(",)]","")
  userID = int(cleanup3) #turn the resulting varible into a integer
  print("")
  print(f"Your Passkey is {passkey}.") # we tell them their passkey
  print("You can See your PassKey in My Account.")
  print("But try not to forget it regardless.")
  return userID # then return userID

def add_account(): #repeatable function to add a new account to database
  conn = get_connection()
  cursor = conn.cursor()
  checkisblank = []
  print("")
  while True:
    accountname = add_accountname() # name of the new account
    cursor.execute("SELECT AccountName FROM Accounts WHERE AccountName = ?", (accountname,))
    rows = cursor.fetchall()
    if rows != checkisblank: # we make sure there isnt an account with this name already
      define_error(6) # if their is we flag an error
      choice = get_choice() # and ask if they want to try again
      if choice <= 0:
        define_error(3)
      elif choice >= 3:
        define_error(4)
      elif choice == 2:
        return -1
    else: # other wise
      break # we let them move on
  password = new_password() # we get their password
  if password == -1:
    return -1
  today = date.today() # we get todays date
  formatted_date = today.strftime("%d-%m-%Y") # add format it properly
  cursor.execute("INSERT INTO Accounts(AccountName,JoinDate,Password,EditAccess) VALUES(?,?,?,0)", (accountname,formatted_date,password)) # we add the account
  conn.commit()
  cursor.execute("SELECT AccountID FROM Accounts WHERE AccountName = ?", (accountname,)) # we get their accountID using their accountname
  rows = cursor.fetchall()
  cleanup1 = str(rows)
  cleanup2 = cleanup1.replace("[(","")
  cleanup3 = cleanup2.replace(",)]","")
  accountID = int(cleanup3) #turn the resulting varible into a integer
  return accountID

def new_password(): # a reatable function to create a new password
  print("")
  while True:
    password = add_password() # Get requested password #
    print("Enter password again to confirm")
    confirmpassword = add_password() # Enter it again#
    if password != confirmpassword: #If their not the same,
      define_error(7) # ask the user if they want to try again.
      while True:
        choice = get_choice()
        if choice <= 0:
          define_error(3)
        elif choice >= 3:
          define_error(4)
        elif choice == 2:
          return -1
        else:
          break
    else:
      return password # Otherwise return the input

def main_menu(accountID): # the main menu for using the database
  conn = get_connection()
  cursor = conn.cursor()
  print("")
  cursor.execute("SELECT AccountName FROM Accounts WHERE AccountID = ?", (accountID,)) # find the accounts name
  rows = cursor.fetchall()
  cleanup1 = str(rows)
  cleanup2 = cleanup1.replace("[('","")
  accountname = cleanup2.replace("',)]","")
  print(f"You have Logged in as {accountname}.") # and address the user as the account name.
  while True:
    print("")
    print(f"What would you like to do {accountname}?") # we ask the user what they want to do in the data base.
    print("")
    print("View My Account: 1.")
    print("View All Accounts: 2.")
    print("View Cards: 3")
    print("View Collections: 4.")
    print("View Listings: 5.")
    print("Admin Panel: 6.")
    print("Quit: 0.")
    choice = get_choice() # and get their selectiong
    if choice == 1:
      view_my_account(accountID) # They view their account and can change some things.
    elif choice == 2:
      view_accounts() # they can view all accounts
    elif choice == 3:
      view_cards() # they can view all cards
    elif choice == 4:
      view_collections() # they can view all collections
    elif choice == 5:
      view_listings() # they can view all listings
    elif choice == 6:
      admin_panel(accountID) # they can (try to) use the admin panel
    elif choice >= 7:
      define_error(4)
    elif choice <= -1:
      define_error(3)
    elif choice == 0:
      return


def view_my_account(accountID):
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT Users.UserID FROM Users JOIN Accounts ON Users.UserID = Accounts.AccountID WHERE Accounts.AccountID = ?,", (accountID,)) #we get their userID
  rows = cursor.fetchall()
  cleanup1 = str(rows)
  cleanup2 = cleanup1.replace("[(","")
  cleanup3 = cleanup2.replace(",)]","")
  userID = int(cleanup3)
  while True:
    cursor.execute("SELECT Accounts.AccountName, Accounts.JoinDate, Accounts.Password, Accounts.AccountID, Accounts.UserID, Users.Email FROM Accounts JOIN Users ON Accounts.UserID = Users.UserID WHERE Accounts.AccountID = ?", (accountID,)) # we show all data a user might want when viewing their account whilst keeping some privacy
    rows = cursor.fetchall()
    print(rows)
    print("")
    print("See User: 1") # we ask what the user wants to do.
    print("Change AccountName: 2")
    print("Change Password: 3")
    print("Return: 0")
    choice = get_choice()
    if choice == 1:
      view_user(userID) # view the user of their account
    elif choice == 2:
      account = add_accountname() # update their account name
      cursor.execute("UPDATE Accounts Set AccountName =? WHERE AccountID = ?", (account,accountID,))
    elif choice == 3:
      password = new_password() # update their password
      cursor.execute("UPDATE Accounts Set Password =? WHERE AccountID = ?", (password,accountID,))
    elif choice >= 4:
      define_error(4)
    elif choice <= -1:
      define_error(3)
    elif choice == 0:
      return

def view_user(userID):
  conn = get_connection()
  cursor = conn.cursor()
  while True:
    cursor.execute("SELECT FirstName, LastName, Email, Passkey, UserID FROM Users WHERE UserID = ?", (userID,)) #show all data about their user
    print(userinfo)
    print("")
    print("Change First Name: 1") #ask what they would like to do
    print("Change Last Name: 2")
    print("Change Email: 3")
    print("Return: 0")
    choice = get_choice()
    if choice == 1:
      firstname = get_firstname() # change their first name
      cursor.execute("UPDATE Users Set FirstName =? WHERE UserID = ?", (firstname,userID,))
    elif choice == 2:
      lastname = get_firstname() # change their last name
      cursor.execute("UPDATE Users Set lastName =? WHERE UserID = ?", (lastname,userID,))
    elif choice == 3:
      email = add_email() # change their email
      cursor.execute("UPDATE Users Set Email =? WHERE UserID = ?", (email,userID,))
    elif choice >= 4:
      define_error(4)
    elif choice <= -1:
      define_error(3)
    elif choice == 0:
      return

def get_firstname(): # a repeatablke function that gets a users first name as an input
 while True:
   try:
     print("")
     firstname = str(input("Enter Firstname: "))
     print(f"Entered Name {firstname}")
     print("")
     return firstname
   except ValueError:
     define_error(9)

def get_lastname(): # a repeatablke function that gets a users last name as an input
 while True:
   try:
     print("")
     lastname = str(input("Enter lastname: "))
     print(f"Entered Name {lastname}")
     print("")
     return lastname
   except ValueError:
     define_error(9)

def add_accountname(): # a repeatablke function that gets a users account name as an input
 while True:
   try:
     print("")
     accountname = str(input("Enter Account Name: "))
     print(f"Entered Account Name {accountname}")
     print("")
     return accountname
   except ValueError:
     define_error(9)

def add_password(): # a repeatablke function that gets a password as an input
 while True:
   try:
     print("")
     password = str(input("Enter Password: "))
     print(f"Entered Password {password}")
     print("")
     return password
   except ValueError:
     define_error(9)

def add_email(): # a repeatablke function that gets a email as an input
   while True:
    try:
      print("")
      email = str(input("Enter Email: "))
      print(f"Entered Email {email}")
      print("")
      return email
    except ValueError:
      define_error(9)

def view_accounts(): # a repeatable function that shows all account data with exeption of password & edit access.
  conn = get_connection()
  cursor = conn.cursor()
  print("")
  cursor.execute("SELECT Accounts.AccountID, Accounts.AccountName, Accounts.JoinDate, Accounts.UserID, Users.Email FROM Accounts JOIN Users ON Accounts.UserID = Users.UserID ORDER BY Accounts.AccountID ASC")
  accounts = cursor.fetchall()
  print(accounts)
  print("Hello")

def view_cards(): # a repeatable function that shows all card data
  conn = get_connection()
  cursor = conn.cursor()
  print("")
  cursor.execute("SELECT * FROM Cards ORDER BY CardID ASC")
  cards =cursor.fetchall()
  print(cards)

def view_collections(): # a repeatable function that shows all collection data
  conn = get_connection()
  cursor = conn.cursor()
  print("")
  cursor.execute("SELECT * FROM Collections ORDER BY CollectionID ASC")
  collections =cursor.fetchall()
  print(collections)

def view_listings(): # a repeatable function that shows all listing data
  conn = get_connection()
  cursor = conn.cursor()
  print("")
  cursor.execute("SELECT * FROM Listings ORDER BY ListingID ASC")
  listings =cursor.fetchall()
  print(listings)

def admin_panel(accountID): # the function that allows and admin to edit most tables in the database
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT EditAccess FROM Accounts WHERE AccountID = ?", (accountID,)) # we get the users editaccess
  rows = cursor.fetchall()
  cleanup1 = str(rows)
  cleanup2 = cleanup1.replace("[(","")
  cleanup3 = cleanup2.replace(",)]","")
  editaccess = int(cleanup3)
  if editaccess == 0: # if a users edit access is false,
    print("") # they cant use the admin panel
    print("Unable to enter admin panel.") # and are informed so
    print("You are not an admin.")
    return
  else: # other wise
    while True:
      view_cards() # we show them the current stat of Cards, Collections and Listings
      view_collections()
      view_listings()
      print("") # and ask what they would like to do
      print("Change Cards: 1")
      print("Change Collections: 2")
      print("Change Listings: 3")
      print("Return: 0")
      choice = get_choice()
      if choice == 1:
        change_cards()
      elif choice == 2:
        change_collections()
      elif choice == 3:
        change_listings()
      elif choice >= 4:
        define_error(4)
      elif choice <= -1:
        define_error(3)
      elif choice == 0:
        return

def change_cards(): # a function that alows a user to insert, updat and delete data from the Cards table
  conn = get_connection()
  cursor = conn.cursor()
  view_cards() # show the state of the cards table
  print("")
  print("Add card: 1")
  print("Update card: 2")
  print("Delete Card")
  while True:
    choice = get_choice()
    if choice == 1:
      print("")
      print("Add card.")
      cardname = get_cardname() # get the name of a card as an input
      game = get_game() # get game the card is from as an input
      cardvalue = get_cardvalue() # get the value of the card
      cursor.execute("INSERT INTO Cards(CardName, Game, Price) VALUES(?,?,?)", (cardname,game,cardvalue)) # add it to the database
      conn.commit()
    elif choice == 2:
      print("")
      print("Update card.")
      cardname = get_cardname()
      game = get_game()
      cardvalue = get_cardvalue()
      cardID = get_cardID() # get cardID as a varible
      cursor.execute("SELECT * FROM Cards WHERE CardID = ?"(cardID,))
      rows = cursor.fetchall()
      if rows == checkisblank: # check theirs a card with thsi card id
        print("Their isnt a Card with this ID") # if so dont update the database
      else: # otherwise update the database
        cursor.execute("UPDATE Cards SET CardName = ?, Game = ?, CardValue = ? WHERE CardID = ?", (cardname,game,cardvalue,cardID))
        conn.commit()
    elif choice == 3:
      print("")
      print("Delete card.")
      cardID = get_cardID()
      cursor.execute("SELECT * FROM Cards WHERE CardID = ?"(cardID,))
      rows = cursor.fetchall()
      if rows == checkisblank: # check theirs a card with thsi card id
        print("Their isnt a Card with this ID")# if so dont delete any data from the database
      else:# otherwise the data from the database
        cursor.execute("DELETE FROM Cards WHERE CardID = ?,"(cardID))
        conn.commit()
    elif choice >= 4:
      define_error(4)
    elif choice <= -1:
      define_error(3)
    elif choice == 0:
      return

def get_cardname(): # a repeatable function that returns card name as an input
   while True:
    try:
      print("")
      cardname = str(input("Enter Cardname: "))
      print(f"Entered Cardname {cardname}")
      print("")
      return cardname
    except ValueError:
      define_error(9)

def get_game(): # a repeatable function that returns game as an input
   while True:
    try:
      print("")
      game = str(input("Enter Game: "))
      print(f"Entered cardname {game}")
      print("")
      return game
    except ValueError:
      define_error(9)

def get_cardvalue():# a repeatable function that returns card value as an input
   while True:
    try:
      print("")
      cardvalue = float(input("Enter Card Value: "))
      print(f"Entered Card Value {cardvalue}")
      print("")
      return cardvalue
    except ValueError:
      define_error(2)

def change_collections(): # works the same as change_cards but for collections
  checkisblank = []
  conn = get_connection()
  cursor = conn.cursor()
  view_cards() # show the state of the collections table
  print("")
  print("Add Collection: 1")
  print("Update Collection: 2")
  print("Delete Collection")
  while True:
    choice = get_choice()
    if choice == 1:
      print("")
      print("Add collection.")
      accountID = get_accountID()
      cardID = get_cardID()
      quantity = get_quantity()
      today = date.today()
      formatted_date = today.strftime("%d-%m-%Y")
      cursor.execute("INSERT INTO Collections(AccountID, CardID, Quantity, LastUpdated) VALUES(?,?,?,?)", (accountID,cardID,quantity,formatted_date))
      conn.commit()
    elif choice == 2:
      print("")
      print("Update Collection.")
      accountID = get_accountID()
      cardID = get_cardID()
      quantity = get_quantity()
      today = date.today()
      formatted_date = today.strftime("%d-%m-%Y")
      collectionID = get_collectionID()
      cursor.execute("SELECT * FROM Collections WHERE CollectionID = ?"(collectionID,))
      rows = cursor.fetchall()
      if rows == checkisblank:
        print("Their isnt a Collection with this ID")
      else:
        cursor.execute("UPDATE Collection SET AccountID = ?, CardID = ?, Quantity = ?, LastUpdated = ?  WHERE CollectionID = ?", (accountID,cardID,quantity,formatted_date,collectionID))
        conn.commit()
    elif choice == 3:
      print("")
      print("Delete Collection.")
      collectionID = get_collectionID()
      cursor.execute("SELECT * FROM Collections WHERE CollectionID = ?"(collectionID,))
      rows = cursor.fetchall()
      if rows == checkisblank:
        print("Their isnt a Collection with this ID")
      else:
        cursor.execute("DELETE FROM Collections WHERE CollectionID = ?,"(collectionID))
        conn.commit()
    elif choice >= 4:
      define_error(4)
    elif choice <= -1:
      define_error(3)
    elif choice == 0:
      return

def get_quantity(): #get quantity and return it as an input
   while True:
    try:
      print("")
      quantity = int(input("Enter Quantity: "))
      print(f"Entered Cardname {quantity}")
      print("")
      return quantity
    except ValueError:
      define_error(1)

def get_cardID(): #get card id and return it as an input
  while True:
    try:
      print("")
      cardID = int(input("Enter CardID: "))
      print(f"Entered Card Value {cardID}")
      print("")
      return cardID
    except ValueError:
      define_error(1)

def get_accountID(): #get account id and return it as an input
  while True:
    try:
      print("")
      accountID = int(input("Enter AccountID: "))
      print(f"Entered Card Value {accountID}")
      print("")
      if accountID <= 0:
        define_error(4)
      else:
        return accountID
    except ValueError:
      define_error(1)

def get_collectionID(): #get collection id and return it as an input
  while True:
    try:
      print("")
      collectionID = int(input("Enter CollectionID: "))
      print(f"Entered Card Value {collectionID}")
      print("")
      if collectionID <= 0:
        define_error(4)
      else:
        return collectionID
    except ValueError:
      define_error(1)

def get_listingID(): #get listings id and return it as an input
  while True:
    try:
      print("")
      listingID = int(input("Enter ListingID: "))
      print(f"Entered Card Value {listingID}")
      print("")
      if listingID <= 0:
        define_error(4)
      else:
        return listingID
    except ValueError:
      define_error(1)

def change_listings(): # works the same as change_cards and change_collections but for listings
  checkisblank = []
  conn = get_connection()
  cursor = conn.cursor()
  view_listings() # show the state of the listings table
  print(rows)
  print("")
  print("Add Listing: 1")
  print("Update Listing: 2")
  print("Delete Listing")
  while True:
    choice = get_choice()
    if choice == 1:
      print("")
      print("Add Listing.")
      accountID = get_accountID
      cardID = get_cardID()
      listingtype = input("Enter Listing Type (Sell, trade, etc.): ")
      quantity = get_quantity()
      status = input("Enter Lising Status (Open, Closed, etc.); ")
      today = date.today()
      formatted_date = today.strftime("%d-%m-%Y")
      cursor.execute("INSERT INTO ListingS(AccountID, CardID, Listingtype, Quantity, Status, LastUpdated) VALUES(?,?,?,?)", (accountID,cardID,listingtype,quantity,status,formatted_date))
      conn.commit()
    elif choice == 2:
      print("")
      print("Update Lisitng.")
      accountID = get_accountID
      cardID = get_cardID()
      listingtype = input("Enter Listing Type (Sell, trade, etc.): ")
      quantity = get_quantity()
      status = input("Enter Lising Status (Open, Closed, etc.); ")
      today = date.today()
      formatted_date = today.strftime("%d-%m-%Y")
      lisitngID = get_ID()
      cursor.execute("SELECT * FROM Listings WHERE ListingID =?" (lisitngID,))
      rows = cursor.fetchall()
      if rows == checkisblank:
        print("Their isnt a listing with this ID")
      else:
        cursor.execute("UPDATE Listings SET AccountID = ?, CardID = ?, Listingtype = ?, Quantity = ?, Status = ?, LastUpdated = ? WHERE ListingID = ?", (accountID,cardID,listingtype,quantity,status,formatted_date,lisitngID))
        conn.commit()
    elif choice == 3:
      print("")
      print("Delete listing.")
      listingID = get_ID()
      cursor.execute("SELECT * FROM Listings WHERE ListingID =?" (lisitngID,))
      rows = cursor.fetchall()
      if rows == checkisblank:
        print("Their isnt a listing with this ID")
      else:
        cursor.execute("DELETE FROM Listings WHERE ListingID = ?,"(listingID))
        conn.commit()
    elif choice >= 4:
      define_error(4)
    elif choice <= -1:
      define_error(3)
    elif choice == 0:
      return


def create(): # a function that quickly inserts all the databases data into the database. USed when changing the file of the database or for recovery.
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("CREATE TABLE Users(UserID INTEGER PRIMARY KEY, FirstName TEXT NOT NULL, LastName TEXT NOT NULL, Email TEXT NOT NULL, PassKey TEXT NOT NULL)")
  conn.commit()
  cursor.execute("INSERT INTO USERS(FirstName,LastName,Email,PassKey) VALUES('Alex','Morgan','MorganAlex@email',4016)")
  conn.commit()
  cursor.execute("INSERT INTO USERS(FirstName,LastName,Email,PassKey) VALUES('Bob','Smith','SmithBob@email',2182)")
  conn.commit()
  cursor.execute("INSERT INTO USERS(FirstName,LastName,Email,PassKey) VALUES('Eva','Grace','GraceEva@email',0254)")
  conn.commit()
  cursor.execute("CREATE TABLE Accounts(AccountID INTEGER PRIMARY KEY, AccountName TEXT NOT NULL, JoinDate TEXT NOT NULL, Password TEXT NOT NULL, EditAccess BOOLEAN NOT NULL, UserID INTEGER, FOREIGN KEY (UserID) REFERENCES Users(UserID))")
  conn.commit()
  cursor.execute("INSERT INTO ACCOUNTS(AccountName,JoinDate,Password,EditAccess,UserID) VALUES('AdminTest1','20-10-2026','Admin1Password',1,1)")
  conn.commit()
  cursor.execute("INSERT INTO ACCOUNTS(AccountName,JoinDate,Password,EditAccess,UserID) VALUES('SleepyDeath','20-10-2026','Imt0L@zy',1,1)")
  conn.commit()
  cursor.execute("INSERT INTO ACCOUNTS(AccountName,JoinDate,Password,EditAccess,UserID) VALUES('SuperSmith','23-10-2026','BobWasHere!',0,2)")
  conn.commit()
  cursor.execute("INSERT INTO ACCOUNTS(AccountName,JoinDate,Password,EditAccess,UserID) VALUES('3V01UT10N','25-10-2026','EvesGrace',0,3)")
  conn.commit()
  cursor.execute("CREATE TABLE Cards(CardID INTEGER PRIMARY KEY, CardName TEXT NOT NULL, Game TEXT NOT NULL, CardValue FLOAT NOT NULL)")
  conn.commit()
  cursor.execute("INSERT INTO CARDS(CardName,Game,CardValue) VALUES('Sol Ring','Magic the Gathering',1.25)")
  conn.commit()
  cursor.execute("INSERT INTO CARDS(CardName,Game,CardValue) VALUES('Pot of Greed','Yu-Gi-Oh',5.35)")
  conn.commit()
  cursor.execute("INSERT INTO CARDS(CardName,Game,CardValue) VALUES('Arcane Signet','Magic the Gathering',0.8)")
  conn.commit()
  cursor.execute("CREATE TABLE Collections(CollectionID INTEGER PRIMARY KEY, AccountID INTEGER, CardID INTEGER, Quantity INTEGER NOT NULL, LastUpdated TEXT NOT NULL, FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID) FOREIGN KEY (CardID) REFERENCES Cards(CardID))")
  conn.commit()
  cursor.execute("INSERT INTO COLLECTIONS(AccountID,CardID,Quantity,LastUpdated) VALUES(2,3,5,26-10-2026)")
  conn.commit()
  cursor.execute("INSERT INTO COLLECTIONS(AccountID,CardID,Quantity,LastUpdated) VALUES(4,1,3,23-10-2026)")
  conn.commit()
  cursor.execute("INSERT INTO COLLECTIONS(AccountID,CardID,Quantity,LastUpdated) VALUES(3,2,1,25-10-2026)")
  conn.commit()
  cursor.execute("INSERT INTO COLLECTIONS(AccountID,CardID,Quantity,LastUpdated)VALUES(4,3,5,26-10-2026)")
  conn.commit()
  cursor.execute("CREATE TABLE Listings(LisitngID INTEGER PRIMARY KEY, AccountID INTEGER, CardID INTEGER, ListingType TEXT NOT NULL, Quantity INTEGER NOT NULL, Status TEXT NOT NULL, LastUpdated TEXT NOT NULL, FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID) FOREIGN KEY (CardID) REFERENCES Cards(CardID))")
  conn.commit()
  cursor.execute("INSERT INTO LISTINGS(AccountID,CardID,ListingType,Quantity,Status,LastUpdated) VALUES(2,1,'Selling',5,'Closed','26-10-2026')")
  conn.commit()
  conn.close()

# create() Was used to create the database quickly after the file change issue.
main()
