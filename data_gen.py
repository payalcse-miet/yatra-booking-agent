"""
data_gen.py
Kept as a thin compatibility layer so app.py's existing
`from data_gen import build_database` call keeps working.

On first run: builds the master CSV datasets (if not already present)
via build_dataset.py, then creates the live/mutable CSVs via db.py.
"""

import os

import build_dataset
import db


def build_database():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists("data/yatra_slots_dataset.csv"):
        build_dataset.build_yatra_slots_dataset()
    if not os.path.exists("data/flights_dataset.csv"):
        build_dataset.build_flights_dataset()
    if not os.path.exists("data/trains_dataset.csv"):
        build_dataset.build_trains_dataset()
    if not os.path.exists("data/buses_dataset.csv"):
        build_dataset.build_buses_dataset()
    if not os.path.exists("data/hotels_dataset.csv"):
        build_dataset.build_hotels_dataset()
    if not os.path.exists("data/users_dataset.csv"):
        build_dataset.build_users_dataset()
    db.ensure_live_data()


if __name__ == "__main__":
    build_database()
