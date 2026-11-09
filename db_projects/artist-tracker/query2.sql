-- CREATE TABLE Artist (
--     ArtistID INTEGER PRIMARY KEY,
--     ArtistName TEXT NOT NULL,
--     Nationality TEXT NOT NULL,
--     Genre TEXT
-- )

-- CREATE TABLE Collaboration (
--     ArtistID INTEGER PRIMARY KEY,
--     TrackID INTEGER PRIMARY KEY,
--     Contribution TEXT NOT NULL,
-- )

-- CREATE TABLE Track (
--     TrackID INTEGER PRIMARY KEY,
--     AlbumID INTEGER NOT NULL,
--     TrackName TEXT NOT NULL,
--     Duration TEXT NOT NULL,
--     ReleaseDate, TEXT NOT NULL
-- )

-- CREATE TABLE Album (
--     AlbumID INTEGER PRIMARY KEY,
--     AlbumName TEXT NOT NULL,
--     ReleaseDate TEXT NOT NULl
-- )

-- INSERT INTO Artist (ArtistID, ArtistName, Nationality, Genre)
-- VALUES (001, 'Ye', 'American', 'Hip Hop')

-- INSERT INTO Artist (ArtistID, ArtistName, Nationality, Genre)
-- VALUES (002, 'Drake', 'Canadian', 'RNB')


-- INSERT INTO Artist (ArtistID, ArtistName, Nationality, Genre)
-- VALUES (003, 'Travis Scott', 'American', 'Hip Hop')


-- INSERT INTO Artist (ArtistID, ArtistName, Nationality, Genre)
-- VALUES (004, 'Playboi Carti', 'American', 'Rage')

-- INSERT INTO Artist (ArtistID, ArtistName, Nationality, Genre)
-- VALUES (005, 'The Weeknd', 'Canadian', 'RNB')

-- INSERT INTO Artist (ArtistID, ArtistName, Nationality, Genre)
-- VALUES (006, '2Slimey', 'Mexican', 'Rage')

-- INSERT INTO Artist (ArtistID, ArtistName, Nationality, Genre)
-- VALUES (007, 'A$AP Rocky', 'American', 'Cloud Rap')

-- INSERT INTO Artist (ArtistID, ArtistName, Nationality, Genre)
-- VALUES (008, 'Yeat', 'American', 'Rage')

-- INSERT INTO Artist (ArtistID, ArtistName, Nationality, Genre)
-- VALUES (009, 'Future', 'American', 'Trap')

-- INSERT INTO Artist (ArtistID, ArtistName, Nationality, Genre)
-- VALUES (010, 'Don Toliver', 'American', 'Hip Hop')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (001, 'Yeezus', '18-06-2013')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (002, 'Rodeo', '04-09-2015')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (003, 'MBDTF', '22-11-2010')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (004, 'Iceman', '15-05-2026')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (005, 'High Anxiety', '14-11-2025')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (006, 'Hardstone Psycho', '14-06-2024')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (007, 'Up 2 Me', '10-09-2021')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (008, 'HNDRXX', '27-07-2017')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (009, 'LONG.LIVE.A$AP', '15-01-2013')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (010, 'Starboy', '25-11-2016')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (011, 'Whole Lotta Red', '25-12-2020')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (012, 'Hurry Up Tomorrow', '31-01-2025')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (013, 'Late Registration', '30-08-2005')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (014, 'Lyfe', '9-11-2022')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (015, 'More Anxiety', '06-02-2026')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (016, 'Astroworld', '03-08-2018')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (017, 'Die Lit', '11-05-2018')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (018, 'I NEVER LIKED YOU', '29-04-2022')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (019, 'LIVE.LOVE.A$AP', '31-10-2011')

-- INSERT INTO Album (AlbumID, AlbumName, ReleaseDate)
-- VALUES (020, 'Take Care', '15-11-2011')

-- INSERT INTO Track (TrackID, AlbumID, TrackName, Duration, ReleaseDate)
-- VALUES (001, 016, 'Cant Say', '03:17', '03-08-2018')

-- ALTER TABLE Track DROP COLUMN TEXT;

-- INSERT INTO Track (TrackID, AlbumID, TrackName, Duration, ReleaseDate)
-- VALUES (002, 001, 'Hold My Liquor', '03:17', '18-06-2013')

-- INSERT INTO Track (TrackID, AlbumID, TrackName, Duration, ReleaseDate)
-- VALUES (003, 006, 'Purple Rain', '03:27', '14-06-2024')

-- INSERT INTO Track (TrackID, AlbumID, TrackName, Duration, ReleaseDate)
-- VALUES
-- (004, 001, 'Black Skinhead', '03:08', '18-06-2013'),
-- (005, 001, 'New Slaves', '04:16', '18-06-2013'),
-- (006, 001, 'Bound 2', '03:49', '18-06-2013'),

-- (007, 002, '90210', '05:39', '04-09-2015'),
-- (008, 002, 'Antidote', '04:22', '04-09-2015'),
-- (009, 002, '3500', '07:41', '04-09-2015'),

-- (010, 003, 'Runaway', '09:08', '22-11-2010'),
-- (011, 003, 'POWER', '04:52', '22-11-2010'),
-- (012, 003, 'Devil in a New Dress', '05:52', '22-11-2010'),

-- (013, 006, 'TORE UP', '02:06', '14-06-2024'),
-- (014, 006, 'BANDIT', '02:28', '14-06-2024'),
-- (015, 006, 'BROTHER STONE', '03:22', '14-06-2024'),

-- (016, 007, 'Money So Big', '02:40', '10-09-2021'),
-- (017, 007, 'Turban', '02:35', '10-09-2021'),
-- (018, 007, 'Get Busy', '02:38', '10-09-2021'),

-- (019, 008, 'My Collection', '04:15', '24-02-2017'),
-- (020, 008, 'Solo', '04:25', '24-02-2017'),

-- (021, 009, 'Goldie', '03:12', '15-01-2013'),
-- (022, 009, 'Fashion Killa', '03:56', '15-01-2013'),

-- (023, 010, 'Starboy', '03:50', '25-11-2016'),
-- (024, 010, 'Die For You', '04:20', '25-11-2016'),
-- (025, 010, 'Reminder', '03:39', '25-11-2016'),

-- (026, 011, 'Stop Breathing', '03:38', '25-12-2020'),
-- (027, 011, 'Sky', '03:13', '25-12-2020'),
-- (028, 011, 'Rockstar Made', '03:13', '25-12-2020'),

-- (029, 012, 'Timeless', '04:16', '31-01-2025'),
-- (030, 012, 'Cry For Me', '03:44', '31-01-2025'),

-- (031, 013, 'Gold Digger', '03:27', '30-08-2005'),
-- (032, 013, 'Touch the Sky', '03:57', '30-08-2005'),

-- (033, 014, 'Out the Way', '02:30', '09-09-2022'),
-- (034, 014, 'Talk', '02:54', '09-09-2022'),

-- (035, 016, 'SICKO MODE', '05:12', '03-08-2018'),
-- (036, 016, 'STARGAZING', '04:30', '03-08-2018'),
-- (037, 016, 'BUTTERFLY EFFECT', '03:10', '03-08-2018'),

-- (038, 017, 'Shoota', '02:33', '11-05-2018'),
-- (039, 017, 'R.I.P.', '03:12', '11-05-2018'),

-- (040, 018, 'WAIT FOR U', '03:09', '29-04-2022'),
-- (041, 018, 'PUFFIN ON ZOOTIEZ', '02:52', '29-04-2022'),

-- (042, 020, 'Marvins Room', '05:47', '15-11-2011'),
-- (043, 020, 'Headlines', '03:55', '15-11-2011');

-- DROP TABLE IF EXISTS Collaboration;
-- CREATE TABLE Collaboration (
--     ArtistID INTEGER NOT NULL,
--     TrackID INTEGER NOT NULL,
--     Contribution TEXT NOT NULL,
--     PRIMARY KEY (ArtistID, TrackID),
--     FOREIGN KEY (ArtistID) REFERENCES Artist(ArtistID),
--     FOREIGN KEY (TrackID) REFERENCES Track(TrackID)
-- );


INSERT INTO Collaboration (ArtistID, TrackID, Contribution)
VALUES
(001, 002, 'Main Artist'),
(001, 004, 'Main Artist'),
(001, 005, 'Main Artist'),
(001, 006, 'Main Artist'),
(001, 010, 'Main Artist'),
(001, 011, 'Main Artist'),
(001, 012, 'Main Artist'),
(001, 031, 'Main Artist'),
(001, 032, 'Main Artist'),

(002, 042, 'Main Artist'),
(002, 043, 'Main Artist'),
(002, 035, 'Featured Artist'),

(003, 001, 'Main Artist'),
(003, 007, 'Main Artist'),
(003, 008, 'Main Artist'),
(003, 009, 'Main Artist'),
(003, 035, 'Main Artist'),
(003, 036, 'Main Artist'),
(003, 037, 'Main Artist'),

(004, 026, 'Main Artist'),
(004, 027, 'Main Artist'),
(004, 028, 'Main Artist'),
(004, 038, 'Main Artist'),
(004, 039, 'Main Artist'),
(004, 029, 'Featured Artist'),

(005, 023, 'Main Artist'),
(005, 024, 'Main Artist'),
(005, 025, 'Main Artist'),
(005, 029, 'Main Artist'),
(005, 030, 'Main Artist'),

(007, 021, 'Main Artist'),
(007, 022, 'Main Artist'),

(008, 016, 'Main Artist'),
(008, 017, 'Main Artist'),
(008, 018, 'Main Artist'),
(008, 033, 'Main Artist'),
(008, 034, 'Main Artist'),

(009, 009, 'Featured Artist'),
(009, 040, 'Main Artist'),
(009, 041, 'Main Artist'),

(010, 001, 'Featured Artist'),
(010, 013, 'Main Artist'),
(010, 014, 'Main Artist'),
(010, 015, 'Main Artist');
