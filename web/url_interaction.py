import requests
from bs4 import BeautifulSoup
import os
import tempfile
from langchain_community.document_loaders import WebBaseLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI  # Updated import
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate

def validate_url(url):
    """
    Validates if a URL is reachable.

    Parameters:
    - url (str): The URL to validate.

    Returns:
    - bool: True if the URL is valid and reachable, False otherwise.
    - response: The HTTP response object if valid, None otherwise.
    """
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200, response
    except requests.RequestException:
        return False, None

def get_url_metadata(response):
    """
    Extracts metadata from the response of a URL.

    Parameters:
    - response: The HTTP response object from a URL request.

    Returns:
    - tuple: A tuple containing the title and description of the URL's content.
    """
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string if soup.title else "No Title"
    description = soup.find('meta', attrs={'name': 'description'})
    if description and 'content' in description.attrs:
        description = description['content']
    else:
        description = "No Description"
    return title, description

def get_vectorstore_from_urls(urls):
    """
    Creates a vector store from the text content of the given URLs.

    Parameters:
    - urls (list): List of URLs to process.

    Returns:
    - Chroma: A vector store containing embeddings of the text from the URLs.
    """
    documents = []
    for url in urls:
        loader = WebBaseLoader(url)
        document = loader.load()
        text_splitter = RecursiveCharacterTextSplitter()
        document_chunks = text_splitter.split_documents(document)
        documents.extend(document_chunks)
    return Chroma.from_documents(documents, OpenAIEmbeddings())

def get_vectorstore_from_pdfs(pdf_files):
    """
    Creates a vector store from the text content of the given PDF files.

    Parameters:
    - pdf_files (list): List of uploaded PDF files.

    Returns:
    - Chroma: A vector store containing embeddings of the text from the PDF files.
    """
    documents = []
    for pdf_file in pdf_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.getbuffer())
            tmp_file_path = tmp_file.name
        loader = PyMuPDFLoader(tmp_file_path)
        document = loader.load()
        text_splitter = RecursiveCharacterTextSplitter()
        document_chunks = text_splitter.split_documents(document)
        documents.extend(document_chunks)
        os.remove(tmp_file_path)
    return Chroma.from_documents(documents, OpenAIEmbeddings())

def summarize_url_content(urls):
    """
    Summarizes the content of the given URLs in a natural, paragraph-style format.

    Parameters:
    - urls (list): List of URLs to summarize.

    Returns:
    - str: Formatted string containing summaries of the content of the URLs.
    """
    llm = OpenAI(temperature=0.5, max_tokens=256)  # Adjust as needed
    
    # Create a custom prompt template
    prompt_template = """Write a concise summary of the following text in a natural, flowing paragraph style:

    {text}

    CONCISE SUMMARY:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
    
    summarize_chain = load_summarize_chain(llm, chain_type="map_reduce", map_prompt=PROMPT, combine_prompt=PROMPT)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    formatted_summaries = []

    for url in urls:
        # Load the content from the URL
        loader = WebBaseLoader(url)
        document = loader.load()

        # Split the document into chunks
        chunked_documents = text_splitter.split_documents(document)

        # Summarize the chunks
        summary = summarize_chain.invoke({"input_documents": chunked_documents})
        
        # Format the summary
        formatted_summary = f"""
Summary of {url}:

{summary['output_text'].strip()}

"""
        formatted_summaries.append(formatted_summary)

    # Join all formatted summaries with newlines
    return "\n".join(formatted_summaries)
