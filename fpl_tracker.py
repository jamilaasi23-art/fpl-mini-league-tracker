import streamlit as st
import requests
import time

st.set_page_config(page_title="إيد مين بطيز مين", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;700&display=swap');
    .main {background: #0D1117; color: #FFFFFF; font-family: 'Inter', sans-serif; padding: 8px;}
    .title {font-size: 24px; text-align: center; background: linear-gradient(90deg, #0057B8, #E90052); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 3px 0; font-weight: 700;}
    .logo {height: 32px; display: block; margin: 0 auto 3px;}
    .row {display: flex; align-items: center; padding: 6px 10px; margin: 1px 0; 
          background: #161B22; border-radius: 6px; border-left: 4px solid #30363D; font-size: 11.5px;}
    .top1 {background: linear-gradient(135deg, #E90052, #0057B8) !important; color: #FFF !important; border-left-color: #FFD700;}
    .top2 {background: linear-gradient(135deg, #3D195B, #0057B8) !important; color: #FFF !important;}
    .top3 {background: linear-gradient(135deg, #E90052, #3D195B) !important; color: #FFF !important;}
    .rank {font-weight: 700; font-size: 13px; min-width: 24px;}
    .points {font-weight: 700; font-size: 13px; min-width: 44px; text-align: right;}
    .gw {font-size: 10px; color: #10B981;}
    .gw-down {color: #EF4444;}
    .chip {font-size: 9px; padding: 1px 5px; background: #E90052; color: #FFF; border-radius: 8px; margin-left: 3px;}
    .pitch {background: #1A5F3D; height: 360px; position: relative; border-radius: 10px; margin: 8px 0; 
            border: 2px solid #30363D; overflow: hidden;}
    .player-pos {position: absolute; text-align: center; color: #FFF; font-size: 11px; 
                 font-weight: 700; text-shadow: 1px 1px 2px #000; width: 80px;}
    .player-circle {width: 38px; height: 38px; background: #0057B8; color: #FFF; border-radius: 50%; 
                    margin: 0 auto 4px; display: flex; align-items: center; justify-content: center; 
                    font-size: 9px; font-weight: 700; border: 2px solid #FFF;}
    .captain {border: 3px solid #FFD700 !important; background: #FFD700 !important; color: #000 !important;}
    .player-name {font-size: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 70px;}
    .bench-row {display: flex; justify-content: center; gap: 8px; margin-top: 8px; flex-wrap: wrap;}
    .bench-player {text-align: center; width: 60px; opacity: 0.7; font-size: 10px;}
    .bench-circle {width: 32px; height: 32px; background: #30363D; color: #AAA; border-radius: 50%; 
                   margin: 0 auto 3px; display: flex; align-items: center; justify-content: center; 
                   font-size: 9px; border: 1px solid #555;}
    .collapsible {background: #161B22; padding: 6px; border-radius: 6px; margin: 2px 0; color: #FFF; font-size: 11px;}
    .stButton>button {background: #0057B8; color: #FFF; font-size: 10px; padding: 3px 6px; border-radius: 6px;}
</style>
""", unsafe_allow_html=True)

# LOGO
LOGO_URL = "https://via.placeholder.com/180x32/0D1117/E90052?text=إيد+مين+بطيز+مين"
st.markdown(f"<img src='{LOGO_URL}' class='logo'>", unsafe_allow_html=True)
st.markdown("<h1 class='title'>إيد مين بطيز مين</h1>", True)

LEAGUE_ID = 443392
BASE_URL = "https://fantasy.premierleague.com/api/"

@st.cache_data(ttl=60)
def get_data():
    try:
        standings = requests.get(f"{BASE_URL}leagues-classic/{LEAGUE_ID}/standings/").json()['standings']['results']
        boot = requests.get(f"{BASE_URL}bootstrap-static/").json()
        gw = next((e['id'] for e in boot['events'] if e['is_current']), 1)
        live = requests.get(f"{BASE_URL}event/{gw}/live/").json()
        players = {p['id']: p for p in boot['elements']}
        return standings, gw, live, players
    except:
        return [], 1, {}, {}

standings, gw, live, players = get_data()
live_pts = {e['id']: e['stats']['total_points'] for e in live.get('elements', [])}

# === VERTICAL FORMATION COORDINATES (OFFICIAL FPL STYLE) ===
VERTICAL_POS = {
    # GK
    1: [(50, 88)],
    # DEF (vertical line at x=50)
    3: [(50, 72), (50, 66), (50, 60)],
    4: [(50, 75), (50, 68), (50, 61), (50, 54)],
    5: [(50, 78), (50, 71), (50, 64), (50, 57), (50, 50)],
    # MID (vertical)
    2: [(50, 45), (50, 38)],
    3: [(50, 48), (50, 41), (50, 34)],
    4: [(50, 50), (50, 43), (50, 36), (50, 29)],
    5: [(50, 52), (50, 45), (50, 38), (50, 31), (50, 24)],
    # FWD (vertical)
    1: [(50, 18)],
    2: [(50, 20), (50, 14)],
    3: [(50, 22), (50, 16), (50, 10)]
}

# === MAIN LOOP ===
for player in standings:
    rank = player['rank']
    name = player['player_name'][:10]
    team = player['entry_name'][:13]
    total = player['total']
    entry_id = player['entry']
    
    # Live change
    change_str = chip_str = ""
    picks = []
    try:
        picks_data = requests.get(f"{BASE_URL}entry/{entry_id}/event/{gw}/picks/").json()
        picks = picks_data.get('picks', [])
        chip = picks_data.get('active_chip')
        if chip:
            chip_str = f"<span class='chip'>{chip[0].upper()}</span>"
        if picks:
            gw_live = sum(live_pts.get(p['element'], 0) * p['multiplier'] for p in picks)
            change = gw_live - player['event_total']
            change_str = f"<span class='gw'>+{change}</span>" if change > 0 else f"<span class='gw-down'>{change}</span>" if change < 0 else ""
    except:
        pass

    row_class = "top1" if rank == 1 else "top2" if rank == 2 else "top3" if rank <= 3 else ""
    
    with st.container():
        st.markdown(f"""
        <div class='row {row_class}'>
            <span class='rank'>#{rank}</span>
            <span style='flex:1; margin-left:6px;'>{name}</span>
            <span style='font-weight:600; min-width:100px;'>{team}</span>
            <span class='points'>{total}</span>
            <span style='min-width:50px;'>
                <span class='points'>{player['event_total']}</span>{change_str}{chip_str}
            </span>
        </div>
        """, True)
        
        with st.expander("", expanded=False):
            st.markdown("<div class='collapsible'>", True)
            
            if not picks:
                st.markdown("**Squad locked until kickoff**", True)
            else:
                # Count starters by position
                pos_count = {1: 0, 2: 0, 3: 0, 4: 0}
                starters = picks[:11]
                for p in starters:
                    pos = players[p['element']]['element_type']
                    pos_count[pos] += 1
                
                st.markdown("<div class='pitch'>", True)
                for p in starters:
                    pl = players[p['element']]
                    pos = pl['element_type']
                    idx = sum(1 for s in starters if players[s['element']]['element_type'] == pos and starters.index(s) < starters.index(p))
                    try:
                        x, y = VERTICAL_POS[pos_count[pos]][idx]
                    except:
                        x, y = 50, 50
                    full_name = pl['second_name']
                    short_name = full_name if len(full_name) <= 10 else full_name[:8] + "."
                    pts = live_pts.get(p['element'], 0)
                    cap = "captain" if p['is_captain'] else ""
                    st.markdown(f"""
                    <div class='player-pos' style='left:{x}%; top:{y}%; transform: translateX(-50%);'>
                        <div class='player-circle {cap}'>{pl['web_name'][:3].upper()}</div>
                        <div class='player-name'>{short_name}</div>
                        <div style='color:#10B981; font-weight:700; font-size:12px;'>{pts}</div>
                    </div>
                    """, True)
                st.markdown("</div>", True)
                
                # Bench
                st.markdown("<div class='bench-row'>", True)
                for p in picks[11:]:
                    pl = players[p['element']]
                    short_name = pl['second_name'] if len(pl['second_name']) <= 10 else pl['second_name'][:8] + "."
                    st.markdown(f"""
                    <div class='bench-player'>
                        <div class='bench-circle'>{pl['web_name'][:3].upper()}</div>
                        <div>{short_name}</div>
                    </div>
                    """, True)
                st.markdown("</div>", True)
            
            st.markdown("</div>", True)

# Footer
st.markdown(f"""
<div style='text-align:center; margin:15px 0; padding:10px; background:#0057B8; border-radius:8px; color:#FFF; font-size:11px;'>
    Leader: {standings[0]['entry_name']} – {standings[0]['total']} pts | GW {gw} | {time.strftime('%H:%M:%S')}
</div>
""", True)

time.sleep(60)
st.rerun()
