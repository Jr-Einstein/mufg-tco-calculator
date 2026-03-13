import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Resource Forecast", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS FOR HIGH-END UI ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    
    /* Header Note Styling */
    .header-note { 
        background-color: #ffffff; 
        padding: 12px; 
        border: 1px solid #E2E8F0; 
        border-radius: 8px; 
        text-align: center; 
        font-size: 13px; 
        color: #475569; 
        margin-bottom: 25px; 
    }

    /* Result Box with Border and Red Hover-style Header */
    .prediction-container {
        border: 2px solid #E34A4A;
        border-radius: 10px;
        padding: 0px;
        margin-bottom: 20px;
        overflow: hidden;
        background-color: white;
    }
    .prediction-header {
        background-color: #E34A4A; /* Solid Red like hover state */
        color: white;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 15px;
    }
    .prediction-body {
        padding: 15px;
    }
    .pred-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #F1F5F9;
        font-size: 14px;
        color: #1E293B;
    }
    .pred-row:last-child { border-bottom: none; }
    .val-highlight { color: #D32F2F; font-weight: 800; }

    /* Impact Section */
    .impact-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        text-align: center;
    }

    /* Custom Blue Refresh Button */
    div.stButton > button:first-child {
        background-color: #0066CC !important;
        color: white !important;
        border: none !important;
    }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. BRANDING & HEADER ---
col_logo, col_title, col_time = st.columns([1, 3, 1])
with col_logo:
    if os.path.exists("logo.png"): st.image("logo.png", width=240)
    else: st.markdown("<h3 style='color:#D32F2F; font-weight:900;'>MUFG</h3>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h2 style='text-align: center; color: #1E293B; font-weight: 800; margin: 0;'>Resource & Cost Forecast</h2>", unsafe_allow_html=True)
with col_time:
    st.markdown(f"<div style='text-align: right; color: #64748B; font-weight: 600; font-size: 13px; margin-top: 15px;'>{datetime.now().strftime('%b %d, %Y')}</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 10px 0 20px 0; border: 0; height: 1px; background: #E2E8F0;'>", unsafe_allow_html=True)

# --- 4. TOP CONTROLS ---
col_note, col_btn, col_ent = st.columns([3.5, 0.8, 1.2])
with col_note:
    st.markdown('<div class="header-note"><b>Note:</b> Adjust the "Total Applications" below to see the forecasted resource and cost impact.</div>', unsafe_allow_html=True)
with col_btn:
    # Refresh button now in BLUE via CSS
    if st.button("Refresh", use_container_width=True): st.rerun()
with col_ent:
    ents = st.session_state.get('entities', ['MUBK', 'MUSA', 'BRAZIL'])
    selected_ent = st.selectbox("Select Entity", ents, label_visibility="collapsed")

# --- 5. ALIGNED INPUTS (One Line) ---
curr_apps = st.session_state.get('entity_data', {}).get(selected_ent, {}).get('apps', 730)
current_resources = 38 
base_cost = 8589900.00 

st.write("")
col_in1, col_in2, _ = st.columns([2.5, 2.5, 1])
with col_in1:
    st.markdown(f"**Current Applications ({selected_ent}):**")
    st.info(f"{curr_apps}")
with col_in2:
    st.markdown("**Applications After Onboarding:**")
    target_apps = st.number_input("Enter Application", value=int(curr_apps + 25), step=1, label_visibility="collapsed")

# CALCULATIONS
added_apps = target_apps - curr_apps
added_op_eng = added_apps / 11 if added_apps > 0 else 0
added_iam_eng = added_apps / 25 if added_apps > 0 else 0

total_res_op = current_resources + added_op_eng
total_res_iam = current_resources + added_iam_eng
cost_op = base_cost + (added_op_eng * 226050)
cost_iam = base_cost + (added_iam_eng * 226050)
pct_change = ((cost_op - base_cost) / base_cost) * 100 if base_cost > 0 else 0

# --- 6. MAIN CONTENT ---
left_col, right_col = st.columns([2.8, 1.2], gap="medium")

with left_col:
    st.markdown("<h4 style='font-size: 15px; color: #475569;'>Forecasted Resource Matrix</h4>", unsafe_allow_html=True)
    categories = ["Number of users", "Number of Privilege Users", "Number of Accounts", "Number of App", "Servers - Windows", "Servers - Linux", "Servers - Other"]
    keys = ['users', 'priv_users', 'accounts', 'apps', 'servers_win', 'servers_linux', 'servers_other']
    
    table_data = {"Category": categories}
    for ent in ents:
        val_list = []
        for k in keys:
            val = st.session_state.get('entity_data', {}).get(ent, {}).get(k, 0)
            # DYNAMIC UPDATE: If this is the selected entity, use the user input for 'apps'
            if ent == selected_ent and k == 'apps':
                val = target_apps
            val_list.append(val)
        table_data[ent] = val_list
    
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

with right_col:
    st.markdown(f"<h5 style='color:#D32F2F; text-align:center; font-weight:bold; margin-bottom:15px;'>{selected_ent} Predictions</h5>", unsafe_allow_html=True)
    
    # IAM OPERATION ENGINEER
    st.markdown(f'''
    <div class="prediction-container">
        <div class="prediction-header">IAM Operation Engineer</div>
        <div class="prediction-body">
            <div class="pred-row"><span>Resources (Before):</span><span>{current_resources}</span></div>
            <div class="pred-row"><span>Resources (After):</span><span class="val-highlight">{total_res_op:.2f}</span></div>
            <div class="pred-row"><span>Total Cost (After):</span><span class="val-highlight">${cost_op:,.0f}</span></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # IAM ENGINEER
    st.markdown(f'''
    <div class="prediction-container">
        <div class="prediction-header">IAM Engineer</div>
        <div class="prediction-body">
            <div class="pred-row"><span>Resources (Before):</span><span>{current_resources}</span></div>
            <div class="pred-row"><span>Resources (After):</span><span class="val-highlight">{total_res_iam:.2f}</span></div>
            <div class="pred-row"><span>Total Cost (After):</span><span class="val-highlight">${cost_iam:,.0f}</span></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# --- 7. BOTTOM SECTION: IMPACT ANALYSIS ---
st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #1E293B; font-weight:bold;'>Total Impact Analysis</h3>", unsafe_allow_html=True)

low_col, high_col = st.columns([1, 2], gap="large")

with low_col:
    st.markdown('<div class="impact-card">', unsafe_allow_html=True)
    st.write("**Total % Cost Change**")
    st.metric(label="Variance", value=f"{pct_change:.2f}%", delta=f"{pct_change:.2f}%", delta_color="inverse")
    st.progress(min(pct_change / 100, 1.0))
    st.caption("Forecast Variance vs Actual")
    st.markdown('</div>', unsafe_allow_html=True)

with high_col:
    chart_data = pd.DataFrame({
        'Scenario': ['Current', 'Op Eng Forecast', 'IAM Eng Forecast'],
        'Cost ($)': [base_cost, cost_op, cost_iam]
    })
    
    bar_chart = alt.Chart(chart_data).mark_bar(size=50, cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X('Scenario', sort=None, title=None),
        y=alt.Y('Cost ($)', title="Cost in USD"),
        color=alt.condition(
            alt.datum.Scenario == 'Current',
            alt.value('#94A3B8'), 
            alt.value('#D32F2F')  
        )
    ).properties(height=250)
    
    st.altair_chart(bar_chart, use_container_width=True)