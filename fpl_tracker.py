import streamlit as st
import requests
import time
from streamlit.components.v1 import html

st.set_page_config(page_title="إيد مين بطيز مين", layout="wide")

# === 580px PITCH + JERSEY NAME ===
def render_formation(picks, players, live_pts, teams):
    if not picks:
        return '<div class="collapsible"><div class="locked">Squad locked</div></div>'
   
    starters = picks[:11]
    bench = picks[11:]
   
    gk = [p for p in starters if players[p['element']]['element_type'] == 1]
    defs = [p for p in starters if players[p['element']]['element_type'] == 2]
    mids = [p for p in starters if players[p['element']]['element_type'] == 3]
    fwds = [p for p in starters if players[p['element']]['element_type'] == 4]
   
    def get_team_code(pid):
        return teams.get(players[pid]['team'], "??")
   
    # === GET CAPTAIN & CHIP FOR HEADER ===
    captain_name = ""
    active_chip = ""
    if picks:
        captain = next((p for p in picks if p['is_captain']), None)
        if captain:
            captain_name = players[captain['element']]['web_name']
        chip = picks[0].get('active_chip') if picks else None
        if chip:
            active_chip = chip.upper()[:2]
    
    # === HEADER WITH CAPTAIN + CHIP (BEFORE OPENING) ===
    header_html = ""
    if captain_name or active_chip:
        header_html = f"""
        <div style='text-align:center; padding:6px 0; font-size:11px; color:#AAA; background:#0D1117;'>
            {f'<span style="color:#FFD700; font-weight:700;">C: {captain_name}</span>' if captain_name else ''}
            {f'<span style="color:#E90052; font-weight:700; margin-left:8px;">{active_chip}</span>' if active_chip else ''}
        </div>
        """
    
    rows = [
        ("FWD", fwds, 10),
        ("MID", mids, 23),
        ("DEF", defs, 36),
        ("GK", gk, 54)
    ]
   
    html_content = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;700&display=swap');
    .collapsible {{
        background: #1A5F3D;
        height: 580px;
        position: relative;
        border-radius: 18px;
        border: 2px solid #30363D;
        overflow: hidden;
        font-family: 'Inter', sans-serif;
        margin: 8px 0;
        width: 100vw;
        max-width: 100vw;
        margin-left: calc(-50vw + 50%);
        margin-right: calc(-50vw + 50%);
        left: 50%;
        right: 50%;
        transform: translateX(-50%);
    }}
    .row-container {{
        position: absolute;
        left: 0; right: 0;
        display: flex;
        justify-content: center;
        gap: 18px;
        padding: 0 14px;
    }}
    .player {{
        width: 64px;
        text-align: center;
        font-size: 9.5px;
        color: #FFF;
        font-weight: 700;
        text-shadow: 1px 1px 2px #000;
    }}
    .circle {{
        width: 23px;
        height: 23px;
        background: #0057B8;
        color: #FFF;
        border-radius: 50%;
        margin: 0 auto 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 8px;
        font-weight: 700;
        border: 2px solid #FFF;
    }}
    .captain {{
        border: 3px solid #FFD700 !important;
        background: #0057B8 !important;
        color: #FFF !important;
    }}
    .name {{
        font-size: 9.5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 62px;
        margin: 0 auto 2px;
    }}
    .pts {{
        color: #FFFFFF !important;
        font-weight: 700;
        font-size: 13px !important;
        margin-top: 1px;
        text-shadow: 1px 1px 2px #000;
    }}
    .bench {{
        position: absolute;
        bottom: 18px;
        left: 0;
        right: 0;
        display: flex;
        justify-content: center;
        gap: 24px;
        padding: 0 16px;
        overflow-x: auto;
        white-space: nowrap;
    }}
    .bench-item {{
        text-align: center;
        min-width: 64px;
        opacity: 0.9;
        font-size: 9px;
    }}
    .bench-circle {{
        width: 21px;
        height: 21px;
        background: #30363D;
        color: #EEE;
        border-radius: 50%;
        margin: 0 auto 3px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 7.5px;
        border: 1.5px solid #777;
    }}
    .bench-pts {{
        color: #FFFFFF;
        font-weight: 700;
        font-size: 12px;
        text-shadow: 1px 1px 2px #000;
    }}
    .locked {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #AAA;
        font-size: 14px;
    }}
    </style>
    <div class="collapsible">
    {header_html}
    """
   
    for pos, data, top_pct in rows:
        if not data: continue
        html_content += f'<div class="row-container" style="top:{top_pct}%;">'
        for p in data:
            pl = players[p['element']]
            pts = live_pts.get(p['element'], 0)
            cap = "captain" if p['is_captain'] else ""
            team_code = get_team_code(p['element'])
            name = pl['web_name']
            html_content += f"""
            <div class="player">
                <div class="circle {cap}">{team_code}</div>
                <div class="name">{name}</div>
                <div class="pts">{pts}</div>
            </div>
            """
        html_content += "</div>"
   
    html_content += '<div class="bench">'
    for p in bench:
        pl = players[p['element']]
        pts = live_pts.get(p['element'], 0)
        team_code = get_team_code(p['element'])
        name = pl['web_name']
        html_content += f"""
        <div class="bench-item">
            <div class="bench-circle">{team_code}</div>
            <div class="name">{name}</div>
            <div class="bench-pts">{pts}</div>
        </div>
        """
    html_content += "</div></div>"
   
    return html_content

# === MAIN STYLES: FULL LIST COLORED (1st to last) ===
st.markdown("""
<style>
    .main {background: #0D1117; color: #FFFFFF; padding: 6px;}
    .title {font-size: 20px; text-align: center; background: linear-gradient(90deg, #0057B8, #E90052);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 2px 0; font-weight: 700;}
    .row {display: flex; align-items: center; padding: 6px 8px; margin: 2px 0;
          background: #161B22; border-radius: 6px; border-left: 3px solid #30363D; font-size: 11.5px;}
    .rank {font-weight: 700; font-size: 12px; min-width: 22px;}
    .points {font-weight: 700; font-size: 12px; min-width: 38px; text-align: right;}
    .gw-label {color: #888; font-size: 9px; margin: 0 4px;}
    .gw {font-size: 10px; color: #10B981;}
    .gw-down {color: #EF4444;}
</style>
""", unsafe_allow_html=True)

# === DYNAMIC COLOR PER RANK ===
def get_row_class(rank, total_managers):
    if rank == 1:
        return "top1"
    elif rank == 2:
        return "top2"
    elif rank == 3:
        return "top3"
    else:
        # Gradient from #161B22 (4th) to #0D1117 (last)
        ratio = (rank - 3) / (total_managers - 3) if total_managers > 3 else 0
        r = int(22 + (13 - 22) * ratio)
        g = int(27 + (17 - 27) * ratio)
        b = int(34 + (23 - 34) * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        return f"rank{rank}"

# Add dynamic styles
dynamic_styles = ""
for player in standings:
    rank = player['rank']
    total_managers = len(standings)
    row_class = get_row_class(rank, total_managers)
    if rank > 3:
        ratio = (rank - 3) / (total_managers - 3) if total_managers > 3 else 0
        r = int(22 + (13 - 22) * ratio)
        g = int(27 + (17 - 27) * ratio)
        b = int(34 + (23 - 34) * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        dynamic_styles += f"""
        .row.rank{rank} {{
            background: {color} !important;
            border-left-color: #30363D !important;
        }}
        """

st.markdown(f"<style>{dynamic_styles}</style>", unsafe_allow_html=True)

st.markdown(f"<img src='https://via.placeholder.com/160x28/0D1117/E90052?text=إيد+مين+بطيز+مين' class='logo'>", True)
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
        teams = {t['id']: t['short_name'] for t in boot['teams']}
        return standings, gw, live, players, teams
    except:
        return [], 1, {}, {}, {}

standings, gw, live, players, teams = get_data()
live_pts = {e['id']: e['stats']['total_points'] for e in live.get('elements', [])}

total_managers = len(standings)

for player in standings:
    rank = player['rank']
    name = player['player_name'][:11]
    team = player['entry_name'][:16]
    total = player['total']
    entry_id = player['entry']
   
    change_str = ""
    picks = []
   
    try:
        picks_data = requests.get(f"{BASE_URL}entry/{entry_id}/event/{gw}/picks/").json()
        picks = picks_data.get('picks', [])
        if picks:
            gw_live = sum(live_pts.get(p['element'], 0) * p['multiplier'] for p in picks)
            change = gw_live - player['event_total']
            change_str = f"<span class='gw'>+{change}</span>" if change > 0 else f"<span class='gw-down'>{change}</span>" if change < 0 else ""
    except:
        pass

    row_class = get_row_class(rank, total_managers)
   
    # === COLORED ROW: FULL LIST ===
    st.markdown(f"""
    <div class='row {row_class}'>
        <span class='rank'>#{rank}</span>
        <span style='flex:1; margin-left:5px;'>{name}</span>
        <span style='font-weight:600; min-width:95px;'>{team}</span>
        <span class='points'>{player['event_total']}</span><span class='gw-label'>GW</span>
        <span class='points'>{total}</span><span class='gw-label'>Total</span>
        {change_str}
    </div>
    """, unsafe_allow_html=True)
   
    with st.expander("", expanded=False):
        formation_html = render_formation(picks, players, live_pts, teams)
        html(formation_html, height=600)

st.markdown(f"""
<div style='text-align:center; margin:8px 0; padding:6px; background:#0057B8; border-radius:6px; color:#FFF; font-size:10px;'>
    GW {gw} • {time.strftime('%H:%M:%S')}
</div>
""", unsafe_allow_html=True)

time.sleep(60)
st.rerun()
