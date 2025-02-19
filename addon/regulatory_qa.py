import streamlit as st
import json
import logging
from pathlib import Path
import os
from typing import Dict, Any
import tiktoken

logger = logging.getLogger(__name__)

EXA_API_KEY = os.getenv("EXA_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

try:
    from langchain_exa import ExaSearchRetriever
    from langchain_core.prompts import PromptTemplate
    from langchain_core.runnables import RunnableLambda, RunnablePassthrough
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import StrOutputParser
    
    EXA_AVAILABLE = True
except ImportError:
    logger.warning("langchain_exa library not found. AI-powered answers will not be available.")
    EXA_AVAILABLE = False

# Pricing per 1000 tokens (as of March 2024)
PRICING = {
    "gpt-3.5-turbo": 0.0015,
    "gpt-4": 0.03,
}

def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Calculate the cost of the API call based on input and output tokens."""
    total_tokens = input_tokens + output_tokens
    return (total_tokens / 1000) * PRICING[model]

def query_exa_ai(question: str, config: Dict[str, Any]):
    if not EXA_AVAILABLE:
        return None, 0, 0, 0
    try:
        retriever = ExaSearchRetriever(k=3, highlights=True)

        document_prompt = PromptTemplate.from_template("""
        <source>
            <url>{url}</url>
            <highlights>{highlights}</highlights>
        </source>
        """)

        document_chain = RunnableLambda(
            lambda document: {
                "highlights": document.metadata["highlights"], 
                "url": document.metadata["url"]
            }
        ) | document_prompt

        retrieval_chain = retriever | document_chain.map() | (lambda docs: "\n".join([i.text for i in docs]))

        generation_prompt = PromptTemplate.from_template("""
        You are a regulatory reporting expert with extensive knowledge of financial regulations, compliance requirements, and reporting standards. Please answer the following query based on the provided context, focusing on regulatory reporting aspects. Ensure your response is accurate, up-to-date, and compliant with current regulations. If there are any recent changes or upcoming regulations relevant to the query, please mention them.

        Query: {query}
        ---
        <context>
        {context}
        </context>

        Please provide a comprehensive answer, citing your sources at the end of your response. If the information is not available in the context or if you're unsure, please state so clearly.
        """)

        llm = ChatOpenAI(temperature=config['temperature'], model_name=config['model'])
        output_parser = StrOutputParser()

        chain = (
            {
                "context": retrieval_chain,
                "query": RunnablePassthrough()
            }
            | generation_prompt
            | llm
            | output_parser
        )

        result = chain.invoke(question)
        
        # Count tokens
        input_tokens = num_tokens_from_string(question, config['model'])
        output_tokens = num_tokens_from_string(result, config['model'])
        
        # Calculate cost
        cost = calculate_cost(input_tokens, output_tokens, config['model'])
        
        return result, input_tokens, output_tokens, cost
    except Exception as e:
        logger.error(f"Error querying Exa AI: {str(e)}")
        st.error(f"Error querying Exa AI: {str(e)}")  # Display error in Streamlit
        return None, 0, 0, 0

def display_regulatory_qa():
    try:
        st.header("Regulatory Q&A")
        
        if not EXA_AVAILABLE:
            st.error("AI-powered answers are not available. Please install the required libraries.")
            st.info("To install the necessary packages, run the following command:")
            st.code("pip install langchain langchain_exa openai tiktoken")
            return

        json_path = Path("json/regulatory_qa.json")
        
        # Customization options
        with st.expander("Customization Options"):
            model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4"], index=0)
            temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1)

        config = {
            "model": model,
            "temperature": temperature
        }
        
        if json_path.exists():
            with open(json_path, "r") as f:
                qa_data = json.load(f)
            
            question = st.text_input("Enter your regulatory question:")
            if st.button("Submit"):
                # First, check the local JSON data
                answer = next((qa['answer'] for qa in qa_data if qa['question'].lower() == question.lower()), None)
                
                if answer:
                    st.write(f"Answer from local data: {answer}")
                elif EXA_AVAILABLE:
                    # If not found in local data, query Exa AI
                    st.info("Searching for an answer using AI...")
                    ai_answer, input_tokens, output_tokens, cost = query_exa_ai(question, config)
                    if ai_answer:
                        st.write(f"AI-generated answer: {ai_answer}")
                        st.info(f"Tokens used - Input: {input_tokens}, Output: {output_tokens}, Total: {input_tokens + output_tokens}")
                        st.info(f"Estimated cost: ${cost:.4f}")
                    else:
                        st.write("Sorry, I couldn't find an answer to that question.")
                else:
                    st.warning("AI-powered answers are not available. Please install the langchain_exa library.")
        else:
            if EXA_AVAILABLE:
                st.warning("No local regulatory Q&A data found. Using AI for all queries.")
                question = st.text_input("Enter your regulatory question:")
                if st.button("Submit"):
                    st.info("Searching for an answer using AI...")
                    ai_answer, input_tokens, output_tokens, cost = query_exa_ai(question, config)
                    if ai_answer:
                        st.write(f"AI-generated answer: {ai_answer}")
                        st.info(f"Tokens used - Input: {input_tokens}, Output: {output_tokens}, Total: {input_tokens + output_tokens}")
                        st.info(f"Estimated cost: ${cost:.4f}")
                    else:
                        st.write("Sorry, I couldn't find an answer to that question.")
            else:
                st.error("No local regulatory Q&A data found and AI-powered answers are not available. Please add local data or install the langchain_exa library.")
    except Exception as e:
        st.error(f"Error in regulatory Q&A: {str(e)}")
        logger.error(f"Error in regulatory Q&A: {str(e)}")