"""
data_gen.py
Generates mock data for Vaishno Devi yatra slots and flights, and
initializes the SQLite database. This simulates what real APIs / RPA
scraping would eventually feed into the system - kept as a separate
module so swapping in real data sources later only means rewriting
this file, not the agent or UI.
"""

import sqlite3
import random
from datetime import date, timedelta

DB_PATH = "data/yatra.db"

YATRA_CATEGORIES = [
    ("Normal Darshan", 0, 500),      # (name, price, max_seats_per_slot)
    ("VIP Darshan", 500, 100),
    ("Helicopter Darshan", 3500, 40),
]

SLOT_TIMES = ["06:00", "09:00", "12:00", "15:00", "18:00"]

CITIES = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Ahmedabad"]
AIRLINES = ["IndiGo", "Air India", "SpiceJet", "Vistara"]
DEST = "Jammu"  # nearest airport to Vaishno Devi


def init_schema(conn):
    cur = conn.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS yatra_slots;
        DROP TABLE IF EXISTS flights;
        DROP TABLE IF EXISTS bookings;

        CREATE TABLE yatra_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_date TEXT NOT NULL,
            slot_time TEXT NOT NULL,
            category TEXT NOT NULL,
            price INTEGER NOT NULL,
            seats_available INTEGER NOT NULL
        );

        CREATE TABLE flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_no TEXT NOT NULL,
            airline TEXT NOT NULL,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            flight_date TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            price INTEGER NOT NULL,
            seats_available INTEGER NOT NULL
        );

        CREATE TABLE bookings (
            booking_id TEXT PRIMARY KEY,
            user_name TEXT,
            pax_count INTEGER,
            yatra_slot_id INTEGER,
            flight_id INTEGER,
            total_price INTEGER,
            status TEXT,
            created_at TEXT
        );
        """
    )
    conn.commit()


def generate_yatra_slots(conn, days_ahead=45):
    cur = conn.cursor()
    today = date.today()
    rows = []
    for d in range(days_ahead):
        slot_date = today + timedelta(days=d)
        for cat_name, price, max_seats in YATRA_CATEGORIES:
            for t in SLOT_TIMES:
                # Helicopter slots are rarer (fewer time slots realistically)
                if cat_name == "Helicopter Darshan" and t not in ["09:00", "12:00"]:
                    continue
                seats = random.randint(int(max_seats * 0.1), max_seats)
                rows.append((slot_date.isoformat(), t, cat_name, price, seats))
    cur.executemany(
        "INSERT INTO yatra_slots (slot_date, slot_time, category, price, seats_available) VALUES (?,?,?,?,?)",
        rows,
    )
    conn.commit()


def generate_flights(conn, days_ahead=45):
    cur = conn.cursor()
    today = date.today()
    rows = []
    flight_counter = 100
    for d in range(days_ahead):
        flight_date = today + timedelta(days=d)
        for city in CITIES:
            # 1-2 flights per city per day
            for _ in range(random.choice([1, 1, 2])):
                airline = random.choice(AIRLINES)
                flight_no = f"{airline[:2].upper()}{flight_counter}"
                flight_counter += 1
                dep_hour = random.randint(5, 20)
                price = random.randint(3200, 9500)
                seats = random.randint(0, 180)
                rows.append(
                    (
                        flight_no,
                        airline,
                        city,
                        DEST,
                        flight_date.isoformat(),
                        f"{dep_hour:02d}:00",
                        price,
                        seats,
                    )
                )
    cur.executemany(
        """INSERT INTO flights
           (flight_no, airline, origin, destination, flight_date, departure_time, price, seats_available)
           VALUES (?,?,?,?,?,?,?,?)""",
        rows,
    )
    conn.commit()


def build_database():
    import os

    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_schema(conn)
    generate_yatra_slots(conn)
    generate_flights(conn)
    conn.close()
    print(f"Database built at {DB_PATH}")


if __name__ == "__main__":
    build_database()
