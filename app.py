"""
app.py
Streamlit front-end for the Vaishno Devi Yatra Booking Agent prototype.
Run locally with: streamlit run app.py
"""

import os
from datetime import date, datetime, timedelta

import streamlit as st

import agent
import auth
import db
import explore_data
import payment
from data_gen import build_database


def fmt_time(hhmm):
    """Formats a 24-hour 'HH:MM' string as 12-hour with AM/PM, e.g. '06:00' -> '6:00 AM'.
    Built manually rather than with %-I/%#I strftime flags, since those aren't
    portable between Windows and Mac/Linux."""
    try:
        t = datetime.strptime(str(hhmm), "%H:%M")
        hour_12 = t.hour % 12 or 12
        return f"{hour_12}:{t.minute:02d} {'AM' if t.hour < 12 else 'PM'}"
    except (ValueError, TypeError):
        return str(hhmm)

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
    .mode-badge {
        display:inline-block; font-weight:700; font-size:0.72rem; padding:3px 10px;
        border-radius:999px; margin-left:6px; background:#2E4A66; color:#fff;
    }
    .place-card-title { font-weight:800; font-size:1.02rem; margin-bottom:2px; }
    .place-cat { color:#B33A1E; font-weight:700; font-size:0.75rem; }
    div[data-testid="stExpander"] { border-radius: 12px !important; }

    .search-card {
        background: linear-gradient(180deg, #FFF9F2 0%, #FCEEDD 100%);
        border: 1px solid #F0D3B0;
        border-radius: 18px;
        padding: 1.4rem 1.4rem 0.6rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 6px 20px rgba(179,58,30,0.10);
    }
    .search-card-title { font-family:'Poppins',sans-serif; font-weight:800; font-size:1.05rem; color:#8f3420; margin-bottom:0.8rem; }
    div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #D3491F 0%, #B33A1E 100%) !important;
        border: none !important; font-weight:700 !important; letter-spacing:0.02em;
        box-shadow: 0 4px 14px rgba(179,58,30,0.35) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- One-time DB setup: must happen BEFORE the login gate, since
# signing up/logging in itself touches the users/bookings CSVs, which
# depend on the dataset CSVs already existing. build_database() checks
# each dataset file individually and only (re)builds what's actually
# missing, so it's safe and cheap to call on every run - this also
# self-heals a data/ folder that has some older dataset files (e.g.
# yatra/flights from an earlier version) but not the newer ones
# (trains/buses/users), instead of erroring on the missing ones. ---
with st.spinner("Setting up mock yatra, flight, train & bus data..."):
    build_database()

# --- Login gate: everything below only renders once authenticated ---
auth.require_login()

MODE_ICON = {"flight": "✈️", "train": "🚆", "bus": "🚌"}
MODE_LABEL = {"flight": "Flight", "train": "Train", "bus": "Bus"}

# --- Banner ---
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

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                f"Namaste {st.session_state.auth_display_name}! I'm your Vaishno Devi yatra booking agent (prototype). "
                "Tell me your travel dates, city, and number of pilgrims — I'll compare flights, trains, and buses. E.g. "
                "\"Book for 3 people from Delhi next week, VIP darshan\" or \"2 people from Delhi by train, helicopter darshan.\""
            ),
        }
    ]
if "pending_options" not in st.session_state:
    st.session_state.pending_options = None
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
if "hotel_decision" not in st.session_state:
    st.session_state.hotel_decision = None  # None = not decided yet, {} = skipped, {...} = chosen
if "sightseeing_decision" not in st.session_state:
    st.session_state.sightseeing_decision = None  # None = not decided yet, [] = skipped, [names...] = chosen

# --- Sidebar ---
with st.sidebar:
    st.header(f"👋 {st.session_state.auth_display_name}")
    auth.logout_button()
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
            mode = b.get("transport_mode", "-")
            icon = MODE_ICON.get(mode, "")
            st.write(f"**{icon} {MODE_LABEL.get(mode, 'Transport')}:** {b.get('transport_no', '-')} from {b.get('origin', '-')}")
            if b.get("hotel_name") and str(b.get("hotel_name")) != "nan":
                st.write(f"**🏨 Hotel:** {b.get('hotel_name')} ({b.get('hotel_category', '-')}), {b.get('hotel_nights', '-')} night(s)")
            if b.get("sightseeing_places") and str(b.get("sightseeing_places")) != "nan":
                st.write(f"**🗺️ Sightseeing:** {b.get('sightseeing_places')}")
            st.write(f"**Total:** ₹{b['total_price']}")


def render_steps(current):
    labels = ["1 · Tell us your trip", "2 · Review options", "3 · Add a stay", "4 · Sightseeing", "5 · Pay & confirm"]
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


def _reset_flow():
    st.session_state.pending_options = None
    st.session_state.selected_option = None
    st.session_state.hotel_decision = None
    st.session_state.sightseeing_decision = None


# --- Top-level tabs ---
tab_book, tab_explore = st.tabs(["🎫 Book your yatra", "🗺️ Explore Katra"])

with tab_book:
    if st.session_state.selected_option and st.session_state.hotel_decision is not None and st.session_state.sightseeing_decision is not None:
        current_step = 5
    elif st.session_state.selected_option and st.session_state.hotel_decision is not None:
        current_step = 4
    elif st.session_state.selected_option:
        current_step = 3
    elif st.session_state.pending_options:
        current_step = 2
    else:
        current_step = 1
    render_steps(current_step)

    st.caption(
        "Prototype — bookings are simulated against mock data, not real yatra registration or "
        "airline/rail/bus systems. Payment is a simulated demo checkout."
    )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- STEP 2: selectable option cards, one per transport mode when possible ---
    if st.session_state.pending_options:
        bundle = st.session_state.pending_options
        pax = bundle["pax"]
        options = bundle["options"]

        with st.chat_message("assistant"):
            st.markdown(f"**Here are the top {len(options)} option(s) I found — pick one to continue:**")

            for i, opt in enumerate(options):
                tr, s = opt["flight"], opt["slot"]
                mode = tr.get("mode", "flight")
                icon = MODE_ICON.get(mode, "🚗")
                label = MODE_LABEL.get(mode, mode.title())

                with st.container(border=True):
                    badge_html = f'<span class="option-badge">Option {i + 1}</span><span class="mode-badge">{icon} {label}</span>'
                    if i == 0:
                        badge_html += '<span class="best-badge">💰 Cheapest</span>'
                    st.markdown(badge_html, unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{icon} {label}**")
                        st.write(f"{tr.get('operator', '-')} {tr.get('transport_no', '')}")
                        st.write(f"{tr['origin']} → {tr['destination']}")
                        st.write(f"{tr['travel_date']} at {fmt_time(tr['departure_time'])}")
                        st.write(f"₹{tr['price']} / person")
                    with col2:
                        st.markdown("**🙏 Yatra slot**")
                        st.write(f"{s['category']}")
                        st.write(f"{s['slot_date']} at {fmt_time(s['slot_time'])}")
                        st.write(f"₹{s['price']} / person")

                    st.markdown(
                        f'<div class="plan-total">Total for {pax} pilgrim(s): ₹{opt["total_price"]}</div>',
                        unsafe_allow_html=True,
                    )

                    with st.expander("View full details"):
                        st.write(f"**{label} details**")
                        st.json({
                            "Operator": tr.get("operator", "-"), "Number": tr.get("transport_no", "-"),
                            "Route": f"{tr['origin']} → {tr['destination']}", "Date": tr["travel_date"],
                            "Departure": fmt_time(tr["departure_time"]), "Duration": f"{tr.get('duration_mins', '-')} min",
                            "Seats left": tr["seats_available"], "Fare / person": f"₹{tr['price']}",
                        })
                        st.write("**Yatra slot details**")
                        st.json({
                            "Category": s["category"], "Date": s["slot_date"], "Time": fmt_time(s["slot_time"]),
                            "Seats left": s["seats_available"], "Fee / person": f"₹{s['price']}",
                        })

                    if st.button(f"Select option {i + 1}", key=f"select_opt_{i}", type="primary", use_container_width=True):
                        st.session_state.selected_option = {"pax": pax, "option": opt}
                        st.session_state.pending_options = None
                        st.rerun()

            if st.button("← Start over", key="restart_from_step2"):
                _reset_flow()
                st.rerun()

    # --- STEP 3: optional hotel stay in Katra, plus how-to-reach-Katra taxi info ---
    elif st.session_state.selected_option and st.session_state.hotel_decision is None:
        bundle = st.session_state.selected_option
        pax, opt = bundle["pax"], bundle["option"]
        tr, s = opt["flight"], opt["slot"]
        check_in_default = tr["travel_date"]

        with st.chat_message("assistant"):
            st.markdown("**Getting to Katra, and where to stay:**")

            taxi = explore_data.get_taxi_info()
            with st.container(border=True):
                st.markdown(f"🚕 **{taxi['route']}** · {taxi['distance']} · {taxi['duration']}")
                for opt_taxi in taxi["options"]:
                    st.write(f"- {opt_taxi['vehicle']} (up to {opt_taxi['capacity']}): {opt_taxi['fare_range']}")
                st.caption(taxi["note"])
                if tr.get("mode") != "flight":
                    st.caption(f"Note: since you're arriving in Katra directly by {MODE_LABEL.get(tr.get('mode'), 'this mode')}, you may not need this leg — it mainly applies to flight arrivals via Jammu Airport.")

            st.markdown("**🏨 Would you like to add a hotel stay in Katra?**")

            with st.form("hotel_form"):
                want_hotel = st.radio("Add a hotel?", ["No, skip this", "Yes, show me hotels"], horizontal=True)
                col1, col2 = st.columns(2)
                with col1:
                    hotel_category_choice = st.selectbox("Category", ["Any", "Budget", "Mid-Range", "Premium"])
                with col2:
                    nights = st.number_input("Nights", min_value=1, max_value=7, value=1)
                hotel_search_clicked = st.form_submit_button("Continue", type="primary", use_container_width=True)

            if hotel_search_clicked:
                if want_hotel == "No, skip this":
                    st.session_state.hotel_decision = {}
                    st.rerun()
                else:
                    hotels = db.search_hotels(
                        check_in_default,
                        category=None if hotel_category_choice == "Any" else hotel_category_choice,
                    )
                    st.session_state[f"_hotel_results"] = {"hotels": hotels, "nights": nights}

            hotel_results = st.session_state.get("_hotel_results")
            if hotel_results:
                hotels, nights = hotel_results["hotels"], hotel_results["nights"]
                if not hotels:
                    st.warning("No hotels found for that category on this date. Try 'Any' category or skip.")
                else:
                    for h in hotels[:5]:
                        with st.container(border=True):
                            st.markdown(f"**{h['name']}** · {h['category']}")
                            st.write(f"₹{h['price_per_night']}/night · {nights} night(s) → ₹{h['price_per_night'] * nights} total")
                            st.caption(f"{h['rooms_available']} rooms left for check-in {check_in_default}")
                            if st.button(f"Select {h['name']}", key=f"select_hotel_{h['id']}", use_container_width=True):
                                st.session_state.hotel_decision = {"hotel": h, "nights": nights}
                                st.session_state.pop("_hotel_results", None)
                                st.rerun()

            if st.button("← Back to options", key="back_to_step2_from_hotel"):
                st.session_state.pending_options = {"pax": pax, "options": [opt]}
                st.session_state.selected_option = None
                st.rerun()

    # --- STEP 4: optional sightseeing after darshan, using the Explore Katra data ---
    elif st.session_state.selected_option and st.session_state.hotel_decision is not None and st.session_state.sightseeing_decision is None:
        bundle = st.session_state.selected_option
        pax, opt = bundle["pax"], bundle["option"]

        with st.chat_message("assistant"):
            st.markdown("**Planning to visit any tourist places after darshan?**")
            st.caption("These places aren't bookable — just recommendations with local-travel guidance, so you can plan your time.")

            want_sightseeing = st.radio(
                "Interested in sightseeing after darshan?",
                ["No, skip this", "Yes, show me places"],
                horizontal=True,
                key="sightseeing_radio",
            )

            if want_sightseeing == "No, skip this":
                if st.button("Continue", type="primary", key="skip_sightseeing", use_container_width=True):
                    st.session_state.sightseeing_decision = []
                    st.rerun()
            else:
                categories = ["All"] + explore_data.get_categories()
                chosen_cat = st.selectbox("Filter by category", categories, key="sightseeing_cat_filter")
                places = explore_data.get_places(None if chosen_cat == "All" else chosen_cat)

                st.markdown("Select any places you'd like added to your trip notes:")
                picked = []
                for p in places:
                    with st.container(border=True):
                        checked = st.checkbox(
                            f"**{p['name']}** · {p['category']} · {p['distance']}",
                            key=f"sight_{p['name']}",
                        )
                        st.caption(p["description"])
                        st.caption(f"🚕 Getting there: {explore_data.get_local_travel_note(p['category'])}")
                        if checked:
                            picked.append(p["name"])

                if st.button("Continue with selected places", type="primary", key="confirm_sightseeing", use_container_width=True):
                    st.session_state.sightseeing_decision = picked
                    st.rerun()

            if st.button("← Back", key="back_to_step3_from_sightseeing"):
                st.session_state.hotel_decision = None
                st.rerun()

    # --- STEP 5: payment gateway, then confirm the booking ---
    elif st.session_state.selected_option:
        bundle = st.session_state.selected_option
        pax, opt = bundle["pax"], bundle["option"]
        tr, s = opt["flight"], opt["slot"]
        mode = tr.get("mode", "flight")
        icon = MODE_ICON.get(mode, "🚗")
        hotel_choice = st.session_state.hotel_decision or {}
        hotel = hotel_choice.get("hotel")
        hotel_nights = hotel_choice.get("nights", 0)
        hotel_cost = (hotel["price_per_night"] * hotel_nights) if hotel else 0
        grand_total = opt["total_price"] + hotel_cost
        sightseeing_places = st.session_state.sightseeing_decision or []

        with st.chat_message("assistant"):
            st.markdown("**Review & pay to confirm your booking:**")
            with st.container(border=True):
                st.write(f"{icon} {tr.get('operator', '-')} {tr.get('transport_no', '')} · {tr['origin']} → {tr['destination']} · {tr['travel_date']}")
                st.write(f"🙏 {s['category']} · {s['slot_date']} at {fmt_time(s['slot_time'])}")
                st.write(f"👥 {pax} pilgrim(s)")
                if hotel:
                    st.write(f"🏨 {hotel['name']} ({hotel['category']}) · {hotel_nights} night(s) · ₹{hotel_cost}")
                else:
                    st.write("🏨 No hotel added")
                if sightseeing_places:
                    st.write(f"🗺️ Planning to visit: {', '.join(sightseeing_places)}")
                else:
                    st.write("🗺️ No sightseeing planned")

            paid = payment.render_payment_form("Total for this booking:", grand_total)

            if paid:
                booking_id = agent.confirm_booking(
                    opt, pax, st.session_state.auth_display_name,
                    hotel=hotel, hotel_nights=hotel_nights,
                    sightseeing_places=sightseeing_places,
                )
                st.balloons()
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"✅ Booked! Your confirmation ID is **{booking_id}**. Total paid (mock): ₹{grand_total}.",
                    }
                )
                _reset_flow()
                st.rerun()

            if st.button("← Back", key="back_to_step4"):
                st.session_state.sightseeing_decision = None
                st.rerun()

    # --- STEP 1: MakeMyTrip-style search form, plus an optional free-text fallback ---
    else:

        def _handle_search_result(result, user_summary):
            """Shared by both the dropdown form and the free-text box: appends
            the exchange to chat history and stashes options for step 2."""
            st.session_state.messages.append({"role": "user", "content": user_summary})

            if result["status"] in ("NEEDS_INFO", "NO_AVAILABILITY", "NO_COMBINATION"):
                reply = result["message"]
            elif result["status"] == "PLAN_READY":
                modes_found = sorted({o["flight"]["mode"] for o in result["options"]})
                mode_str = ", ".join(MODE_LABEL.get(m, m) for m in modes_found)
                reply = (
                    f"Found a plan across {result['alt_flights_count']} travel option(s) and "
                    f"{result['alt_slots_count']} yatra slot option(s). Here are the top "
                    f"{len(result['options'])} to compare ({mode_str}) below."
                )
                st.session_state.pending_options = {"pax": result["pax"], "options": result["options"]}
            else:
                reply = "Something went wrong — could you try again with a city, date, and number of pilgrims?"

            st.session_state.messages.append({"role": "assistant", "content": reply})

        origins = db.get_distinct_origins()

        with st.container():
            st.markdown('<div class="search-card">', unsafe_allow_html=True)
            st.markdown('<div class="search-card-title">🔍 Search flights, trains & buses to Katra</div>', unsafe_allow_html=True)

            with st.form("search_form"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    origin = st.selectbox("📍 From", origins, index=origins.index("Delhi") if "Delhi" in origins else 0)
                with c2:
                    mode_choice = st.selectbox("🚦 Travel by", ["Any", "Flight", "Train", "Bus"])
                with c3:
                    pax = st.selectbox("👥 Pilgrims", list(range(1, 11)), index=0)

                c4, c5 = st.columns(2)
                with c4:
                    category_choice = st.selectbox(
                        "🙏 Darshan type", ["Any", "Normal Darshan", "VIP Darshan", "Helicopter Darshan"]
                    )
                with c5:
                    min_date = date.today()
                    max_date = date.today() + timedelta(days=44)
                    default_date = min(min_date + timedelta(days=7), max_date)
                    journey_date = st.date_input(
                        "📅 Journey date", value=default_date, min_value=min_date, max_value=max_date
                    )

                search_clicked = st.form_submit_button("🔍 Search", type="primary", use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        if search_clicked:
            request = {
                "pax": pax,
                "origin": origin,
                "category": None if category_choice == "Any" else category_choice,
                "mode": None if mode_choice == "Any" else mode_choice.lower(),
                "start_date": journey_date.isoformat(),
                "end_date": journey_date.isoformat(),
            }
            with st.spinner("Checking slots, flights, trains & buses..."):
                result = agent.build_plan(request)

            summary = f"{pax} pilgrim(s) from {origin} on {journey_date.isoformat()}"
            if mode_choice != "Any":
                summary += f", by {mode_choice}"
            if category_choice != "Any":
                summary += f", {category_choice}"
            _handle_search_result(result, summary)
            st.rerun()

with tab_explore:
    st.subheader("Getting from Jammu to Katra")
    taxi = explore_data.get_taxi_info()
    with st.container(border=True):
        st.markdown(f"🚕 **{taxi['route']}** · {taxi['distance']} · {taxi['duration']}")
        for opt_taxi in taxi["options"]:
            st.write(f"- {opt_taxi['vehicle']} (up to {opt_taxi['capacity']}): {opt_taxi['fare_range']}")
        st.caption(taxi["note"])

    st.subheader("Places to see around Katra & Jammu")
    st.caption(
        "Informational only — not bookable through this app. Distances are approximate, "
        "drawn from general pilgrimage-tourism sources."
    )

    categories = ["All"] + explore_data.get_categories()
    chosen = st.selectbox("Filter by category", categories)
    places = explore_data.get_places(None if chosen == "All" else chosen)

    for p in places:
        with st.container(border=True):
            st.markdown(f'<div class="place-card-title">{p["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<span class="place-cat">{p["category"]}</span> · {p["distance"]}', unsafe_allow_html=True)
            st.write(p["description"])
            st.caption(f"🚕 Getting there: {explore_data.get_local_travel_note(p['category'])}")
