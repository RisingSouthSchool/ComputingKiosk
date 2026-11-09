DROP TABLE IF EXISTS Menu;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Food;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Restaurant;

CREATE TABLE Restaurant(
    RestaurantID INTEGER PRIMARY KEY AUTOINCREMENT,
    Restaurant_Name TEXT NOT NULL,
    Address TEXT NOT NULL,
    Phone_Number TEXT
);

CREATE TABLE Customer(
    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
    First_Name TEXT NOT NULL,
    Last_Name TEXT NOT NULL,
    Phone_Number TEXT
);

CREATE TABLE Food(
    FoodID INTEGER PRIMARY KEY AUTOINCREMENT,
    Food_Name TEXT NOT NULL,
    Price REAL NOT NULL,
    Food_Description TEXT
);

CREATE TABLE Orders(
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    Order_Time TEXT,
    Order_Date TEXT,
    RestaurantID INTEGER,
    CustomerID INTEGER,
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
);


CREATE TABLE Menu(
    MenuID INTEGER PRIMARY KEY AUTOINCREMENT,
    Menu_Item TEXT NOT NULL,
    price REAL NOT NULL,
    FoodID INTEGER,
    FOREIGN KEY (FoodID) REFERENCES Food(FoodID)
);


CREATE TABLE Order_Items(
    OrderID INTEGER,
    MenuID INTEGER,
    Quantity INTEGER DEFAULT 1,
    PRIMARY KEY (OrderID, MenuID),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (MenuID) REFERENCES Menu(MenuID)
);


INSERT INTO Restaurant (Restaurant_Name, Address, Phone_Number)
VALUES ('Authentic_Italian_Pizza', '246 Rainboy St', '123-456');

INSERT INTO Customer (First_Name, Last_Name, Phone_Number) VALUES
('David', 'Malan', '123-457'),
('Mike', 'Hawk', '123-458'),
('Steve', 'Jobs', '123-459'),
('Mark', 'Sullovean', '123-460');

INSERT INTO Food (Food_Name, Price, Food_Description) VALUES
('Margherita Pizza', 14.00, 'Original Cheese and Tomato base with basil.'),
('Spaghetti Carabona', 16.50, 'Creamy pasta sauce with egg, hard cheese, fresh pork and black pepper.'),
('Fettucina Alfredo', 15.00, 'Rich fettuccine tossed with pure butter and Parmesean cheese.'),
('Garlic Bread', 6.00, 'Why do you need a description for this.'),
('Tiramisu', 8.00, 'coffee-flavoured Italian dessert dipped in coffee.');

INSERT INTO Menu (Menu_Item, price, FoodID) VALUES
('Margherita Pizza', 14.00, 1),   
('Spaghetti Carabona', 16.50, 2),
('Fettucina Alfredo', 15.00, 3),
('Garlic Bread', 6.00, 4),
('Tiramisu', 8.00, 5);


-- Cleaned up sample orders using valid IDs from references above
INSERT INTO Orders (Order_Time, Order_Date, RestaurantID, CustomerID) VALUES
('18:00:00', '2026-10-24', 1, 1),
('18:15:00', '2026-10-24', 1, 2);

