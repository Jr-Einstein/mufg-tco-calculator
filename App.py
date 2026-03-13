import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
from fpdf import FPDF # <-- NEW: For PDF Generation
from engine import update_all_results # <-- IMPORTING THE ENGINE

# --- PDF GENERATOR HELPER ---
def generate_pdf(entity_name, inputs, results):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Header with Logo, Entity Name, and Title
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 33)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"IAM TCO Executive Report", 0, 1, 'C')
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Entity: {entity_name}", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%b %d, %Y | %H:%M:%S')}", 0, 1, 'R')
    
    pdf.set_draw_color(211, 47, 47) # MUFG Red
    pdf.line(10, 42, 200, 42) # Horizontal Line Adjusted for double header
    pdf.ln(12)

    # 2. Section: User Inputs
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(0, 10, f" Section 1: User Inputs", 0, 1, 'L', fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", '', 10)
    input_data = [
        ["Metric", "Value"],
        ["Number of Users", f"{inputs.get('users', 0):,}"],
        ["Privilege Users", f"{inputs.get('priv_users', 0):,}"],
        ["Accounts", f"{inputs.get('accounts', 0):,}"],
        ["App / GSI Count", f"{inputs.get('apps', 0):,}"],
        ["Windows Servers", f"{inputs.get('servers_win', 0):,}"],
        ["Linux Servers", f"{inputs.get('servers_linux', 0):,}"],
        ["Other Servers (DB)", f"{inputs.get('servers_other', 0):,}"]
    ]
    
    for row in input_data:
        pdf.cell(95, 8, row[0], 1)
        pdf.cell(95, 8, row[1], 1, 1)
    
    pdf.ln(10)

    # 3. Section: Output Calculations (Expanded to include Cost by App data)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " Section 2: Output Calculations", 0, 1, 'L', fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", '', 10)
    output_data = [
        ["Category", "Calculated Value (USD)"],
        ["IAM Operation Cost", f"${results.get('iam_ops_total', 0):,.2f}"],
        ["Cost by App + License", f"${results.get('tot_by_app_lic', 0):,.2f}"],
        ["Standard User + License", f"${results.get('tot_std_lic', 0):,.2f}"],
        ["Privileged User + License", f"${results.get('tot_priv_lic', 0):,.2f}"],
        ["---", "---"],
        ["By App (Unit)", f"${results.get('unit_by_app', 0):,.2f}"],
        ["By App + License (Unit)", f"${results.get('unit_by_app_lic', 0):,.2f}"],
        ["By Standard User (Unit)", f"${results.get('unit_by_std', 0):,.2f}"],
        ["By Standard User + License (Unit)", f"${results.get('unit_by_std_lic', 0):,.2f}"],
        ["By Privileged User + License (Unit)", f"${results.get('unit_by_priv_lic', 0):,.2f}"]
    ]
    
    for row in output_data:
        pdf.cell(95, 8, row[0], 1)
        pdf.cell(95, 8, row[1], 1, 1)

    # 4. Highlighted Grand Total
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(211, 47, 47)
    pdf.cell(0, 15, f"GRAND TOTAL TCO: ${results.get('grand_total', 0):,.2f}", 0, 1, 'C')

    # 5. Footer with Page Numbers
    pdf.set_y(-15)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(128)
    pdf.cell(0, 10, f'Page {pdf.page_no()}', 0, 0, 'C')
    
    return bytes(pdf.output()) 

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="IAM TCO Analytics", layout="wide", initial_sidebar_state="collapsed")

# --- PERSISTENCE HELPERS ---
STORAGE_FILE = "data_storage.json"

def save_persistent_data(data=None):
    # Ignoring the 'data' argument to instead capture the entire global state
    state_to_save = {
        "entity_data": st.session_state.get('entity_data', {}),
        "iam_rates": st.session_state.get('iam_rates', {}),
        "license_rates": st.session_state.get('license_rates', {}),
        "customizations": st.session_state.get('customizations', {}),
        "calculated_results": st.session_state.get('calculated_results', {}),
        "tco_df_dict": {ent: df.to_json() for ent, df in st.session_state.get('tco_df_dict', {}).items()} if 'tco_df_dict' in st.session_state else {}
    }
    with open(STORAGE_FILE, "w") as f:
        json.dump(state_to_save, f, indent=4)

def load_persistent_data():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return None
    return None

# --- FEATURE 1 HELPER: GLOBAL VIEWER COUNT ---
@st.cache_resource
def get_viewer_count():
    return {"count": 0}

viewers = get_viewer_count()
if 'has_counted' not in st.session_state:
    viewers["count"] += 1
    st.session_state.has_counted = True

# --- 2. GLOBAL SESSION STATE & DEFAULTS ---
# Load EVERYTHING from storage upfront
saved_data = load_persistent_data() or {}

if 'entities' not in st.session_state:
    st.session_state.entities = ['MUBK', 'MUSA', 'BRAZIL', 'MEXICO', 'INTREPID', 'BRAZIL (SOW1)']

if 'current_entity' not in st.session_state:
    st.session_state.current_entity = 'MUBK'

if 'has_notified' not in st.session_state:
    st.session_state.has_notified = False

if 'entity_data' not in st.session_state:
    st.session_state.entity_data = saved_data.get("entity_data", {})

for ent in st.session_state.entities:
    if ent not in st.session_state.entity_data:
        if ent == 'MUBK':
            st.session_state.entity_data['MUBK'] = {
                'users': 9800, 'priv_users': 4500, 'accounts': 17000, 
                'apps': 730, 'servers_win': 3000, 'servers_linux': 2500, 'servers_other': 3500
            }
        else:
            st.session_state.entity_data[ent] = {
                'users': 0, 'priv_users': 0, 'accounts': 0, 'apps': 0, 
                'servers_win': 0, 'servers_linux': 0, 'servers_other': 0
            }

GSIs = ['AAD', 'AC2', 'ARK', 'CTF', 'IGA', 'Q03', 'R22', 'UDA', 'SNOW', 'Entra']
LICENSES = ['ACAT', 'StealthBit', 'IGA', 'CyberArk', 'Centrify', 'ServiceNow']
TCO_CATEGORIES = ['Asset Cost (HY)', 'Resource Cost - FTE', 'Managed Services - TCS PS']

if 'asset_uplift_pct' not in st.session_state: st.session_state.asset_uplift_pct = 40.0
if 'manual_overrides_dict' not in st.session_state: st.session_state.manual_overrides_dict = {ent: {} for ent in st.session_state.entities}
if 'tco_emp' not in st.session_state: st.session_state.tco_emp = 38
if 'tco_cost' not in st.session_state: st.session_state.tco_cost = 226050.0

# ---------------------------------------------------------
# DYNAMIC LOAD: IAM Rates, License Rates, TCO Data, Results
# ---------------------------------------------------------
if 'iam_rates' not in st.session_state:
    if "iam_rates" in saved_data and saved_data["iam_rates"]:
        st.session_state.iam_rates = saved_data["iam_rates"]
    else:
        st.session_state.iam_rates = {'Unix_Support': 1500.0, 'Win_Support': 1500.0, 'AD_Support': 1500.0}
        for g in GSIs: st.session_state.iam_rates[g] = 500.0

if 'license_rates' not in st.session_state:
    if "license_rates" in saved_data and saved_data["license_rates"]:
        st.session_state.license_rates = saved_data["license_rates"]
    else:
        st.session_state.license_rates = {'ACAT': 10.0, 'StealthBit': 20.0, 'IGA': 30.0, 'CyberArk': 40.0, 'Centrify': 50.0, 'ServiceNow': 60.0}

if 'tco_df_dict' not in st.session_state:
    if "tco_df_dict" in saved_data and saved_data["tco_df_dict"]:
        st.session_state.tco_df_dict = {ent: pd.read_json(js) for ent, js in saved_data["tco_df_dict"].items()}
    else:
        st.session_state.tco_df_dict = {}
        init_data = {'Category': TCO_CATEGORIES}
        asset_costs = [287540.0, 432711.0, 815031.0, 68187.2, 40928.5, 335563.0, 156179.0, 308172.0, 0.0, 0.0]
        for i, gsi in enumerate(GSIs):
            init_data[gsi] = [asset_costs[i], 858990.0, 230000.0]
        base_df = pd.DataFrame(init_data)
        for ent in st.session_state.entities:
            st.session_state.tco_df_dict[ent] = base_df.copy()

if 'customizations' not in st.session_state:
    if "customizations" in saved_data and saved_data["customizations"]:
        st.session_state.customizations = saved_data["customizations"]
    else:
        st.session_state.customizations = {}
        for ent in st.session_state.entities:
            st.session_state.customizations[ent] = {
                'tco': {cat: {gsi: True for gsi in GSIs} for cat in TCO_CATEGORIES},
                'license': {lic: True for lic in LICENSES},
                'use_uplift': False, 'uplift_val': 40.0
            }

if 'calculated_results' not in st.session_state or not st.session_state.calculated_results:
    if "calculated_results" in saved_data and saved_data["calculated_results"]:
        st.session_state.calculated_results = saved_data["calculated_results"]
    else:
        update_all_results()

# --- 3. UNIFORM CSS ---
st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    .stApp { background-color: #F0F2F6; font-family: sans-serif; }
    .input-card { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;}
    .section-title { color: #333; font-size: 1.2rem; font-weight: bold; border-bottom: 2px solid #EEE; padding-bottom: 10px; margin-bottom: 15px; }
    .result-box { background-color: white; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.15); margin-bottom: 20px; border: 1px solid #CCC; }
    .red-header { background-color: #D32F2F; color: white; text-align: center; padding: 10px; font-weight: bold; font-size: 16px; }
    .grey-subheader { background-color: #E0E0E0; color: #333; text-align: center; padding: 8px; font-weight: bold; font-size: 14px; margin-top: 10px; margin-bottom: 10px; }
    .center-content { padding: 0 15px 15px 15px; text-align: center; }
    .item-label { font-size: 14px; color: #555; font-weight: bold; margin-bottom: 3px; }
    .item-value { font-size: 16px; color: #000; font-weight: bold; background-color: #F5F5F5; padding: 8px; border-radius: 4px; margin-bottom: 10px; border: 1px solid #E0E0E0;}
    .divider { height: 2px; background-color: #CCC; margin: 15px 0; }
    .grand-total-label { font-size: 16px; font-weight: bold; color: #333; }
    .grand-total-value { font-size: 22px; font-weight: 900; color: #D32F2F; background-color: #FEE2E2; padding: 10px; border-radius: 4px; margin-top: 5px; border: 1px solid #FCA5A5;}
    .list-content { padding: 5px 20px 20px 20px; }
    .list-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #EEE; font-size: 14px; color: #333;}
    .list-row:last-child { border-bottom: none; }
    .list-label { font-weight: 600; }
    .list-val { font-weight: bold; }
    .stNumberInput > div { margin-bottom: -10px; }
    .green-box-small { background-color: #ECFDF5; color: #065F46; border: 1px solid #10B981; padding: 6px 12px; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .custom-footer { width: 100%; background-color: white; color: #555; text-align: center; padding: 12px; font-size: 13px; font-weight: bold; border-top: 3px solid #D32F2F; margin-top: 40px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
    @keyframes slideInRight { 0% { transform: translateX(100%); opacity: 0; } 10% { transform: translateX(0); opacity: 1; } 90% { transform: translateX(0); opacity: 1; } 100% { transform: translateX(100%); opacity: 0; } }
    @keyframes progressFill { from { width: 100%; } to { width: 0%; } }
    .side-notification { position: fixed; top: 80px; right: 20px; width: 350px; background-color: #1E293B; color: white; padding: 18px; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); z-index: 999999; animation: slideInRight 4s ease-in-out forwards; border-left: 6px solid #D32F2F; }
    .progress-timer { position: absolute; bottom: 0; left: 0; height: 4px; background-color: #D32F2F; animation: progressFill 4s linear forwards; }
    </style>
""", unsafe_allow_html=True)

# --- 4. BRANDING & HEADER ---
col_logo, col_title, col_time = st.columns([1, 3, 1])
with col_logo:
    if os.path.exists("logo.png"): st.image("logo.png", width=250)
    else: st.markdown("<h3 style='color:#D32F2F; font-weight:900; font-size: 35px;'>MUFG</h3>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h2 style='text-align: center; color: #333; font-weight: 800; margin: 0;'>IAM TCO Analytics</h2>", unsafe_allow_html=True)
with col_time:
    st.markdown(f"<div style='text-align: right; color: #666; font-weight: 600; font-size: 14px; margin-top: 15px;'>{datetime.now().strftime('%b %d, %Y | %H:%M:%S')}</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 10px 0; border: 0; height: 2px; background: #CCC;'>", unsafe_allow_html=True)

# --- ALIGNMENT FIX & CLEAR DATA LOGIC ---
col_ent, col_sess, col_space, col_clear = st.columns([1.5, 1.5, 3.5, 1])
with col_ent:
    st.session_state.current_entity = st.selectbox("Active Entity Workspace", st.session_state.entities, index=st.session_state.entities.index(st.session_state.current_entity))
with col_sess:
    st.markdown(f"<div style='margin-top: 28px;'><span class='green-box-small'>🟢 Active Sessions: {viewers['count']}</span></div>", unsafe_allow_html=True)
with col_clear:
    st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Data", use_container_width=True):
        if os.path.exists(STORAGE_FILE):
            os.remove(STORAGE_FILE)
        st.session_state.entity_data[st.session_state.current_entity] = {
            'users': 0, 'priv_users': 0, 'accounts': 0, 'apps': 0, 
            'servers_win': 0, 'servers_linux': 0, 'servers_other': 0
        }
        save_persistent_data() 
        update_all_results() 
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.write("") 

# --- 5. MAIN DASHBOARD LAYOUT ---
left_col, right_col = st.columns([1.3, 1], gap="large")

with left_col:
    if 'show_notif' in st.session_state and st.session_state.show_notif:
        st.markdown("""<div class="side-notification"><div style="font-weight: 800; font-size: 15px; margin-bottom: 5px;">Calculation Complete</div><div>Please ensure <b>TCO Data</b> or <b>License Data</b> tabs are updated.</div><div class="progress-timer"></div></div>""", unsafe_allow_html=True)
        st.session_state.show_notif = False

    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Data Inputs</div>', unsafe_allow_html=True)
    
    with st.expander("⚡ Quick Paste from Excel", expanded=False):
        pasted_data = st.text_area("Paste 7 values column here:", height=100, label_visibility="collapsed")
        if st.button("Auto-Fill Fields", key="autofill"):
            try:
                lines = [line.strip().replace(',', '') for line in pasted_data.split('\n') if line.strip()]
                if len(lines) >= 7:
                    st.session_state.entity_data[st.session_state.current_entity].update({'users': int(float(lines[0])), 'priv_users': int(float(lines[1])), 'accounts': int(float(lines[2])), 'apps': int(float(lines[3])), 'servers_win': int(float(lines[4])), 'servers_linux': int(float(lines[5])), 'servers_other': int(float(lines[6]))})
                    save_persistent_data()
                    st.rerun()
            except ValueError: st.error("Format error.")
    
    curr_data = st.session_state.entity_data.get(st.session_state.current_entity, {'users':0, 'priv_users':0, 'accounts':0, 'apps':0, 'servers_win':0, 'servers_linux':0, 'servers_other':0})
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        u_users = st.number_input("Number of Users", value=int(curr_data['users']), step=1)
        u_priv = st.number_input("Number of Privilege Users", value=int(curr_data['priv_users']), step=1)
        u_acc = st.number_input("Number of Accounts", value=int(curr_data['accounts']), step=1)
        u_app = st.number_input("Number of App / GSI", value=int(curr_data['apps']), step=1)
    with c2:
        u_win = st.number_input("Windows Servers", value=int(curr_data['servers_win']), step=1)
        u_lin = st.number_input("Linux Servers", value=int(curr_data['servers_linux']), step=1)
        u_oth = st.number_input("Other Servers (DB)", value=int(curr_data['servers_other']), step=1)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Run Calculations", type="primary", use_container_width=True):
        st.session_state.entity_data[st.session_state.current_entity] = {'users': u_users, 'priv_users': u_priv, 'accounts': u_acc, 'apps': u_app, 'servers_win': u_win, 'servers_linux': u_lin, 'servers_other': u_oth}
        save_persistent_data() 
        update_all_results() 
        save_persistent_data() # Save newly calculated results
        if not st.session_state.has_notified:
            st.session_state.show_notif = True
            st.session_state.has_notified = True
        st.rerun()

    # --- DOWNLOAD REPORT BUTTON ---
    res_for_pdf = st.session_state.calculated_results.get(st.session_state.current_entity, {})
    if res_for_pdf:
        pdf_data = generate_pdf(st.session_state.current_entity, curr_data, res_for_pdf)
        st.download_button(
            label="📥 Download Report",
            data=pdf_data,
            file_name=f"IAM_TCO_Report_{st.session_state.current_entity}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    res = st.session_state.calculated_results.get(st.session_state.current_entity, {})
    iam_op_cost = res.get("iam_ops_total", 0.0)
    tot_app_lic = res.get("tot_by_app_lic", 0.0)
    tot_std_lic = res.get("tot_std_lic", 0.0)
    tot_priv_lic = res.get("tot_priv_lic", 0.0)
    grand_total = res.get("grand_total", 0.0)
    
    html_box1 = f"""
<div class="result-box">
    <div class="red-header">Total Cost to User</div>
    <div class="center-content">
        <div style="margin-top: 15px;"></div>
        <div class="item-label">IAM Operation Cost</div><div class="item-value">${iam_op_cost:,.2f}</div>
        <div class="item-label">Cost by App + License</div><div class="item-value">${tot_app_lic:,.2f}</div>
    </div>
    <div class="grey-subheader">Cost by Identity</div>
    <div class="center-content">
        <div style="margin-label">Standard User + License</div><div class="item-value">${tot_std_lic:,.2f}</div>
        <div class="item-label">Privileged User + License</div><div class="item-value">${tot_priv_lic:,.2f}</div>
        <div class="divider"></div>
        <div class="grand-total-label">Grand Total</div><div class="grand-total-value">${grand_total:,.2f}</div>
    </div>
</div>"""
    st.markdown(html_box1, unsafe_allow_html=True)

    html_box2 = f"""
<div class="result-box">
    <div class="red-header">Total Cost by App</div>
    <div class="grey-subheader">Total cost by per App.</div>
    <div class="list-content">
        <div class="list-row"><span class="list-label">By App:</span><span class="list-val">${res.get('unit_by_app', 0):,.2f}</span></div>
        <div class="list-row"><span class="list-label">By App + License:</span><span class="list-val">${res.get('unit_by_app_lic', 0):,.2f}</span></div>
        <div class="list-row"><span class="list-label">By Standard User:</span><span class="list-val">${res.get('unit_by_std', 0):,.2f}</span></div>
        <div class="list-row"><span class="list-label">By Standard User + License:</span><span class="list-val">${res.get('unit_by_std_lic', 0):,.2f}</span></div>
        <div class="list-row"><span class="list-label">By Privileged User + License:</span><span class="list-val">${res.get('unit_by_priv_lic', 0):,.2f}</span></div>
    </div>
</div>"""
    st.markdown(html_box2, unsafe_allow_html=True)

st.markdown("""<div class="custom-footer">© 2026 MUFG Bank, Ltd. All rights reserved. | IAM TCO Analytics Platform</div>""", unsafe_allow_html=True)