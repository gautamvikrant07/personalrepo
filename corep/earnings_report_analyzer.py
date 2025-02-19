import hashlib
import json
import os
import re

import matplotlib.pyplot as plt
import pandas as pd
import pdfplumber
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from textstat import flesch_kincaid_grade
from wordcloud import WordCloud

load_dotenv()  # Load environment variables from .env file

# Set up OpenAI API key


def analyze_earnings_report():
    st.title("Advanced Earnings Report Analyzer")
    st.markdown("### Powered by AI and Big Data Analytics")

    uploaded_file = st.file_uploader("Choose an earnings report file", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Analyze Report", key="analyze_button"):
            with st.spinner("Performing comprehensive analysis..."):
                try:
                    file_hash = generate_file_hash(uploaded_file)

                    if is_file_in_vector_db(file_hash):
                        st.info("Utilizing cached analysis for faster results.")
                        vector_store = load_vector_db(file_hash)
                    else:
                        text_chunks = extract_financial_data(uploaded_file)
                        if not text_chunks:
                            st.error(
                                "Failed to extract meaningful text from the uploaded file. Please ensure the file has "
                                "readable financial content.")
                            return

                        vector_store = store_in_vector_db(text_chunks, file_hash)

                    summary = analyze_with_llm(vector_store)
                    display_analysis(summary)

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.error("Please try again or contact support if the issue persists.")


def generate_file_hash(file):
    file.seek(0)
    file_content = file.read()
    file.seek(0)
    return hashlib.sha256(file_content).hexdigest()


def is_file_in_vector_db(file_hash):
    vector_store_path = os.path.join("../vector_db", f"{file_hash}.chroma")
    return os.path.exists(vector_store_path)


def load_vector_db(file_hash):
    return Chroma(embedding_function=OpenAIEmbeddings(),
                  persist_directory=os.path.join("../vector_db", f"{file_hash}.chroma"))


def extract_financial_data(file):
    try:
        text_chunks = []
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    chunks = [page_text[i:i + 2000] for i in range(0, len(page_text), 2000)]
                    text_chunks.extend(chunks)

        st.write(f"Extracted {len(text_chunks)} chunks from the PDF.")
        return text_chunks
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None


def store_in_vector_db(text_chunks, file_hash):
    embeddings = OpenAIEmbeddings()
    vector_store_path = os.path.join("../vector_db", f"{file_hash}.chroma")
    vector_store = Chroma(embedding_function=embeddings,
                          persist_directory=vector_store_path)

    for chunk in text_chunks:
        vector_store.add_texts([chunk])

    st.write("Stored extracted data in vector database.")
    return vector_store


def clean_json_response(response_text):
    try:
        response_text = re.sub(r'\\n', '', response_text)
        response_text = re.sub(r'\\', '', response_text)
        response_text = re.sub(r'`{3}', '', response_text)
        response_text = response_text.strip()

        json_data = json.loads(response_text)
        return json_data
    except json.JSONDecodeError:
        st.error("The LLM response was not in valid JSON format after cleanup.")
        return None


def analyze_with_llm(vector_store):
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    prompt_template = PromptTemplate.from_template(
        "Analyze the following financial data and provide a comprehensive summary of the company's performance.\n"
        "Ensure that the response is in JSON format with the following structure:\n"
        "{{\n"
        '  "summary": "Detailed summary text",\n'
        '  "companyName": "Name of the company",\n'
        '  "financialMetrics": [\n'
        '    {{"name": "Revenue", "value": "Value in millions", "change": "Year-over-year change"}},\n'
        '    {{"name": "Net Income", "value": "Value in millions", "change": "Year-over-year change"}},\n'
        '    {{"name": "EPS", "value": "Earnings per share", "change": "Year-over-year change"}},\n'
        '    {{"name": "Operating Margin", "value": "Percentage", "change": "Year-over-year change"}},\n'
        '    {{"name": "Free Cash Flow", "value": "Value in millions", "change": "Year-over-year change"}},\n'
        '    {{"name": "Return on Equity", "value": "Percentage", "change": "Year-over-year change"}},\n'
        '    {{"name": "Gross Profit Margin", "value": "Percentage", "change": "Year-over-year change"}},\n'
        '    {{"name": "EBITDA", "value": "Value in millions", "change": "Year-over-year change"}},\n'
        '    {{"name": "Debt-to-Equity Ratio", "value": "Ratio", "change": "Year-over-year change"}},\n'
        '    {{"name": "Current Ratio", "value": "Ratio", "change": "Year-over-year change"}},\n'
        '    {{"name": "Inventory Turnover", "value": "Ratio", "change": "Year-over-year change"}},\n'
        '    {{"name": "R&D Expenses", "value": "Value in millions", "change": "Year-over-year change"}}\n'
        '  ],\n'
        '  "keyHighlights": ["Point 1", "Point 2", "Point 3"],\n'
        '  "riskFactors": ["Risk 1", "Risk 2", "Risk 3"],\n'
        '  "futurePrediction": "Detailed future prediction based on trends in financial metrics and market '
        'conditions.",\n'
        '  "competitiveAnalysis": "Brief analysis of the company\'s position relative to competitors"\n'
        '}}\n'
        "The data provided is:\n{context}"
    )

    retrieved_texts = vector_store.similarity_search("financial summary", k=5)
    combined_text = " ".join([doc.page_content for doc in retrieved_texts])
    input_data = prompt_template.format(context=combined_text[:4000])

    try:
        response = llm.invoke(input_data)

        if hasattr(response, 'content'):
            result_text = response.content
        else:
            st.error("Unexpected LLM output format.")
            return None

        st.write("Raw LLM Response:", result_text)

        summary = clean_json_response(result_text)
        if summary is None:
            st.error("Unable to parse the cleaned JSON response.")
        return summary
    except Exception as parse_error:
        st.error(f"Error during LLM chain execution: {str(parse_error)}")
        return None


def display_analysis(summary):
    if summary is None:
        st.error("Unable to display analysis due to parsing error.")
        return

    company_name = summary.get("companyName", "Unknown Company")
    st.title(f"{company_name} Earnings Report Analysis")

    st.subheader("Executive Summary")
    st.write(summary.get("summary", "No summary available"))

    display_financial_metrics(summary)
    display_key_highlights(summary)
    display_risk_factors(summary)
    display_future_prediction(summary)
    display_competitive_analysis(summary)
    display_text_complexity(summary)
    display_word_cloud(summary)


def display_financial_metrics(summary):
    st.subheader("Key Financial Metrics")
    metrics = summary.get("financialMetrics", [])
    if metrics:
        filtered_metrics = [metric for metric in metrics if 'N/A' not in (metric['value'], metric['change'])]

        if filtered_metrics:
            df = pd.DataFrame(filtered_metrics)

            fig = px.bar(df, x='name', y='value', text='value',
                         title='Key Financial Metrics',
                         labels={'name': 'Metric', 'value': 'Value'},
                         color='change', color_continuous_scale='RdYlGn')
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            st.plotly_chart(fig)

            st.table(df)
        else:
            st.write("No valid financial metrics available after filtering out 'N/A' values.")
    else:
        st.write("No financial metrics available")


def display_key_highlights(summary):
    st.subheader("Key Highlights")
    highlights = summary.get("keyHighlights", [])
    for highlight in highlights:
        st.markdown(f"• {highlight}")


def display_risk_factors(summary):
    st.subheader("Risk Factors")
    risks = summary.get("riskFactors", [])
    for risk in risks:
        st.markdown(f"• {risk}")


def display_future_prediction(summary):
    st.subheader("Future Outlook")
    st.write(summary.get("futurePrediction", "No future prediction available"))


def display_competitive_analysis(summary):
    st.subheader("Competitive Analysis")
    st.write(summary.get("competitiveAnalysis", "No competitive analysis available"))


def display_text_complexity(summary):
    st.subheader("Report Complexity Analysis")
    text = summary.get("summary", "") + " " + summary.get("futurePrediction", "")
    grade = flesch_kincaid_grade(text)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=grade,
        title={'text': "Flesch-Kincaid Grade Level"},
        gauge={'axis': {'range': [None, 20]},
               'steps': [
                   {'range': [0, 6], 'color': "lightgreen"},
                   {'range': [6, 12], 'color': "yellow"},
                   {'range': [12, 20], 'color': "red"}],
               'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': grade}}))

    st.plotly_chart(fig)


def display_word_cloud(summary):
    st.subheader("Key Terms Word Cloud")
    text = summary.get("summary", "") + " " + summary.get("futurePrediction", "")
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
