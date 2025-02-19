import logging
from typing import List, Dict
import streamlit as st
import requests
from datetime import datetime, timedelta
import traceback
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the API key from environment variables
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

if not NEWS_API_KEY:
    st.error("NEWS_API_KEY not found in environment variables. Please check your .env file.")
    st.stop()

def fetch_news_from_newsapi(query: str = '"regulatory reporting" OR "financial regulation"') -> List[Dict]:
    try:
        url = "https://newsapi.org/v2/everything"
        
        # Set the date range for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        params = {
            'apiKey': NEWS_API_KEY,
            'q': query,
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d')
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get('articles', [])
        
        news_items = []
        for article in articles[:10]:  # Limit to 10 articles
            news_items.append({
                'title': article['title'],
                'date': article['publishedAt'],
                'link': article['url'],
                'source': article['source']['name']
            })
        
        return news_items
    except Exception as e:
        st.error(f"Error fetching news from NewsAPI: {str(e)}")
        logger.error(f"Error fetching news from NewsAPI: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def fetch_regulatory_news(query: str = '"regulatory reporting" OR "financial regulation"') -> List[Dict]:
    try:
        news_items = fetch_news_from_newsapi(query)
        
        if not news_items:
            st.warning("No news items were fetched.")
            return []
        
        # Sort news items by date
        news_items.sort(key=lambda x: datetime.fromisoformat(x['date'].replace('Z', '+00:00')), reverse=True)
        
        return news_items[:10]  # Return top 10 most recent news items
    except Exception as e:
        st.error(f"Error in fetch_regulatory_news: {str(e)}")
        logger.error(f"Error in fetch_regulatory_news: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def display_regulatory_news():
    try:
        st.title("Regulatory Reporting News")
        
        # Add a search box
        search_query = st.text_input("Search for specific news (e.g., GDPR, Basel III)", "")
        
        # Add a search button
        search_button = st.button("Search")
        
        # Add a refresh button
        refresh_button = st.button("Refresh News")
        
        if search_button or refresh_button or 'news_items' not in st.session_state:
            query = search_query if search_query else '"regulatory reporting" OR "financial regulation"'
            with st.spinner("Fetching latest regulatory reporting news..."):
                news_items = fetch_regulatory_news(query)
            st.session_state.news_items = news_items
        else:
            news_items = st.session_state.news_items
        
        if not news_items:
            st.warning("No recent regulatory reporting news found. Please try again later.")
            return

        st.success(f"Found {len(news_items)} recent regulatory reporting news articles.")
        
        for item in news_items:
            with st.expander(f"{item['title']} - {item['source']}"):
                st.write(f"**Date:** {item['date']}")
                st.write(f"**Source:** {item['source']}")
                st.write(f"**Link:** [{item['link']}]({item['link']})")
        
        st.info("Click on a news title to expand and view details.")
        
    except Exception as e:
        st.error(f"Error displaying regulatory news: {str(e)}")
        logger.error(f"Error displaying regulatory news: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    display_regulatory_news()