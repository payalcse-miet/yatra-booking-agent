"""
app.py
Streamlit front-end for the Vaishno Devi Yatra Booking Agent prototype.
Run locally with: streamlit run app.py
"""

import os
import streamlit as st

import agent
import db
from data_gen import build_database

st.set_page_config(page_title="Vaishno Devi Yatra Agent", page_icon="🛕", layout="centered")

# --- One-time DB setup ---
if not os.path.exists("data/yatra.db"):
    with st.spinner("Setting up mock yatra & flight data..."):
        build_database()

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Namaste! I'm your Vaishno Devi yatra booking agent (prototype). "
                "Tell me your travel dates, city, and number of pilgrims, e.g. "
                "\"Book for 3 people from Delhi next week, VIP darshan.\""
            ),
        }
    ]
if "pending_plan" not in st.session_state:
    st.session_state.pending_plan = None

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input(
        "Anthropic API key (optional)",
        type="password",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        help="Leave blank to use the built-in rule-based agent. Add a key to let Claude handle understanding requests.",
    )
    if api_key_input:
        st.success("LLM-powered mode active")
    else:
        st.info("Rule-based mode active (no key needed)")

    st.divider()
    st.header("Booking history")
    bookings = db.list_bookings()
    if not bookings:
        st.caption("No bookings yet.")
    for b in bookings:
        with st.expander(f"{b['booking_id']} · {b['status']}"):
            st.write(f"**Name:** {b['user_name']}")
            st.write(f"**Pax:** {b['pax_count']}")
            st.write(f"**Yatra:** {b.get('category', '-')} on {b.get('slot_date', '-')}")
            st.write(f"**Flight:** {b.get('flight_no', '-')} from {b.get('origin', '-')}")
            st.write(f"**Total:** ₹{b['total_price']}")

st.title("🛕 Vaishno Devi Yatra Booking Agent")
st.caption("Prototype — bookings are simulated against mock data, not real yatra registration or airline systems.")

# --- Chat history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Render a pending plan as a confirmable card ---
if st.session_state.pending_plan:
    plan = st.session_state.pending_plan
    with st.chat_message("assistant"):
        f, s = plan["flight"], plan["slot"]
        st.markdown("**Here's the best plan I found:**")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**✈️ Flight**")
            st.write(f"{f['airline']} {f['flight_no']}")
            st.write(f"{f['origin']} → {f['destination']}")
            st.write(f"{f['flight_date']} at {f['departure_time']}")
            st.write(f"₹{f['price']} / person")
        with col2:
            st.markdown("**🙏 Yatra slot**")
            st.write(f"{s['category']}")
            st.write(f"{s['slot_date']} at {s['slot_time']}")
            st.write(f"₹{s['price']} / person")
        st.markdown(f"**Total for {plan['pax']} pilgrim(s): ₹{plan['total_price']}**")

        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name for booking", key="booking_name")
        with c2:
            st.write("")
            if st.button("Confirm booking", type="primary"):
                if name.strip():
                    booking_id = agent.confirm_booking(plan, name.strip())
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": f"✅ Booked! Your confirmation ID is **{booking_id}**. Total paid (mock): ₹{plan['total_price']}.",
                        }
                    )
                    st.session_state.pending_plan = None
                    st.rerun()
                else:
                    st.warning("Please enter a name first.")

# --- Chat input ---
if prompt := st.chat_input("Describe your trip..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Checking slots and flights..."):
            result = agent.process_message(prompt, api_key=api_key_input or None)

        if result["status"] == "NEEDS_INFO":
            reply = result["message"]
        elif result["status"] == "NO_AVAILABILITY":
            reply = result["message"]
        elif result["status"] == "NO_COMBINATION":
            reply = result["message"]
        elif result["status"] == "PLAN_READY":
            reply = (
                f"Found a plan across {result['alt_flights_count']} flight option(s) and "
                f"{result['alt_slots_count']} yatra slot option(s). Showing the best match below — "
                "confirm to book."
            )
            st.session_state.pending_plan = result
        else:
            reply = "Something went wrong understanding that — could you rephrase with your city, dates, and number of pilgrims?"

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    if result["status"] == "PLAN_READY":
        st.rerun()
