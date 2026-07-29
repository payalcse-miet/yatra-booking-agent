# Vaishno Devi Yatra Booking Agent (Prototype)

An AI agent prototype that plans and books Vaishno Devi yatra slots + travel
(flight, train, or bus) based on natural-language user requests. Built with
Streamlit.

> **Important:** This is a prototype for demo purposes. Yatra darshan
> **prices** are real, researched figures (see Data Sources below); flight,
> train, and bus prices are realistic but synthetic. **Seat/slot
> availability for all of these is simulated** — no public dataset or API
> anywhere publishes real-time yatra slot, airline, rail, or bus seat
> inventory. **Login and payment are also simulated** — see the sections
> below.

## What's new in this version

- **Multi-modal travel** — the agent now searches flights, trains, *and*
  buses, not just flights. Say "by train" or "by bus" for a specific mode,
  or leave it unspecified and the agent shows one option per mode so you
  can compare.
- **Hotel stay in Katra (Step 3)** — after picking a travel + darshan
  option, choose to add a hotel stay (Budget/Mid-Range/Premium, real
  researched price tiers) or skip it. Room availability decrements per
  booking, same as transport seats.
- **Weather for your darshan date (Step 3)** — shown right alongside the
  taxi/hotel info, since the darshan date is already fixed at that point.
  Dates within roughly the next 15 days show a live short-range forecast
  (via [Open-Meteo](https://open-meteo.com), a free API needing no key);
  dates further out show a real, researched seasonal average for Katra
  instead, since no forecast API is meaningfully accurate that far ahead.
  Falls back to the seasonal average automatically if the live call fails
  for any reason (offline, rate-limited, etc) — the feature never breaks
  the booking flow.
- **Sightseeing after darshan (Step 4)** — pick from the same curated
  Explore Katra places, filtered by category, and check off the ones
  you plan to visit. Informational only (no price impact), but your
  picks are carried through to the confirmation, payment summary, and
  booking history — or skip in one click.
- **Yatra Essentials (Explore Katra tab)** — real, cross-checked pilgrim
  info: Aarti timings (darshan pauses 6:20-8:00 AM and 7:20-8:30 PM),
  free/mandatory registration steps, the three route options to Bhawan
  (trek, Tarakote Marg, helicopter), a packing & prohibited-items list,
  free facilities (langar, medical centers), and the official Shrine
  Board helpline.
- **Weather-based packing tip (Step 3)** — a one-line, season-specific
  packing suggestion shown right next to the weather card.
- **Rough trip budget estimate (Step 5)** — a general planning estimate
  for food/local taxis/prasad, clearly separated from the actual
  bookable total.
- **Hotel ratings** — a star rating shown per hotel, kept consistent per
  property (clearly labeled as sample data, not real reviews — no public
  review data exists for these generic property names).
- **Jammu → Katra taxi guidance** — shown both during the booking flow
  (Step 3) and as a standalone section in the Explore Katra tab, with
  real researched fare ranges by vehicle type. Each "Explore Katra" place
  also shows a local-travel note (auto/taxi guidance to reach it).
- **Explore Katra tab** — a second tab with real, researched places to see
  around Katra, the trek route, and Jammu city (temples, viewpoints, hill
  stations), filterable by category. Informational only, not bookable.
- **Login page** — sign in, sign up, or continue as a guest. Demo account:
  `demo` / `demo123`.
- **Multi-option review step** — the agent surfaces up to 3 travel + yatra-
  slot combinations, each expandable for full details, with a clickable
  "Select this option" button.
- **A real 5-step flow** — *Tell us your trip → Review options → Add a
  stay (+weather) → Sightseeing → Pay & confirm* — with a working
  back/cancel path at each step.
- **Mock payment gateway** — a card/UPI checkout screen sits between
  choosing a plan (hotel + sightseeing) and getting a confirmation ID.
  No real transaction ever occurs.
- **Booking history is per-account**, filtered to whoever is logged in,
  and now shows the hotel stay and sightseeing picks if added.

## Data Sources

CSV datasets under `data/*_dataset.csv` are the actual data source — not a
live API, not random on-the-fly generation.

| Field | Status | Source |
|---|---|---|
| Yatra Registration (Normal Darshan) price | **Real** | Free, per Shrine Board (maavaishnodevi.org) |
| Helicopter Darshan price (₹4,640 round-trip) | **Real, verified** | Official Shrine Board rate, Katra–Sanjichhat route, revised Oct 2025 |
| VIP/Special Darshan price (~₹500) | **Commonly cited, not officially confirmed** | Consistent across multiple pilgrimage sites |
| Katra has its own railway station (SVDK) with direct trains from Delhi, Mumbai, Kolkata, Chennai, Ahmedabad | **Real** | Station opened 2014; widely documented. Bangalore has no confirmed direct service, so it's deliberately left out of the train dataset rather than invented. |
| Direct bus services to Katra | **Real, but Delhi-only in this dataset** | Regularly documented from Delhi; other cities' bus links weren't confirmed, so they're left out rather than guessed |
| Flight/train/bus *prices, schedules* | Realistic structure, synthetic exact figures | Flight fares calibrated against real Kaggle India flight-price datasets; train fares follow real IRCTC Sleeper/3AC/2AC tiering; none of this is live pricing |
| Jammu ↔ Katra taxi fares (₹1,300–3,800 by vehicle type) | **Real, researched** | Cross-checked across multiple cab-booking sites (Jagat Travels, CabBazar, Savaari, EaseMyTrip Cabs); ~44-55 km, ~1-1.5 hrs |
| Katra hotel price tiers (Budget ₹600-1,500 / Mid-Range ₹1,800-4,000 / Premium ₹5,000-12,000 per night) | **Real, researched price ranges; property names are generic/fictional** | Cross-checked across multiple hotel-booking sites; no real per-hotel room-inventory data exists publicly, so specific property names and room availability are simulated |
| Weather (near-term dates) | **Real, live** | [Open-Meteo](https://open-meteo.com) free forecast API, no key required |
| Weather (dates beyond ~15 days out) | **Real seasonal averages, not a forecast** | General, well-documented Katra/Jammu regional climate patterns (monsoon timing, summer/winter ranges) |
| Aarti timings, registration rules, route options, helpline number | **Real, cross-checked** | Official Shrine Board site (maavaishnodevi.org) and its public notices, cross-checked with independent pilgrim-guide sources |
| Hotel star ratings | **Sample/illustrative, not real reviews** | No public review data exists for these generic property names — ratings are fixed per property so they're at least consistent, not randomized every visit |
| All seat/slot/room availability | **Simulated** | Not public anywhere — gated behind each system's own booking backend |
| Explore Katra tourist info + local-travel notes | **Real places, general sourcing; travel cost notes are estimates** | Compiled from general pilgrimage-tourism sources; distances and local taxi/auto fares are approximate |
| User accounts | **Demo only** | Seeded `demo`/`guest` accounts plus local sign-ups; SHA-256 hashed, no salt — not production auth |

A real production version of this agent would need an official
data-sharing agreement with the Shrine Board, IRCTC, an airline/GDS
partner, state road transport corporations, and individual hotels for
live inventory.

## How the data layer works

- `build_dataset.py` — generates the master dataset CSVs: yatra slots,
  flights, trains, buses, and seed user accounts. Uses `day_offset`
  instead of fixed dates.
- `db.py` — on first app run, copies the dataset CSVs into "live" working
  copies with actual calendar dates computed in, plus `data/bookings.csv`.
  Bookings are **transport-mode-generic**: one booking row stores whichever
  mode (flight/train/bus) was chosen directly, rather than a foreign key
  into one specific mode's table.
- The dataset CSVs are committed to the repo; live/mutable files and
  bookings are gitignored (per-install state, not the dataset itself).

## Persistent storage (signups & bookings survive redeploys)

Optional, via a free Airtable base — see `airtable_store.py`. Setup is
unchanged from before **except the `bookings` table's columns**, which
now need to match the new transport-mode-generic, hotel- and
sightseeing-inclusive schema. If you already set up Airtable, update your
`bookings` table's fields to exactly:

```
booking_id, user_name, pax_count, yatra_slot_id, category, slot_date,
slot_time, transport_mode, transport_no, transport_operator, origin,
destination, transport_date, departure_time, transport_price,
yatra_price, hotel_id, hotel_name, hotel_category, hotel_price_per_night,
hotel_nights, hotel_total, sightseeing_places, total_price, status,
created_at
```

(All "Single line text" is fine.) The `users` table is unchanged. If
you haven't set up Airtable yet, everything still works fine against
local CSV files — this section is optional.

## Login

`auth.py` gates the whole app behind a login screen: Log in, Sign up, or
Guest access. Demo-grade only — SHA-256 hashed, no salt, no password
reset.

## Payment

`payment.py` renders a mock card/UPI checkout between selecting a plan and
getting a confirmation ID. **Never contacts any real payment network** —
do not enter a real card number.

## Project structure

```
yatra-agent/
├── app.py                  # Streamlit UI: login gate, tabs, 3-step booking flow
├── auth.py                  # Login / sign-up / guest access
├── payment.py                 # Mock payment gateway (card/UPI checkout)
├── airtable_store.py            # Optional: persist users/bookings to Airtable
├── agent.py                       # Agent reasoning (rule-based request parsing + ranking)
├── db.py                            # CSV-backed data access layer (multi-modal transport + users)
├── explore_data.py                    # Curated tourist info for the Explore Katra tab
├── weather.py                            # Live forecast (Open-Meteo) + seasonal-average fallback
├── yatra_info.py                            # Real pilgrim essentials: aarti, registration, routes, helpline
├── build_dataset.py                     # Builds the master CSV datasets (run once)
├── data_gen.py                            # Compatibility shim, bootstraps live data on first run
├── requirements.txt
├── .gitignore
└── data/
    ├── yatra_slots_dataset.csv   # master dataset (committed)
    ├── flights_dataset.csv        # master dataset (committed)
    ├── trains_dataset.csv          # master dataset (committed)
    ├── buses_dataset.csv            # master dataset (committed)
    ├── hotels_dataset.csv             # master dataset (committed)
    ├── users_dataset.csv               # seed demo accounts (committed)
    └── *_live.csv, bookings.csv          # generated on first run (gitignored)
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Live data files are generated automatically on first run. Log in with
`demo` / `demo123`, sign up fresh, or continue as a guest.

## Deploy for free (Streamlit Community Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub
3. "New app" → pick this repo/branch → main file `app.py` → Deploy
4. (Optional) Add Airtable secrets under App settings → Secrets, for
   persistent storage — see "Persistent storage" above

## Example prompts to try

- "Book 2 people from Delhi next week"
- "I want VIP darshan for 4 pilgrims from Mumbai this week"
- "2 people from Delhi by train, helicopter darshan"
- "Book a bus for 3 people from Delhi next month"

## Roadmap / what a real version would need

- Official Shrine Board data-sharing agreement for real slot inventory
- IRCTC / airline-GDS / state transport-corporation API partnerships for
  real schedules, fares, and booking
- A real payment gateway integration (Razorpay/Stripe)
- Proper salted-hash auth or a real identity provider
- A proper database (Postgres/etc.) instead of CSV files

## Disclaimer

This project is an independent prototype and is not affiliated with or
endorsed by the Shri Mata Vaishno Devi Shrine Board, Indian Railways, or
any airline/bus operator.
