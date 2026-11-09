#!/usr/bin/env python3
import sqlite3
from pathlib import Path

database_path = Path(__file__).with_name("pedalboard.db")

def create_tables():
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Band (
        BandID TEXT PRIMARY KEY,
        BandName TEXT,
        Genre TEXT,
        ContactEmail TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Song (
        SongID TEXT PRIMARY KEY,
        SongTitle TEXT,
        TempoBPM INTEGER,
        TimeSignature TEXT,
        BandID TEXT,
        FOREIGN KEY (BandID) REFERENCES Band(BandID)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pedal (
        PedalID TEXT PRIMARY KEY,
        PedalName TEXT,
        Manufacturer TEXT,
        Type TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Song_Pedal_Setting (
        SongID TEXT,
        PedalID TEXT,
        ChainOrder INTEGER,
        KnobPreset TEXT,

        PRIMARY KEY (SongID, PedalID),

        FOREIGN KEY (SongID) REFERENCES Song(SongID),
        FOREIGN KEY (PedalID) REFERENCES Pedal(PedalID)
    )
    """)

    connection.commit()
    connection.close()

