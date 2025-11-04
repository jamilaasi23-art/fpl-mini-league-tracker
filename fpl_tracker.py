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
    
    /* PITCH IMAGE + OVERLAY */
    .pitch-wrapper {
        position: relative;
        width: 100%;
        max-width: 400px;
        margin: 16px auto;
    }
    .pitch-img {
        width: 100%;
        height: auto;
        border-radius: 16px;
        border: 3px solid #30363D;
    }
    .player-overlay {
        position: absolute;
        width: 60px;
        text-align: center;
        font-size: 9px;
        color: #FFF;
        font-weight: 700;
        text-shadow: 1px 1px 2px #000;
    }
    .player-circle {
        width: 36px;
        height: 36px;
        background: #0057B8;
        color: #FFF;
        border-radius: 50%;
        margin: 0 auto 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 8px;
        font-weight: 700;
        border: 2.5px solid #FFF;
    }
    .captain {
        border: 3px solid #FFD700 !important;
        background: #FFD700 !important;
        color: #000 !important;
    }
    .player-name {
        font-size: 10px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 58px;
        margin: 0 auto;
    }
    .player-pts {
        color: #10B981;
        font-weight: 700;
        font-size: 12px;
    }
    
    .bench-container {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-top: 12px;
        flex-wrap: nowrap;
        overflow-x: auto;
    }
    .bench-player {
        text-align: center;
        min-width: 60px;
        opacity: 0.8;
        font-size: 9px;
    }
    .bench-circle {
        width: 32px;
        height: 32px;
        background: #30363D;
        color: #AAA;
        border-radius: 50%;
        margin: 0 auto 3px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 8px;
        border: 1px solid #555;
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

# === FIXED POSITIONS ON PITCH IMAGE ===
POSITIONS = {
    "GK": [(50, 85)],
    "DEF": [(20, 65), (40, 65), (60, 65), (80, 65)],
    "MID": [(15, 45), (35, 45), (50, 45), (65, 45), (85, 45)],
    "FWD": [(30, 25), (50, 25), (70, 25)]
}

# PITCH IMAGE
PITCH_IMAGE = "https://i.imgur.com/8Y5fO3j.png"  # Clean FPL-style pitch

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
                
                # PITCH WITH IMAGE
                st.markdown(f"""
                <div class='pitch-wrapper'>
                    <img src='{PITCH_IMAGE}' class='pitch-img'>
                """, True)
                
                # PLAYERS
                all_pos = []
                for pos, data in [("GK", gk), ("DEF", defs), ("MID", mids), ("FWD", fwds)]:
                    for i, p in enumerate(data):
                        if i >= len(POSITIONS[pos]): break
                        x, y = POSITIONS[pos][i]
                        pl = players[p['element']]
                        name = pl['second_name']
                        pts = live_pts.get(p['element'], 0)
                        cap = "captain" if p['is_captain'] else ""
                        all_pos.append((x, y, pl, pts, cap))
                
                for x, y, pl, pts, cap in all_pos:
                    st.markdown(f"""
                    <div class='player-overlay' style='left:{x}%; top:{y}%;'>
                        <div class='player-circle {cap}'>{pl['web_name'][:3].upper()}</div>
                        <div class='player-name'>{pl['second_name']}</div>
                        <div class='player-pts'>{pts}</div>
                    </div>
                    """, True)
                
                st.markdown("</div>", True)
                
                # BENCH
                st.markdown("<div class='bench-container'>", True)
                for p in picks[11:]:
                    pl = players[p['element']]
                    st.markdown(f"""
                    <div class='bench-player'>
                        <div class='bench-circle'>{pl['web_name'][:3].upper()}</div>
                        <div>{pl['second_name']}</div>
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
