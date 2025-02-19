import streamlit as st
import logging
from datetime import datetime
import time


def save_feedback_to_file(feedback: str) -> None:
    """
    Save the feedback to a file and log the action.

    Args:
        feedback (str): The feedback text to save.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_feedback = f"[{timestamp}] {feedback}\n"

    with open("feedback.txt", "a") as file:
        file.write(formatted_feedback)

    logging.info(f"Feedback saved: {feedback[:50]}...")  # Log first 50 chars


def feedback_section():
    """Display the feedback section in the Streamlit sidebar."""
    st.sidebar.markdown("## Feedback")

    if 'feedback' not in st.session_state:
        st.session_state.feedback = ""

    def submit_feedback():
        if st.session_state.feedback.strip():
            save_feedback_to_file(st.session_state.feedback)
            st.sidebar.success("Thank you for your valuable feedback!")
            time.sleep(2)  # Wait for 2 seconds
            st.session_state.feedback = ""  # Clear the feedback
        else:
            st.sidebar.warning("Please enter your feedback before submitting.")

    feedback = st.sidebar.text_area(
        "We value your input. Please share your thoughts or report any issues:",
        max_chars=500,
        key="feedback"
    )

    st.sidebar.button("Submit Feedback", on_click=submit_feedback, type="primary")