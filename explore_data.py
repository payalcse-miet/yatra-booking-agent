"""
explore_data.py
Static, curated list of real places to see around Katra, the Vaishno
Devi trek route, and Jammu city — for the app's "Explore Katra" tab.

This is reference/informational content only (nothing here is
bookable or searched against seat inventory). Distances and travel
notes are drawn from general pilgrimage-tourism sources and are
approximate, not survey-grade figures.

Taxi fare figures in TAXI_INFO are grounded in real, researched
figures from multiple cab-booking sites (Jagat Travels, CabBazar,
Savaari, EaseMyTrip Cabs, etc.), cross-checked for consistency.
"""

# Real, researched: Jammu <-> Katra is ~44-55 km, ~1-1.5 hrs by road.
# Sedan fares commonly quoted ₹1,300-2,500 one-way; SUV/Tempo Traveller
# fares run higher, ₹2,500-3,800+. Figures cross-checked across several
# cab-booking sites; treated as a realistic range, not a live-quoted price.
TAXI_INFO = {
    "route": "Jammu (Airport / Railway Station) → Katra",
    "distance": "approx. 44-55 km",
    "duration": "approx. 1-1.5 hours by road",
    "options": [
        {"vehicle": "AC Sedan (Dzire, Etios, or similar)", "capacity": "up to 4", "fare_range": "₹1,300-2,500 one-way"},
        {"vehicle": "SUV (Innova or similar)", "capacity": "up to 7", "fare_range": "₹2,500-3,800 one-way"},
        {"vehicle": "Tempo Traveller", "capacity": "12-16", "fare_range": "₹3,800+ one-way, varies by group size"},
    ],
    "note": (
        "Prices vary by season, demand, and operator — treat these as a realistic planning "
        "range, not a live quote. Shared/shuttle options are usually cheaper than a private cab."
    ),
}

LOCAL_TRAVEL_NOTES = {
    "On the trek route": "Reached on foot (the pilgrimage trek itself) or by pony/palki/e-vehicle available along the route for a fee.",
    "Nearby temple": "Best reached by local taxi or auto-rickshaw from Katra town, typically a short ₹100-300 ride.",
    "Nature": "Usually a half/full-day taxi hire from Katra, roughly ₹1,500-3,000 depending on distance and wait time.",
    "Hill station": "Best reached by taxi from Jammu or Katra; a full-day hire for a hill-station trip commonly runs ₹2,500-4,500.",
    "Hill station / adventure": "Best reached by taxi from Jammu or Katra; a full-day hire for a hill-station trip commonly runs ₹2,500-4,500.",
    "Nature / heritage": "Usually a half/full-day taxi hire from Jammu, roughly ₹1,500-3,000.",
    "Jammu city": "Local taxi or auto-rickshaw from Katra, roughly ₹1,000-1,800 one-way given the distance to Jammu city.",
}

PLACES = [
    {
        "name": "Bhairavnath Temple",
        "category": "On the trek route",
        "distance": "~3 km uphill from the main Bhawan",
        "description": (
            "A shrine many pilgrims visit right after Vaishno Devi darshan itself — "
            "local tradition holds the pilgrimage is considered incomplete without it."
        ),
    },
    {
        "name": "Ardhkuwari Cave",
        "category": "On the trek route",
        "distance": "Roughly halfway up the 13 km trek from Katra",
        "description": (
            "A cave shrine associated with the goddess's own legend, and a natural "
            "resting point partway through the climb."
        ),
    },
    {
        "name": "Charan Paduka",
        "category": "On the trek route",
        "distance": "~1.5 km from Katra",
        "description": "A short, easy stop marking footprints said to belong to the goddess — good for a quick, low-effort detour early in the trek.",
    },
    {
        "name": "Nau Devi Cave Temple",
        "category": "Nearby temple",
        "distance": "~10 km from Katra",
        "description": "A cave temple dedicated to the nine forms of Durga, with naturally formed idols inside — a quieter, less-crowded alternative pilgrimage stop.",
    },
    {
        "name": "Baba Dhansar",
        "category": "Nature",
        "distance": "Day-trip distance from Katra",
        "description": "A scenic spot with natural pools and a waterfall, popular for a relaxed break from the pilgrimage crowds.",
    },
    {
        "name": "Jhajjar Kotli",
        "category": "Nature",
        "distance": "~15 km from Katra",
        "description": "A picnic spot on a clear mountain stream, with a small tourism complex if you want to stay over.",
    },
    {
        "name": "Patnitop",
        "category": "Hill station",
        "distance": "~112 km from Jammu",
        "description": "A well-known Himalayan hill station with meadows and Chenab-valley views — trekking in summer, skiing in winter.",
    },
    {
        "name": "Sanasar",
        "category": "Hill station / adventure",
        "distance": "Near Patnitop",
        "description": "A quieter meadow destination popular for paragliding, rock climbing, and trekking.",
    },
    {
        "name": "Mansar Lake",
        "category": "Nature / heritage",
        "distance": "~60 km from Jammu",
        "description": "A lake with mythological ties to the Mahabharata, ringed by temples and greenery.",
    },
    {
        "name": "Raghunath Temple, Jammu",
        "category": "Jammu city",
        "distance": "~45 minutes from Katra",
        "description": "One of North India's largest temple complexes, in the heart of Jammu city.",
    },
    {
        "name": "Bahu Fort & Bagh-e-Bahu",
        "category": "Jammu city",
        "distance": "~45 minutes from Katra",
        "description": "A historic Dogra-era fort with a garden overlooking the Tawi river — a good sunset stop.",
    },
    {
        "name": "Amar Mahal Palace",
        "category": "Jammu city",
        "distance": "~45 minutes from Katra",
        "description": "A 19th-century palace built in a French-chateau style, now a museum with miniature paintings and manuscripts.",
    },
]

CATEGORIES = ["On the trek route", "Nearby temple", "Nature", "Hill station", "Hill station / adventure", "Nature / heritage", "Jammu city"]


def get_places(category=None):
    if category:
        return [p for p in PLACES if p["category"] == category]
    return PLACES


def get_categories():
    seen = []
    for p in PLACES:
        if p["category"] not in seen:
            seen.append(p["category"])
    return seen


def get_taxi_info():
    return TAXI_INFO


def get_local_travel_note(category):
    return LOCAL_TRAVEL_NOTES.get(category, "Local taxi or auto-rickshaw hire recommended; check current rates locally.")
