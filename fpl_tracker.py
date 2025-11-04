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
    
    /* PITCH */
    .pitch {
        background: #1A5F3D;
        height: 500px;
        position: relative;
        border-radius: 16px;
        margin: 16px 0;
        border: 3px solid #30363D;
        overflow: visible !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .player-pos {
        position: absolute;
        width: 80px;
        text-align: center;
        font-size: 10px;
        color: #FFF;
        font-weight: 700;
        text-shadow: 1px 1px 3px #000;
        transform: translateX(-50%);
        z-index: 100;
    }
    .player-circle {
        width: 40px;
        height: 40px;
        background: #0057B8;
        color: #FFF;
        border-radius: 50%;
        margin: 0 auto 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 9px;
        font-weight: 700;
        border: 3px solid #FFF;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
    }
    .captain {
        border: 3.5px solid #FFD700 !important;
        background: #FFD700 !important;
        color: #000 !important;
        box-shadow: 0 0 8px #FFD700;
    }
    .player-name {
        font-size: 11px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 76px;
        margin: 0 auto;
    }
    .player-pts {
        color: #10B981;
        font-weight: 700;
        font-size: 13px;
        margin-top: 4px;
    }
    
    /* BENCH — HORIZONTAL LINE */
    .bench-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 10px;
        padding: 10px 0;
        border-top: 1px solid #30363D;
        flex-wrap: nowrap;
        overflow-x: auto;
    }
    .bench-player {
        text-align: center;
        min-width: 70px;
        opacity: 0.8;
        font-size: 10px;
    }
    .bench-circle {
        width: 36px;
        height: 36px;
        background: #30363D;
        color: #AAA;
        border-radius: 50%;
        margin: 0 auto 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 9px;
        border: 1.5px solid #555;
    }
    .collapsible {background: #161B22; padding: 12px; border-radius: 10px; margin: 2px 0; color: #FFF;}
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

# === SPACING ===
def get_positions(num, base_y, spacing):
    if num == 0: return []
    start = 50 - (num - 1) * spacing / 2
    return [(start + i * spacing, base_y) for i in range(num)]

POS = {
    "GK": lambda n: get_positions(n, 75, 0) if n > 0 else [],
    "DEF": lambda n: get_positions(n, 58, 18),
    "MID": lambda n: get_positions(n, 38, 20),
    "FWD": lambda n: get_positions(n, 18, 24)
}

# === MAIN LOOP ===
for player in standings:
    rank = player['rank']
    name = player['player_name'][:10]
    team = player['entry_name'][:13]
    total = player['total']
    entry_id = player['entry']
    
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
                starters = picks[:11]
                gk = [p for p in starters if players[p['element']]['element_type'] == 1]
                defs = [p for p in starters if players[p['element']]['element_type'] == 2]
                mids = [p for p in starters if players[p['element']]['element_type'] == 3]
                fwds = [p for p in starters if players[p['element']]['element_type'] == 4]
                
                st.markdown("<div class='pitch'>", True)
                
                # === STARTERS ON PITCH ===
                for pos, data in [("GK", gk), ("DEF", defs), ("MID", mids), ("FWD", fwds)]:
                    for i, p in enumerate(data):
                        pl = players[p['element']]
                        x, y = POS[pos](len(data))[i]
                        name = pl['second_name']
                        pts = live_pts.get(p['element'], 0)
                        cap = "captain" if p['is_captain'] else ""
                        st.markdown(f"""
                        <div class='player-pos' style='left:{x}%; top:{y}%;'>
                            <div class='player-circle {cap}'>{pl['web_name'][:3].upper()}</div>
                            <div class='player-name'>{name}</div>
                            <div class='player-pts'>{pts}</div>
                        </div>
                        """, True)
                
                st.markdown("</div>", True)
                
                # === BENCH — HORIZONTAL LINE ===
                st.markdown("<div class='bench-container'>", True)
                for p in picks[11:]:
                    pl = players[p['element']]
                    name = pl['second_name']
                    st.markdown(f"""
                    <div class='bench-player'>
                        <div class='bench-circle'>{pl['web_name'][:3].upper()}</div>
                        <div>{name}</div>
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
