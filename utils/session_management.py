import streamlit as st


def save_session_history(query, result, tab_name):
    """
    Save the history of user interactions with the application.

    Parameters:
    - query (str): The user's query or action.
    - result: The result of the query or action.
    - tab_name (str): The name of the tab or section where the interaction occurred.
    """
    if 'session_history' not in st.session_state:
        st.session_state.session_history = []
    st.session_state.session_history.append({
        'tab': tab_name,
        'query': query,
        'result': result
    })


def display_session_history():
    """
    Display the user's session history, showing all past interactions.
    """
    if 'session_history' in st.session_state:
        st.header("Session History")
        for entry in st.session_state.session_history:
            st.subheader(f"Tab: {entry.get('tab', 'Unknown')}")
            st.write(f"Query: {entry.get('query', 'N/A')}")
            st.write("Result:")
            st.write(entry.get('result', 'No result available'))
    else:
        st.write("No session history available.")


def save_user_preferences(preferences):
    """
    Save user preferences to the session state.

    Parameters:
    - preferences (dict): A dictionary containing the user's preferences.
    """
    st.session_state.user_preferences = preferences


def load_user_preferences():
    """
    Load user preferences from the session state.

    Returns:
    - dict: The user preferences stored in session state, or default values if none exist.
    """
    return st.session_state.get('user_preferences', {
        'preferred_websites': [],
        'document_types': []
    })


def submit_feedback(message_index):
    """
    Saves user feedback for a specific message.

    Parameters:
    - message_index (int): The index of the message in the chat history for which feedback is being provided.
    """
    feedback = st.session_state.get(f"feedback_{message_index}", "")
    if 'feedback' not in st.session_state:
        st.session_state['feedback'] = {}
    st.session_state.feedback[message_index] = feedback
    st.success("Thank you for your feedback!")