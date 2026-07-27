"""
db.py
All database access lives here. These are the functions the agent
calls as its "tools". If real APIs or RPA automation are added later,
only the *internals* of these functions need to change - their
signatures and return shapes should stay the same so the agent layer
doesn't need to be touched.
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "data/yatra.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def search_yatra_slots(start_date, end_date, category=None, min_seats=1):
    """Return available yatra slots between two dates (inclusive), optionally filtered by category."""
    conn = get_conn()
    query = """
        SELECT * FROM yatra_slots
        WHERE slot_date BETWEEN ? AND ?
        AND seats_available >= ?
    """
    params = [start_date, end_date, min_seats]
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY slot_date, price ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_flights(origin, start_date, end_date, min_seats=1):
    """Return available flights from a city to Jammu between two dates."""
    conn = get_conn()
    query = """
        SELECT * FROM flights
        WHERE origin = ?
        AND flight_date BETWEEN ? AND ?
        AND seats_available >= ?
        ORDER BY flight_date, price ASC
    """
    rows = conn.execute(query, (origin, start_date, end_date, min_seats)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_distinct_origins():
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT origin FROM flights ORDER BY origin").fetchall()
    conn.close()
    return [r["origin"] for r in rows]


def create_booking(user_name, pax_count, yatra_slot_id, flight_id, total_price):
    """
    Creates a booking record (mock booking - no real payment or ticketing).
    Decrements available seats to simulate a real reservation system.
    """
    conn = get_conn()
    cur = conn.cursor()

    booking_id = "VD" + uuid.uuid4().hex[:8].upper()

    if yatra_slot_id:
        cur.execute(
            "UPDATE yatra_slots SET seats_available = seats_available - ? WHERE id = ? AND seats_available >= ?",
            (pax_count, yatra_slot_id, pax_count),
        )
    if flight_id:
        cur.execute(
            "UPDATE flights SET seats_available = seats_available - ? WHERE id = ? AND seats_available >= ?",
            (pax_count, flight_id, pax_count),
        )

    cur.execute(
        """INSERT INTO bookings
           (booking_id, user_name, pax_count, yatra_slot_id, flight_id, total_price, status, created_at)
           VALUES (?,?,?,?,?,?,?,?)""",
        (
            booking_id,
            user_name,
            pax_count,
            yatra_slot_id,
            flight_id,
            total_price,
            "CONFIRMED",
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()
    return booking_id


def get_booking(booking_id):
    conn = get_conn()
    row = conn.execute(
        """
        SELECT b.*, y.slot_date, y.slot_time, y.category,
               f.flight_no, f.airline, f.origin, f.destination, f.flight_date, f.departure_time
        FROM bookings b
        LEFT JOIN yatra_slots y ON b.yatra_slot_id = y.id
        LEFT JOIN flights f ON b.flight_id = f.id
        WHERE b.booking_id = ?
        """,
        (booking_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def list_bookings():
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT b.*, y.slot_date, y.category, f.flight_no, f.origin
        FROM bookings b
        LEFT JOIN yatra_slots y ON b.yatra_slot_id = y.id
        LEFT JOIN flights f ON b.flight_id = f.id
        ORDER BY b.created_at DESC
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
