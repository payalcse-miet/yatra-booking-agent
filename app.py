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

# --- Custom styling ---
st.markdown(
    """
    <style>
    .stChatMessage { border-radius: 14px; }
    div[data-testid="stChatMessage"] { padding: 4px 0; }
    .banner-wrap {
        border-radius: 18px;
        overflow: hidden;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 18px rgba(179,58,30,0.18);
    }
    .step-pill {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 1rem;
    }
    .step-active { background: #B33A1E; color: #FFFFFF; }
    .step-inactive { background: #FCEEDD; color: #5c3a22; }
    .plan-total {
        font-size: 1.1rem;
        font-weight: 700;
        color: #B33A1E;
        margin-top: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Banner (pure decorative SVG — no text embedded, so nothing is ever hard to read) ---
st.markdown(
    """
    <div class="banner-wrap">
    <svg viewBox="0 0 900 140" width="100%" style="display:block;">
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#F7A469"/>
          <stop offset="100%" stop-color="#B33A1E"/>
        </linearGradient>
      </defs>
      <rect width="900" height="140" fill="url(#sky)"/>
      <circle cx="770" cy="40" r="28" fill="#FFE9C7" opacity="0.9"/>
      <polygon points="0,140 140,55 260,140" fill="#7a2a17" opacity="0.55"/>
      <polygon points="180,140 340,30 520,140" fill="#8f3420" opacity="0.75"/>
      <polygon points="420,140 560,60 760,140" fill="#7a2a17" opacity="0.55"/>
      <polygon points="650,140 780,45 900,140" fill="#8f3420" opacity="0.75"/>
      <g fill="#FFF3E2" opacity="0.95">
        <rect x="415" y="105" width="70" height="35"/>
        <polygon points="415,105 450,72 485,105"/>
        <rect x="443" y="55" width="14" height="20"/>
        <circle cx="450" cy="50" r="6"/>
      </g>
    </svg>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Title, plain text on the normal page background for full readability ---
st.title("🛕 Vaishno Devi Yatra Agent")

# --- One-time DB setup ---
if not os.path.exists("data/yatra_slots_dataset.csv"):
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

def render_steps(current):
    labels = ["1 · Tell us your trip", "2 · Review options", "3 · Confirm booking"]
    html = ""
    for i, label in enumerate(labels, start=1):
        cls = "step-active" if i == current else "step-inactive"
        html += f'<span class="step-pill {cls}">{label}</span>'
    st.markdown(html, unsafe_allow_html=True)

current_step = 2 if st.session_state.pending_plan else 1
render_steps(current_step)

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
        with st.container(border=True):
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
            st.markdown(
                f'<div class="plan-total">Total for {plan["pax"]} pilgrim(s): ₹{plan["total_price"]}</div>',
                unsafe_allow_html=True,
            )

            with st.form(key="booking_form", clear_on_submit=False):
                name = st.text_input("Name for booking")
                submitted = st.form_submit_button("Confirm booking", type="primary")
                if submitted:
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
