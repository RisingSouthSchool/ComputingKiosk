#!/usr/bin/env python3
import sqlite3
import os
import time
from datetime import datetime

# import sys


def get_connection():
    conn = sqlite3.connect("store.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


conn = get_connection()
cursor = conn.cursor()


def QOL(data):
    # print a nice little ------ line above the data, this corisponds to the row with the most characters so it fits nicely
    num = len(str(data))
    print(f"{"-" * num}")


def QOLext(
    data,
):  # an extended version of the function above, as these function may contain more than just the SQL values, they may contain strings
    num: int = len(str(data))
    print(f"-----{"-" * num}")


def fetchdata():
    results = cursor.fetchall()  # fetch all of the results in a given table
    count: int = 0

    if not results:
        print("No data found.")
        return

    QOL(results[0])  # gathers the data of row one in the database
    for row in results:
        print(f"{row}")  # print each row of data from SQL
    QOL(results[0])
    while count < 3:
        print(f".", end=" ", flush=True)
        count += 1
        time.sleep(1)


def fetchList():
    results = cursor.fetchall()
    n: int = 0

    if not results:
        print("No data found.")
        return

    QOLext(results[0])
    for row in results:
        # have n increase for each print of the for statement.
        print(f"{n+1}: {row}")
        n += 1
    QOLext(results[0])


def viewTables(requestedID, requestedTable):
    cursor.execute(f"""SELECT {requestedID} FROM {requestedTable}""")
    fetchList()

    cursor.execute(f"""SELECT {requestedID} FROM {requestedTable}""")
    allRows = cursor.fetchall()
    if not allRows:  # if theres no rows detected it returns false
        print("No data available.")
        return
    return allRows


# from the rows below, you might be like: "WeLl PaL, tHiS dAtAbAsE iSn'T sAfE bEcAuSe YoUr uSiNg f"" sTrIng, ThIs Is a MaJoR sEcUrItY cOncern!1!1" half yes and half no,
# the only infomation the user ACTUALLY gets to select is the deleteRow parameter. requestedID and requestedTable is already set inside the function, so the user is unable to select different types of tables.
# if what i say doesn't make sense, (most likely), just line: 645 and line: 668, that might make a little more sense


def viewData(requestedID, requestedTable):
    cursor.execute(
        f"""SELECT * FROM {requestedTable} ORDER BY {requestedID} ASC"""  # states that we're calling data from this table
    )
    fetchdata()  # calls the fetchdata() function to create the ------- bar from QOL() and print each row


def deleteDataRow(requestedID, requestedTable, deleteRow):
    cursor.execute(
        f"""DELETE FROM {requestedTable} WHERE {requestedID} = ?""", (deleteRow,)
    )
    conn.commit()  # makes it so that the data we delete stays permanant


def autoInsertPrimaryKey(requestedID, requestedTable):
    cursor.execute(f"""SELECT MAX({requestedID}) FROM {requestedTable}""")
    result = cursor.fetchone()[0]  # fetches the highest primary key

    # adds 1 to the current highest primary key
    valueOne = 1 if result is None else result + 1

    print(f"Automatic primary key selected: {valueOne}")
    return valueOne  # returns the primary key


# list of functions to validate data below


def validateEmail(email):
    if "@" not in email:  # checks to see if @ is in the email
        return False

    parts = email.split(
        "@"
        # splits the email into two to assess different parts (name and the rest after @)
    )

    if len(parts) != 2:  # if theres more then one @ it returns false
        return False

    if (
        "." not in parts[1]
    ):  # if therr is no . present in the second half of the email it returns false
        return False

    if parts[1].startswith(".") or parts[1].endswith(
        "."
    ):  # if it starts with or ends with . returns false
        return False

    return True


def validatePhone(phone):
    if any(
        not (char.isdigit() or char in " +()-")
        for char in phone
        # checks if the phone number is a digit, and allows +, -, () to pass through.
    ):
        return False

    digits = "".join(
        char for char in phone if char.isdigit()
    )  # removes all spaces and other symbols to count the length.

    if (
        len(digits) < 8 or len(digits) > 15
    ):  # if the length is below 8 or exceeds 15 returns false
        return False

    return True


def validateDate(date):
    try:
        datetime.strptime(
            date, "%d/%m/%Y"
        )  # checks to see if the input matches the date format
        return True
    except ValueError:
        return False


def validateEmptyTable(table):
    if not table:  # if there are no rows detected it returns false
        print("No data available.")
        return False

    return True


def validateRowChoice(table, choice):
    if not choice.isdigit():  # if the value is not a digit return false
        return False

    choice = int(choice)

    if choice < 1 or choice > len(
        table
    ):  # if the choice is larger than the amount of rows avalible, return false
        return False

    return True


def getInteger(prompt):
    while True:
        try:
            value = int(input(prompt))  # if the value is an int return the value
            return value
        except ValueError:  # if not return a ValueError
            print("Invalid value. Please enter an integer.")


def getNonNegativeInteger(prompt):
    while True:
        value = input(prompt).strip()

        if value.isdigit():
            return int(value)

        print("Unsupported value. Please enter a non-negative integer.")


def getBoolean(prompt):
    while True:
        value = input(prompt).strip()

        if value in (
            "0",
            "1",
        ):  # if value is a 1 or 0, return value, if not return error
            return int(value)

        print("Unsupported value. MUST BE 0 OR 1.")


def customerJoinPiano():
    # delcares what the data will be set as
    print(f"ORDERED BY: CustomerName, CustomerEmail, PianoModel and PurchaseDate")
    cursor.execute("""
        SELECT Customers.CustomerName, Customers.CustomerEmail, PianoInfomation.PianoModel, Purchases.PurchaseDate
        FROM Purchases
        JOIN PianoInfomation ON Purchases.PianoID = PianoInfomation.PianoID
        JOIN Customers ON Purchases.CustomerID = Customers.CustomerID
        ORDER BY PurchaseID ASC
    """)
    fetchdata()


def employeeJoin():
    print(
        f"ORDERED BY: EmployeeID, EmployeeName, EmployeeSales, PianoModel and PurchaseDate"
    )
    cursor.execute("""
        SELECT Employees.EmployeeID, Employees.EmployeeName, Employees.EmployeeSales, PianoInfomation.PianoModel, Purchases.PurchaseDate
        FROM Purchases
        JOIN Employees ON Purchases.EmployeeID = Employees.EmployeeID
        JOIN PianoInfomation ON Purchases.PianoID = PianoInfomation.PianoID
        ORDER BY Employees.EmployeeID ASC
    """)
    fetchdata()


def cashBackJoin():
    print(f"ORDERED BY: PurchaseID, PurchaseDate and CashBack (TRUE/FALSE, 1 = TRUE)")
    cursor.execute("""
        SELECT Purchases.PurchaseID, Purchases.PurchaseDate, PianoInfomation.CashBack
        FROM Purchases
        JOIN PianoInfomation ON Purchases.PianoID = PianoInfomation.PianoID
        ORDER BY PurchaseID ASC
    """)
    fetchdata()


def countSales():
    print(f"ORDERED BY: Total sales")
    cursor.execute("""
        SELECT COUNT(*) AS TotalPurchases
        FROM Purchases
    """)
    fetchdata()


def insertPianoInfomation():
    while True:
        try:
            querry = """
            INSERT OR IGNORE INTO PianoInfomation (PianoID, PianoModel, CashBack)
            VALUES (?, ?, ?);
            """

            # call the auto insert primary key function so the user doesn't create a duplicate or incorrect key
            valueOne = autoInsertPrimaryKey("PianoID", "PianoInfomation")

            valueTwo = input(f"Piano model: ").strip()

            if not valueTwo:
                print(f"Piano model cannot be empty.")
                continue

            valueThree = getBoolean(f"Is cashback supported? 1 for true 0 for false: ")

            confirm = input(f"\nConfirm Y/N: ").strip().upper()

            # if the user confirms by typing either y or Y, it inserts the values into the querry and saves the data.
            if confirm == "Y":
                insertValues = (valueOne, valueTwo, valueThree)

                cursor.execute(querry, insertValues)
                conn.commit()

                print(f"\nInserted values:")
                print(f"{valueOne, valueTwo, valueThree}\n")
                break

            elif confirm == "N":  # cancels the inserted data
                print(f"\nAction canceled.\n")
                break

            else:
                print(f"\nNot a valid option, try again.")
        except sqlite3.Error as error:
            conn.rollback()
            print(f"INSERT ERROR: {error}")


def insertCustomerInfomation():
    while True:
        try:
            querry = """
            INSERT OR IGNORE INTO Customers (CustomerID, CustomerName, CustomerEmail, CustomerPhone, CustomerNumberOfSales)
            VALUES (?, ?, ?, ?, ?);
            """

            valueOne = autoInsertPrimaryKey("CustomerID", "Customers")

            valueTwo = input(f"Customer's name: ").strip()

            if not valueTwo:
                print(f"Customer name cannot be empty.")
                continue

            valueThree = input(f"Customer's email: ").strip()

            # calls the validateEmail function to see if the inputted email matches the needed format
            if not validateEmail(valueThree):
                print(f"Invalid email. Please try again.")
                continue

            valueFour = input(f"Customer's phone number: ").strip()
            # calls the validatePhone function to see if the inputted phone number matches the needed format
            if not validatePhone(valueFour):
                print(f"Invalid phone. Please try again.\nFollow +NN NNN NNN NNN (N is the numbers)")
                continue

            valueFive = getNonNegativeInteger(
                f"Number of sales this customer has made: "
            )

            confirm = input(f"\nConfirm Y/N: ").strip().upper()

            if confirm == "Y":
                insertValues = (valueOne, valueTwo, valueThree, valueFour, valueFive)

                cursor.execute(querry, insertValues)
                conn.commit()

                print(f"\nInserted values:")
                print(f"{valueOne, valueTwo, valueThree, valueFour, valueFive}\n")
                break

            elif confirm == "N":
                print(f"\nAction canceled.\n")
                break

            else:
                print(f"\nNot a valid option, try again.\n")

        except sqlite3.Error as error:
            conn.rollback()
            print(f"INSERT ERROR: {error}")


def insertEmployeeInfomation():
    while True:
        try:
            querry = """
            INSERT OR IGNORE INTO Employees (EmployeeID, EmployeeName, EmployeeSales, EmployeeRole)
            VALUES (?, ?, ?, ?);
            """

            valueOne = autoInsertPrimaryKey("EmployeeID", "Employees")

            valueTwo = input(f"Employee name's: ").strip()

            if not valueTwo:
                print(f"Employee name cannot be empty.")
                continue

            valueThree = getNonNegativeInteger(f"Employee's sales made (INT ONLY): ")

            # lists a bunch of employee roles you can choose from.
            print(f"Employee's roles:\n")

            while (
                True
            ):  # while loop makes it so that valueFour is saved even when the loop breaks. i think
                print(f"1: Trainee")
                print(f"2: Salesman")
                print(f"3: Manager")

                choice = input(f"\nChoose an option: ")

                if choice == "1":
                    valueFour: str = "Trainee"
                    break
                elif choice == "2":
                    valueFour: str = "Salesman"
                    break
                elif choice == "3":
                    valueFour: str = "Manager"
                    break
                else:
                    print(f"\nUnsupported value. (PLEASE CHOOSE FROM 1 TO 3)\n")
                    continue

            confirm = input(f"\nConfirm Y/N: ").strip().upper()

            if confirm == "Y":
                insertValues = (valueOne, valueTwo, valueThree, valueFour)

                cursor.execute(querry, insertValues)
                conn.commit()

                print(f"\nInserted values:")
                print(f"{valueOne, valueTwo, valueThree, valueFour}\n")
                break

            elif confirm == "N":
                print(f"\nAction canceled.\n")
                break

            else:
                print(f"\nNot a valid option, try again.\n")

        except sqlite3.Error as error:
            conn.rollback()
            print(f"INSERT ERROR: {error}")


def insertPurchaseInfomation():
    while True:
        try:
            querry = """
            INSERT OR IGNORE INTO Purchases (PurchaseID, PianoID, EmployeeID, CustomerID, PurchaseDate)
            VALUES (?, ?, ?, ?, ?);
            """

            valueOne = autoInsertPrimaryKey("PurchaseID", "Purchases")

            print(f"\nChoose the purchased piano (PianoID)")

            allRows = viewTables("PianoID", "PianoInfomation")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"\nChoose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            valueTwo = int(choice) - 1

            print(f"Row chosen: {allRows[valueTwo]}")
            valueTwo = int(allRows[valueTwo][0])

            print(f"\nChoose the sales employee (EmployeeID)")

            allRows = viewTables("EmployeeID", "Employees")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"\nChoose an option (LISTED ABOVE): ").strip()

            # validates the row chosen actually exists
            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            # subtracts 1 to make up for the fact its using an array to select the row
            valueThree = int(choice) - 1

            # prints the row the user selected
            print(f"Row chosen: {allRows[valueThree]}")
            # makes valueThree the first element of the select row and converts it to an int. everything below is pretty much just the same as this
            valueThree = int(allRows[valueThree][0])

            print(f"\nChoose the purchasing customer (CustomerID)")

            allRows = viewTables("CustomerID", "Customers")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"\nChoose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            valueFour = int(choice) - 1

            print(f"Row chosen: {allRows[valueFour]}")
            valueFour = int(allRows[valueFour][0])

            valueFive: str = input(f"\nPurchasing date (DD/MM/YYYY): ").strip()
            # checks the date matches the correct format
            if not validateDate(valueFive):
                print(f"Invalid date. Use DD/MM/YYYY.\n")
                continue

            confirm = input(f"\nConfirm Y/N: ").strip().upper()

            if confirm.upper() == "Y":
                insertValues = (valueOne, valueTwo, valueThree, valueFour, valueFive)

                cursor.execute(querry, insertValues)
                conn.commit()

                print(f"\nInserted values:")
                print(f"{valueOne, valueTwo, valueThree, valueFour, valueFive}\n")
                break

            elif confirm == "N":
                print(f"\nAction canceled.\n")
                break

            else:
                print(f"\nNot a valid option, try again.\n")

        except sqlite3.Error as error:
            conn.rollback()
            print(f"INSERT ERROR: {error}")


def deletePianoInfomation():
    while True:
        try:
            allRows = viewTables("*", "PianoInfomation")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"\nChoose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            deleteRow = int(choice) - 1

            print(f"Row chosen: {allRows[deleteRow]}\n")
            deleteRow = int(allRows[deleteRow][0])

            confirm = (
                input(f"Confirm Y/N (WARNING: MAY DELETE PURCHASE ROW): ")
                .strip()
                .upper()
            )

            if confirm == "Y":
                # sends the desired row infomation to be deleted
                deleteDataRow("PianoID", "PianoInfomation", deleteRow)
                print(f"\nRow deleted.\n")
                break

            elif confirm == "N":
                print(f"\nAction canceled.\n")
                break

            else:
                print(f"\nNot a valid option, try again.")

        except sqlite3.Error as error:
            conn.rollback()
            print(f"DELETE ERROR: {error}")
            print("Check whether this piano is used in a purchase.")


def deleteCustomerInfomation():
    while True:
        try:
            allRows = viewTables("*", "Customers")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"\nChoose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            deleteRow = int(choice) - 1

            print(f"Row chosen: {allRows[deleteRow]}\n")
            deleteRow = int(allRows[deleteRow][0])

            confirm = (
                input(f"Confirm Y/N (WARNING: MAY DELETE PURCHASE ROW): ")
                .strip()
                .upper()
            )

            if confirm == "Y":
                deleteDataRow("CustomerID", "Customers", deleteRow)
                print(f"\nRow deleted.\n")
                break

            elif confirm == "N":
                print(f"\nAction canceled.\n")
                break

            else:
                print(f"\nNot a valid option, try again.")

        except sqlite3.Error as error:
            conn.rollback()
            print(f"DELETE ERROR: {error}")
            print("Check whether this customer has existing purchases.")


def deleteEmployeeInfomation():
    while True:
        try:
            allRows = viewTables("*", "Employees")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"\nChoose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            deleteRow = int(choice) - 1

            print(f"Row chosen: {allRows[deleteRow]}\n")
            deleteRow = int(allRows[deleteRow][0])

            confirm = (
                input(f"Confirm Y/N (WARNING: MAY DELETE PURCHASE ROW): ")
                .strip()
                .upper()
            )

            if confirm == "Y":
                deleteDataRow("EmployeeID", "Employees", deleteRow)
                print(f"\nRow deleted.\n")
                break

            elif confirm == "N":
                print(f"\nAction canceled.\n")
                break

            else:
                print(f"\nNot a valid option, try again.")

        except sqlite3.Error as error:
            conn.rollback()
            print(f"DELETE ERROR: {error}")
            print("Check whether this employee has existing purchases.")


def deletePurchaseInfomation():
    while True:
        try:
            allRows = viewTables("*", "Purchases")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"\nChoose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            selectedRow = allRows[int(choice) - 1]

            # the purchases has a composite primary key
            purchaseID = selectedRow[0]
            pianoID = selectedRow[1]

            confirm = input(f"Confirm Y/N: ").strip().upper()

            if confirm == "Y":
                cursor.execute(
                    """
                    DELETE FROM Purchases
                    WHERE PurchaseID = ? AND PianoID = ?
                    """,
                    (purchaseID, pianoID),
                )

                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"\nRow deleted.\n")
                break

            elif confirm == "N":
                print(f"\nAction canceled.\n")
                break

            else:
                print(f"\nNot a valid option, try again.")

        except sqlite3.Error as error:
            conn.rollback()
            print(f"DELETE ERROR: {error}")


def updatePianoInfomation():
    while True:
        try:
            querry = """
            UPDATE PianoInfomation
            SET PianoModel = ?, CashBack = ?
            WHERE PianoID = ?;
            """

            allRows = viewTables("*", "PianoInfomation")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"Choose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            updateRow = int(choice) - 1

            print(f"Row chosen: {allRows[updateRow]}")
            updateRow = int(allRows[updateRow][0])

            print(f"ID is: {updateRow}")

            valueTwo = input(f"Piano model: ").strip()

            if not valueTwo:
                print("Piano model cannot be empty.")
                continue

            valueThree = getBoolean(f"Is cashback supported? 1 for true 0 for false: ")

            confirm = input(f"\nConfirm Y/N: ").strip().upper()

            if confirm == "Y":
                updateValues = (
                    valueTwo,
                    valueThree,
                    updateRow,
                )

                cursor.execute(querry, updateValues)
                conn.commit()

                print(f"\nUpdated values:")
                print(f"{valueTwo, valueThree}\n")
                break

            elif confirm == "N":
                print(f"\nAction canceled.\n")
                break

            else:
                print(f"\nNot a valid option, try again.\n")
        except sqlite3.Error as error:
            conn.rollback()
            print(f"UPDATE ERROR: {error}")


def updateCustomerInfomation():
    while True:
        try:
            querry = """
            UPDATE Customers
            SET CustomerName = ?, CustomerEmail = ?, CustomerPhone = ?, CustomerNumberOfSales = ?
            WHERE CustomerID = ?;
            """

            allRows = viewTables("*", "Customers")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"Choose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            updateRow = int(choice) - 1

            print(f"Row chosen: {allRows[updateRow]}")
            updateRow = int(allRows[updateRow][0])

            print(f"ID is: {updateRow}")

            valueTwo = input(f"Customer's name: ").strip()

            if not valueTwo:
                print(f"Customer name cannot be empty.")
                continue

            valueThree = input(f"Customer's email: ").strip()

            if not validateEmail(valueThree):
                print(f"Invalid email. Please try again.")
                continue

            valueFour = input(f"Customer's phone number: ").strip()

            if not validatePhone(valueFour):
                print(f"Invalid phone. Please try again.\nFollow +NN NNN NNN NNN (N is the numbers)")
                continue

            valueFive = getNonNegativeInteger(
                f"Number of sales this customer has made: "
            )

            confirm = input(f"\nConfirm Y/N: ").strip().upper()

            if confirm == "Y":
                updateValues = (
                    valueTwo,
                    valueThree,
                    valueFour,
                    valueFive,
                    updateRow,
                )

                cursor.execute(querry, updateValues)
                conn.commit()

                print(f"\nUpdated values:")
                print(f"{valueTwo, valueThree, valueFour, valueFive}\n")
                break

            elif confirm == "N":
                print(f"\nAction canceled.\n")
                break

            else:
                print(f"\nNot a valid option, try again.\n")

        except sqlite3.Error as error:
            conn.rollback()
            print(f"UPDATE ERROR: {error}")


def updateEmployeeInfomation():
    while True:
        try:
            querry = """
            UPDATE Employees
            SET EmployeeName = ?, EmployeeSales = ?, EmployeeRole = ?
            WHERE EmployeeID = ?;
            """

            allRows = viewTables("*", "Employees")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"Choose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            updateRow = int(choice) - 1

            print(f"Row chosen: {allRows[updateRow]}")
            updateRow = int(allRows[updateRow][0])

            print(f"ID is: {updateRow}")

            valueTwo = input(f"Employee's name: ").strip()

            if not valueTwo:
                print(f"Employee name cannot be empty.")
                continue

            valueThree = getNonNegativeInteger(f"Employee's sales made (INT ONLY): ")

            print(f"Employee's roles:")

            while True:
                print(f"1: Trainee")
                print(f"2: Salesman")
                print(f"3: Manager")

                choice = input(f"\nChoose an option: ")

                if choice == "1":
                    valueFour: str = "Trainee"
                    break
                elif choice == "2":
                    valueFour: str = "Salesman"
                    break
                elif choice == "3":
                    valueFour: str = "Manager"
                    break
                else:
                    print(f"\nUnsupported value. (PLEASE CHOOSE FROM 1 TO 3)\n")
                    continue

            confirm = input(f"\nConfirm Y/N: ").strip().upper()

            if confirm == "Y":
                updateValues = (
                    valueTwo,
                    valueThree,
                    valueFour,
                    updateRow,
                )

                cursor.execute(querry, updateValues)
                conn.commit()

                print(f"\nUpdated values:")
                print(f"{valueTwo, valueThree, valueFour}\n")
                break

            elif confirm == "N":
                print(f"\nAction canceled.\n")
                break

            else:
                print(f"\nNot a valid option, try again.\n")

        except sqlite3.Error as error:
            conn.rollback()
            print(f"UPDATE ERROR: {error}")


def updatePurchaseInfomation():
    while True:
        try:
            querry = """
            UPDATE Purchases
            SET PianoID = ?, EmployeeID = ?, CustomerID = ?, PurchaseDate = ?
            WHERE PurchaseID = ? AND PianoID = ?;
            """

            allRows = viewTables("*", "Purchases")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"Choose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            selectedRow = allRows[int(choice) - 1]

            originalPurchaseID = selectedRow[0]
            originalPianoID = selectedRow[1]

            print(f"Row chosen: {selectedRow}")

            print(f"ID is: {originalPurchaseID}")

            print(f"\nChoose the purchased piano (PianoID)")

            allRows = viewTables("PianoID", "PianoInfomation")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"Choose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            valueTwo = int(choice) - 1

            print(f"Row chosen: {allRows[valueTwo]}")
            valueTwo = int(allRows[valueTwo][0])

            print(f"\nChoose the sales employee (EmployeeID)")

            allRows = viewTables("EmployeeID", "Employees")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"Choose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            valueThree = int(choice) - 1

            print(f"Row chosen: {allRows[valueThree]}")
            valueThree = int(allRows[valueThree][0])

            print(f"\nChoose the purchasing customer (CustomerID)")

            allRows = viewTables("CustomerID", "Customers")

            if not validateEmptyTable(allRows):
                break

            choice = input(f"Choose an option (LISTED ABOVE): ").strip()

            if not validateRowChoice(allRows, choice):
                print(f"\nPlease select a listed row.\n")
                continue

            valueFour = int(choice) - 1

            print(f"Row chosen: {allRows[valueFour]}")
            valueFour = int(allRows[valueFour][0])

            valueFive = input(f"\nPurchasing date (DD/MM/YYYY): ").strip()

            if not validateDate(valueFive):
                print(f"Invalid date. Use DD/MM/YYYY.\n")
                continue

            confirm = input(f"\nConfirm Y/N: ").strip().upper()

            if confirm == "Y":
                updateValues = (
                    valueTwo,
                    valueThree,
                    valueFour,
                    valueFive,
                    originalPurchaseID,
                    originalPianoID,
                )

                cursor.execute(querry, updateValues)
                conn.commit()

                print(f"\nUpdated values:")
                print(f"{valueTwo, valueThree, valueFour, valueFive}\n")
                break

            elif confirm == "N":
                print(f"\nAction canceled.\n")
                break

            else:
                print(f"\nNot a valid option, try again.\n")
        except sqlite3.Error as error:
            conn.rollback()
            print(f"UPDATE ERROR: {error}")


def insertData():
    while True:  # creates a loop
        print(f"Where would you like to insert data:")
        print(f"1: PianoInfomation")
        print(f"2: Customers")
        print(f"3: Employees")
        print(f"4: Purchases")
        print(f"5: Go back")

        choice = input(f"\nChoose an option: ")

        if choice == "1":
            insertPianoInfomation()
        elif choice == "2":
            insertCustomerInfomation()
        elif choice == "3":
            insertEmployeeInfomation()
        elif choice == "4":
            insertPurchaseInfomation()
        elif choice == "5":
            print(f"\nGoing back...\n")
            moreChoices()
            return
        else:
            print(f"\nNot a valid option, try again.\n")


def deleteData():
    while True:
        print(f"What table would you like to delete data from?")
        print(f"1: Piano inventory")
        print(f"2: Customer infomation")
        print(f"3: Employee infomation")
        print(f"4: Purchase infomation")
        print(f"5: Go back")

        choice = input(f"\nChoose an option: ")

        if choice == "1":
            deletePianoInfomation()
        elif choice == "2":
            deleteCustomerInfomation()
        elif choice == "3":
            deleteEmployeeInfomation()
        elif choice == "4":
            deletePurchaseInfomation()
        elif choice == "5":
            print(f"\nGoing back...\n")
            moreChoices()
            break
        else:
            print(f"\nNot a valid option, try again.\n")


def updateData():
    while True:
        print(f"Options listed: ")
        print(f"1: Update piano inventory")
        print(f"2: Update customer infomation")
        print(f"3: Update employee infomation")
        print(f"4: Update purchase infomation")
        print(f"5: Go back\n")

        choice = input(f"Choose an option: ")

        if choice == "1":
            updatePianoInfomation()
        elif choice == "2":
            updateCustomerInfomation()
        elif choice == "3":
            updateEmployeeInfomation()
        elif choice == "4":
            updatePurchaseInfomation()
        elif choice == "5":
            print(f"\nGoing back...\n")
            moreChoices()
            break
        else:
            print(f"\nNot a valid option, try again.\n")


def databaseJoins():
    while True:
        print(f"\nJoined and aggerate infomation: ")
        print(f"1: View customer infomation and customer bought pianos")
        print(f"2: View employees and types of pianos sold")
        print(f"3: View purchase, purchase date and whether or not cashback is valid")
        print(f"4: View total sales made")
        print(f"5: Go back\n")

        choice = input(f"Choose an option: ")

        if choice == "1":
            print(f"\nViewing customer infomation and customer bought pianos...\n")
            customerJoinPiano()
        elif choice == "2":
            print(f"\nViewing employees and types of pianos sold...\n")
            employeeJoin()
        elif choice == "3":
            print(
                f"\nViewing purchase, purchase date and whether or not cashback is valid...\n"
            )
            cashBackJoin()
        elif choice == "4":
            print(f"\nViewing total sales made...\n")
            countSales()
        elif choice == "5":
            print(f"\nGoing back...\n")
            return
        else:
            print(f"\nNot a valid option, try again.")


def moreChoices():
    while True:
        print(f"More choices: ")
        print(f"1: View joined and aggerate data")
        print(f"2: Insert more data")
        print(f"3: Delete data")
        print(f"4: Update data")
        print(f"5: Go back\n")

        choice = input(f"Choose an option: ")

        if choice == "1":
            print(f"\nViewing joined and aggerate data...")
            databaseJoins()
        elif choice == "2":
            print(f"\nOpening INSERT menu...\n")
            insertData()
        elif choice == "3":
            print(f"\nOpening DELETE menu...\n")
            deleteData()
        elif choice == "4":
            print(f"\nOpening UPDATE menu...\n")
            updateData()
        elif choice == "5":
            print(f"\nGoing back...")
            mainFunctions()
        else:
            print(f"\nNot a valid option, try again.")


def mainFunctions():
    while True:
        print(f"\nOptions listed: ")
        print(f"1: View piano inventory")
        print(f"2: View customer infomation")
        print(f"3: View employee infomation")
        print(f"4: View purchase infomation")
        print(f"5: View more options")
        print(f"6: End task\n")

        choice = input(f"Choose an option: ")

        if choice == "1":
            print(f"\nViewing piano inventory...\n")
            print(f"ORDERED BY: PianoID, PianoModel, CashBack (TRUE/FALSE, 1 = TRUE)")
            viewData("PianoID", "PianoInfomation")
        elif choice == "2":
            print(f"\nViewing customer infomation...\n")
            print(
                f"ORDERED BY: CustomerID, CustomerName, CustomerEmail, CustomerPhone, CustomerNumberOfPurchases"
            )
            viewData("CustomerID", "Customers")
        elif choice == "3":
            print(f"\nViewing employee infomation...\n")
            print(
                f"ORDERED BY: EmployeeID, EmployeeName, EmployeeNumberOfSales, EmployeeRole"
            )
            viewData("EmployeeID", "Employees")
        elif choice == "4":
            print(f"\nViewing purchase infomation...\n")
            print(
                f"ORDERED BY: PurchaseID, PianoID, EmployeeID, CustomerID, PurchaseDate"
            )
            viewData("PurchaseID", "Purchases")
        elif choice == "5":
            print(f"\nViewing more choices...\n")
            moreChoices()
            break
        elif choice == "6":
            print(f"\nGoodbye!\n")
            conn.commit()
            conn.close()
            # sys.exit() stupid except: functions kept calling when system tried closing, so database now exits at an OS level
            os._exit(0)
        else:
            print("\nNot a valid option, try again.")


def login():
    while True:
        print(f"User detected.\n")
        print(f"{"-" * 57}")
        print(f"| Guys, PLEASE stop forgetting the password, its: 55624 |")
        password: str = input(f"Password: ")
        count: int = 0
        while count < 3:
            print(f".", end=" ", flush=True)
            count += 1
            time.sleep(1)
        if password == "55624":  # could NOT be bothered doing this proper
            print(f"\nLogin successful!")
            print(f"{"-" * 57}")
            mainFunctions()
            break
        else:
            print(f"\nIncorrect password. Exiting.")
            print(f"{"-" * 57}")
            os._exit(1)
            break


try:
    login()

finally:
    conn.commit()
    conn.close()
    # sys.exit() stupid except: functions kept calling when system tried closing, so database now exits at an OS level
    os._exit(0)

# PRESENT BUGS (i think):
# INSERT OR IGNORE can ignore some inserted values without telling the user
# f"" strings may not be compatible in some other python versions (not changing, tuff luck mate, too many f"" strings present)
# os._exit() is not REALLY necessary, but i cant be bothered properly figuring out how to close the database
# security concern, password is present in login screen, but thats just to let you know the password to the database
# some possible data validation could be invalid, although this is just a theroey and hasn't been tested.

# used extention python formatter, so some parts might look better then others.

# to-do:
# fix data handling, check proper data like int ect, expand modular programming & parameter passing, pass insert, update, deletes through parameters

# sorry for the amount of lines, first time properly coding python
# also sorry for the amount of spelling mistakes, fixing them would take a lot of time for me
