import streamlit as st
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI


def get_retriever_chain(vector_store, llm):
    """
    Returns a RetrievalQA chain using the provided vector store and LLM.

    Parameters:
    - vector_store (Chroma): A vector store containing text embeddings.
    - llm (OpenAI): The language model to use for generating responses.

    Returns:
    - RetrievalQA: A chain that retrieves relevant documents and generates a response.
    """
    retriever = vector_store.as_retriever()
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="map_reduce"
    )


def get_response(user_input):
    """
    Generates a response based on the user's input using a retriever chain.

    Parameters:
    - user_input (str): The user's query.

    Returns:
    - str: The generated response from the language model.
    """
    llm = OpenAI()
    retriever_chain = get_retriever_chain(st.session_state.vector_store, llm)
    response = retriever_chain({"query": user_input})
    return response['result']
