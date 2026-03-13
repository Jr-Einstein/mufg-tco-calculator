import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. PAGE CONFIGURATION & CSS ---
st.set_page_config(page_title="Customize Entities", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    .stApp { background-color: #F8F9FA; font-family: sans-serif; }
    
    .input-card { background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; border: 1px solid #E5E7EB;}
    
    /* Pill Badges */
    .pill-green { background-color: #10B981; color: white; padding: 5px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; display: inline-block; margin: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); letter-spacing: 0.5px;}
    .pill-gray { background-color: #94A3B8; color: white; padding: 5px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; display: inline-block; margin: 4px; opacity: 0.85; text-decoration: line-through;}
    .pill-indigo { background-color: #6366F1; color: white; padding: 5px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; display: inline-block; margin: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); letter-spacing: 0.5px;}
    .pill-red { background-color: #EF4444; color: white; padding: 5px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; display: inline-block; margin: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);}
    
    /* Summary Box */
    .summary-box { background-color: white; border-radius: 10px; padding: 25px; margin-bottom: 25px; border-left: 8px solid #D32F2F; box-shadow: 0 4px 10px rgba(0,0,0,0.08); border-top: 1px solid #E5E7EB; border-right: 1px solid #E5E7EB; border-bottom: 1px solid #E5E7EB;}
    .summary-header { background-color: #D32F2F; color: white; display: inline-block; padding: 6px 20px; border-radius: 6px; font-weight: bold; margin-bottom: 20px; font-size: 18px; letter-spacing: 1px;}
    .sub-title { font-weight: 800; color: #333; margin-top: 15px; margin-bottom: 8px; font-size: 16px; border-bottom: 2px solid #F1F5F9; padding-bottom: 6px;}
    .cat-label { font-weight: 700; color: #475569; width: 220px; display: inline-block; margin-top: 8px; font-size: 14px;}
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER ---
col_logo, col_title, col_time = st.columns([1, 3, 1])
with col_logo:
    if os.path.exists("logo.png"): st.image("logo.png", width=240)
    else: st.markdown("<h3 style='color:#D32F2F; font-weight:900;'>MUFG</h3>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h2 style='text-align: center; color: #1E293B; font-weight: 800; margin: 0;'>Entity Customization Engine</h2>", unsafe_allow_html=True)
with col_time:
    st.markdown(f"<div style='text-align: right; color: #64748B; font-weight: 600; font-size: 13px; margin-top: 15px;'>{datetime.now().strftime('%b %d, %Y | %H:%M')}</div>", unsafe_allow_html=True)
st.markdown("<hr style='margin-bottom: 20px; border: 0; height: 1px; background: #E2E8F0;'>", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
GSIs = ['AAD', 'AC2', 'ARK', 'CTF', 'IGA', 'Q03', 'R22', 'UDA', 'SNOW', 'Entra']
LICENSES = ['ACAT', 'StealthBit', 'IGA', 'CyberArk', 'Centrify', 'ServiceNow']

if 'entities' not in st.session_state: st.session_state.entities = ['MUBK', 'MUSA', 'BRAZIL', 'MEXICO', 'INTREPID', 'BRAZIL (SOW1)']
if 'current_customize_entity' not in st.session_state: st.session_state.current_customize_entity = 'MUBK'

TCO_CATEGORIES = ['Asset Cost (HY)', 'Resource Cost - FTE', 'Managed Services - TCS PS']

if 'customizations' not in st.session_state:
    st.session_state.customizations = {}
    for ent in st.session_state.entities:
        st.session_state.customizations[ent] = {
            'tco': {cat: {gsi: True for gsi in GSIs} for cat in TCO_CATEGORIES},
            'license': {lic: True for lic in LICENSES},
            'use_uplift': False,
            'uplift_val': 40.0
        }

# --- 4. TOP CONTROL BAR ---
st.markdown('<div class="input-card" style="padding: 15px 25px;">', unsafe_allow_html=True)
ctrl1, ctrl2, ctrl3 = st.columns([1, 2, 1])
with ctrl2:
    selected_entity = st.selectbox("Select Target Entity:", st.session_state.entities, index=st.session_state.entities.index(st.session_state.current_customize_entity))
    st.session_state.current_customize_entity = selected_entity
with ctrl3:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button(f"💾 Save {selected_entity} Config", type="primary", use_container_width=True):
        st.success(f"Customization profile for {selected_entity} saved!")
st.markdown('</div>', unsafe_allow_html=True)

tab_tco, tab_lic, tab_summary = st.tabs(["📊 TCO Component Filter", "🔑 License Filter", "📋 Entity Profiles"])

# ==========================================
# TAB 1: TCO DATA CUSTOMIZATION
# ==========================================
with tab_tco:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    
    # --- NEW: ASSET UPLIFT SECTION ---
    st.markdown("<h4 style='color: #D32F2F;'>Formula Customization</h4>", unsafe_allow_html=True)
    up_col1, up_col2 = st.columns([1, 2])
    with up_col1:
        st.session_state.customizations[selected_entity]['use_uplift'] = st.checkbox(
            "Apply Custom Asset Uplift %", 
            value=st.session_state.customizations[selected_entity]['use_uplift'],
            key=f"chk_up_{selected_entity}"
        )
    with up_col2:
        if st.session_state.customizations[selected_entity]['use_uplift']:
            st.session_state.customizations[selected_entity]['uplift_val'] = st.number_input(
                "Enter Uplift % (of FTE Cost):", 
                value=float(st.session_state.customizations[selected_entity]['uplift_val']),
                step=1.0, key=f"num_up_{selected_entity}"
            )
            st.caption(f"💡 Formula: Asset_Value + ({st.session_state.customizations[selected_entity]['uplift_val']/100:.2f} * FTE_Cost)")
    
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Standard GSI Filters
    st.markdown(f"<h3 style='color: #1E293B; margin-top: 0;'>Include/Exclude TCO Components</h3>", unsafe_allow_html=True)
    for cat in TCO_CATEGORIES:
        st.markdown(f"<h4 style='color: #334155; font-size: 15px; margin-bottom: 10px;'>{cat}</h4>", unsafe_allow_html=True)
        cols = st.columns(10)
        for i, gsi in enumerate(GSIs):
            with cols[i]:
                st.session_state.customizations[selected_entity]['tco'][cat][gsi] = st.checkbox(
                    gsi, value=st.session_state.customizations[selected_entity]['tco'][cat][gsi], 
                    key=f"tco_{selected_entity}_{cat}_{gsi}"
                )
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: LICENSE CUSTOMIZATION
# ==========================================
with tab_lic:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #1E293B;'>Include/Exclude Licenses</h3>", unsafe_allow_html=True)
    cols = st.columns(6)
    for i, lic in enumerate(LICENSES):
        with cols[i]:
            st.session_state.customizations[selected_entity]['license'][lic] = st.checkbox(
                lic, value=st.session_state.customizations[selected_entity]['license'][lic], 
                key=f"lic_{selected_entity}_{lic}"
            )
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 3: CUSTOMIZED ENTITIES SUMMARY
# ==========================================
with tab_summary:
    st.markdown("<h3 style='color: #1E293B; margin-bottom: 25px;'>Global Customization Profiles</h3>", unsafe_allow_html=True)
    
    for ent in st.session_state.entities:
        ent_data = st.session_state.customizations[ent]
        considered_html = ""
        excluded_html = ""
        
        # Add Uplift Status to Summary
        if ent_data['use_uplift']:
            considered_html += f'<div><span class="cat-label">Asset Formula:</span><span class="pill-red">Uplift Active ({ent_data["uplift_val"]}%)</span></div>'

        for cat in TCO_CATEGORIES:
            inc_pills, exc_pills = "", ""
            for gsi in GSIs:
                if ent_data['tco'][cat].get(gsi, True): inc_pills += f'<span class="pill-green">{gsi}</span>'
                else: exc_pills += f'<span class="pill-gray">{gsi}</span>'
            if inc_pills: considered_html += f'<div><span class="cat-label">{cat}:</span>{inc_pills}</div>'
            if exc_pills: excluded_html += f'<div><span class="cat-label">{cat}:</span>{exc_pills}</div>'
            
        inc_lic, exc_lic = "", ""
        for lic in LICENSES:
            if ent_data['license'].get(lic, True): inc_lic += f'<span class="pill-indigo">{lic}</span>'
            else: exc_lic += f'<span class="pill-gray">{lic}</span>'
        if inc_lic: considered_html += f'<div style="margin-top: 12px; border-top: 1px dashed #eee; padding-top: 8px;"><span class="cat-label">Licenses Chosen:</span>{inc_lic}</div>'

        final_card_html = f"""
<div class="summary-box">
<div class="summary-header">{ent}</div>
<div class="sub-title" style="color: #059669;">✔️ [Considered Values]</div>
<div style="padding-left: 5px;">{considered_html if considered_html else "<i>No components selected.</i>"}</div>
<div style="margin-top: 20px;"></div>
<div class="sub-title" style="color: #64748B;">❌ [Excluded Values]</div>
<div style="padding-left: 5px;">{excluded_html if excluded_html else "<i>No components excluded.</i>"}</div>
</div>
"""
        st.markdown(final_card_html, unsafe_allow_html=True)