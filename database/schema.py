import sqlite3
import pandas as pd
import streamlit as st
from sqlite3 import Error


# Database Connection and Schema Discovery Functions
def discover_schema(db_file):
    schema = {}
    try:
        connection = sqlite3.connect(db_file, check_same_thread=False)
        tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = pd.read_sql_query(tables_query, connection)
        for table in tables['name']:
            columns_query = f"PRAGMA table_info({table});"
            columns = pd.read_sql_query(columns_query, connection)
            schema[table] = columns['name'].tolist()
    except Error as e:
        st.error(f"Error discovering schema: {e}")
    finally:
        if connection:
            connection.close()
    return schema
