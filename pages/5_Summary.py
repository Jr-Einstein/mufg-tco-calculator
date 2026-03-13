import streamlit as st
import pandas as pd
from datetime import datetime
import os
from engine import update_all_results # <-- Importing our Brain

# --- INITIALIZATION CHECK ---
if 'entities' not in st.session_state:
    st.session_state.entities = ['MUBK', 'MUSA', 'BRAZIL', 'MEXICO', 'INTREPID', 'BRAZIL (SOW1)']

if 'entity_data' not in st.session_state:
    st.session_state.entity_data = {
        ent: {
            'users': 0, 'priv_users': 0, 'accounts': 0, 
            'apps': 0, 'servers_win': 0, 'servers_linux': 0, 'servers_other': 0
        } for ent in st.session_state.entities
    }
    
# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Overall Summary", layout="wide", initial_sidebar_state="collapsed")

# 🧠 FIRE THE ENGINE: Ensure we have the latest global math before rendering
update_all_results()

# --- 2. UNIFORM CSS ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    .stApp { background-color: #F4F6F9; }
    
    /* Overall Summary Table Header */
    .summary-title-box { 
        background-color: #E34A4A; 
        color: white; 
        padding: 12px; 
        border-radius: 6px 6px 0 0; 
        text-align: center; 
        font-weight: bold; 
        font-size: 20px; 
    }
    
    /* Result Sidebar - Improved with Border */
    .result-card { 
        background-color: white; 
        padding: 20px; 
        border-radius: 10px; 
        border: 2px solid #E34A4A; /* Solid Red Border */
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        margin-top: 10px;
    }
    .result-header { 
        background-color: #E34A4A; 
        color: white; 
        padding: 10px; 
        text-align: center; 
        font-weight: bold; 
        font-size: 16px; 
        border-radius: 4px; 
        margin-bottom: 20px;
    }
    .result-row { 
        display: flex; 
        justify-content: space-between; 
        padding: 12px 0; 
        border-bottom: 1px solid #DDD; 
        font-size: 14px; 
        font-weight: 700; 
        color: #333;
    }
    .result-row:last-child { border-bottom: none; }
    
    /* KPI Metric Tiles */
    .metric-box { 
        background-color: white; 
        padding: 15px; 
        border-radius: 8px; 
        text-align: center; 
        border-bottom: 4px solid #E34A4A; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .metric-label { font-size: 12px; color: #666; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 24px; color: #D32F2F; font-weight: 900; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. BRANDING & HEADER ---
col_logo, col_title, col_time = st.columns([1, 3, 1])
with col_logo:
    if os.path.exists("logo.png"): st.image("logo.png", width=240)
    else: st.markdown("<h3 style='color:#D32F2F; font-weight:900;'>MUFG</h3>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h2 style='text-align: center; color: #111; font-weight: 800; margin: 0;'>IAM TCO PLATFORM</h2>", unsafe_allow_html=True)
with col_time:
    st.markdown(f"<div style='text-align: right; color: #777; font-weight: 600; font-size: 13px; margin-top: 15px;'>{datetime.now().strftime('%b %d, %Y')}</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 10px 0 10px 0; border: 0; height: 1px; background: #BBB;'>", unsafe_allow_html=True)

# --- 4. ACTION BAR ---
col_ref, _ = st.columns([1, 4])
with col_ref:
    if st.button("🔄 Refresh Summary", use_container_width=True):
        st.rerun()

# --- 5. DATA LOGIC (Building the Matrix) ---
categories = [
    "Number of users", "Number of Privilege Users", "Number of Accounts",
    "Number of App", "Number of Servers - Windows", "Number of Servers - Linux",
    "Number of Servers - Other (Including DB)"
]
key_map = {
    "Number of users": "users", "Number of Privilege Users": "priv_users",
    "Number of Accounts": "accounts", "Number of App": "apps",
    "Number of Servers - Windows": "servers_win", "Number of Servers - Linux": "servers_linux",
    "Number of Servers - Other (Including DB)": "servers_other"
}

summary_table = {"Category": categories}
total_users = 0
total_apps = 0

for ent in st.session_state.entities:
    data = st.session_state.entity_data.get(ent, {k: 0 for k in key_map.values()})
    summary_table[ent] = [data[key_map[cat]] for cat in categories]
    total_users += data['users']
    total_apps += data['apps']

df_summary = pd.DataFrame(summary_table)

# --- 6. KPI METRICS ---
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'<div class="metric-box"><div class="metric-label">Global Total Users</div><div class="metric-value">{total_users:,}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-box"><div class="metric-label">Global Total Apps</div><div class="metric-value">{total_apps:,}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-box"><div class="metric-label">Configured Entities</div><div class="metric-value">{len(st.session_state.entities)}</div></div>', unsafe_allow_html=True)

# --- 7. MAIN CONTENT ---
left_col, right_col = st.columns([2.4, 1], gap="large")

with left_col:
    st.markdown('<div class="summary-title-box">Entity Input Matrix</div>', unsafe_allow_html=True)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

with right_col:
    # 🧠 FETCH THE GLOBAL AVERAGES FROM THE ENGINE
    global_res = st.session_state.calculated_results.get('ALL_ENTITIES_COMBINED', {})
    
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-header">GLOBAL AVERAGE COST</div>', unsafe_allow_html=True)
    
    st.markdown("<p style='text-align:center; font-weight:800; color:#E34A4A; font-size:14px; margin-bottom:10px;'>Blended All-Entity Averages</p>", unsafe_allow_html=True)
    
    # Mapping the engine's global results to your UI labels
    results = [
        ("By App", global_res.get("unit_by_app", 0.00)),
        ("By App + License", global_res.get("unit_by_app_lic", 0.00)),
        ("By Standard User", global_res.get("unit_by_std", 0.00)),
        ("By Standard User + License", global_res.get("unit_by_std_lic", 0.00)),
        ("By Privileged User + License", global_res.get("unit_by_priv_lic", 0.00))
    ]
    
    for label, val in results:
        st.markdown(f'''
            <div class="result-row">
                <span>{label}</span>
                <span style="color:#D32F2F;">${val:,.2f}</span>
            </div>
        ''', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)