import streamlit as st
import requests
import time
from streamlit.components.v1 import html

st.set_page_config(page_title="إيد مين بطيز مين", layout="wide")

# === 580px PITCH ===
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
  
    captain_name = ""
    active_chip = ""
    if picks:
        captain = next((p for p in picks if p['is_captain']), None)
        if captain:
            captain_name = players[captain['element']]['web_name']
        chip = picks[0].get('active_chip') if picks else None
        if chip:
            active_chip = chip.upper()[:2]
   
    header_html = ""
    if captain_name or active_chip:
        header_html = f"""
        <div style='text-align:center; padding:6px 0; font-size:11px; color:#AAA; background:#0D1117;'>
            {f'<span style="color:#FFD700; font-weight:700;">C: {captain_name}</span>' if captain_name else ''}
            {f'<span style="color:#E90052; font-weight:700; margin-left:8px;">{active_chip}</span>' if active_chip else ''}
        </div>
        """
   
    rows = [("FWD", fwds, 10), ("MID", mids, 23), ("DEF", defs, 36), ("GK", gk, 54)]
  
    html_content = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;700&display=swap');
    .collapsible {{background:#1A5F3D;height:580px;position:relative;border-radius:18px;border:2px solid #30363D;overflow:hidden;font-family:'Inter',sans-serif;margin:8px 0;width:100vw;max-width:100vw;margin-left:calc(-50vw + 50%);margin-right:calc(-50vw + 50%);left:50%;right:50%;transform:translateX(-50%);}}
    .row-container {{position:absolute;left:0;right:0;display:flex;justify-content:center;gap:18px;padding:0 14px;}}
    .player {{width:64px;text-align:center;font-size:9.5px;color:#FFF;font-weight:700;text-shadow:1px 1px 2px #000;}}
    .circle {{width:23px;height:23px;background:#0057B8;color:#FFF;border-radius:50%;margin:0 auto 4px;display:flex;align-items:center;justify-content:center;font-size:8px;font-weight:700;border:2px solid #FFF;}}
    .captain {{border:3px solid #FFD700 !important;background:#0057B8 !important;color:#FFF !important;}}
    .name {{font-size:9.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:62px;margin:0 auto 2px;}}
    .pts {{color:#FFFFFF !important;font-weight:700;font-size:13px !important;margin-top:1px;text-shadow:1px 1px 2px #000;}}
    .bench {{position:absolute;bottom:18px;left:0;right:0;display:flex;justify-content:center;gap:24px;padding:0 16px;overflow-x:auto;white-space:nowrap;}}
    .bench-item {{text-align:center;min-width:64px;opacity:0.9;font-size:9px;}}
    .bench-circle {{width:21px;height:21px;background:#30363D;color:#EEE;border-radius:50%;margin:0 auto 3px;display:flex;align-items:center;justify-content:center;font-size:7.5px;border:1.5px solid #777;}}
    .bench-pts {{color:#FFFFFF;font-weight:700;font-size:12px;text-shadow:1px 1px 2px #000;}}
    .locked {{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:#AAA;font-size:14px;}}
    </style>
    <div class="collapsible">{header_html}
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
            html_content += f'<div class="player"><div class="circle {cap}">{team_code}</div><div class="name">{name}</div><div class="pts">{pts}</div></div>'
        html_content += "</div>"
    html_content += '<div class="bench">'
    for p in bench:
        pl = players[p['element']]
        pts = live_pts.get(p['element'], 0)
        team_code = get_team_code(p['element'])
        name = pl['web_name']
        html_content += f'<div class="bench-item"><div class="bench-circle">{team_code}</div><div class="name">{name}</div><div class="bench-pts">{pts}</div></div>'
    html_content += "</div></div>"
    return html_content

# === STYLES ===
st.markdown("""
<style>
    .main {background:#0D1117;color:#FFFFFF;padding:6px;}
    .title {font-size:20px;text-align:center;background:linear-gradient(90deg,#0057B8,#E90052);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:2px 0;font-weight:700;}
    .subtitle {font-size:14px;text-align:center;color:#AAA;margin:0 0 8px;font-weight:500;}
   
    .manager-container {
        display: flex;
        align-items: center;
        margin: 2px 0;
        gap: 6px;
    }
   
    .colored-row {
        flex: 1;
        display: flex;
        align-items: center;
        padding: 6px 8px;
        border-radius: 6px;
        border-left: 3px solid #30363D;
        font-size: 11.5px;
        min-height: 36px;
        overflow: hidden;
    }
    .colored-row:hover {opacity: 0.9;}
   
    .top1 {background:linear-gradient(135deg,#E90052,#0057B8)!important;color:#FFF!important;border-left-color:#FFD700;}
    .top2 {background:linear-gradient(135deg,#3D195B,#0057B8)!important;color:#FFF!important;}
    .top3 {background:linear-gradient(135deg,#E90052,#3D195B)!important;color:#FFF!important;}
   
    .rank {font-weight:700;font-size:12px;min-width:22px;}
    .points {font-weight:700;font-size:12px;min-width:38px;text-align:right;}
    .gw-label {color:#888;font-size:9px;margin:0 4px;}
    .gw {font-size:10px;color:#10B981;}
    .gw-down {color:#EF4444;}
    .team-name {font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex-shrink:0;}
   
    .arrow-btn {
        background: #30363D;
        color: #AAA;
        border: none;
        border-radius: 4px;
        width: 28px;
        height: 28px;
        font-size: 10px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: 0.2s;
        flex-shrink: 0;
    }
    .arrow-btn:hover {background:#444;color:#FFF;}
</style>
""", unsafe_allow_html=True)

st.markdown(f"<img src='https://via.placeholder.com/160x28/0D1117/E90052?text=إيد+مين+بطيز+مين' class='logo'>", True)
st.markdown("<h1 class='title'>إيد مين بطيز مين</h1>", True)

# === FETCH LEAGUE NAME ===
LEAGUE_ID = 443392
BASE_URL = "https://fantasy.premierleague.com/api/"

@st.cache_data(ttl=300)
def get_league_name():
    try:
        league_data = requests.get(f"{BASE_URL}leagues-classic/{LEAGUE_ID}/standings/").json()
        return league_data['league']['name']
    except:
        return "Mini League"

league_name = get_league_name()
st.markdown(f"<p class='subtitle'>{league_name}</p>", unsafe_allow_html=True)

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

# === CALCULATE LIVE POINTS & RE-RANK ===
live_standings = []
for player in standings:
    entry_id = player['entry']
    live_gw = 0
    picks = []
    try:
        picks_data = requests.get(f"{BASE_URL}entry/{entry_id}/event/{gw}/picks/").json()
        picks = picks_data.get('picks', [])
        live_gw = sum(live_pts.get(p['element'], 0) * p['multiplier'] for p in picks)
    except:
        pass
    live_total = player['total'] + live_gw
    live_gain = live_gw - player['event_total']
    live_standings.append({
        **player,
        'live_gw': live_gw,
        'live_total': live_total,
        'live_gain': live_gain,
        'picks': picks
    })

# === SORT BY LIVE TOTAL ===
live_standings.sort(key=lambda x: x['live_total'], reverse=True)

# === DYNAMIC GRADIENT (based on live rank) ===
dynamic_styles = ""
for idx, player in enumerate(live_standings):
    rank = idx + 1
    if rank <= 3: continue
    ratio = (rank - 4) / (len(live_standings) - 4) if len(live_standings) > 4 else 0
    if ratio < 0.25:
        r = int(233 + (0 - 233) * (ratio / 0.25))
        g = int(0 + (87 - 0) * (ratio / 0.25))
        b = int(82 + (184 - 82) * (ratio / 0.25))
    elif ratio < 0.5:
        r = int(0 + (61 - 0) * ((ratio - 0.25) / 0.25))
        g = int(87 + (25 - 87) * ((ratio - 0.25) / 0.25))
        b = int(184 + (91 - 184) * ((ratio - 0.25) / 0.25))
    elif ratio < 0.75:
        r = int(61 + (26 - 61) * ((ratio - 0.5) / 0.25))
        g = int(25 + (95 - 25) * ((ratio - 0.5) / 0.25))
        b = int(91 + (61 - 91) * ((ratio - 0.5) / 0.25))
    else:
        r = int(26 + (13 - 26) * ((ratio - 0.75) / 0.25))
        g = int(95 + (17 - 95) * ((ratio - 0.75) / 0.25))
        b = int(61 + (23 - 61) * ((ratio - 0.75) / 0.25))
    color = f"#{r:02x}{g:02x}{b:02x}"
    dynamic_styles += f".colored-row.rank{rank}{{background:linear-gradient(135deg,{color},#0D1117)!important;color:#FFF!important;border-left-color:#30363D!important;}}"
st.markdown(f"<style>{dynamic_styles}</style>", unsafe_allow_html=True)

# === SESSION STATE ===
if 'expanded' not in st.session_state:
    st.session_state.expanded = {}

# === RENDER LIVE STANDINGS ===
for idx, player in enumerate(live_standings):
    live_rank = idx + 1
    # First name only
    full_name = player['player_name']
    first_name = full_name.split()[0] if full_name else "Player"
    # Full team name (no truncation)
    team_name = player['entry_name']
    live_gw = player['live_gw']
    live_total = player['live_total']
    live_gain = player['live_gain']
    picks = player['picks']

    change_str = f"<span class='gw'>+{live_gain}</span>" if live_gain > 0 else f"<span class='gw-down'>{live_gain}</span>" if live_gain < 0 else ""

    row_class = f"top{live_rank}" if live_rank <= 3 else f"rank{live_rank}"
    key = f"row_{idx}"

    col1, col2 = st.columns([1, 0.1])
   
    with col1:
        st.markdown(f"""
        <div class="colored-row {row_class}">
            <span class="rank">#{live_rank}</span>
            <span style="flex:1;margin-left:5px;min-width:60px;">{first_name}</span>
            <span class="team-name" style="min-width:120px;">{team_name}</span>
            <span class="points">{live_gw}</span><span class="gw-label">GW</span>
            <span class="points">{live_total}</span><span class="gw-label">Total</span>
            {change_str}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        arrow_text = "CLOSE SQUAD" if st.session_state.expanded.get(key, False) else "OPEN SQUAD"
        if st.button(arrow_text, key=f"btn_{key}", help="Toggle squad"):
            st.session_state.expanded[key] = not st.session_state.expanded.get(key, False)
            st.rerun()

    if st.session_state.expanded.get(key, False):
        formation_html = render_formation(picks, players, live_pts, teams)
        html(formation_html, height=600)

st.markdown(f"""
<div style='text-align:center;margin:8px 0;padding:6px;background:#0057B8;border-radius:6px;color:#FFF;font-size:10px;'>
    GW {gw} • LIVE • {time.strftime('%H:%M:%S')}
</div>
""", unsafe_allow_html=True)

time.sleep(60)
st.rerun()

