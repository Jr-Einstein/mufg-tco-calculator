import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF # <-- NEW: For PDF Generation
from engine import update_all_results # <-- Importing our Brain

# --- PDF GENERATOR FOR SUMMARY ---
def generate_summary_pdf(entities, summary_df, global_res):
    pdf = FPDF(orientation='L', unit='mm', format='A4') # Landscape for wide tables
    pdf.add_page()
    
    # 1. Header (MUFG Style)
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 33)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "IAM TCO GLOBAL EXECUTIVE SUMMARY", 0, 1, 'C')
    
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(100, 100, 100)
    # Added Entity list in header
    entity_str = ", ".join(entities)
    pdf.cell(0, 10, f"Considering Entities: {entity_str}", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"Report Date: {datetime.now().strftime('%b %d, %Y | %H:%M:%S')}", 0, 1, 'R')
    
    pdf.set_draw_color(211, 47, 47)
    pdf.line(10, 38, 287, 38)
    pdf.ln(10)

    # 2. Entity Input Matrix Table
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(227, 74, 74) # Red Header
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, " GLOBAL ENTITY INPUT MATRIX", 0, 1, 'L', fill=True)
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(0, 0, 0)
    
    # Calculate column widths dynamically
    base_col_width = 50
    entity_col_width = (277 - base_col_width) / len(entities)
    
    # Table Header Row
    pdf.cell(base_col_width, 8, "Category", 1, 0, 'C', fill=False)
    for ent in entities:
        pdf.cell(entity_col_width, 8, ent, 1, 0, 'C')
    pdf.ln()

    # Table Data Rows
    pdf.set_font("Arial", '', 8)
    for i, row in summary_df.iterrows():
        pdf.cell(base_col_width, 7, str(row['Category']), 1)
        for ent in entities:
            pdf.cell(entity_col_width, 7, f"{row[ent]:,}", 1, 0, 'C')
        pdf.ln()

    pdf.ln(10)

    # 3. Global Average Costs
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, " BLENDED ALL-ENTITY AVERAGES", 0, 1, 'L', fill=True)
    pdf.ln(2)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 10)
    results_map = [
        ["Global Metric", "Blended Average (USD)"],
        ["By App", f"${global_res.get('unit_by_app', 0):,.2f}"],
        ["By App + License", f"${global_res.get('unit_by_app_lic', 0):,.2f}"],
        ["By Standard User", f"${global_res.get('unit_by_std', 0):,.2f}"],
        ["By Standard User + License", f"${global_res.get('unit_by_std_lic', 0):,.2f}"],
        ["By Privileged User + License", f"${global_res.get('unit_by_priv_lic', 0):,.2f}"]
    ]

    for row in results_map:
        pdf.cell(100, 8, row[0], 1)
        pdf.cell(60, 8, row[1], 1, 1, 'R')

    # Footer
    pdf.set_y(-15)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(128)
    pdf.cell(0, 10, f'Page {pdf.page_no()}', 0, 0, 'C')
    
    return bytes(pdf.output())

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
col_ref, col_dl, col_sp = st.columns([1.2, 1.2, 3.6])
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

# Download Button Logic (Added to Action Bar)
global_res = st.session_state.calculated_results.get('ALL_ENTITIES_COMBINED', {})
with col_dl:
    if global_res:
        summary_pdf = generate_summary_pdf(st.session_state.entities, df_summary, global_res)
        st.download_button(
            label="📥 Download Report",
            data=summary_pdf,
            file_name=f"Global_IAM_TCO_Summary_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# Added "Considering Entities" string after header
entity_list_header = ", ".join(st.session_state.entities)
st.markdown(f"<p style='text-align:center; color:#555; font-weight:700;'>Considering Entities: {entity_list_header}</p>", unsafe_allow_html=True)

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
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-header">GLOBAL AVERAGE COST</div>', unsafe_allow_html=True)
    
    st.markdown("<p style='text-align:center; font-weight:800; color:#E34A4A; font-size:14px; margin-bottom:10px;'>Blended All-Entity Averages</p>", unsafe_allow_html=True)
    
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