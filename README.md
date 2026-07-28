# Vaishno Devi Yatra Booking Agent (Prototype)

An AI agent prototype that plans and books Vaishno Devi yatra slots + flights
based on natural-language user requests. Built with Streamlit.

> **Important:** This is a prototype for demo purposes. Yatra darshan
> **prices** are real, researched figures (see Data Sources below);
> flight prices are realistic but synthetic. **Seat/slot availability
> for both is simulated** — no public dataset or API anywhere publishes
> real-time yatra slot or airline seat inventory (that data is gated
> behind the Shrine Board's and airlines' private booking systems).

## Data Sources

This project uses a **CSV-file dataset** (`data/yatra_slots_dataset.csv`,
`data/flights_dataset.csv`) as its actual data source — not a live API,
not random on-the-fly generation. Here's exactly what's real and what
isn't, and where each figure came from:

| Field | Status | Source |
|---|---|---|
| Yatra Registration (Normal Darshan) price | **Real** | Free, per Shrine Board (maavaishnodevi.org) |
| Helicopter Darshan price (₹4,640 round-trip) | **Real, verified** | Official Shrine Board rate, Katra–Sanjichhat route, revised Oct 2025 |
| VIP/Special Darshan price (~₹500) | **Commonly cited, not officially confirmed** | Consistent across multiple pilgrimage sites; no official Shrine Board rate card found |
| Yatra slot *seat availability* | **Simulated** | Not public anywhere — gated behind Shrine Board's login system |
| Flight routes/airlines/times | Realistic structure | Modeled on real domestic route patterns |
| Flight *prices* | Realistic ranges, not exact | Calibrated against real Kaggle India flight-price datasets (Easemytrip, 2019 Jet Airways-era) — but none of those datasets include Jammu specifically, so exact figures are synthetic within realistic bounds |
| Flight *seat availability* | **Simulated** | Real-time airline seat inventory is proprietary GDS data, not public |

**Datasets checked and found not to have the exact data needed:**
- [data.gov.in](https://data.gov.in) — has real air traffic statistics, but only aggregated totals per airport/year, not per-flight records
- Kaggle India flight-price datasets — real historical fares, but limited to 6 major metro-to-metro routes; none include Jammu
- Shrine Board's own [Yatra Statistics](https://www.maavaishnodevi.org/yatrastatistics) page — real pilgrim footfall numbers, but only annual/monthly totals, not slot-level data

This is a genuine gap, not a research shortcut: granular, route-level,
real-time booking data for either system simply isn't published
anywhere publicly. A real production version of this agent would need
an official data-sharing agreement with the Shrine Board and an
airline/GDS partner.

## How the data layer works

- `build_dataset.py` — generates the two master dataset CSVs (run once,
  or already included in the repo). Uses `day_offset` instead of fixed
  dates so the dataset stays usable regardless of when the app runs.
- `db.py` — on first app run, copies the dataset CSVs into "live"
  working copies (`data/yatra_slots_live.csv`, `data/flights_live.csv`)
  with actual calendar dates computed in, and a `data/bookings.csv`.
  All searching and seat-decrementing happens against these live files.
- The dataset CSVs (`*_dataset.csv`) are committed to the repo; the
  live/mutable files and bookings are gitignored, since they're
  per-install state, not the dataset itself.

## Project structure

```
yatra-agent/
├── app.py                  # Streamlit UI
├── agent.py                # Agent reasoning (rule-based + optional LLM mode)
├── db.py                   # CSV-backed data access layer
├── build_dataset.py         # Builds the master CSV datasets (run once)
├── data_gen.py               # Compatibility shim, bootstraps live data on first run
├── requirements.txt
├── .gitignore
└── data/
    ├── yatra_slots_dataset.csv   # master dataset (committed)
    ├── flights_dataset.csv        # master dataset (committed)
    ├── yatra_slots_live.csv       # generated on first run (gitignored)
    ├── flights_live.csv            # generated on first run (gitignored)
    └── bookings.csv                 # generated on first run (gitignored)
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
committed dataset CSVs.

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
- Airline/GDS API partnership (Amadeus, Duffel, or similar) for real
  flight search and booking
- Payment gateway integration
- User authentication + Aadhaar-linked ID verification for yatra slips
- A proper database (Postgres/etc.) instead of CSV files, once
  concurrent multi-user bookings need to be handled reliably

## Disclaimer

This project is an independent prototype and is not affiliated with or
endorsed by the Shri Mata Vaishno Devi Shrine Board or any airline.
