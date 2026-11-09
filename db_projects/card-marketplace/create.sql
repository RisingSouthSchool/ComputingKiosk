CREATE TABLE Users(
    UserID INTEGER PRIMARY KEY,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Email TEXT NOT NULL,
    PassKey TEXT NOT NULL
);

INSERT INTO USERS(FirstName,LastName,Email,PassKey)
VALUES('Alex','Morgan','MorganAlex@email',4016)
;

INSERT INTO USERS(FirstName,LastName,Email,PassKey)
VALUES('Bob','Smith','SmithBob@email',2182)
;

INSERT INTO USERS(FirstName,LastName,Email,PassKey)
VALUES('Eva','Grace','GraceEva@email',0254)
;

CREATE TABLE Accounts(
    AccountID INTEGER PRIMARY KEY,
    AccountName TEXT NOT NULL,
    JoinDate TEXT NOT NULL,
    Password TEXT NOT NULL,
    EditAccess BOOLEAN NOT NULL,
    UserID INTEGER,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);


INSERT INTO ACCOUNTS(AccountName,JoinDate,Password,EditAccess,UserID)
VALUES('AdminTest1','20-10-2026','Admin1Password',1,1)
;

INSERT INTO ACCOUNTS(AccountName,JoinDate,Password,EditAccess,UserID)
VALUES('SleepyDeath','20-10-2026','Imt0L@zy',1,1)
;

INSERT INTO ACCOUNTS(AccountName,JoinDate,Password,EditAccess,UserID)
VALUES('SuperSmith','23-10-2026','BobWasHere!',0,2)
;

INSERT INTO ACCOUNTS(AccountName,JoinDate,Password,EditAccess,UserID)
VALUES('3V01UT10N','25-10-2026','EvesGrace',0,3)

CREATE TABLE Cards(
    CardID INTEGER PRIMARY KEY,
    CardName TEXT NOT NULL,
    Game TEXT NOT NULL,
    CardValue FLOAT NOT NULL
);

INSERT INTO CARDS(CardName,Game,CardValue)
VALUES('Sol Ring','Magic the Gathering',1.25)
;

INSERT INTO CARDS(CardName,Game,CardValue)
VALUES('Pot of Greed','Yu-Gi-Oh',5.35)
;

INSERT INTO CARDS(CardName,Game,CardValue)
VALUES('Arcane Signet','Magic the Gathering',0.8)
;

CREATE TABLE Collections(
    CollectionID INTEGER PRIMARY KEY,
    AccountID INTEGER,
    CardID INTEGER,
    Quantity INTEGER NOT NULL,
    LastUpdated TEXT NOT NULL,
    FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID)
    FOREIGN KEY (CardID) REFERENCES Cards(CardID)
);

INSERT INTO COLLECTIONS(AccountID,CardID,Quantity,LastUpdated)
VALUES(2,3,5,26-10-2026)
;
INSERT INTO COLLECTIONS(AccountID,CardID,Quantity,LastUpdated)
VALUES(4,1,3,23-10-2026)
;
INSERT INTO COLLECTIONS(AccountID,CardID,Quantity,LastUpdated)
VALUES(3,2,1,25-10-2026)
;
INSERT INTO COLLECTIONS(AccountID,CardID,Quantity,LastUpdated)
VALUES(4,3,5,26-10-2026)
;

CREATE TABLE Listings(
    LisitngID INTEGER PRIMARY KEY,
    AccountID INTEGER,
    CardID INTEGER,
    ListingType TEXT NOT NULL,
    Quantity INTEGER NOT NULL,
    Status TEXT NOT NULL,
    LastUpdated TEXT NOT NULL,
    FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID)
    FOREIGN KEY (CardID) REFERENCES Cards(CardID)
);


INSERT INTO COLLECTIONS(AccountID,CardID,ListingType,Quantity,Status,LastUpdated)
VALUES(2,1,'Selling',5,'Closed','26-10-2026')
;
