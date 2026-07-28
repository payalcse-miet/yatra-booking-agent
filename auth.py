"""
auth.py
A lightweight login/sign-up gate for the prototype.

This is demo-grade auth, not production security:
- passwords are hashed (SHA-256) but not salted
- there's no session expiry, email verification, or rate limiting
A real deployment would swap this for a proper identity provider.

Seeded demo accounts (see build_dataset.py):
    demo  / demo123
    guest / guest123
"""

import streamlit as st

import db


def _login_styles():
    st.markdown(
        """
        <style>
        .auth-wrap { max-width: 420px; margin: 2.5rem auto 0 auto; }
        .auth-title { text-align:center; font-size:1.8rem; font-weight:800; margin-bottom:0.2rem; }
        .auth-sub { text-align:center; color:#7a5c46; margin-bottom:1.6rem; }
        .auth-demo { text-align:center; font-size:0.82rem; color:#9c7c5f; margin-top:0.8rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def require_login():
    """Renders a login/sign-up page and halts the rest of the app until
    a user is authenticated. Call this at the very top of app.py."""
    if st.session_state.get("auth_user"):
        return  # already logged in

    _login_styles()
    st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="auth-title">🛕 Vaishno Devi Yatra Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Sign in to plan and book your yatra</div>', unsafe_allow_html=True)

    tab_login, tab_signup, tab_guest = st.tabs(["Log in", "Sign up", "Guest access"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)
            if submitted:
                display_name = db.verify_user(username, password)
                if display_name:
                    st.session_state.auth_user = username.strip().lower()
                    st.session_state.auth_display_name = display_name
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")
        st.markdown(
            '<div class="auth-demo">Demo account: <b>demo</b> / <b>demo123</b></div>',
            unsafe_allow_html=True,
        )

    with tab_signup:
        with st.form("signup_form"):
            new_name = st.text_input("Your name", key="signup_name")
            new_username = st.text_input("Choose a username", key="signup_username")
            new_password = st.text_input("Choose a password", type="password", key="signup_password")
            submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if submitted:
                ok, error = db.create_user(new_username, new_password, new_name)
                if ok:
                    st.session_state.auth_user = new_username.strip().lower()
                    st.session_state.auth_display_name = new_name.strip() or new_username
                    st.success("Account created!")
                    st.rerun()
                else:
                    st.error(error)

    with tab_guest:
        st.write("Skip account creation and try the agent right away. Guest bookings still save to your session's booking history.")
        if st.button("Continue as guest", use_container_width=True):
            st.session_state.auth_user = "guest"
            st.session_state.auth_display_name = "Guest"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


def logout_button():
    if st.sidebar.button("Log out", use_container_width=True):
        for key in ("auth_user", "auth_display_name"):
            st.session_state.pop(key, None)
        st.rerun()
