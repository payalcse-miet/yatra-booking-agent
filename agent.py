"""
agent.py
The 'agent' brain. Two modes:

1. RULE_BASED (default, no API key needed): extracts trip details with
   simple parsing, queries the mock database, ranks combinations, and
   proposes a plan. Deterministic and demo-safe.

2. LLM_POWERED (auto-enabled if ANTHROPIC_API_KEY is set): uses Claude
   with tool-use so the model itself decides which searches to run and
   how to reason about trade-offs, then calls the same db functions.

Both modes produce the same output shape so the Streamlit UI doesn't
need to know which one is active.
"""

import os
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

MAX_OPTIONS = 3  # how many ranked flight+slot combinations to show for review


def _use_llm():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


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


def _extract_date_range(text):
    """Very simple heuristic date parsing for the prototype.
    Defaults to the next 14 days if nothing specific is found."""
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
        "start_date": _extract_date_range(text)[0],
        "end_date": _extract_date_range(text)[1],
    }


def build_plan(request):
    """
    Core planning logic shared by both modes: query slots + flights,
    rank every valid combination, and return the top options so the
    user can compare and pick rather than being handed a single match.
    """
    missing = []
    if not request.get("origin"):
        missing.append("origin city")

    if missing:
        return {
            "status": "NEEDS_INFO",
            "missing": missing,
            "message": f"I need your {', '.join(missing)} to search flights. Which city will you travel from?",
        }

    slots = db.search_yatra_slots(
        request["start_date"], request["end_date"],
        category=request.get("category"), min_seats=request["pax"]
    )
    flights = db.search_flights(
        request["origin"], request["start_date"], request["end_date"],
        min_seats=request["pax"]
    )

    if not slots or not flights:
        return {
            "status": "NO_AVAILABILITY",
            "message": "I couldn't find matching yatra slots and flights for those dates. Want me to widen the date range?",
            "slots_found": len(slots),
            "flights_found": len(flights),
        }

    # Rank every valid combination (flight lands a day before/same day as
    # the yatra slot) by cheapest total, then keep the top few distinct
    # options so the person can compare and choose rather than just
    # being handed one "best" answer.
    combos = []
    for f in flights[:15]:
        for s in slots[:15]:
            if s["slot_date"] >= f["flight_date"]:
                total = (f["price"] + s["price"]) * request["pax"]
                combos.append({"flight": f, "slot": s, "total_price": total})

    if not combos:
        return {
            "status": "NO_COMBINATION",
            "message": "Found flights and slots separately, but no valid combination (flight would arrive after the yatra slot). Try a wider date range.",
        }

    combos.sort(key=lambda c: c["total_price"])

    # De-duplicate by (flight, category) rather than (flight, slot id):
    # slot rows for the same category only differ by time-of-day and share
    # the same price, so keying on slot id alone produced 3 "options" that
    # were really the same flight+price shown 3 times. Keying on category
    # means the top slots shown are meaningfully different in flight
    # and/or price, not just a different clock time for the same thing.
    options = []
    seen = set()
    for c in combos:
        key = (c["flight"]["id"], c["slot"]["category"])
        if key in seen:
            continue
        seen.add(key)
        options.append(c)
        if len(options) >= MAX_OPTIONS:
            break

    return {
        "status": "PLAN_READY",
        "pax": request["pax"],
        "options": options,
        "alt_slots_count": len(slots),
        "alt_flights_count": len(flights),
    }


def confirm_booking(option, pax, user_name):
    """Executes the mock booking for a chosen option from PLAN_READY['options']."""
    booking_id = db.create_booking(
        user_name=user_name,
        pax_count=pax,
        yatra_slot_id=option["slot"]["id"],
        flight_id=option["flight"]["id"],
        total_price=option["total_price"],
    )
    return booking_id


# ---------------------------------------------------------------------
# Optional: LLM-powered mode. Only activates if ANTHROPIC_API_KEY is set.
# Uses Claude to parse free-form text into the same request structure
# that build_plan() expects, so the deterministic booking logic below
# stays identical regardless of which mode parsed the request.
# ---------------------------------------------------------------------

def parse_request_llm(text, api_key):
    import json
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    today = date.today().isoformat()

    system = f"""Extract yatra trip details from the user's message as JSON only.
Today's date is {today}. Fields: pax (integer, default 1), origin (city name or null),
category (one of "Normal Darshan","VIP Darshan","Helicopter Darshan", or null),
start_date (YYYY-MM-DD), end_date (YYYY-MM-DD). If no dates mentioned, use the next 14 days.
Respond with ONLY the JSON object, no other text."""

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=system,
        messages=[{"role": "user", "content": text}],
    )
    raw = "".join(b.text for b in resp.content if b.type == "text")
    raw = raw.strip().strip("`").replace("json", "", 1) if raw.strip().startswith("```") else raw
    return json.loads(raw)


def process_message(text, api_key=None):
    """Single entry point the Streamlit UI calls. Returns a structured plan dict."""
    if api_key:
        try:
            request = parse_request_llm(text, api_key)
        except Exception:
            request = parse_request(text)  # fall back safely
    else:
        request = parse_request(text)

    plan = build_plan(request)
    plan["_request"] = request
    return plan
