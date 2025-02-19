# auth/user_management.py

import streamlit as st
from .authentication import load_users, check_password, save_user


def initialize_session_state() -> None:
    """Initialize session state variables."""
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'home' not in st.session_state:
        st.session_state['home'] = True


def handle_authentication() -> None:
    """Handle user authentication and registration."""
    if not st.session_state['logged_in']:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("Login"):
                st.session_state['show_login'] = True
                st.session_state['show_register'] = False
        with col2:
            if st.button("Register"):
                st.session_state['show_register'] = True
                st.session_state['show_login'] = False
        
        if st.session_state.get('show_login', False):
            authenticate_user()
        elif st.session_state.get('show_register', False):
            registration_page()
    else:
        st.sidebar.success(f"Logged in as {st.session_state['username']}")
        if st.sidebar.button("Logout", key="logout"):
            log_off()


def authenticate_user():
    """Handles user authentication."""
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username", key="login_username")
    password = st.sidebar.text_input("Password", type="password", key="login_password")
    if st.sidebar.button("Submit Login"):
        users_df = load_users()
        if check_password(username, password, users_df):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.sidebar.success(f"Logged in as {username}")
            st.rerun()  # Changed from st.experimental_rerun()
        else:
            st.sidebar.error("Invalid username or password.")


def registration_page():
    """Provides a user registration interface."""
    st.sidebar.subheader("User Registration")
    username = st.sidebar.text_input("Choose a Username", key="reg_username")
    password = st.sidebar.text_input("Choose a Password", type="password", key="reg_password")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password", key="reg_confirm")
    if st.sidebar.button("Submit Registration"):
        if password == confirm_password:
            if save_user(username, password):
                st.sidebar.success("User registered successfully! You can now log in.")
                st.session_state['show_login'] = True
                st.session_state['show_register'] = False
                st.rerun()  # Changed from st.experimental_rerun()
            else:
                st.sidebar.error("Username already exists. Please choose a different username.")
        else:
            st.sidebar.error("Passwords do not match.")


def log_off():
    """Logs out the current user."""
    for key in ['logged_in', 'username', 'show_login', 'show_register']:
        st.session_state[key] = False if key == 'logged_in' else None
    st.sidebar.success("Successfully logged out.")
    st.rerun()  # Changed from st.experimental_rerun()
