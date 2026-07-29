"""
build_dataset.py
Generates the master CSV datasets used by the app:
  - data/yatra_slots_dataset.csv
  - data/flights_dataset.csv
  - data/trains_dataset.csv
  - data/buses_dataset.csv
  - data/users_dataset.csv   (demo login accounts)

These are checked-in, static CSV files rather than randomly regenerated
on every run. Only the calendar date is computed at load-time (see
db.py), using a `day_offset` column so the dataset stays usable
regardless of when the app is actually run.

Prices are grounded in real, researched figures where public data
exists; seat *availability* is simulated, because no public dataset
or API anywhere publishes real-time yatra slot, airline, rail, or bus
seat inventory (this is proprietary/gated data - see README "Data
Sources" section for full sourcing notes).

Flight fare *ranges* and the airline/duration/stops structure are
calibrated against two public Kaggle domestic-fare datasets (the
2019 Jet-Airways-era Easemytrip set, and Muhammad Bin Imran's
"Flight Price Prediction" dataset) - neither covers Jammu routes
specifically, so exact per-route numbers are still synthetic within
realistic bounds. See README for details.

Trains and buses are grounded in real connectivity facts: Katra has
its own railway station (Shri Mata Vaishno Devi Katra, station code
SVDK, opened 2014) with direct trains from Delhi, Mumbai, Kolkata,
Chennai and Ahmedabad. Bangalore has no confirmed direct service, so
it is deliberately left out of the train dataset rather than invented.
Direct bus services to Katra are well-documented from Delhi; other
cities are left out for buses for the same reason. IRCTC fare classes
(Sleeper, 3AC, 2AC) and realistic journey durations are used for
train price tiers.

Run this once to (re)build the dataset:
    python build_dataset.py
"""

import csv
import hashlib
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

# --- Flights: no public dataset covers Jammu specifically (checked) ---
CITIES = {
    # city: (price_low, price_high, typical_duration_minutes)
    "Delhi": (3200, 6500, 95),
    "Mumbai": (4200, 8500, 165),
    "Bangalore": (4800, 9200, 195),
    "Chennai": (5200, 9500, 210),
    "Kolkata": (4500, 9000, 175),
    "Ahmedabad": (3800, 7500, 140),
}
AIRLINES = ["IndiGo", "Air India", "SpiceJet", "Vistara"]
DEST = "Jammu"

# --- Trains: real - Katra (SVDK) has direct rail links from these cities ---
# (city: (price_low, price_high for Sleeper/3AC/2AC tiers, typical duration hours))
# Bangalore intentionally excluded - no confirmed direct SVDK service found.
TRAIN_CITIES = {
    "Delhi": (700, 2400, 12),
    "Mumbai": (1400, 4200, 26),
    "Chennai": (1900, 5200, 42),
    "Kolkata": (1300, 3800, 32),
    "Ahmedabad": (1300, 3600, 27),
}
TRAIN_OPERATORS = ["Northern Railway", "Indian Railways"]
TRAIN_CLASSES = ["Sleeper", "3AC", "2AC"]

# --- Buses: real - regular direct bus services documented only from Delhi ---
BUS_CITIES = {
    "Delhi": (900, 2200, 14),
}
BUS_OPERATORS = ["J&K SRTC", "HRTC Volvo", "Private AC Sleeper"]

# --- Hotels in Katra: real, researched price tiers ---
# Budget: Rs 500-1500/night is well-documented across multiple booking
#   sites for basic pilgrim guest houses near the bus stand/market.
# Mid-Range: Rs 1800-4000/night, typical for 2-3 star AC hotels.
# Premium: Rs 5000-12000/night, matching known 4-5 star properties
#   (Holiday Inn Katra Vaishno Devi, Vivanta Katra, Welcomhotel-class).
# Property names below are generic/fictional - NOT copied from real
# hotel listings, since we have no real per-hotel room-inventory data;
# only the category price tiers are grounded in real research.
HOTEL_CATEGORIES = [
    ("Budget", 600, 1500),
    ("Mid-Range", 1800, 4000),
    ("Premium", 5000, 12000),
]
HOTEL_NAME_POOL = {
    "Budget": ["Trikuta Guest House", "Ban Ganga Comfort Stay", "Yatri Niwas Lodge", "Katra Bus Stand Inn"],
    "Mid-Range": ["Trikuta Residency", "Bhawan View Hotel", "Katra Heritage Inn", "Devi Darshan Hotel"],
    "Premium": ["Trikuta Hills Resort", "Vaishnavi Grand", "Katra Palace Hotel"],
}
ROOMS_PER_PROPERTY = {"Budget": 30, "Mid-Range": 20, "Premium": 12}

# --- Jammu <-> Katra taxi fares: real, researched (see explore_data.py) ---
# Kept here as a single source of truth in case build scripts need it;
# explore_data.py's TAXI_INFO mirrors these figures for display.
JAMMU_KATRA_TAXI_SEDAN = (1300, 2500)
JAMMU_KATRA_TAXI_SUV = (2500, 3800)



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
        for city, (lo, hi, base_duration) in CITIES.items():
            for _ in range(random.choice([1, 1, 2])):
                airline = random.choice(AIRLINES)
                flight_no = f"{airline[:2].upper()}{flight_counter}"
                flight_counter += 1
                dep_hour = random.randint(5, 20)
                stops = random.choice([0, 0, 0, 1])
                duration = base_duration + (random.randint(60, 140) if stops else random.randint(-10, 15))
                price = random.randint(lo, hi)
                if stops:
                    price = int(price * 0.85)
                seats = random.randint(0, 180)
                rows.append(
                    [flight_id, d, flight_no, airline, city, DEST, f"{dep_hour:02d}:00",
                     duration, stops, price, seats]
                )
                flight_id += 1

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["id", "day_offset", "flight_no", "airline", "origin", "destination",
             "departure_time", "duration_mins", "stops", "price", "seats_available"]
        )
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def build_trains_dataset(path="data/trains_dataset.csv"):
    rows = []
    train_id = 1
    number_counter = 12401
    for d in range(DAYS_AHEAD):
        for city, (lo, hi, base_hours) in TRAIN_CITIES.items():
            train_no = str(number_counter)
            number_counter += 1
            operator = random.choice(TRAIN_OPERATORS)
            dep_hour = random.choice([5, 7, 14, 17, 20, 22])
            duration_mins = int(base_hours * 60 + random.randint(-45, 60))
            for travel_class, mult in zip(TRAIN_CLASSES, [1.0, 1.9, 2.8]):
                price = int(random.randint(lo, hi) * mult / 2.8) if travel_class != "2AC" else random.randint(lo, hi)
                seats = random.randint(0, 72)
                rows.append(
                    [train_id, d, train_no, operator, travel_class, city, "Katra (SVDK)",
                     f"{dep_hour:02d}:00", duration_mins, price, seats]
                )
                train_id += 1

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["id", "day_offset", "train_no", "operator", "travel_class", "origin", "destination",
             "departure_time", "duration_mins", "price", "seats_available"]
        )
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def build_buses_dataset(path="data/buses_dataset.csv"):
    rows = []
    bus_id = 1
    for d in range(DAYS_AHEAD):
        for city, (lo, hi, base_hours) in BUS_CITIES.items():
            for _ in range(2):  # a couple of daily departures
                operator = random.choice(BUS_OPERATORS)
                dep_hour = random.choice([18, 19, 20, 21])
                duration_mins = int(base_hours * 60 + random.randint(-60, 90))
                price = random.randint(lo, hi)
                seats = random.randint(0, 40)
                rows.append(
                    [bus_id, d, operator, city, "Katra", f"{dep_hour:02d}:00", duration_mins, price, seats]
                )
                bus_id += 1

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["id", "day_offset", "operator", "origin", "destination",
             "departure_time", "duration_mins", "price", "seats_available"]
        )
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def build_hotels_dataset(path="data/hotels_dataset.csv"):
    rows = []
    hotel_id = 1
    for d in range(DAYS_AHEAD):
        for category, lo, hi in HOTEL_CATEGORIES:
            for name in HOTEL_NAME_POOL[category]:
                price = random.randint(lo, hi)
                max_rooms = ROOMS_PER_PROPERTY[category]
                rooms = random.randint(int(max_rooms * 0.1), max_rooms)
                # Rating is illustrative/sample data (no real per-hotel review
                # data exists publicly for these generic property names - see
                # README) but kept fixed per property name via a hash, so the
                # same hotel shows the same rating every day rather than a
                # new random number on every row.
                rating = 3.3 + (int(hashlib.md5(name.encode()).hexdigest(), 16) % 16) / 10  # 3.3-4.8
                rows.append([hotel_id, d, name, category, price, rooms, round(rating, 1)])
                hotel_id += 1

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "day_offset", "name", "category", "price_per_night", "rooms_available", "rating"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def _hash_pw(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def build_users_dataset(path="data/users_dataset.csv"):
    demo_users = [
        ("demo", "demo123", "Demo Pilgrim"),
        ("guest", "guest123", "Guest User"),
    ]
    rows = [[u, _hash_pw(p), name, "seed"] for u, p, name in demo_users]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["username", "password_hash", "display_name", "created_at"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} seed accounts to {path}")


if __name__ == "__main__":
    import os

    os.makedirs("data", exist_ok=True)
    build_yatra_slots_dataset()
    build_flights_dataset()
    build_trains_dataset()
    build_buses_dataset()
    build_hotels_dataset()
    build_users_dataset()
