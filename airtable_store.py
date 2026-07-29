"""
airtable_store.py
Optional persistent storage backend using Airtable.

WHY THIS EXISTS: Streamlit Community Cloud's filesystem is ephemeral -
every redeploy or sleep/wake cycle wipes anything not committed to
GitHub. Airtable is a free, spreadsheet-like hosted table that lives
outside the app's disk, so data survives restarts. Unlike Google
Cloud, Airtable's free tier does not require a credit card to sign up.

This is OPTIONAL and OFF by default. It only activates once Streamlit
secrets contain `airtable_api_key` and `airtable_base_id`. Without
those (e.g. running locally without setting this up), db.py falls
back to the local CSV files exactly as before.

One-time setup (full steps in README.md -> "Persistent storage"):
1. Create a free Airtable account and a new Base.
2. In that base, create two tables named exactly "users" and
   "bookings" with the field names listed in the README.
3. Create a Personal Access Token (Airtable account settings ->
   Developer Hub -> Personal access tokens) scoped to
   data.records:read + data.records:write for that base, and note
   the Base ID (starts with "app...", found in the base's API docs
   or its URL).
"""

import pandas as pd
import requests
import streamlit as st

API_ROOT = "https://api.airtable.com/v0"


def is_configured():
    try:
        return "airtable_api_key" in st.secrets and "airtable_base_id" in st.secrets
    except Exception:
        return False


def _headers():
    return {
        "Authorization": f"Bearer {st.secrets['airtable_api_key']}",
        "Content-Type": "application/json",
    }


def _table_url(table_name):
    return f"{API_ROOT}/{st.secrets['airtable_base_id']}/{table_name}"


def _read_records(table_name, columns):
    records = []
    params = {"pageSize": 100}
    while True:
        resp = requests.get(_table_url(table_name), headers=_headers(), params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for rec in data.get("records", []):
            row = {c: rec["fields"].get(c, "") for c in columns}
            records.append(row)
        offset = data.get("offset")
        if not offset:
            break
        params["offset"] = offset
    return records


def read_df(name, columns):
    """Reads a named table ('users' or 'bookings') as a DataFrame with
    the given columns. Returns an empty (but correctly-shaped) frame
    if the table has no rows yet."""
    records = _read_records(name, columns)
    if not records:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(records)
    for c in columns:
        if c not in df.columns:
            df[c] = None
    return df[columns]


def append_row(name, columns, row_dict):
    """Creates one new row in the given table."""
    fields = {c: row_dict.get(c, "") for c in columns}
    body = {"records": [{"fields": fields}]}
    resp = requests.post(_table_url(name), headers=_headers(), json=body, timeout=15)
    resp.raise_for_status()
    return resp.json()
