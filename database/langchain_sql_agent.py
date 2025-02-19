import os
import re
from typing import List, Tuple
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from langchain_openai import ChatOpenAI
import streamlit as st
import pandas as pd
from langchain_community.callbacks import get_openai_callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from langchain_openai import OpenAI

# Custom CSS to enhance the visual appeal
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .st-emotion-cache-1v0mbdj.e115fcil1 {
        border: 1px solid #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .st-emotion-cache-1v0mbdj.e115fcil1 h2 {
        margin-top: 0;
    }
    .st-expander {
        border: 1px solid #f0f2f6;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .st-expander-content {
        padding: 10px;
    }
    .metric-card {
        border: 1px solid #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
    }
    .metric-card h3 {
        margin: 0;
        font-size: 14px;
    }
    .metric-card p {
        margin: 5px 0 0;
        font-size: 20px;
        font-weight: bold;
    }
    .chat-message {
        padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
    }
    .chat-message.user {
        background-color: #2b313e
    }
    .chat-message.bot {
        background-color: #475063
    }
    .chat-message .message {
      width: 100%;
      padding: 0 1.5rem;
      color: #fff;
    }
</style>
""", unsafe_allow_html=True)

def extract_sql_query(text):
    pattern = r'(?:SQL Query:|```sql)\s*((?:SELECT|INSERT|UPDATE|DELETE)[\s\S]*?;)\s*(?:```)?'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def run_langchain_sql_agent():
    st.title("AI-Powered SQL Query Assistant")
    st.markdown("---")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Collapsible Chat History Section
    with st.expander("💬 Chat History", expanded=False):
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                if message['is_user']:
                    st.markdown(
                        f"""
                        <div class="chat-message user">
                            <div class="message">🧑 User: {message['content']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="chat-message bot">
                            <div class="message">🤖 AI: {message['content']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No chat history yet. Start by asking a question!")

    if 'db_file' in st.session_state and st.session_state['db_file']:
        st.success(f"✅ Using database file: {st.session_state['db_file']}")
        db = SQLDatabase.from_uri(f"sqlite:///{st.session_state['db_file']}")
        table_names = db.get_usable_table_names()
        st.markdown(f"📊 Available tables: {', '.join(table_names)}")
    else:
        st.error("❌ Please load the database first.")
        return

    user_query = st.text_area("💬 Enter your query in natural language:", height=100)

    if st.button("🚀 Run Query", key="run_query"):
        if not user_query:
            st.warning("⚠️ Please enter a query before running.")
            return

        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
        execute_query = QuerySQLDataBaseTool(db=db)
        write_query = create_sql_query_chain(llm, db)

        answer_prompt = PromptTemplate.from_template(
            """Given the following user question and SQL query result, provide a comprehensive answer:
            Question: {question}
            SQL Query: {query}
            Query Result: {result}
            
            Please structure your answer as follows:
            1. Restate the user's question.
            2. Provide the SQL query used to answer the question. Do not use LIMIT in the SQL query unless specifically asked for in the question.
            3. Show the results of the SQL query in a clear, tabular format. Include all results without limitation.
            4. Give a detailed interpretation of the results, answering the user's question.
            
            Answer: """
        )

        answer = answer_prompt | llm | StrOutputParser()

        chain = (
            RunnablePassthrough.assign(query=write_query).assign(
                result=itemgetter("query") | execute_query
            )
            | answer
        )

        try:
            with st.spinner("🔄 Generating response..."):
                with get_openai_callback() as cb:
                    chain_result = chain.invoke({"question": user_query})
                    
                    if isinstance(chain_result, str):
                        result = chain_result
                        sql_query = extract_sql_query(result)
                        query_result = None
                    else:
                        sql_query = chain_result.get('query')
                        query_result = chain_result.get('result')
                        result = chain_result.get('answer')
            
            st.subheader("🤖 AI Response")
            st.markdown(result)
            
            
            
            # If the SQL query and results are not in the AI's response, display them separately
            if sql_query and sql_query not in result:
                st.subheader("🔍 Generated SQL Query")
                st.code(sql_query, language="sql")
            
            if query_result and str(query_result) not in result:
                st.subheader("📊 SQL Query Result")
                df = pd.DataFrame(query_result)
                st.dataframe(df, use_container_width=True)
            
            st.markdown("---")

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(
                    """
                    <div class="metric-card">
                        <h3>Total Tokens</h3>
                        <p>{}</p>
                    </div>
                    """.format(cb.total_tokens),
                    unsafe_allow_html=True
                )
            with col2:
                st.markdown(
                    """
                    <div class="metric-card">
                        <h3>Prompt Tokens</h3>
                        <p>{}</p>
                    </div>
                    """.format(cb.prompt_tokens),
                    unsafe_allow_html=True
                )
            with col3:
                st.markdown(
                    """
                    <div class="metric-card">
                        <h3>Completion Tokens</h3>
                        <p>{}</p>
                    </div>
                    """.format(cb.completion_tokens),
                    unsafe_allow_html=True
                )
            with col4:
                st.markdown(
                    """
                    <div class="metric-card">
                        <h3>Total Cost (USD)</h3>
                        <p>${:.4f}</p>
                    </div>
                    """.format(cb.total_cost),
                    unsafe_allow_html=True
                )

            # Update chat history
            st.session_state.chat_history.append({"content": user_query, "is_user": True})
            st.session_state.chat_history.append({"content": result, "is_user": False})

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.error("Full error message:")
            st.exception(e)

    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()


