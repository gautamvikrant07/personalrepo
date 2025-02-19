from langchain_community.utilities import SQLDatabase
import streamlit as st


def connect_to_sqlite(db_file):
    try:
        db = SQLDatabase.from_uri(f"sqlite:///{db_file}")
        return db
    except Exception as e:
        st.error(f"Error connecting to SQLite: {e}")
        return None
