import streamlit as st
import requests
import time
from streamlit.components.v1 import html

st.set_page_config(page_title="إيد مين بطيز مين", layout="centered")

# === FULL HTML + CSS IN ONE BLOCK ===
def render_formation(picks, players, live_pts, POS):
    if not picks:
        return '<div class="collapsible"><div class="locked">Squad locked</div></div>'
    
    starters = picks[:11]
    bench = picks[11:]
    
    gk = [p for p in starters if players[p['element']]['element_type'] == 1]
    defs = [p for p in starters if players[p['element']]['element_type'] == 2]
    mids = [p for p in starters if players[p['element']]['element_type'] == 3]
    fwds = [p for p in starters if players[p['element']]['element_type'] == 4]
    
    html_content = """
    <style>
    .collapsible {
        background: #1A5F3D;
        height: 360px;
        position: relative;
        border-radius: 14px;
        border: 2px solid #30363D;
        overflow: hidden;
        font-family: 'Inter', sans-serif;
    }
    .player {
        position: absolute;
        width: 64px;
        text-align: center;
        font-size: 9.5px;
        color: #FFF;
        font-weight: 700;
        text-shadow: 1px 1px 2px #000;
        transform: translateX(-50%);
    }
    .circle {
        width: 34px;
        height: 34px;
        background: #0057B8;
        color: #FFF;
        border-radius: 50%;
        margin: 0 auto 3px;
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
    .name {
        font-size: 9.8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 62px;
        margin: 0 auto;
    }
    .pts {
        color: #10B981;
        font-weight: 700;
        font-size: 12px;
        margin-top: 2px;
    }
    .bench {
        position: absolute;
        bottom: 8px;
        left: 0;
        right: 0;
        display: flex;
        justify-content: center;
        gap: 14px;
        padding: 0 10px;
        overflow-x: auto;
    }
    .bench-item {
        text-align: center;
        min-width: 56px;
        opacity: 0.75;
        font-size: 9px;
    }
    .bench-circle {
        width: 30px;
        height: 30px;
        background: #30363D;
        color: #AAA;
        border-radius: 50%;
        margin: 0 auto 2px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 7.5px;
        border: 1px solid #555;
    }
    .locked {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #AAA;
        font-size: 11px;
    }
    </style>
    <div class="collapsible">
    """
    
    # Players
    for pos, data in [("GK", gk), ("DEF", defs), ("MID", mids), ("FWD", fwds)]:
        positions = POS[pos]
        for i, p in enumerate(data):
            if i >= len(positions): break
            x, y = positions[i]
            pl = players[p['element']]
            pts = live_pts.get(p['element'], 0)
            cap = "captain" if p['is_captain'] else ""
            html_content += f"""
            <div class="player" style="left:{x}%; top:{y}%;">
                <div class="circle {cap}">{pl['web_name'][:3].upper()}</div>
                <div class="name">{pl['second_name']}</div>
                <div class="pts">{pts}</div>
            </div>
            """
    
    # Bench
    html_content += '<div class="bench">'
    for p in bench:
        pl = players[p['element']]
        html_content += f"""
        <div class="bench-item">
            <div class="bench-circle">{pl['web_name'][:3].upper()}</div>
            <div>{pl['second_name']}</div>
        </div>
        """
    html_content += "</div></div>"
    
    return html_content

# === MAIN ===
st.markdown("<h1 style='text-align:center; font-size:20px; background:linear-gradient(90deg,#0057B8,#E90052);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:2px 0;'>إيد مين بطيز مين</h1>", True)

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

POS = {
    "GK":  [(50, 80)],
    "DEF": [(18, 60), (36, 60), (54, 60), (72, 60)],
    "MID": [(14, 40), (32, 40), (50, 40), (68, 40), (86, 40)],
    "FWD": [(28, 20), (50, 20), (72, 20)]
}

for player in standings:
    rank = player['rank']
    name = player['player_name'][:11]
    team = player['entry_name'][:16]
    total = player['total']
    entry_id = player['entry']
    
    change_str = chip_str = ""
    picks = []
    try:
        picks_data = requests.get(f"{BASE_URL}entry/{entry_id}/event/{gw}/picks/").json()
        picks = picks_data.get('picks', [])
        chip = picks_data.get('active_chip')
        if chip:
            chip_str = f"<span style='font-size:8px;padding:1px 4px;background:#E90052;color:#FFF;border-radius:6px;margin-left:3px;'>{chip[0].upper()}</span>"
        if picks:
            gw_live = sum(live_pts.get(p['element'], 0) * p['multiplier'] for p in picks)
            change = gw_live - player['event_total']
            change_str = f"<span style='font-size:10px;color:#10B981;'>+{change}</span>" if change > 0 else f"<span style='font-size:10px;color:#EF4444;'>{change}</span>" if change < 0 else ""
    except:
        pass

    row_class = "style='background:linear-gradient(135deg,#E90052,#0057B8);color:#FFF;border-left-color:#FFD700;'" if rank == 1 else "style='background:linear-gradient(135deg,#3D195B,#0057B8);color:#FFF;'" if rank == 2 else "style='background:linear-gradient(135deg,#E90052,#3D195B);color:#FFF;'" if rank <= 3 else ""
    
    st.markdown(f"""
    <div style='display:flex;align-items:center;padding:6px 8px;margin:2px 0;background:#161B22;border-radius:6px;border-left:3px solid #30363D;font-size:11.5px;' {row_class}>
        <span style='font-weight:700;font-size:12px;min-width:22px;'>#{rank}</span>
        <span style='flex:1;margin-left:5px;'>{name}</span>
        <span style='font-weight:600;min-width:95px;'>{team}</span>
        <span style='font-weight:700;font-size:12px;min-width:38px;text-align:right;'>{player['event_total']}</span><span style='color:#888;font-size:9px;margin:0 4px;'>GW</span>
        <span style='font-weight:700;font-size:12px;min-width:38px;text-align:right;'>{total}</span><span style='color:#888;font-size:9px;margin:0 4px;'>Total</span>
        {change_str}{chip_str}
    </div>
    """, True)
    
    with st.expander("", expanded=False):
        formation_html = render_formation(picks, players, live_pts, POS)
        html(formation_html, height=380)

st.markdown(f"<div style='text-align:center;margin:8px 0;padding:6px;background:#0057B8;border-radius:6px;color:#FFF;font-size:10px;'>GW {gw} • {time.strftime('%H:%M:%S')}</div>", True)

time.sleep(60)
st.rerun()
