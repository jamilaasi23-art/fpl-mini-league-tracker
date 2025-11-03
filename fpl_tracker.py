import streamlit as st
import requests
import time
import json

# === CONFIG ===
st.set_page_config(page_title="ايد مين بطيز مين", layout="wide")
st.markdown("""
<style>
    .main {background: #0e1117; color: #fafafa;}
    .stApp {background: #0e1117;}
    .stButton>button {background: #ff4b4b; color: white; border-radius: 8px;}
    .stText {color: #cccccc;}
    .highlight {background: linear-gradient(90deg, #1e3a8a, #1e40af); padding: 12px; border-radius: 10px; margin: 8px 0; border-left: 6px solid gold;}
    .top3 {background: #1a1a2e; border-left: 6px solid #f59e0b;}
    .squad {background: #16213e; padding: 15px; border-radius: 10px; border: 1px solid #334155;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#ff4b4b; font-size:52px; text-shadow: 2px 2px 8px #000;'>ايد مين بطيز مين</h1>", True)

LEAGUE_ID = 443392
BASE_URL = "https://fantasy.premierleague.com/api/"
EMOJI = {1: "🥇", 2: "🥈", 3: "🥉", "BB": "🪄", "TC": "3️⃣", "FH": "🔄", "WC": "🎭"}

# === CACHING ===
@st.cache_data(ttl=55)
def get_bootstrap():
    return requests.get(f"{BASE_URL}bootstrap-static/").json()

@st.cache_data(ttl=60)
def get_standings():
    url = f"{BASE_URL}leagues-classic/{LEAGUE_ID}/standings/"
    try:
        return requests.get(url).json()['standings']['results']
    except:
        return []

@st.cache_data(ttl=60)
def get_current_gw():
    data = get_bootstrap()
    for e in data['events']:
        if e['is_current']:
            return e['id']
    return 1

@st.cache_data(ttl=60)
def get_live_gw(gw):
    return requests.get(f"{BASE_URL}event/{gw}/live/").json()

@st.cache_data(ttl=60)
def get_picks(entry_id, gw):
    url = f"{BASE_URL}entry/{entry_id}/event/{gw}/picks/"
    try:
        data = requests.get(url).json()
        return data['picks'], data.get('active_chip')
    except:
        return [], None

# === INIT ===
if 'player_names' not in st.session_state:
    st.session_state.player_names = {}
if 'live_points' not in st.session_state:
    st.session_state.live_points = {}

bootstrap = get_bootstrap()
player_map = {p['id']: f"{p['first_name']} {p['second_name']}" for p in bootstrap['elements']}
gw = get_current_gw()
live_data = get_live_gw(gw)
standings = get_standings()

# === SIDEBAR ===
refresh = st.sidebar.slider("🔄 Refresh (sec)", 30, 300, 60)
if st.sidebar.button("🔥 Refresh Now"):
    st.rerun()
st.sidebar.markdown("---")
st.sidebar.markdown("**🔔 Alerts**")
alerts = st.sidebar.checkbox("Goal = Browser Alert", value=True)

# === MAIN ===
with st.spinner("جاري تحميل الدوري..."):
    if not standings:
        st.error("❌ No connection or invalid league ID")
        st.stop()

    # Update live points
    for explain in live_data['elements']:
        pid = explain['id']
        pts = explain['stats']['total_points']
        st.session_state.live_points[pid] = pts

    for player in standings:
        rank = player['rank']
        name = player['player_name']
        team = player['entry_name']
        total = player['total']
        entry_id = player['entry']
        gw_pts = player['event_total']

        # Live change
        try:
            picks, chip = get_picks(entry_id, gw)
            live_total = sum(
                st.session_state.live_points.get(p['element'], 0) * p['multiplier']
                for p in picks
            )
            change = live_total - gw_pts
            change_str = f" **(+{change})**" if change > 0 else f" **({change})**" if change < 0 else ""
        except:
            change_str = ""

        # Rank emoji
        rank_emoji = EMOJI.get(rank, f"#{rank}")

        # Chip
        chip_emoji = f" {EMOJI.get(chip, '')}" if chip else ""

        col1, col2 = st.columns([4, 1])
        with col1:
            if rank <= 3:
                st.markdown(f"<div class='top3'><b>{rank_emoji} {name}</b> | **{team}** | **{total}** pts | GW: **{gw_pts}{change_str}**{chip_emoji}</div>", True)
            else:
                st.markdown(f"<div class='highlight'><b>{rank_emoji} {name}</b> | **{team}** | **{total}** pts | GW: **{gw_pts}{change_str}**{chip_emoji}</div>", True)
        with col2:
            if st.button("Squad", key=f"btn_{entry_id}"):
                st.session_state.selected = entry_id

    # === SQUAD VIEW ===
    if 'selected' in st.session_state:
        entry_id = st.session_state.selected
        player = next(p for p in standings if p['entry'] == entry_id)
        st.markdown(f"<div class='squad'><h3>👥 Squad: **{player['entry_name']}**</h3>", True)

        picks, chip = get_picks(entry_id, gw)
        if picks:
            if chip:
                st.markdown(f"**🪄 Active Chip: {chip.upper()} {EMOJI.get(chip, '')}**")

            starters = [p for p in picks if p['position'] <= 11]
            bench = [p for p in picks if p['position'] > 11]

            st.markdown("**⚡ Starters**")
            for p in starters:
                pid = p['element']
                name = player_map.get(pid, f"Player {pid}")
                mult = p['multiplier']
                live_pt = st.session_state.live_points.get(pid, 0)
                caption = " (C) 👑" if p['is_captain'] else " (VC)" if p['is_vice_captain'] else ""
                st.markdown(f"• **{name}**{caption} ×**{mult}** → **{live_pt}** pts")

            st.markdown("**🪑 Bench**")
            for p in bench:
                name = player_map.get(p['element'], f"Player {p['element']}")
                st.markdown(f"• {name}")

            # Export button
            export_data = {
                "team": player['entry_name'],
                "total": player['total'],
                "gw_points": player['event_total'],
                "squad": [player_map.get(p['element'], "Unknown") for p in picks]
            }
            st.download_button("📥 Export to JSON", data=json.dumps(export_data, indent=2), file_name=f"{team}_squad.json")

        else:
            st.info("No squad data yet (GW not started).")

        if st.button("✖ Close"):
            del st.session_state.selected
        st.markdown("</div>", True)

# === FOOTER ===
leader = standings[0]
st.markdown("---")
st.markdown(f"**🏆 Leader:** **{leader['entry_name']}** – **{leader['total']}** pts")
st.caption(f"Gameweek {gw} • Updated: {time.strftime('%H:%M:%S')}")

# === ALERTS ===
if alerts and change_str:
    st.toast(f"Goal! {team} +{change}", icon="⚽")

# === REFRESH ===
time.sleep(refresh)
st.rerun()
