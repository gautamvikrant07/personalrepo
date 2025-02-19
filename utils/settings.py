import streamlit as st
from utils.session_management import save_user_preferences, load_user_preferences


def settings():
    st.title("Regulatory Reporting Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.header("AI and Data Infrastructure")
        ai_model = st.selectbox("AI Model", ["GPT-4", "GPT-3.5", "Claude", "BERT"])
        embedding_model = st.selectbox("Embedding Model", ["OpenAI", "HuggingFace", "Custom"])
        database = st.selectbox("Database", ["PostgreSQL", "MongoDB", "SQLite", "Elasticsearch"])

        st.header("Regulatory Preferences")
        jurisdictions = st.multiselect("Jurisdictions", ["US", "EU", "UK", "APAC", "Global"])
        industries = st.multiselect("Industries", ["Banking", "Insurance", "Securities", "Fintech", "Healthcare"])

        st.subheader("Regulators")
        regulators = {
            "SEC (US Securities and Exchange Commission)": "https://www.sec.gov/",
            "EBA (European Banking Authority)": "https://www.eba.europa.eu/",
            "RBI (Reserve Bank of India)": "https://www.rbi.org.in/",
            "PRA (Prudential Regulation Authority, UK)": "https://www.bankofengland.co.uk/prudential-regulation",
            "FINRA (Financial Industry Regulatory Authority)": "https://www.finra.org/",
            "ESMA (European Securities and Markets Authority)": "https://www.esma.europa.eu/",
            "APRA (Australian Prudential Regulation Authority)": "https://www.apra.gov.au/",
            "HKMA (Hong Kong Monetary Authority)": "https://www.hkma.gov.hk/",
            "MAS (Monetary Authority of Singapore)": "https://www.mas.gov.sg/",
            "OSFI (Office of the Superintendent of Financial Institutions, Canada)": "https://www.osfi-bsif.gc.ca/",
            "BaFin (Federal Financial Supervisory Authority, Germany)": "https://www.bafin.de/",
            "JFSA (Japan Financial Services Agency)": "https://www.fsa.go.jp/en/",
            "CFTC (Commodity Futures Trading Commission)": "https://www.cftc.gov/",
            "FCA (Financial Conduct Authority, UK)": "https://www.fca.org.uk/",
        }
        selected_regulators = st.multiselect(
            "Select Regulators",
            options=list(regulators.keys()),
            format_func=lambda x: x.split(" (")[0]
        )
        if selected_regulators:
            st.write("Selected regulator websites:")
            for reg in selected_regulators:
                st.markdown(f"- [{reg.split(' (')[0]}]({regulators[reg]})")

    with col2:
        st.header("Document and Source Settings")
        preferred_websites = st.text_area("Preferred Regulatory Websites",
                                          placeholder="Enter URLs, one per line")
        document_types = st.multiselect("Preferred Document Types",
                                        ["Regulations", "Guidance", "Consultation Papers",
                                         "Enforcement Actions", "Industry Letters"])

        uploaded_file = st.file_uploader("Upload additional document types", type=['txt', 'csv'])
        if uploaded_file:
            uploaded_content = uploaded_file.read().decode('utf-8')
            uploaded_types = [line.strip() for line in uploaded_content.splitlines() if line.strip()]
            document_types.extend(uploaded_types)

    st.header("Reporting and Notification Settings")
    col3, col4 = st.columns(2)
    with col3:
        language = st.selectbox("Preferred Language", ["English", "Spanish", "French", "German", "Mandarin"])

    with col4:
        notification_types = st.multiselect("Notification Types",
                                            ["Email", "In-app", "SMS", "API Webhook"])


    if st.button("Save Configuration", type="primary"):
        preferences = {
            'ai_model': ai_model,
            'embedding_model': embedding_model,
            'database': database,
            'jurisdictions': jurisdictions,
            'industries': industries,
            'selected_regulators': selected_regulators,
            'preferred_websites': [w.strip() for w in preferred_websites.split('\n') if w.strip()],
            'document_types': document_types,
            'language': language,
            'notification_types': notification_types,
        }
        save_user_preferences(preferences)
        st.success("Configuration saved successfully!")

    st.header("Current Configuration")
    current_preferences = load_user_preferences()
    for key, value in current_preferences.items():
        if isinstance(value, list):
            st.write(f"**{key.replace('_', ' ').title()}:** {', '.join(map(str, value))}")
        else:
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
