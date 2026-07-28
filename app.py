"""
app.py
Streamlit front-end for the Vaishno Devi Yatra Booking Agent prototype.
Run locally with: streamlit run app.py
"""

import os
import streamlit as st

import agent
import auth
import db
import payment
from data_gen import build_database

st.set_page_config(page_title="Vaishno Devi Yatra Agent", page_icon="🛕", layout="centered")

# --- Custom styling ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Poppins', sans-serif; }

    .stChatMessage { border-radius: 14px; }
    div[data-testid="stChatMessage"] { padding: 4px 0; }

    .banner-wrap {
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 24px rgba(179,58,30,0.22);
    }
    .step-pill {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    .step-active { background: #B33A1E; color: #FFFFFF; box-shadow: 0 3px 10px rgba(179,58,30,0.35); }
    .step-done { background: #E8C097; color: #5c3a22; }
    .step-inactive { background: #FCEEDD; color: #a88a6f; }

    .plan-total {
        font-size: 1.15rem;
        font-weight: 800;
        color: #B33A1E;
        margin-top: 0.4rem;
    }
    .option-badge {
        display:inline-block; background:#FCEEDD; color:#B33A1E; font-weight:700;
        font-size:0.75rem; padding:3px 10px; border-radius:999px; margin-bottom:6px;
    }
    .best-badge {
        display:inline-block; background:#1E8449; color:#fff; font-weight:700;
        font-size:0.72rem; padding:3px 10px; border-radius:999px; margin-left:6px;
    }
    div[data-testid="stExpander"] { border-radius: 12px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Login gate: everything below only renders once authenticated ---
auth.require_login()

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

st.title("🛕 Vaishno Devi Yatra Agent")

# --- One-time DB setup ---
if not os.path.exists("data/yatra_slots_dataset.csv"):
    with st.spinner("Setting up mock yatra & flight data..."):
        build_database()
else:
    db.ensure_live_data()

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                f"Namaste {st.session_state.auth_display_name}! I'm your Vaishno Devi yatra booking agent (prototype). "
                "Tell me your travel dates, city, and number of pilgrims, e.g. "
                "\"Book for 3 people from Delhi next week, VIP darshan.\""
            ),
        }
    ]
if "pending_options" not in st.session_state:
    st.session_state.pending_options = None  # {"pax":.., "options":[...]}
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None  # {"pax":.., "option":{...}}

# --- Sidebar ---
with st.sidebar:
    st.header(f"👋 {st.session_state.auth_display_name}")
    auth.logout_button()
    st.divider()

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
    bookings = db.list_bookings(user_name=st.session_state.auth_display_name)
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
    labels = ["1 · Tell us your trip", "2 · Review options", "3 · Pay & confirm"]
    html = ""
    for i, label in enumerate(labels, start=1):
        if i == current:
            cls = "step-active"
        elif i < current:
            cls = "step-done"
        else:
            cls = "step-inactive"
        html += f'<span class="step-pill {cls}">{label}</span>'
    st.markdown(html, unsafe_allow_html=True)


if st.session_state.selected_option:
    current_step = 3
elif st.session_state.pending_options:
    current_step = 2
else:
    current_step = 1
render_steps(current_step)

st.caption("Prototype — bookings are simulated against mock data, not real yatra registration or airline systems. Payment is a simulated demo checkout.")

# --- Chat history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


def _reset_flow():
    st.session_state.pending_options = None
    st.session_state.selected_option = None


# --- STEP 2: render selectable, clickable option cards ---
if st.session_state.pending_options:
    bundle = st.session_state.pending_options
    pax = bundle["pax"]
    options = bundle["options"]

    with st.chat_message("assistant"):
        st.markdown(f"**Here are the top {len(options)} option(s) I found — pick one to continue:**")

        for i, opt in enumerate(options):
            f, s = opt["flight"], opt["slot"]
            with st.container(border=True):
                badge_html = f'<span class="option-badge">Option {i + 1}</span>'
                if i == 0:
                    badge_html += '<span class="best-badge">💰 Cheapest</span>'
                st.markdown(badge_html, unsafe_allow_html=True)

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
                    f'<div class="plan-total">Total for {pax} pilgrim(s): ₹{opt["total_price"]}</div>',
                    unsafe_allow_html=True,
                )

                with st.expander("View full flight & yatra slot details"):
                    st.write("**Flight details**")
                    st.json({
                        "Flight no.": f["flight_no"], "Airline": f["airline"],
                        "Route": f"{f['origin']} → {f['destination']}", "Date": f["flight_date"],
                        "Departure": f["departure_time"], "Duration": f"{f.get('duration_mins', '-')} min",
                        "Stops": f.get("stops", "-"), "Seats left": f["seats_available"],
                        "Fare / person": f"₹{f['price']}",
                    })
                    st.write("**Yatra slot details**")
                    st.json({
                        "Category": s["category"], "Date": s["slot_date"], "Time": s["slot_time"],
                        "Seats left": s["seats_available"], "Fee / person": f"₹{s['price']}",
                    })

                if st.button(f"Select option {i + 1}", key=f"select_opt_{i}", type="primary", use_container_width=True):
                    st.session_state.selected_option = {"pax": pax, "option": opt}
                    st.session_state.pending_options = None
                    st.rerun()

        if st.button("← Start over", key="restart_from_step2"):
            _reset_flow()
            st.rerun()

# --- STEP 3: payment gateway, then confirm the booking ---
elif st.session_state.selected_option:
    bundle = st.session_state.selected_option
    pax, opt = bundle["pax"], bundle["option"]
    f, s = opt["flight"], opt["slot"]

    with st.chat_message("assistant"):
        st.markdown("**Review & pay to confirm your booking:**")
        with st.container(border=True):
            st.write(f"✈️ {f['airline']} {f['flight_no']} · {f['origin']} → {f['destination']} · {f['flight_date']}")
            st.write(f"🙏 {s['category']} · {s['slot_date']} at {s['slot_time']}")
            st.write(f"👥 {pax} pilgrim(s)")

        paid = payment.render_payment_form("Total for this booking:", opt["total_price"])

        if paid:
            booking_id = agent.confirm_booking(opt, pax, st.session_state.auth_display_name)
            st.balloons()
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"✅ Booked! Your confirmation ID is **{booking_id}**. Total paid (mock): ₹{opt['total_price']}.",
                }
            )
            _reset_flow()
            st.rerun()

        if st.button("← Back to options", key="back_to_step2"):
            st.session_state.pending_options = {"pax": pax, "options": [opt]}
            st.session_state.selected_option = None
            st.rerun()

# --- STEP 1: chat input ---
else:
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
                    f"{result['alt_slots_count']} yatra slot option(s). Here are the top "
                    f"{len(result['options'])} to compare below."
                )
                st.session_state.pending_options = {"pax": result["pax"], "options": result["options"]}
            else:
                reply = "Something went wrong understanding that — could you rephrase with your city, dates, and number of pilgrims?"

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        if result["status"] == "PLAN_READY":
            st.rerun()
