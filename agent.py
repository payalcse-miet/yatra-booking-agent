"""
agent.py
The 'agent' brain: extracts trip details from either the dropdown
search form or a free-text request using simple rule-based parsing,
queries the mock database across all transport modes (flight/train/
bus), ranks combinations, and proposes options.
"""

import re
from datetime import date, timedelta

import db

ORIGIN_CITIES = ["delhi", "mumbai", "bangalore", "bengaluru", "chennai", "kolkata", "ahmedabad"]
CATEGORY_KEYWORDS = {
    "helicopter": "Helicopter Darshan",
    "heli": "Helicopter Darshan",
    "vip": "VIP Darshan",
    "normal": "Normal Darshan",
}
MODE_KEYWORDS = {
    "train": "train", "rail": "train", "railway": "train",
    "bus": "bus", "flight": "flight", "fly": "flight", "flying": "flight", "plane": "flight", "air": "flight",
}

MAX_OPTIONS = 3  # how many ranked combinations to show for review


def _extract_pax(text):
    m = re.search(r"(\d+)\s*(people|pax|person|persons|members|pilgrims)?", text.lower())
    if m:
        return max(1, int(m.group(1)))
    return 1


def _extract_origin(text):
    t = text.lower()
    for city in ORIGIN_CITIES:
        if city in t:
            return "Bangalore" if city == "bengaluru" else city.capitalize()
    return None


def _extract_category(text):
    t = text.lower()
    for kw, cat in CATEGORY_KEYWORDS.items():
        if kw in t:
            return cat
    return None


def _extract_mode(text):
    t = text.lower()
    for kw, mode in MODE_KEYWORDS.items():
        if kw in t:
            return mode
    return None  # no preference -> show a diversified mix


def _extract_date_range(text):
    t = text.lower()
    today = date.today()
    if "next week" in t:
        start = today + timedelta(days=7)
        end = start + timedelta(days=6)
    elif "this week" in t:
        start = today
        end = today + timedelta(days=6)
    elif "next month" in t:
        start = today + timedelta(days=30)
        end = start + timedelta(days=6)
    else:
        start = today
        end = today + timedelta(days=14)
    return start.isoformat(), end.isoformat()


def parse_request(text):
    """Rule-based extraction of a structured trip request from free text."""
    return {
        "pax": _extract_pax(text),
        "origin": _extract_origin(text),
        "category": _extract_category(text),
        "mode": _extract_mode(text),
        "start_date": _extract_date_range(text)[0],
        "end_date": _extract_date_range(text)[1],
    }


def _search_transport(request):
    """Searches whichever modes are relevant and returns one combined list."""
    origin, start, end, pax = request["origin"], request["start_date"], request["end_date"], request["pax"]
    mode = request.get("mode")

    searchers = {
        "flight": db.search_flights,
        "train": db.search_trains,
        "bus": db.search_buses,
    }
    modes_to_search = [mode] if mode in searchers else list(searchers.keys())

    results = []
    for m in modes_to_search:
        results.extend(searchers[m](origin, start, end, min_seats=pax))
    return results


def build_plan(request):
    """
    Core planning logic shared by both modes: query slots + transport
    across all relevant modes, rank every valid combination, and
    return the top options so the user can compare and pick.
    """
    missing = []
    if not request.get("origin"):
        missing.append("origin city")

    if missing:
        return {
            "status": "NEEDS_INFO",
            "missing": missing,
            "message": f"I need your {', '.join(missing)} to search travel options. Which city will you travel from?",
        }

    slots = db.search_yatra_slots(
        request["start_date"], request["end_date"],
        category=request.get("category"), min_seats=request["pax"]
    )
    transport = _search_transport(request)

    if not slots or not transport:
        mode_note = f" by {request['mode']}" if request.get("mode") else ""
        return {
            "status": "NO_AVAILABILITY",
            "message": f"I couldn't find matching yatra slots and travel options{mode_note} for those dates. "
                       "Want me to widen the date range or try a different mode of transport?",
            "slots_found": len(slots),
            "flights_found": len(transport),
        }

    # Rank every valid combination (transport arrives a day before/same day
    # as the yatra slot) by cheapest total.
    combos = []
    for tr in transport[:30]:
        for s in slots[:15]:
            if s["slot_date"] >= tr["travel_date"]:
                total = (tr["price"] + s["price"]) * request["pax"]
                combos.append({"flight": tr, "slot": s, "total_price": total})

    if not combos:
        return {
            "status": "NO_COMBINATION",
            "message": "Found travel options and yatra slots separately, but no valid combination "
                       "(travel would arrive after the yatra slot). Try a wider date range.",
        }

    combos.sort(key=lambda c: c["total_price"])

    options = []
    seen = set()

    if not request.get("mode"):
        # No preference stated: show one option per mode first, so the
        # person can actually compare flight vs train vs bus, rather
        # than three near-identical cheap-train results dominating the
        # list just because trains are usually cheapest.
        for m in ("flight", "train", "bus"):
            for c in combos:
                if c["flight"]["mode"] == m:
                    key = (c["flight"]["id"], c["flight"]["mode"], c["slot"]["category"])
                    if key not in seen:
                        seen.add(key)
                        options.append(c)
                        break

    for c in combos:
        if len(options) >= MAX_OPTIONS:
            break
        key = (c["flight"]["id"], c["flight"]["mode"], c["slot"]["category"])
        if key in seen:
            continue
        seen.add(key)
        options.append(c)

    options.sort(key=lambda c: c["total_price"])
    options = options[:MAX_OPTIONS]

    return {
        "status": "PLAN_READY",
        "pax": request["pax"],
        "options": options,
        "alt_slots_count": len(slots),
        "alt_flights_count": len(transport),
    }


def confirm_booking(option, pax, user_name, hotel=None, hotel_nights=0, sightseeing_places=None):
    """Executes the mock booking for a chosen option from PLAN_READY['options'],
    optionally including a hotel stay (hotel cost is added to the total) and a
    list of sightseeing places (informational only, doesn't affect price)."""
    total = option["total_price"]
    if hotel:
        total += hotel.get("price_per_night", 0) * hotel_nights

    booking_id = db.create_booking(
        user_name=user_name,
        pax_count=pax,
        yatra_slot=option["slot"],
        transport=option["flight"],
        total_price=total,
        hotel=hotel,
        hotel_nights=hotel_nights,
        sightseeing_places=sightseeing_places,
    )
    return booking_id


def process_message(text):
    """Single entry point the Streamlit UI calls for free-text requests.
    Returns a structured plan dict."""
    request = parse_request(text)
    plan = build_plan(request)
    plan["_request"] = request
    return plan
