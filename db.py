"""
db.py
All data access lives here, backed by CSV files instead of a database.

- data/yatra_slots_dataset.csv, data/flights_dataset.csv and
  data/users_dataset.csv are the static, checked-in datasets (built
  once by build_dataset.py).
- On first run, these are copied into "live" working CSVs
  (data/yatra_slots_live.csv, data/flights_live.csv, data/users_live.csv)
  with actual calendar dates computed from each row's day_offset. All
  searching, seat-decrementing, and new sign-ups happen against these
  live copies.
- data/bookings.csv stores completed (mock) bookings.

Function signatures match the previous SQLite version, so agent.py
and app.py don't need to change.

NOTE on auth: passwords are stored as plain SHA-256 hashes with no
per-user salt. That's fine for a local prototype/demo, but it is NOT
production-grade auth - a real deployment would need salted hashing
(e.g. bcrypt/argon2) and a real identity provider.
"""

import hashlib
import os
import uuid
from datetime import date, datetime, timedelta

import pandas as pd

DATA_DIR = "data"
YATRA_DATASET = f"{DATA_DIR}/yatra_slots_dataset.csv"
FLIGHTS_DATASET = f"{DATA_DIR}/flights_dataset.csv"
USERS_DATASET = f"{DATA_DIR}/users_dataset.csv"
YATRA_LIVE = f"{DATA_DIR}/yatra_slots_live.csv"
FLIGHTS_LIVE = f"{DATA_DIR}/flights_live.csv"
USERS_LIVE = f"{DATA_DIR}/users_live.csv"
BOOKINGS_FILE = f"{DATA_DIR}/bookings.csv"

BOOKINGS_COLUMNS = [
    "booking_id", "user_name", "pax_count", "yatra_slot_id", "flight_id",
    "total_price", "status", "created_at",
]
USERS_COLUMNS = ["username", "password_hash", "display_name", "created_at"]


def ensure_live_data():
    """Create the mutable 'live' CSVs from the static dataset CSVs on first run."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(YATRA_LIVE):
        df = pd.read_csv(YATRA_DATASET)
        today = date.today()
        df["slot_date"] = df["day_offset"].apply(lambda d: (today + timedelta(days=int(d))).isoformat())
        df = df.drop(columns=["day_offset"])
        df.to_csv(YATRA_LIVE, index=False)

    if not os.path.exists(FLIGHTS_LIVE):
        df = pd.read_csv(FLIGHTS_DATASET)
        today = date.today()
        df["flight_date"] = df["day_offset"].apply(lambda d: (today + timedelta(days=int(d))).isoformat())
        df = df.drop(columns=["day_offset"])
        df.to_csv(FLIGHTS_LIVE, index=False)

    if not os.path.exists(USERS_LIVE):
        if os.path.exists(USERS_DATASET):
            df = pd.read_csv(USERS_DATASET)
        else:
            df = pd.DataFrame(columns=USERS_COLUMNS)
        df.to_csv(USERS_LIVE, index=False)

    if not os.path.exists(BOOKINGS_FILE):
        pd.DataFrame(columns=BOOKINGS_COLUMNS).to_csv(BOOKINGS_FILE, index=False)


def search_yatra_slots(start_date, end_date, category=None, min_seats=1):
    ensure_live_data()
    df = pd.read_csv(YATRA_LIVE)
    mask = (df["slot_date"] >= start_date) & (df["slot_date"] <= end_date) & (df["seats_available"] >= min_seats)
    if category:
        mask &= df["category"] == category
    result = df[mask].sort_values(["slot_date", "price"])
    return result.to_dict("records")


def search_flights(origin, start_date, end_date, min_seats=1):
    ensure_live_data()
    df = pd.read_csv(FLIGHTS_LIVE)
    mask = (
        (df["origin"] == origin)
        & (df["flight_date"] >= start_date)
        & (df["flight_date"] <= end_date)
        & (df["seats_available"] >= min_seats)
    )
    result = df[mask].sort_values(["flight_date", "price"])
    return result.to_dict("records")


def get_distinct_origins():
    ensure_live_data()
    df = pd.read_csv(FLIGHTS_LIVE)
    return sorted(df["origin"].unique().tolist())


def create_booking(user_name, pax_count, yatra_slot_id, flight_id, total_price):
    """Creates a booking record and decrements seats in the live CSVs."""
    ensure_live_data()
    booking_id = "VD" + uuid.uuid4().hex[:8].upper()

    if yatra_slot_id:
        slots = pd.read_csv(YATRA_LIVE)
        idx = slots.index[slots["id"] == yatra_slot_id]
        if len(idx) and slots.loc[idx[0], "seats_available"] >= pax_count:
            slots.loc[idx[0], "seats_available"] -= pax_count
            slots.to_csv(YATRA_LIVE, index=False)

    if flight_id:
        flights = pd.read_csv(FLIGHTS_LIVE)
        idx = flights.index[flights["id"] == flight_id]
        if len(idx) and flights.loc[idx[0], "seats_available"] >= pax_count:
            flights.loc[idx[0], "seats_available"] -= pax_count
            flights.to_csv(FLIGHTS_LIVE, index=False)

    bookings = pd.read_csv(BOOKINGS_FILE)
    new_row = {
        "booking_id": booking_id,
        "user_name": user_name,
        "pax_count": pax_count,
        "yatra_slot_id": yatra_slot_id,
        "flight_id": flight_id,
        "total_price": total_price,
        "status": "CONFIRMED",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    bookings = pd.concat([bookings, pd.DataFrame([new_row])], ignore_index=True)
    bookings.to_csv(BOOKINGS_FILE, index=False)
    return booking_id


def get_booking(booking_id):
    ensure_live_data()
    bookings = pd.read_csv(BOOKINGS_FILE)
    row = bookings[bookings["booking_id"] == booking_id]
    if row.empty:
        return None
    b = row.iloc[0].to_dict()

    slots = pd.read_csv(YATRA_LIVE)
    flights = pd.read_csv(FLIGHTS_LIVE)

    if pd.notna(b.get("yatra_slot_id")):
        s = slots[slots["id"] == b["yatra_slot_id"]]
        if not s.empty:
            b.update({"slot_date": s.iloc[0]["slot_date"], "slot_time": s.iloc[0]["slot_time"], "category": s.iloc[0]["category"]})
    if pd.notna(b.get("flight_id")):
        f = flights[flights["id"] == b["flight_id"]]
        if not f.empty:
            b.update({
                "flight_no": f.iloc[0]["flight_no"], "airline": f.iloc[0]["airline"],
                "origin": f.iloc[0]["origin"], "destination": f.iloc[0]["destination"],
                "flight_date": f.iloc[0]["flight_date"], "departure_time": f.iloc[0]["departure_time"],
            })
    return b


def list_bookings(user_name=None):
    ensure_live_data()
    bookings = pd.read_csv(BOOKINGS_FILE)
    if bookings.empty:
        return []
    if user_name:
        bookings = bookings[bookings["user_name"] == user_name]
        if bookings.empty:
            return []
    slots = pd.read_csv(YATRA_LIVE)
    flights = pd.read_csv(FLIGHTS_LIVE)

    results = []
    for _, b in bookings.sort_values("created_at", ascending=False).iterrows():
        b = b.to_dict()
        if pd.notna(b.get("yatra_slot_id")):
            s = slots[slots["id"] == b["yatra_slot_id"]]
            if not s.empty:
                b["slot_date"] = s.iloc[0]["slot_date"]
                b["category"] = s.iloc[0]["category"]
        if pd.notna(b.get("flight_id")):
            f = flights[flights["id"] == b["flight_id"]]
            if not f.empty:
                b["flight_no"] = f.iloc[0]["flight_no"]
                b["origin"] = f.iloc[0]["origin"]
        results.append(b)
    return results


# ---------------------------------------------------------------------
# User accounts (demo auth for the login page)
# ---------------------------------------------------------------------

def _hash_pw(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(username, password, display_name):
    """Returns (True, None) on success, or (False, error_message) on failure."""
    ensure_live_data()
    username = username.strip().lower()
    if not username or not password:
        return False, "Username and password are required."
    users = pd.read_csv(USERS_LIVE)
    if (users["username"] == username).any():
        return False, "That username is already taken."
    new_row = {
        "username": username,
        "password_hash": _hash_pw(password),
        "display_name": display_name.strip() or username,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    users = pd.concat([users, pd.DataFrame([new_row])], ignore_index=True)
    users.to_csv(USERS_LIVE, index=False)
    return True, None


def verify_user(username, password):
    """Returns display_name if credentials match, else None."""
    ensure_live_data()
    username = username.strip().lower()
    users = pd.read_csv(USERS_LIVE)
    match = users[users["username"] == username]
    if match.empty:
        return None
    if match.iloc[0]["password_hash"] == _hash_pw(password):
        return match.iloc[0]["display_name"]
    return None
