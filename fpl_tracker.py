import streamlit as st
import requests
import time

st.set_page_config(page_title="إيد مين بطيز مين", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;700&display=swap');
    .main {background: #3D195B; color: #FFFFFF; font-family: 'Inter', sans-serif; padding: 10px;}
    .title {font-size: 28px; text-align: center; background: linear-gradient(90deg, #0057B8, #E90052); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 5px 0; font-weight: 700;}
    .logo {height: 40px; display: block; margin: 0 auto 5px;}
    .row {display: flex; align-items: center; padding: 8px 12px; margin: 2px 0; 
          background: #F5F5F5; border-radius: 8px; border-left: 4px solid #0057B8; font-size: 13px; color: #000;}
    .top1 {background: linear-gradient(135deg, #E90052, #0057B8) !important; color: #FFF !important; border-left-color: #FFFFFF;}
    .top2 {background: linear-gradient(135deg, #3D195B, #0057B8) !important; color: #FFF !important;}
    .top3 {background: linear-gradient(135deg, #E90052, #3D195B) !important; color: #FFF !important;}
    .rank {font-weight: 700; font-size: 16px; min-width: 30px;}
    .points {font-weight: 700; font-size: 15px; min-width: 50px; text-align: right;}
    .gw {font-size: 12px; color: #0057B8;}
    .gw-down {color: #E90052;}
    .chip {font-size: 10px; padding: 2px 6px; background: #E90052; color: #FFF; border-radius: 10px; margin-left: 4px;}
    .pitch {background: url('https://i.imgur.com/8vY5j7I.png') no-repeat center center; 
            background-size: cover; height: 400px; position: relative; border-radius: 12px; margin: 10px 0;}
    .player-pos {position: absolute; width: 50px; text-align: center; color: #FFF; font-weight: 700; text-shadow: 1px 1px 3px #000;}
    .player-img {width: 40px; height: 40px; border-radius: 50%; border: 2px solid #FFF; margin-bottom: 4px;}
    .captain {border: 3px solid #FFD700 !important;}
    .bench-row {display: flex; justify-content: center; gap: 10px; margin-top: 10px;}
    .bench-player {text-align: center; width: 70px; opacity: 0.8;}
    .collapsible {background: #F5F5F5; padding: 10px; border-radius: 8px; margin: 5px 0; color: #000;}
    .stButton>button {background: #0057B8; color: #FFF; border-radius: 8px; font-weight: 600; font-size: 12px; padding: 4px 8px;}
</style>
""", unsafe_allow_html=True)

# LOGO
LOGO_URL = "https://via.placeholder.com/200x40/3D195B/E90052?text=إيد+مين+بطيز+مين"
st.markdown(f"<img src='{LOGO_URL}' class='logo'>", unsafe_allow_html=True)
st.markdown("<h1 class='title'>إيد مين بطيز مين</h1>", True)

LEAGUE_ID = 443392
BASE_URL = "https://fantasy.premierleague.com/api/"
IMG_BASE = "https://resources.premierleague.com/premierleague/photos/players/110x140/"

# === DATA ===
@st.cache_data(ttl=60)
def get_all_data():
    try:
        standings = requests.get(f"{BASE_URL}leagues-classic/{LEAGUE_ID}/standings/").json()['standings']['results']
        boot = requests.get(f"{BASE_URL}bootstrap-static/").json()
        gw = next(e['id'] for e in boot['events'] if e['is_current'])
        live = requests.get(f"{BASE_URL}event/{gw}/live/").json()
        players = {p['id']: p for p in boot['elements']}
        return standings, gw, live, players
    except:
        return [], 1, {}, {}

standings, gw, live, players = get_all_data()
live_pts = {e['id']: e['stats']['total_points'] for e in live.get('elements', [])}

# === POSITIONS ON PITCH (x, y in %) ===
POSITIONS = {
    1: {"GK": (50, 85)},
    2: {"DEF": [(25, 70), (50, 70), (75, 70)]},
    3: {"DEF": [(20, 70), (40, 70), (60, 70), (80, 70)]},
    4: {"DEF": [(15, 70), (35, 70), (65, 70), (85, 70)]},
    5: {"DEF": [(10, 70), (30, 70), (50, 70), (70, 70), (90, 70)]},
    2: {"MID": [(35, 50), (65, 50)]},
    3: {"MID": [(25, 50), (50, 50), (75, 50)]},
    4: {"MID": [(20, 50), (40, 50), (60, 50), (80, 50)]},
    5: {"MID": [(15, 50), (35, 50), (50, 50), (65, 50), (85, 50)]},
    1: {"FWD": [(50, 25)]},
    2: {"FWD": [(35, 25), (65, 25)]},
    3: {"FWD": [(25, 25), (50, 25), (75, 25)]}
}

# === MAIN LOOP ===
for player in standings:
    rank = player['rank']
    name = player['player_name'][:12]
    team = player['entry_name'][:15]
    total = player['total']
    entry_id = player['entry']
    
    # Live GW
    change_str = chip_str = ""
    try:
        picks_data = requests.get(f"{BASE_URL}entry/{entry_id}/event/{gw}/picks/").json()
        picks = picks_data['picks']
        chip = picks_data.get('active_chip')
        if chip:
            chip_str = f"<span class='chip'>{chip[0].upper()}</span>"
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
            <span style='flex:1; margin-left:10px;'>{name}</span>
            <span style='font-weight:600; min-width:120px;'>{team}</span>
            <span class='points'>{total}</span>
            <span style='min-width:60px;'>
                <span class='points'>{player['event_total']}</span>{change_str}{chip_str}
            </span>
        </div>
        """, True)
        
        # COLLAPSIBLE SQUAD
        with st.expander("", expanded=False):
            st.markdown("<div class='collapsible'>", True)
            
            # Get picks
            try:
                picks_data = requests.get(f"{BASE_URL}entry/{entry_id}/event/{gw}/picks/").json()
                picks = picks_data['picks']
                chip = picks_data.get('active_chip')
                if chip:
                    st.markdown(f"<p style='text-align:center; margin:5px;'><span class='chip'>{chip.upper()}</span></p>", True)
                
                starters = [p for p in picks if p['position'] <= 11]
                bench = [p for p in picks if p['position'] > 11]
                
                # Count by position
                gk = [p for p in starters if players[p['element']]['element_type'] == 1]
                defs = [p for p in starters if players[p['element']]['element_type'] == 2]
                mids = [p for p in starters if players[p['element']]['element_type'] == 3]
                fwds = [p for p in starters if players[p['element']]['element_type'] == 4]
                
                # Pitch
                st.markdown("<div class='pitch'>", True)
                for p in starters:
                    pl = players[p['element']]
                    pos = pl['element_type']
                    idx = [s for s in starters if players[s['element']]['element_type'] == pos].index(p)
                    coords = POSITIONS[len([s for s in starters if players[s['element']]['element_type'] <= pos])][["GK","DEF","MID","FWD"][pos-1]][idx]
                    x, y = coords
                    img_code = pl['photo'].replace('.jpg', '')
                    img = f"{IMG_BASE}p{img_code}.png"
                    name = f"{pl['first_name']} {pl['second_name']}".split()[-1]
                    pts = live_pts.get(p['element'], 0)
                    cap = "captain" if p['is_captain'] else ""
                    st.markdown(f"""
                    <div class='player-pos' style='left:{x}%; top:{y}%; transform:translate(-50%,-50%);'>
                        <img src='{img}' class='player-img {cap}' onerror="this.src='https://via.placeholder.com/40/0057B8/FFFFFF?text=?';">
                        <div style='font-size:10px;'>{name}</div>
                        <div style='font-size:11px; color:#10b981;'>{pts}</div>
                    </div>
                    """, True)
                st.markdown("</div>", True)
                
                # Bench
                st.markdown("<div class='bench-row'>", True)
                for p in bench:
                    pl = players[p['element']]
                    img_code = pl['photo'].replace('.jpg', '')
                    img = f"{IMG_BASE}p{img_code}.png"
                    name = f"{pl['first_name']} {pl['second_name']}".split()[-1]
                    st.markdown(f"""
                    <div class='bench-player'>
                        <img src='{img}' class='player-img' style='width:35px;height:35px;' onerror="this.src='https://via.placeholder.com/35/334155/94a3b8?text=?';">
                        <div style='font-size:10px; margin-top:2px;'>{name}</div>
                    </div>
                    """, True)
                st.markdown("</div>", True)
                
            except:
                st.write("Squad not available")
            
            st.markdown("</div>", True)

# Footer
st.markdown(f"""
<div style='text-align:center; margin:20px 0; padding:15px; background:#0057B8; border-radius:12px; color:#FFF; font-size:12px;'>
    🏆 Leader: {standings[0]['entry_name']} – {standings[0]['total']} pts | GW {gw} | Updated: {time.strftime('%H:%M:%S')}
</div>
""", True)

time.sleep(90)
st.rerun()
