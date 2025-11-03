import streamlit as st
import requests
import time
import pandas as pd

# ============= CONFIGURATION =============
APP_TITLE = "ايد مين بطيز مين"   # Arabic name
LEAGUE_ID = 443392
BASE_URL = "https://fantasy.premierleague.com/api/"
# =========================================

def fetch_standings(league_id):
    url = f"{BASE_URL}leagues-classic/{league_id}/standings/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        results = data['standings']['results']
        df = pd.DataFrame(results)
        return df[['rank', 'player_name', 'entry_name', 'total', 'event_total']]
    except:
        return None

# ============= STREAMLIT APP =============
st.set_page_config(page_title=APP_TITLE, layout="wide")

# Always show Arabic title at the top
st.markdown(f"<h1 style='text-align: center; color: #1f77b4;'>{APP_TITLE}</h1>", unsafe_allow_html=True)

# Sidebar controls (in English)
st.sidebar.header("Auto Refresh")
refresh_interval = st.sidebar.slider("Refresh every (seconds)", 30, 300, 60)
if st.sidebar.button("Manual Refresh"):
    st.rerun()

# Fetch and display data
with st.spinner("Fetching live standings..."):
    df = fetch_standings(LEAGUE_ID)

if df is not None and not df.empty:
    # English column names
    df.columns = ['Rank', 'Player Name', 'Team Name', 'Total Points', 'GW Points']
    
    # Highlight top 3
    def highlight_top(row):
        return ['background-color: #d4edda' if row['Rank'] <= 3 else ''] * len(row)
    
    styled = df.style.apply(highlight_top, axis=1)
    
    st.subheader(f"Live Standings – Updated: {pd.Timestamp.now().strftime('%H:%M:%S')}")
    st.dataframe(styled, use_container_width=True)
    
    top = df.iloc[0]
    st.success(f"Current Leader: **{top['Team Name']}** – {top['Total Points']} points")
else:
    st.error("Error: Could not load data. Check your league ID or internet connection.")

# Auto-refresh
time.sleep(refresh_interval)
st.rerun()