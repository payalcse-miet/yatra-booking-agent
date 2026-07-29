"""
yatra_info.py
Real, researched pilgrimage-essentials content for the Explore Katra tab -
the kind of practical info a first-time pilgrim actually needs, beyond
just booking transport/darshan/hotel.

Everything here is cross-checked against the official Shrine Board
site (maavaishnodevi.org) and its own public notices, plus several
independent pilgrim-guide sources, as of this writing. Shrine Board
rules and timings can change (e.g. around festivals/Navratri, or
crowd-management updates) - always confirm anything time-critical via
the official site or helpline before traveling.
"""

AARTI_SCHEDULE = {
    "note": "Darshan at the Holy Cave pauses during Aarti - plan around these windows if you want uninterrupted darshan time.",
    "windows": [
        {"label": "Morning Aarti", "time": "6:20 AM - 8:00 AM"},
        {"label": "Evening Aarti", "time": "7:20 PM - 8:30 PM"},
    ],
    "shrine_hours": "The shrine itself is open 24x7, 365 days a year - only darshan during the two Aarti windows above is paused, not the whole shrine.",
}

REGISTRATION_INFO = {
    "summary": "Yatra registration (the 'Yatra Parchi' / RFID card) is free and mandatory for every pilgrim - you cannot start the trek without it.",
    "how": "Register free online at maavaishnodevi.org, or in person at a Yatra Registration Counter (YRC) in Katra (Bus Stand, Railway Station, Niharika Complex) or Jammu.",
    "note": "The RFID card is scanned at checkpoints along the route and is also how the Shrine Board tracks pilgrims for safety - don't lose it during the trek.",
}

ROUTE_OPTIONS = [
    {
        "name": "Traditional trek via Banganga",
        "distance": "~13 km one-way from Katra to Bhawan",
        "detail": "The classic pilgrim route, on foot, pony, palki, or battery-operated vehicle for parts of it. Can take 5-9 hours on foot depending on fitness and crowd levels.",
    },
    {
        "name": "Tarakote Marg",
        "distance": "Slightly shorter, similar distance to Bhawan",
        "detail": "A gentler-gradient alternative route many pilgrims prefer for an easier climb.",
    },
    {
        "name": "Helicopter to Sanjichhat",
        "distance": "~8-minute flight, then a short walk/vehicle ride to Bhawan",
        "detail": "The fastest option, booked as 'Helicopter Darshan' in this app. Subject to weather - can be delayed or grounded in poor conditions, especially during monsoon.",
    },
]

PACKING_AND_RULES = {
    "prohibited": [
        "Electronic devices - cameras, laptops, tablets, and similar are strictly prohibited on the yatra track (official Shrine Board rule).",
        "Large baggage - travel light; cloak rooms are available at Katra and Bhawan to store what you don't need on the trek.",
    ],
    "general_tips": [
        "Comfortable walking shoes with good grip - the track includes steps and can be slippery, especially in monsoon.",
        "A light raincoat/poncho during monsoon months, and warm layers in winter (see the weather card for what applies to your dates).",
        "A small water bottle and some cash for tea stalls and prasad along the route (free drinking water and langar are also available at several points).",
        "A valid photo ID - required for registration and for helicopter/Aarti bookings.",
    ],
}

FREE_FACILITIES = [
    "Free Langar (community meals) at several points along the route, including Tarakote Marg and Sanjichhat.",
    "24x7 medical centers along the track, including an ICU at Bhawan itself.",
    "Cloak rooms to safely store baggage/electronics you can't carry on the trek.",
]

EMERGENCY_HELPLINE = {
    "toll_free": "1800-180-7212",
    "phone": "01991-234804",
    "whatsapp": "9906019494",
    "note": "24x7 Shrine Board helpline/call centre for yatra-related help. For anything urgent, always double-check the current number on maavaishnodevi.org, since helpline numbers do occasionally change.",
}


def get_packing_tip(weather_info):
    """Takes the dict returned by weather.get_weather() and returns one
    short, practical packing line tailored to that season - shown right
    next to the weather card so the info is actionable, not just trivia."""
    summary = weather_info.get("summary", "").lower()
    if "snow" in summary or weather_info.get("low_c", 99) <= 8:
        return "❄️ Pack warm layers, gloves, and a cap - it'll be cold, especially higher up toward Bhawan."
    if "monsoon" in summary or "rain" in summary:
        return "🌧️ Pack a raincoat/poncho and waterproof footwear - the trek can get slippery in the rain."
    if weather_info.get("high_c", 0) >= 32:
        return "☀️ Pack light cotton clothes, sunscreen, and extra water - it'll be hot on the trek."
    return "🌤️ Comfortable walking shoes and a light jacket for the evenings should cover it."
