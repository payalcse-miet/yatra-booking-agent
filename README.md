# Vaishno Devi Yatra Booking Agent (Prototype)

An AI agent prototype that plans and books Vaishno Devi yatra slots + flights
based on natural-language user requests. Built with Streamlit.

> **Important:** This is a prototype for demo purposes. Yatra darshan
> **prices** are real, researched figures (see Data Sources below);
> flight prices are realistic but synthetic. **Seat/slot availability
> for both is simulated** — no public dataset or API anywhere publishes
> real-time yatra slot or airline seat inventory (that data is gated
> behind the Shrine Board's and airlines' private booking systems).
> **Login and payment are also simulated** — see the sections below.

## What's new in this version

- **Login page** — sign in, sign up, or continue as a guest before using the agent. Demo account: `demo` / `demo123`.
- **Multi-option review step** — instead of one "best match," the agent now surfaces the top 3 flight + yatra-slot combinations, each expandable for full details, with a clickable "Select this option" button.
- **A real 3-step flow** — *Tell us your trip → Review options → Pay & confirm* — with a working back/cancel path at each step.
- **Mock payment gateway** — a card/UPI checkout screen (Luhn-validated card number, expiry, CVV) sits between choosing a plan and getting a confirmation ID. No real transaction ever occurs; see the warning in `payment.py`.
- **Booking history is now per-account**, filtered to whoever is logged in.
- Refreshed visual design (custom typography, card shadows, status badges).

## Data Sources

This project uses **CSV-file datasets** (`data/yatra_slots_dataset.csv`,
`data/flights_dataset.csv`, `data/users_dataset.csv`) as its actual data
source — not a live API, not random on-the-fly generation. Here's
exactly what's real and what isn't, and where each figure came from:

| Field | Status | Source |
|---|---|---|
| Yatra Registration (Normal Darshan) price | **Real** | Free, per Shrine Board (maavaishnodevi.org) |
| Helicopter Darshan price (₹4,640 round-trip) | **Real, verified** | Official Shrine Board rate, Katra–Sanjichhat route, revised Oct 2025 |
| VIP/Special Darshan price (~₹500) | **Commonly cited, not officially confirmed** | Consistent across multiple pilgrimage sites; no official Shrine Board rate card found |
| Yatra slot *seat availability* | **Simulated** | Not public anywhere — gated behind Shrine Board's login system |
| Flight routes/airlines/times/duration/stops | Realistic structure | Modeled on real domestic route patterns |
| Flight *prices* | Realistic ranges, not exact | Calibrated against real Kaggle India flight-price datasets — the Easemytrip/Jet-Airways-era set, and [Muhammad Bin Imran's "Flight Price Prediction" dataset](https://www.kaggle.com/datasets/muhammadbinimran/flight-price-prediction) — but neither includes Jammu specifically, so exact figures are synthetic within realistic bounds |
| Flight *seat availability* | **Simulated** | Real-time airline seat inventory is proprietary GDS data, not public |
| User accounts | **Demo only** | Seeded `demo`/`guest` accounts plus anything signed up locally; SHA-256 hashed, no salt — not production auth |

**Datasets checked and found not to have the exact data needed:**
- [data.gov.in](https://data.gov.in) — has real air traffic statistics, but only aggregated totals per airport/year, not per-flight records
- Kaggle India flight-price datasets — real historical fares, but limited to a handful of major metro-to-metro routes; none include Jammu
- Shrine Board's own [Yatra Statistics](https://www.maavaishnodevi.org/yatrastatistics) page — real pilgrim footfall numbers, but only annual/monthly totals, not slot-level data

This is a genuine gap, not a research shortcut: granular, route-level,
real-time booking data for either system simply isn't published
anywhere publicly. A real production version of this agent would need
an official data-sharing agreement with the Shrine Board and an
airline/GDS partner.

## How the data layer works

- `build_dataset.py` — generates the master dataset CSVs (run once, or
  already included in the repo): yatra slots, flights, and seed user
  accounts. Uses `day_offset` instead of fixed dates so the dataset
  stays usable regardless of when the app runs.
- `db.py` — on first app run, copies the dataset CSVs into "live"
  working copies (`data/yatra_slots_live.csv`, `data/flights_live.csv`,
  `data/users_live.csv`) with actual calendar dates computed in, plus
  `data/bookings.csv`. All searching, seat-decrementing, and new
  sign-ups happen against these live files.
- The dataset CSVs (`*_dataset.csv`) are committed to the repo; the
  live/mutable files and bookings are gitignored, since they're
  per-install state, not the dataset itself.

## Login

`auth.py` gates the whole app behind a login screen with three tabs:
Log in, Sign up, or Guest access. New sign-ups are written to
`data/users_live.csv` (gitignored — local to your install). This is
intentionally simple: no password reset, no email verification, no
salting. Good enough to demo "the app has accounts"; not good enough
to hold real user data.

## Payment

`payment.py` renders a checkout screen (card or UPI) between selecting
a plan and getting a confirmation ID. It performs basic client-side
checks (Luhn checksum on the card number, expiry format, CVV length)
so the flow feels real, but it **never contacts any payment network**
and nothing is stored. **Do not enter a real card number, even out of
habit** — it's not needed and isn't sent anywhere real.

A production version would integrate an actual gateway (Razorpay,
Stripe, etc.), with card fields hosted by the gateway itself so raw
card data never touches this app's server at all.

## Project structure

```
yatra-agent/
├── app.py                  # Streamlit UI: login gate, 3-step booking flow
├── auth.py                  # Login / sign-up / guest access
├── payment.py                # Mock payment gateway (card/UPI checkout)
├── agent.py                   # Agent reasoning (rule-based + optional LLM mode)
├── db.py                       # CSV-backed data access layer (+ user accounts)
├── build_dataset.py             # Builds the master CSV datasets (run once)
├── data_gen.py                    # Compatibility shim, bootstraps live data on first run
├── requirements.txt
├── .gitignore
└── data/
    ├── yatra_slots_dataset.csv   # master dataset (committed)
    ├── flights_dataset.csv        # master dataset (committed)
    ├── users_dataset.csv           # seed demo accounts (committed)
    ├── yatra_slots_live.csv         # generated on first run (gitignored)
    ├── flights_live.csv              # generated on first run (gitignored)
    ├── users_live.csv                 # generated on first run (gitignored)
    └── bookings.csv                    # generated on first run (gitignored)
```

## Run locally

```bash
git clone <your-repo-url>
cd yatra-agent
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Live data files are generated automatically on first run from the
committed dataset CSVs. Log in with `demo` / `demo123`, sign up fresh,
or continue as a guest.

### Optional: enable LLM-powered mode

Paste your Anthropic API key into the sidebar field in the running app,
or set it as an environment variable before launching:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
streamlit run app.py
```

## Deploy for free (Streamlit Community Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub
3. Click "New app", pick this repo and branch, set main file to `app.py`
4. (Optional) Add `ANTHROPIC_API_KEY` under App settings → Secrets
5. Deploy — you get a public URL, e.g. `https://your-app.streamlit.app`

## Example prompts to try

- "Book 2 people from Delhi next week"
- "I want VIP darshan for 4 pilgrims from Mumbai this week"
- "Helicopter darshan for 1 person from Bangalore next month"

## Roadmap / what a real version would need

- Official Shrine Board data-sharing agreement for real slot inventory
- Airline/GDS API partnership (e.g. Duffel, which offers a free sandbox
  suitable for prototyping — see project notes) for real flight search and booking
- A real payment gateway integration (Razorpay/Stripe) instead of the mock checkout
- Proper salted-hash auth or a real identity provider instead of the demo login
- User authentication + Aadhaar-linked ID verification for yatra slips
- A proper database (Postgres/etc.) instead of CSV files, once
  concurrent multi-user bookings need to be handled reliably

## Disclaimer

This project is an independent prototype and is not affiliated with or
endorsed by the Shri Mata Vaishno Devi Shrine Board or any airline.
