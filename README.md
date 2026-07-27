# Vaishno Devi Yatra Booking Agent (Prototype)

An AI agent prototype that plans and books Vaishno Devi yatra slots + flights
based on natural-language user requests. Built with Streamlit.

> **Important:** This is a prototype for demo purposes. It books against a
> **mock database** of generated yatra slots and flights — it does **not**
> connect to the real Shrine Board registration system or real airline
> booking systems (no public APIs exist for these, and automating them
> without permission would raise ToS/legal issues). The architecture is
> designed so the mock data layer (`db.py`) can be swapped for real
> integrations later without touching the agent or UI.

## Features

- Conversational chat UI (Streamlit `st.chat_message`)
- Hybrid agent brain:
  - **Rule-based mode** (default) — works with zero setup, no API key
  - **LLM-powered mode** — auto-enables if you provide an `ANTHROPIC_API_KEY`,
    using Claude to parse free-form requests
- Searches mock yatra slot + flight inventory, ranks combinations by price
- Mock booking confirmation with a generated booking ID
- Booking history sidebar

## Project structure

```
yatra-agent/
├── app.py          # Streamlit UI
├── agent.py        # Agent reasoning (rule-based + optional LLM mode)
├── db.py            # Database access layer (the "tools" the agent calls)
├── data_gen.py       # Generates mock yatra slot & flight data into SQLite
├── requirements.txt
├── .gitignore
└── data/             # SQLite DB lives here (generated on first run, gitignored)
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

The mock database is generated automatically on first run.

### Optional: enable LLM-powered mode

Either paste your key into the sidebar field in the running app, or set it
as an environment variable before launching:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
streamlit run app.py
```

## Deploy for free (Streamlit Community Cloud)

1. Push this repo to GitHub (see below)
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub
3. Click "New app", pick this repo and branch, set main file to `app.py`
4. (Optional) Add `ANTHROPIC_API_KEY` under App settings → Secrets:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Deploy — you'll get a public URL, e.g. `https://your-app.streamlit.app`

## Pushing to GitHub

```bash
cd yatra-agent
git init
git add .
git commit -m "Initial prototype: Vaishno Devi yatra booking agent"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## Example prompts to try

- "Book 2 people from Delhi next week"
- "I want VIP darshan for 4 pilgrims from Mumbai this week"
- "Helicopter darshan for 1 person from Bangalore next month"

## Roadmap / what a real version would need

- Real yatra registration integration (requires Shrine Board API access
  or authorized partnership — not available publicly)
- Real airline booking (via GDS/airline APIs like Amadeus, not scraping)
- Payment gateway integration
- User authentication + Aadhaar-linked ID verification for yatra slips
- Proper error handling for concurrent seat updates (current SQLite
  approach is fine for a demo, not for production concurrency)

## Disclaimer

This project is an independent prototype and is not affiliated with or
endorsed by the Shri Mata Vaishno Devi Shrine Board or any airline.
