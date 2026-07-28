"""
build_dataset.py
Generates the two master CSV datasets used by the app:
  - data/yatra_slots_dataset.csv
  - data/flights_dataset.csv

These are checked-in, static CSV files (the actual "dataset" for the
project) rather than randomly regenerated on every run. Only the
calendar date is computed at load-time (see db.py), using a
`day_offset` column so the dataset stays usable regardless of when
the app is actually run.

Prices are grounded in real, researched figures where public data
exists; seat *availability* is simulated, because no public dataset
or API anywhere publishes real-time yatra slot or airline seat
inventory (this is proprietary/gated data - see README "Data Sources"
section for full sourcing notes).

Run this once to (re)build the dataset:
    python build_dataset.py
"""

import csv
import random

DAYS_AHEAD = 45

# --- Yatra slot categories: real, researched prices ---
# Normal Darshan: yatra registration is officially free (Shrine Board, 2026)
# VIP/Special Darshan: ~Rs 500, widely cited across pilgrimage sites
#   (not an official Shrine Board rate card figure - flagged as approximate)
# Helicopter Darshan: Rs 4,640 round-trip, official Shrine Board rate,
#   Katra-Sanjichhat route, revised Oct 2025 (verified, current for 2026)
YATRA_CATEGORIES = [
    # (category, price, max_seats_per_slot)
    ("Normal Darshan", 0, 500),
    ("VIP Darshan", 500, 100),
    ("Helicopter Darshan", 4640, 40),
]
SLOT_TIMES = ["06:00", "09:00", "12:00", "15:00", "18:00"]

# --- Flights: no public dataset covers Jammu specifically (checked  ---
# Kaggle's major India flight-price datasets - Easemytrip ~300k rows,
# 2019 Jet Airways-era set - only cover the 6 biggest metro-to-metro
# routes). Price ranges below are calibrated against those real
# datasets' typical domestic fare patterns, tiered roughly by distance
# from Jammu, rather than pure guesswork.
CITIES = {
    # city: (airline pool bias not used directly, price range Rs)
    "Delhi": (3200, 6500),       # closest, budget-carrier heavy
    "Mumbai": (4200, 8500),
    "Bangalore": (4800, 9200),
    "Chennai": (5200, 9500),
    "Kolkata": (4500, 9000),
    "Ahmedabad": (3800, 7500),
}
AIRLINES = ["IndiGo", "Air India", "SpiceJet", "Vistara"]
DEST = "Jammu"


def build_yatra_slots_dataset(path="data/yatra_slots_dataset.csv"):
    rows = []
    slot_id = 1
    for d in range(DAYS_AHEAD):
        for cat_name, price, max_seats in YATRA_CATEGORIES:
            for t in SLOT_TIMES:
                if cat_name == "Helicopter Darshan" and t not in ["09:00", "12:00"]:
                    continue  # heli only flies limited daily windows, weather permitting
                seats = random.randint(int(max_seats * 0.1), max_seats)
                rows.append([slot_id, d, t, cat_name, price, seats])
                slot_id += 1

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "day_offset", "slot_time", "category", "price", "seats_available"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def build_flights_dataset(path="data/flights_dataset.csv"):
    rows = []
    flight_id = 1
    flight_counter = 100
    for d in range(DAYS_AHEAD):
        for city, (lo, hi) in CITIES.items():
            for _ in range(random.choice([1, 1, 2])):
                airline = random.choice(AIRLINES)
                flight_no = f"{airline[:2].upper()}{flight_counter}"
                flight_counter += 1
                dep_hour = random.randint(5, 20)
                price = random.randint(lo, hi)
                seats = random.randint(0, 180)
                rows.append(
                    [flight_id, d, flight_no, airline, city, DEST, f"{dep_hour:02d}:00", price, seats]
                )
                flight_id += 1

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["id", "day_offset", "flight_no", "airline", "origin", "destination", "departure_time", "price", "seats_available"]
        )
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    import os

    os.makedirs("data", exist_ok=True)
    build_yatra_slots_dataset()
    build_flights_dataset()
