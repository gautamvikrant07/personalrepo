import logging
from datetime import datetime, timedelta
import sqlite3
import streamlit as st
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    conn = sqlite3.connect('regulatory_reports.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS reports')
    c.execute('''CREATE TABLE reports
                 (id INTEGER PRIMARY KEY,
                  name TEXT,
                  frequency TEXT,
                  deadline_date TEXT,
                  status TEXT)''')
    conn.commit()
    conn.close()

def insert_sample_data():
    conn = sqlite3.connect('regulatory_reports.db')
    c = conn.cursor()
    today = datetime.now()
    current_year = today.year
    sample_data = [
        ('Call Report (FFIEC 031)', 'Quarterly', (today + timedelta(days=10)).strftime('%Y-%m-%d'), 'Preparing'),
        ('FR Y-9C', 'Quarterly', (today + timedelta(days=15)).strftime('%Y-%m-%d'), 'Not Started'),
        ('FR Y-9LP', 'Quarterly', (today + timedelta(days=15)).strftime('%Y-%m-%d'), 'Not Started'),
        ('FR Y-15 (Banking Organization Systemic Risk Report)', 'Quarterly', (today + timedelta(days=20)).strftime('%Y-%m-%d'), 'In Review'),
        ('Stress Test Results (DFAST)', 'Annually', f'{current_year}-06-30', 'Not Started'),
        ('Comprehensive Capital Analysis and Review (CCAR)', 'Annually', f'{current_year}-04-05', 'Submitted'),
        ('Living Will (Resolution Plan)', 'Annually', f'{current_year}-07-01', 'Not Started'),
        ('FR Y-14A (Annual Collection)', 'Annually', f'{current_year}-04-05', 'Submitted'),
        ('FR Y-14Q (Quarterly Collection)', 'Quarterly', (today + timedelta(days=25)).strftime('%Y-%m-%d'), 'Preparing'),
        ('FR Y-14M (Monthly Collection)', 'Monthly', (today + timedelta(days=5)).strftime('%Y-%m-%d'), 'In Review'),
        ('Liquidity Coverage Ratio (LCR) Report', 'Monthly', (today + timedelta(days=7)).strftime('%Y-%m-%d'), 'Preparing'),
        ('Net Stable Funding Ratio (NSFR) Report', 'Quarterly', (today + timedelta(days=18)).strftime('%Y-%m-%d'), 'Not Started'),
        ('FR 2052a (Complex Institution Liquidity Monitoring Report)', 'Monthly', (today + timedelta(days=8)).strftime('%Y-%m-%d'), 'Preparing'),
        ('FFIEC 102 (Market Risk Regulatory Report)', 'Quarterly', (today + timedelta(days=22)).strftime('%Y-%m-%d'), 'Not Started'),
        ('FFIEC 016 (Country Exposure Report)', 'Quarterly', (today + timedelta(days=28)).strftime('%Y-%m-%d'), 'Not Started'),
        ('FR Y-11 (Financial Statements of U.S. Nonbank Subsidiaries)', 'Quarterly', (today + timedelta(days=35)).strftime('%Y-%m-%d'), 'Not Started'),
        ('FR 2644 (Weekly Report of Selected Assets and Liabilities)', 'Weekly', (today + timedelta(days=2)).strftime('%Y-%m-%d'), 'Preparing'),
        ('FR Y-6 (Annual Report of Bank Holding Companies)', 'Annually', f'{current_year}-03-31', 'Submitted'),
        ('FR Y-7 (Annual Report of Foreign Banking Organizations)', 'Annually', f'{current_year}-03-31', 'Submitted'),
        ('FFIEC 009 (Country Exposure Report)', 'Quarterly', (today + timedelta(days=30)).strftime('%Y-%m-%d'), 'Not Started'),
        ('FFIEC 030 (Foreign Branch Report of Condition)', 'Annually', f'{current_year}-12-31', 'Not Started'),
        ('FR 2886b (Consolidated Report of Condition and Income for Edge and Agreement Corporations)', 'Quarterly', (today + timedelta(days=23)).strftime('%Y-%m-%d'), 'Not Started'),
        ('FDIC 6420/07 (Deposit Insurance Assessment)', 'Quarterly', (today + timedelta(days=12)).strftime('%Y-%m-%d'), 'Preparing'),
        ('Schedule RC-O (Other Data for Deposit Insurance Assessments)', 'Quarterly', (today + timedelta(days=17)).strftime('%Y-%m-%d'), 'Not Started'),
        ('Volcker Rule Compliance Report', 'Annually', f'{current_year}-03-31', 'Submitted'),
        ('FR Y-12 (Annual Report of Merchant Banking Investments)', 'Annually', f'{current_year}-03-31', 'Submitted'),
        ('FR Y-20 (Financial Statements for Foreign Subsidiaries of U.S. Banking Organizations)', 'Quarterly', (today + timedelta(days=33)).strftime('%Y-%m-%d'), 'Not Started'),
    ]
    c.executemany('INSERT OR REPLACE INTO reports (name, frequency, deadline_date, status) VALUES (?, ?, ?, ?)', sample_data)
    conn.commit()
    conn.close()

def load_events():
    conn = sqlite3.connect('regulatory_reports.db')
    c = conn.cursor()
    c.execute('SELECT name, frequency, deadline_date, status FROM reports')
    events = [{'name': row[0], 'frequency': row[1], 'date': row[2], 'status': row[3]} for row in c.fetchall()]
    conn.close()
    return events

def display_regulatory_calendar():
    try:
        create_database()
        insert_sample_data()  # Comment this out after initial run if you don't want to reset data each time
        events = load_events()
        today = datetime.now()
        
        st.title("Regulatory Reporting Calendar")
        st.write(f"Total reports: {len(events)}")
        
        # Display table of all reports
        st.header("All Regulatory Reports")
        df = pd.DataFrame(events)
        df['deadline_date'] = pd.to_datetime(df['date'])
        df = df.sort_values('deadline_date')
        st.dataframe(df, hide_index=True)
        
        # Display upcoming deadlines
        st.header("Upcoming Deadlines (Next 30 Days)")
        upcoming_events = [e for e in events if 0 <= (datetime.strptime(e['date'], '%Y-%m-%d') - today).days <= 30]
        upcoming_events.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
        
        if upcoming_events:
            upcoming_df = pd.DataFrame(upcoming_events)
            upcoming_df['deadline_date'] = pd.to_datetime(upcoming_df['date'])
            upcoming_df['days_until_deadline'] = (upcoming_df['deadline_date'] - pd.Timestamp.now()).dt.days
            upcoming_df = upcoming_df[['name', 'frequency', 'deadline_date', 'days_until_deadline', 'status']]
            upcoming_df = upcoming_df.sort_values('deadline_date')
            st.dataframe(upcoming_df, hide_index=True)
        else:
            st.write("No upcoming deadlines in the next 30 days.")
        
        # Status summary
        st.header("Report Status Summary")
        status_summary = df['status'].value_counts()
        st.bar_chart(status_summary)
        
    except Exception as e:
        st.error(f"Error displaying regulatory calendar: {str(e)}")
        logger.error(f"Error displaying regulatory calendar: {str(e)}")

if __name__ == "__main__":
    display_regulatory_calendar()
