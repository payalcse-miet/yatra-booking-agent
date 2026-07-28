"""
payment.py
A simulated payment gateway step.

Important: this is a DEMO checkout screen only. It never contacts a
real payment processor, never validates against a real card network,
and nothing entered here should be a real card number, expiry, or CVV.
It exists purely so the booking flow *feels* like a real checkout
(review -> pay -> confirmation) for the prototype/demo.

A production version would integrate a real gateway (Razorpay, Stripe,
etc.) server-side, with the card fields hosted directly by the gateway
so raw card data never touches this app's code at all.
"""

import time

import streamlit as st


def _luhn_ok(card_number):
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 12:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def render_payment_form(amount_label, amount_value):
    """Renders the mock payment form. Returns True once payment is
    'completed' in this render pass (so the caller can proceed to
    create the booking), otherwise False."""
    st.caption("🔒 Demo payment screen — no real transaction occurs. Do not enter a real card number.")

    with st.container(border=True):
        st.markdown(f"**Amount due:** {amount_label} ₹{amount_value}")
        method = st.radio("Pay with", ["Card", "UPI"], horizontal=True)

        with st.form("payment_form"):
            if method == "Card":
                name_on_card = st.text_input("Name on card")
                card_number = st.text_input("Card number", max_chars=19, placeholder="4242 4242 4242 4242")
                col1, col2 = st.columns(2)
                with col1:
                    expiry = st.text_input("Expiry (MM/YY)", max_chars=5, placeholder="12/29")
                with col2:
                    cvv = st.text_input("CVV", max_chars=3, type="password", placeholder="123")
                upi_id = None
            else:
                upi_id = st.text_input("UPI ID", placeholder="yourname@upi")
                name_on_card = card_number = expiry = cvv = None

            pay_clicked = st.form_submit_button(f"Pay ₹{amount_value}", type="primary", use_container_width=True)

        if pay_clicked:
            if method == "Card":
                errors = []
                if not name_on_card or not name_on_card.strip():
                    errors.append("Enter the name on the card.")
                if not _luhn_ok(card_number or ""):
                    errors.append("That card number doesn't look valid.")
                if not expiry or "/" not in expiry:
                    errors.append("Enter expiry as MM/YY.")
                if not cvv or not cvv.isdigit() or len(cvv) != 3:
                    errors.append("CVV should be 3 digits.")
                if errors:
                    for e in errors:
                        st.warning(e)
                    return False
            else:
                if not upi_id or "@" not in upi_id:
                    st.warning("Enter a valid-looking UPI ID (e.g. name@upi).")
                    return False

            with st.spinner("Processing payment..."):
                time.sleep(1.1)
            st.success("Payment successful ✅")
            return True

    return False
