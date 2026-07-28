"""
build_dataset.py
Generates the master CSV datasets used by the app:
  - data/yatra_slots_dataset.csv
  - data/flights_dataset.csv
  - data/users_dataset.csv   (demo login accounts)

These are checked-in, static CSV files rather than randomly regenerated
on every run. Only the calendar date is computed at load-time (see
db.py), using a `day_offset` column so the dataset stays usable
regardless of when the app is actually run.

Prices are grounded in real, researched figures where public data
exists; seat *availability* is simulated, because no public dataset
or API anywhere publishes real-time yatra slot or airline seat
inventory (this is proprietary/gated data - see README "Data Sources"
section for full sourcing notes).

Flight fare *ranges* and the airline/duration/stops structure are
calibrated against two public Kaggle domestic-fare datasets (the
2019 Jet-Airways-era Easemytrip set, and Muhammad Bin Imran's
"Flight Price Prediction" dataset) - neither covers Jammu routes
specifically, so exact per-route numbers are still synthetic within
realistic bounds. See README for details.

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
# Kaggle's major India flight-price datasets (Easemytrip ~300k rows,
# Jet-Airways-era set; also Muhammad Bin Imran's Flight Price Prediction
# set) only cover the biggest metro-to-metro routes. Price ranges below
# are calibrated against those real datasets' typical domestic fare
# patterns, tiered roughly by distance from Jammu.
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
                stops = random.choice([0, 0, 0, 1])  # mostly direct, some 1-stop
                duration = base_duration + (random.randint(60, 140) if stops else random.randint(-10, 15))
                price = random.randint(lo, hi)
                if stops:
                    price = int(price * 0.85)  # 1-stop fares tend to run a bit cheaper
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


def _hash_pw(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def build_users_dataset(path="data/users_dataset.csv"):
    """Seed demo login accounts, committed to the repo so the app is
    usable out of the box. Anyone can also sign up for a new account
    from the login page - those go into the gitignored 'live' copy."""
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
    build_users_dataset()
