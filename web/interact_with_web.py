import streamlit as st
from langchain.schema import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI  # Updated import
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.callbacks.manager import get_openai_callback
from utils.session_management import save_session_history
from .url_interaction import validate_url, get_url_metadata, get_vectorstore_from_urls, summarize_url_content, get_vectorstore_from_pdfs
from .web_interaction import get_response

def interact_with_web():
    st.header("Interact with Web")
    
    # Initialize session state variables
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0
    if "total_cost" not in st.session_state:
        st.session_state.total_cost = 0
    if "prompt_tokens" not in st.session_state:
        st.session_state.prompt_tokens = 0
    if "completion_tokens" not in st.session_state:
        st.session_state.completion_tokens = 0
    if "successful_requests" not in st.session_state:
        st.session_state.successful_requests = 0
    if "model_usage" not in st.session_state:
        st.session_state.model_usage = {}

    # Sidebar for LLM parameters
    st.sidebar.header("LLM Parameters")
    temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    model_name = st.sidebar.selectbox("Model", ["gpt-3.5-turbo", "gpt-4"], index=0)
    max_tokens = st.sidebar.number_input("Max Tokens", min_value=50, max_value=4000, value=256, step=50)

    website_urls = []
    num_sections = st.number_input("Number of URL Sections", min_value=1, max_value=10, value=1, step=1)

    for i in range(num_sections):
        st.subheader(f"Website Section {i + 1}")
        section_urls = st.text_area(f"Website URLs (one per line) for Section {i + 1}", key=f"urls_{i}",
                                    value="https://www.investopedia.com/basel-iv-5218598").splitlines()

        for url in section_urls:
            url = url.strip()
            if url:
                is_valid, response = validate_url(url)
                if is_valid:
                    title, description = get_url_metadata(response)
                    st.write(f"**URL:** {url}")
                    st.write(f"**Title:** {title}")
                    st.write(f"**Description:** {description}")
                    website_urls.append(url)
                else:
                    st.warning(f"The URL '{url}' is not valid or reachable.")

    uploaded_pdfs = st.file_uploader("Upload PDF documents for analysis", type=["pdf"], accept_multiple_files=True)
    if uploaded_pdfs:
        st.session_state.pdf_vector_store = get_vectorstore_from_pdfs(uploaded_pdfs)
        st.success("PDF documents processed and added to the knowledge base.")

    if website_urls and st.button("Summarize URLs"):
        summaries = summarize_url_content(website_urls)
        st.subheader("Summarized Content")
        st.markdown(summaries)  # Using markdown for better formatting

    if "pdf_vector_store" in st.session_state or website_urls:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                AIMessage(content="Hello, I am Capgemini Regulatory Reporting AI Bot. How can I assist you?")
            ]

        if "vector_store" not in st.session_state and website_urls:
            st.session_state.vector_store = get_vectorstore_from_urls(website_urls)

        if "memory" not in st.session_state:
            st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Update LLM with user-selected parameters
        llm = ChatOpenAI(temperature=temperature, model_name=model_name, max_tokens=max_tokens)
        st.session_state.qa_chain = ConversationalRetrievalChain.from_llm(
            llm,
            retriever=st.session_state.vector_store.as_retriever(),
            memory=st.session_state.memory
        )

        user_query = st.chat_input("Type your message here...")
        if user_query:
            with get_openai_callback() as cb:
                response = st.session_state.qa_chain({"question": user_query})
                ai_response = response['answer']
                
                # Update usage statistics
                st.session_state.total_tokens += cb.total_tokens
                st.session_state.total_cost += cb.total_cost
                st.session_state.prompt_tokens += cb.prompt_tokens
                st.session_state.completion_tokens += cb.completion_tokens
                st.session_state.successful_requests += 1
                
                if model_name not in st.session_state.model_usage:
                    st.session_state.model_usage[model_name] = 0
                st.session_state.model_usage[model_name] += cb.total_tokens

            st.session_state.chat_history.append(HumanMessage(content=user_query))
            st.session_state.chat_history.append(AIMessage(content=ai_response))
            save_session_history(user_query, ai_response, "Interact with Web")

        # Display chat history
        for message in st.session_state.chat_history:
            if isinstance(message, AIMessage):
                with st.chat_message("AI"):
                    st.write(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("Human"):
                    st.write(message.content)

        # Display token usage and cost information
        with st.sidebar.expander("Usage Statistics", expanded=False):
            st.write(f"Total Tokens Used: {st.session_state.total_tokens}")
            st.write(f"Prompt Tokens: {st.session_state.prompt_tokens}")
            st.write(f"Completion Tokens: {st.session_state.completion_tokens}")
            st.write(f"Successful Requests: {st.session_state.successful_requests}")
            st.write(f"Total Cost: ${st.session_state.total_cost:.4f}")

            if st.session_state.successful_requests > 0:
                avg_tokens = st.session_state.total_tokens / st.session_state.successful_requests
                avg_cost = st.session_state.total_cost / st.session_state.successful_requests
                st.write(f"Avg Tokens per Request: {avg_tokens:.2f}")
                st.write(f"Avg Cost per Request: ${avg_cost:.4f}")

            st.subheader("Model Usage")
            for model, tokens in st.session_state.model_usage.items():
                st.write(f"{model}: {tokens} tokens")
