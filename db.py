"""
db.py
All data access lives here, backed by CSV files instead of a database.

- data/yatra_slots_dataset.csv and data/flights_dataset.csv are the
  static, checked-in datasets (built once by build_dataset.py).
- On first run, these are copied into "live" working CSVs
  (data/yatra_slots_live.csv, data/flights_live.csv) with actual
  calendar dates computed from each row's day_offset. All searching
  and seat-decrementing happens against these live copies.
- data/bookings.csv stores completed (mock) bookings.

Function signatures match the previous SQLite version, so agent.py
and app.py don't need to change.
"""

import os
import uuid
from datetime import date, timedelta

import pandas as pd

DATA_DIR = "data"
YATRA_DATASET = f"{DATA_DIR}/yatra_slots_dataset.csv"
FLIGHTS_DATASET = f"{DATA_DIR}/flights_dataset.csv"
YATRA_LIVE = f"{DATA_DIR}/yatra_slots_live.csv"
FLIGHTS_LIVE = f"{DATA_DIR}/flights_live.csv"
BOOKINGS_FILE = f"{DATA_DIR}/bookings.csv"

BOOKINGS_COLUMNS = [
    "booking_id", "user_name", "pax_count", "yatra_slot_id", "flight_id",
    "total_price", "status", "created_at",
]


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

    from datetime import datetime

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


def list_bookings():
    ensure_live_data()
    bookings = pd.read_csv(BOOKINGS_FILE)
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
