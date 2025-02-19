import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

load_dotenv()

# OpenAI pricing details
COST_PER_1K_TOKENS_GPT4_INPUT = 0.03
COST_PER_1K_TOKENS_GPT4_OUTPUT = 0.06

# Expanded Knowledge Base Data
knowledge_base = {
    "What is COREP?": "COREP (Common Reporting) is a standardized reporting framework for credit institutions and investment firms in the EU, focusing on capital adequacy and risk reporting.",
    "What is FINREP?": "FINREP (Financial Reporting) is a standardized EU-wide framework for reporting financial information to supervisory authorities.",
    "What are the key Basel III requirements?": "Basel III key requirements include increased capital ratios, introduction of liquidity coverage ratio (LCR) and net stable funding ratio (NSFR), and enhanced risk management practices.",
    "What is the CRR?": "The Capital Requirements Regulation (CRR) is an EU law that aims to decrease the likelihood that banks go insolvent, implementing Basel III in the EU.",
    "What is Solvency II?": "Solvency II is an EU Directive that codifies and harmonises EU insurance regulation, primarily concerning the amount of capital that EU insurance companies must hold to reduce the risk of insolvency.",
    "What is IFRS 9?": "IFRS 9 is an International Financial Reporting Standard addressing the accounting for financial instruments, replacing IAS 39. It introduces new requirements for classifying and measuring financial instruments and impairment of financial assets.",
    "What is the FRTB?": "The Fundamental Review of the Trading Book (FRTB) is a set of proposals by the Basel Committee on Banking Supervision to improve the capital requirements for market risk.",
    "What is BCBS 239?": "BCBS 239 refers to the Basel Committee on Banking Supervision's principles for effective risk data aggregation and risk reporting, aimed at strengthening banks' risk data aggregation capabilities and internal risk reporting practices.",
    "What is the Dodd-Frank Act?": "The Dodd-Frank Wall Street Reform and Consumer Protection Act is a U.S. federal law enacted in 2010, introducing significant changes to financial regulation in the aftermath of the 2008 financial crisis.",
    "What is MiFID II?": "The Markets in Financial Instruments Directive II (MiFID II) is an EU legislation that regulates firms providing services to clients linked to financial instruments and the venues where those instruments are traded.",
}


def search_knowledge_base(query):
    query_words = set(query.lower().split())
    best_match = None
    highest_score = 0
    threshold = 0.5  # Adjust this value to change the matching sensitivity

    for question, answer in knowledge_base.items():
        question_words = set(question.lower().split())
        score = len(query_words.intersection(question_words)) / len(query_words)

        if score > highest_score:
            highest_score = score
            best_match = answer

    return best_match if highest_score >= threshold else None


def calculate_cost(usage):
    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens
    cost = (input_tokens / 1000) * COST_PER_1K_TOKENS_GPT4_INPUT + (
            output_tokens / 1000) * COST_PER_1K_TOKENS_GPT4_OUTPUT
    return cost, total_tokens


def display_knowledge_base():
    st.header("Regulatory Reporting Knowledge Hub")

    st.subheader("AI-Powered Regulatory Assistant")
    st.write("Ask any questions about regulatory reporting, and our AI will assist you!")

    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'total_cost' not in st.session_state:
        st.session_state['total_cost'] = 0.0

    # Add a reset button
    if st.button("Reset Conversation"):
        st.session_state['chat_history'] = []
        st.session_state['total_cost'] = 0.0
        st.success("Conversation has been reset!")
        st.empty()  # Clear the current content

    # Display chat history
    for message in st.session_state['chat_history']:
        if isinstance(message, dict):
            role = message.get("role", "assistant")
            content = message.get("content", "")
        else:
            role = getattr(message, "role", "assistant")
            content = getattr(message, "content", "")
        st.chat_message(role).write(content)

    user_input = st.text_input("You:", key="user_input", placeholder="E.g., Explain COREP reporting requirements")

    if st.button("Send") and user_input:
        st.session_state['chat_history'].append({"role": "user", "content": user_input})

        knowledge_base_answer = search_knowledge_base(user_input)

        if knowledge_base_answer:
            bot_response = knowledge_base_answer
            st.session_state['chat_history'].append({"role": "assistant", "content": bot_response})
            st.chat_message("assistant").write(bot_response)
        else:
            try:
                formatted_messages = [{"role": msg["role"], "content": msg["content"]} for msg in
                                      st.session_state['chat_history']]

                system_message = """You are an expert AI assistant specializing in regulatory reporting. 
                Focus on providing accurate, up-to-date information on topics like COREP, FINREP, Basel III, 
                and other relevant regulatory frameworks. Offer practical advice and cite official sources when possible.
                If you're not sure about something, please say so rather than making up information."""

                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "system", "content": system_message}] + formatted_messages,
                    max_tokens=500,
                    temperature=0.7
                )

                bot_response = response.choices[0].message.content
                st.session_state['chat_history'].append({"role": "assistant", "content": bot_response})
                st.chat_message("assistant").write(bot_response)

                cost, total_tokens = calculate_cost(response.usage)
                st.session_state['total_cost'] += cost
                st.write(f"Query cost: ${cost:.4f} for {total_tokens} tokens")
                st.write(f"Total cost so far: ${st.session_state['total_cost']:.4f}")

            except Exception as e:
                st.error(f"Error in chatbot response: {str(e)}")
                st.error(f"Error type: {type(e).__name__}")
                st.error(f"Error details: {e.args}")

    # Always display the "Explore Regulatory Reporting Topics" section
    st.subheader("Explore Regulatory Reporting Topics")
    sections = ["Reporting Frameworks", "Compliance Tools", "Regulatory Updates", "Data Quality", "AI in Reporting"]
    selected_section = st.selectbox("Select a topic:", sections)

    if selected_section == "Reporting Frameworks":
        display_reporting_frameworks()
    elif selected_section == "Compliance Tools":
        display_compliance_tools()
    elif selected_section == "Regulatory Updates":
        display_regulatory_updates()
    elif selected_section == "Data Quality":
        display_data_quality()
    elif selected_section == "AI in Reporting":
        display_ai_in_reporting()


def display_reporting_frameworks():
    st.subheader("Regulatory Reporting Frameworks")
    st.markdown("""
    ### Key Reporting Frameworks
    - **COREP (Common Reporting)**: EU framework for capital adequacy and risk reporting.
    - **FINREP (Financial Reporting)**: EU framework for financial information reporting.
    - **Basel III**: Global regulatory framework for bank capital adequacy, stress testing, and market liquidity risk.
    - **Solvency II**: EU Directive for insurance firms' capital requirements.
    - **IFRS 9**: International Financial Reporting Standard for financial instruments.
    - **FRTB (Fundamental Review of the Trading Book)**: Basel Committee framework for market risk capital requirements.
    - **BCBS 239**: Principles for effective risk data aggregation and risk reporting.

    [Learn more about reporting frameworks](#)
    """)


def display_compliance_tools():
    st.subheader("AI-Powered Compliance Tools")
    st.markdown("""
    ### Next-Gen Regulatory Compliance Solutions
    - **Automated Data Validation**: AI-driven tools to ensure data accuracy and completeness.
    - **Predictive Analytics for Risk Assessment**: Machine learning models for proactive risk management.
    - **Natural Language Processing for Regulatory Text**: AI that interprets and summarizes complex regulations.
    - **Intelligent Reporting Dashboards**: Real-time, AI-enhanced visualizations of regulatory metrics.
    - **Automated Regulatory Mapping**: AI tools to map regulations to internal policies and controls.
    - **AI-Driven Scenario Analysis**: Advanced modeling for stress testing and capital planning.

    [Explore our AI compliance suite](#)
    """)


def display_regulatory_updates():
    st.subheader("Latest Regulatory Updates")
    st.markdown("""
    ### Stay Informed with AI-Curated Updates
    - **Basel III Finalization (Basel IV)**:
      - Implementation timeline extended to January 1, 2023, with transitional arrangements to January 1, 2028.
      - Key changes include revisions to the standardized approach for credit risk and operational risk.

    - **ESG Reporting Requirements**:
      - EU Sustainable Finance Disclosure Regulation (SFDR) came into effect on March 10, 2021.
      - Taxonomy Regulation applicable from January 1, 2022, for climate change mitigation and adaptation objectives.

    - **Digital Operational Resilience Act (DORA)**:
      - New EU framework for digital operational resilience for the financial sector.
      - Expected to come into force in late 2022 or early 2023, with a two-year implementation period.

    - **Central Bank Digital Currencies (CBDCs)**:
      - Several central banks, including the ECB and Federal Reserve, are exploring CBDCs.
      - Potential implications for regulatory reporting and compliance.

    - **AI in Financial Services Regulation**:
      - EU's proposed AI Act includes specific provisions for AI use in financial services.
      - Increased focus on explainable AI and algorithmic accountability in regulatory compliance.

    [Subscribe to AI-powered regulatory alerts](#)
    """)


def display_data_quality():
    st.subheader("Data Quality Management")
    st.markdown("""
    ### Ensuring Data Integrity in Regulatory Reporting
    - **[AI-Driven Data Cleansing](#)**: Advanced algorithms for identifying and correcting data anomalies.
    - **[Real-time Data Validation](#)**: Continuous monitoring and validation of regulatory data inputs.
    - **[Data Lineage Tracking](#)**: AI-enhanced tracking of data from source to regulatory report.
    - **[Automated Data Reconciliation](#)**: AI systems to reconcile data across multiple sources and reports.
    - **[Intelligent Data Governance](#)**: AI-powered tools for maintaining data quality standards and policies.

    [Learn about our data quality AI](#)
    """)


def display_ai_in_reporting():
    st.subheader("AI in Regulatory Reporting")
    st.markdown("""
    ### Revolutionizing Reporting with AI
    - **[Automated Report Generation](#)**: AI systems that compile and format regulatory reports.
    - **[Anomaly Detection in Financial Data](#)**: Machine learning models for identifying reporting discrepancies.
    - **[Regulatory Scenario Analysis](#)**: AI-powered stress testing and scenario modeling.
    - **[Chatbots for Regulatory Queries](#)**: Advanced NLP for answering complex regulatory questions.
    - **[Predictive Compliance](#)**: AI models to forecast potential compliance issues before they occur.
    - **[AI-Driven Regulatory Change Management](#)**: Automated impact assessment of new regulations on reporting requirements.

    [Discover the future of AI in reporting](#)
    """)
