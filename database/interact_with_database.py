# interact_with_database.py

import streamlit as st
import pandas as pd
from database.schema import discover_schema
from database.langchain_sql_agent import run_langchain_sql_agent
from database.database_validations import database_validations
from database.impact_analysis import impact_analysis
from langchain_community.utilities import SQLDatabase

def interact_with_database():
    st.header("Interact with Database")

    if 'db_file' not in st.session_state:
        st.session_state['db_file'] = None

    db_file = st.text_input("Enter the path to your Regulatory Reporting DB:", "corep_large_exposure.db")

    if st.button("Load Regulatory Reporting Database"):
        st.session_state['db_file'] = db_file
        st.session_state['schema'] = discover_schema(db_file)
        st.session_state['db'] = SQLDatabase.from_uri(f"sqlite:///{db_file}")
        st.success(f"Regulatory Reporting DB loaded successfully!")

        if st.session_state['schema']:
            schema_data = []
            for table, columns in st.session_state['schema'].items():
                schema_data.append({"Table": table, "Columns": ', '.join(columns)})

            st.session_state['schema_df'] = pd.DataFrame(schema_data)

    if 'schema_df' in st.session_state:
        st.subheader("Database Schema")
        st.dataframe(st.session_state['schema_df'])

    if st.session_state.get('db_file'):
        sub_tabs = st.radio("Select an option", ["Run Query", "Validations", "Impact Analysis"])

        if sub_tabs == "Run Query":
            run_langchain_sql_agent()

        elif sub_tabs == "Validations":
            database_validations()

        elif sub_tabs == "Impact Analysis":
            impact_analysis()
