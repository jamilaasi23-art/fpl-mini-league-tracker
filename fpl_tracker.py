import streamlit as st
import requests
import time

# === CONFIG ===
st.set_page_config(page_title="إيد مين بطيز مين", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    .main {background: #0f172a; color: #e2e8f0; font-family: 'Inter', sans-serif;}
    .title {font-size: 48px; text-align: center; font-weight: 700; 
            background: linear-gradient(90deg, #f43f5e, #fbbf24); -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; margin: 20px 0;}
    .logo {display: block; margin: 0 auto 10px; height: 80px; border-radius: 12px;}
    .card {background: #1e293b; border-radius: 12px; padding: 16px; margin: 12px 0; 
           border: 1px solid #334155; transition: all 0.2s;}
    .card:hover {border-color: #f43f5e; transform: translateY(-2px);}
    .rank {font-size: 24px; font-weight: 700; color: #fbbf24;}
    .top1 {background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #000;}
    .top2 {background: #94a3b8;}
    .top3 {background: #f97316;}
    .player-img {width: 50px; height: 50px; border-radius: 50%; object-fit: cover; 
                 border: 2px solid #475569;}
    .captain {border: 3px solid #fbbf24 !important;}
    .chip {background: #dc2626; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;}
    .stButton>button {background: #f43f5e; color: white; border-radius: 8px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# === LOGO (CHANGE THIS URL) ===
LOGO_URL = "https://via.placeholder.com/300x80/1e293b/f43f5e?text=Your+Logo"  # ← REPLACE THIS
st.markdown(f"<img src='{LOGO_URL}' class='logo'>", unsafe_allow_html=True)
st.markdown("<h1 class='title'>إيد مين بطيز مين</h1>", True)

LEAGUE_ID = 443392
BASE_URL = "https://fantasy.premierleague.com/api/"
IMG_BASE = "https://resources.premierleague.com/premierleague/photos/players/110x140/"

# === DATA ===
@st.cache_data(ttl=60)
def get_all():
    try:
        # Standings
        standings = requests.get(f"{BASE_URL}leagues-classic/{LEAGUE_ID}/standings/").json()['standings']['results']
        # Bootstrap
        boot = requests.get(f"{BASE_URL}bootstrap-static/").json()
        gw = next(e['id'] for e in boot['events'] if e['is_current'])
        live = requests.get(f"{BASE_URL}event/{gw}/live/").json()
        players = {p['id']: p for p in boot['elements']}
        return standings, gw, live, players
    except:
        return [], 1, {}, {}

standings, gw, live, players = get_all()
live_pts = {e['id']: e['stats']['total_points'] for e in live.get('elements', [])}

# === REFRESH ===
refresh = st.sidebar.slider("Refresh", 30, 300, 60)
if st.sidebar.button("Refresh"):
    st.rerun()

# === TABLE ===
if not standings:
    st.error("No data")
    st.stop()

for p in standings:
    rank = p['rank']
    name = p['player_name']
    team = p['entry_name']
    total = p['total']
    entry_id = p['entry']
    
    # Live GW
    try:
        picks_data = requests.get(f"{BASE_URL}entry/{entry_id}/event/{gw}/picks/").json()
        picks = picks_data['picks']
        chip = picks_data.get('active_chip')
        gw_live = sum(live_pts.get(pk['element'], 0) * pk['multiplier'] for pk in picks)
        change = gw_live - p['event_total']
        change_str = f"<span style='color:#10b981; font-weight:600'> (+{change})</span>" if change > 0 else \
                     f"<span style='color:#ef4444; font-weight:600'> ({change})</span>" if change < 0 else ""
    except:
        change_str = ""
        chip = None

    rank_class = "top1" if rank == 1 else "top2" if rank == 2 else "top3" if rank == 3 else ""
    st.markdown(f"""
    <div class='card {rank_class}'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <div>
                <span class='rank'>#{rank}</span> 
                <b style='font-size:18px; margin-left:8px;'>{name}</b>
            </div>
            <div style='text-align:right;'>
                <div style='font-size:20px; font-weight:700;'>{total}</div>
                <div style='font-size:14px; color:#94a3b8;'>
                    GW: <b>{p['event_total']}</b>{change_str} {f"<span class='chip'>{chip.upper()}</span>" if chip else ""}
                </div>
            </div>
        </div>
        <div style='margin-top:12px; font-weight:600; color:#e2e8f0;'>{team}</div>
    </div>
    """, True)
    
    if st.button("View Squad", key=f"v_{entry_id}"):
        st.session_state.selected = entry_id

# === SQUAD WITH PHOTOS ===
if 'selected' in st.session_state:
    entry_id = st.session_state.selected
    player = next(p for p in standings if p['entry'] == entry_id)
    picks_data = requests.get(f"{BASE_URL}entry/{entry_id}/event/{gw}/picks/").json()
    picks = picks_data['picks']
    chip = picks_data.get('active_chip')
    
    st.markdown(f"<h2 style='text-align:center; color:#f43f5e; margin:30px 0 10px;'>Squad: {player['entry_name']}</h2>", True)
    if chip:
        st.markdown(f"<p style='text-align:center; margin-bottom:20px;'><span class='chip'>{chip.upper()}</span></p>", True)
    
    starters = [pk for pk in picks if pk['position'] <= 11]
    bench = [pk for pk in picks if pk['position'] > 11]
    
    # Starters
    cols = st.columns(5)
    for i, pk in enumerate(starters):
        with cols[i % 5]:
            pl = players.get(pk['element'], {})
            code = pl.get('photo', 'p0.jpg').replace('.jpg', '')
            img = f"{IMG_BASE}p{code}.png"
            name = f"{pl.get('first_name','')} {pl.get('second_name','')}".strip()
            pts = live_pts.get(pk['element'], 0)
            mult = pk['multiplier']
            cap = "captain" if pk['is_captain'] else ""
            st.markdown(f"""
            <div style='text-align:center; margin:15px 0;'>
                <img src='{img}' class='player-img {cap}' onerror="this.src='https://via.placeholder.com/50/1e293b/f43f5e?text=?';">
                <div style='margin-top:6px; font-size:13px; font-weight:600;'>{name}</div>
                <div style='color:#10b981; font-weight:700; font-size:14px;'>{pts} × {mult}</div>
            </div>
            """, True)
    
    # Bench
    st.markdown("**Bench**", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, pk in enumerate(bench):
        with cols[i % 4]:
            pl = players.get(pk['element'], {})
            code = pl.get('photo', 'p0.jpg').replace('.jpg', '')
            img = f"{IMG_BASE}p{code}.png"
            name = f"{pl.get('first_name','')} {pl.get('second_name','')}".strip()
            st.markdown(f"""
            <div style='text-align:center; opacity:0.6; margin:10px 0;'>
                <img src='{img}' class='player-img' onerror="this.src='https://via.placeholder.com/50/334155/94a3b8?text=?';">
                <div style='margin-top:6px; font-size:12px;'>{name}</div>
            </div>
            """, True)
    
    if st.button("Close Squad"):
        del st.session_state.selected

# === FOOTER ===
st.markdown("---")
st.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:14px;'>Gameweek {gw} • Updated: {time.strftime('%H:%M:%S')}</div>", True)

time.sleep(refresh)
st.rerun()
