import json
import os
import openai
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from utils.session_management import save_session_history, submit_feedback

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key

# Initialize LangChain's ChatOpenAI as the LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Define a prompt template for interacting with XBRL data
xbrl_prompt_template = PromptTemplate.from_template(
    "You are an XBRL data assistant specialized in financial data analysis. Based on the provided XBRL data, perform the following tasks:\n"
    "1. Summarize the overall financial position, highlighting key figures like total revenue, net income, and total assets.\n"
    "2. Identify and explain any significant trends or anomalies.\n"
    "3. Provide any additional insights based on the available data.\n"
    "Ensure your response is clear, concise, and in plain language suitable for a financial analyst.\n"
    "\nData Provided:\n{context}\n"
    "Your response should include:\n"
    "{{\n"
    '  "summary": "Summary of the financial position",\n'
    '  "keyMetrics": [\n'
    '    {{"name": "Metric Name", "value": "Metric Value", "description": "Description of the metric"}},\n'
    '    ...\n'
    '  ],\n'
    '  "insights": "Additional insights and observations."\n'
    '}}\n'
)


def format_ai_response(ai_response):
    """
    Format the AI response to make it more readable and professional.
    """
    try:
        # Parse the JSON response from the AI
        data = json.loads(ai_response)

        # Extracting and formatting the key components
        summary = data.get("summary", "No summary available.")
        key_metrics = data.get("keyMetrics", [])
        insights = data.get("insights", "No additional insights available.")

        # Build the formatted response
        formatted_response = f"**Summary:**\n{summary}\n\n**Key Metrics:**\n"

        for metric in key_metrics:
            name = metric.get("name", "Unknown Metric")
            value = metric.get("value", "N/A")
            description = metric.get("description", "No description available.")
            formatted_response += f"- **{name}:**\n  - **Current Year vs Prior Year:** {value}\n  - **Description:** {description}\n\n"

        formatted_response += f"**Insights:**\n{insights}"

        return formatted_response

    except json.JSONDecodeError as e:
        return f"Error formatting AI response: {e}"


def interact_with_xbrl():
    st.header("Interact with XBRL Reports")

    # Initialize session state variables if not already set
    if 'feedback_dict' not in st.session_state:
        st.session_state.feedback_dict = {}
    if 'xbrl_data' not in st.session_state:
        st.session_state.xbrl_data = []
    if "chat_history_xbrl" not in st.session_state:
        st.session_state.chat_history_xbrl = [
            AIMessage(content="Hello, I am your XBRL data assistant. How can I help you with the XBRL reports today?")
        ]
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Allow the user to upload XBRL files
    uploaded_xbrl_files = st.file_uploader("Upload XBRL files for analysis", type=["xml", "xbrl"],
                                           accept_multiple_files=True)

    if uploaded_xbrl_files:
        try:
            # Read and decode each uploaded file
            for xbrl_file in uploaded_xbrl_files:
                xbrl_content = xbrl_file.read().decode("utf-8")
                st.session_state.xbrl_data.append(xbrl_content)
            st.success(f"Uploaded {len(uploaded_xbrl_files)} XBRL file(s) successfully!")
        except Exception as e:
            st.error(f"Error reading XBRL files: {e}")

    if st.session_state.xbrl_data:
        # Debug: Display the loaded XBRL data for verification
        st.write("Debug: Loaded XBRL data for analysis:", st.session_state.xbrl_data)

        # Chat interface for interacting with XBRL data
        user_query_xbrl = st.chat_input("Ask a question about the XBRL data...")

        if user_query_xbrl:
            try:
                # Retrieve the most relevant context for the query
                context = "\n\n".join(st.session_state.xbrl_data[:4000])  # Limit context size for prompt

                # Format the input data using the LangChain prompt template
                prompt_input = xbrl_prompt_template.format(context=context)

                # Invoke the LLM with the formatted prompt
                response = llm.invoke(prompt_input)

                # Extract content from the AIMessage object
                if hasattr(response, 'content'):
                    result_text = response.content
                else:
                    st.error("Unexpected LLM output format.")
                    result_text = "An unexpected error occurred with the AI response."

                # Format the AI response
                formatted_response = format_ai_response(result_text)

                # Update chat history
                st.session_state.chat_history_xbrl.append(HumanMessage(content=user_query_xbrl))
                st.session_state.chat_history_xbrl.append(AIMessage(content=formatted_response))

                # Save chat history for XBRL tab
                save_session_history(user_query_xbrl, formatted_response, "Interact with XBRL Reports")

            except Exception as e:
                st.error(f"Error generating response: {e}")
                st.session_state.chat_history_xbrl.append(AIMessage(content=f"An error occurred: {e}"))

        # Display chat history
        for i, message in enumerate(st.session_state.chat_history_xbrl):
            if isinstance(message, AIMessage):
                with st.chat_message("AI"):
                    st.write(message.content)
                    feedback_key = f"feedback_{i}"
                    if feedback_key not in st.session_state.feedback_dict:
                        st.radio("Rate this response:", options=["👎", "👍"], key=feedback_key,
                                 on_change=submit_feedback, args=(feedback_key,))
                    else:
                        st.write(f"Your feedback: {st.session_state.feedback_dict[feedback_key]}")
            elif isinstance(message, HumanMessage):
                with st.chat_message("Human"):
                    st.write(message.content)
