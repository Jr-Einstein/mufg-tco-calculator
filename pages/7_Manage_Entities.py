import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io
from engine import update_all_results

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Manage Entities", layout="wide", initial_sidebar_state="collapsed")

# --- 2. UNIFORM CSS ---
st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    .stApp { background-color: #F8F9FA; font-family: sans-serif; }
    
    .input-card { background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; border: 1px solid #E5E7EB;}
    .section-title { color: #1E293B; font-size: 1.2rem; font-weight: bold; border-bottom: 2px solid #EEE; padding-bottom: 10px; margin-bottom: 20px; }
    
    .entity-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 10px; background-color: #F8FAFC;}
    .entity-name { font-weight: bold; color: #334155; font-size: 16px;}
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. BRANDING & HEADER ---
col_logo, col_title, col_time = st.columns([1, 3, 1])
with col_logo:
    if os.path.exists("logo.png"): st.image("logo.png", width=240)
    else: st.markdown("<h3 style='color:#D32F2F; font-weight:900;'>MUFG</h3>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h2 style='text-align: center; color: #1E293B; font-weight: 800; margin: 0;'>Entity Command Center</h2>", unsafe_allow_html=True)
with col_time:
    st.markdown(f"<div style='text-align: right; color: #64748B; font-weight: 600; font-size: 13px; margin-top: 15px;'>{datetime.now().strftime('%b %d, %Y')}</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin-bottom: 20px; border: 0; height: 1px; background: #E2E8F0;'>", unsafe_allow_html=True)

# --- NOTIFICATION SYSTEM ---
if 'flash_message' in st.session_state:
    if st.session_state.flash_message['type'] == 'success':
        st.success(st.session_state.flash_message['msg'])
    elif st.session_state.flash_message['type'] == 'error':
        st.error(st.session_state.flash_message['msg'])
    del st.session_state.flash_message

# --- 4. ENSURE CORE SESSION STATE EXISTS ---
if 'entities' not in st.session_state: st.session_state.entities = ['MUBK', 'MUSA', 'BRAZIL']
if 'entity_data' not in st.session_state: st.session_state.entity_data = {}
if 'new_ent_vols' not in st.session_state: st.session_state.new_ent_vols = [0, 0, 0, 0, 0, 0, 0]

GSIs = ['AAD', 'AC2', 'ARK', 'CTF', 'IGA', 'Q03', 'R22', 'UDA', 'SNOW', 'Entra']
LICENSES = ['ACAT', 'StealthBit', 'IGA', 'CyberArk', 'Centrify', 'ServiceNow']
TCO_CATEGORIES = ['Asset Cost (HY)', 'Resource Cost - FTE', 'Managed Services - TCS PS']

# 🧠 Master Function to Inject a New Entity
def initialize_new_entity(ent_name, vols, clone_from=None):
    if ent_name in st.session_state.entities or ent_name == "ALL_ENTITIES_COMBINED":
        return False 
        
    st.session_state.entities.append(ent_name)
    st.session_state.entity_data[ent_name] = vols
    
    if 'tco_df_dict' not in st.session_state: st.session_state.tco_df_dict = {}
    if 'customizations' not in st.session_state: st.session_state.customizations = {}
    
    if clone_from and clone_from in st.session_state.entities:
        st.session_state.tco_df_dict[ent_name] = st.session_state.tco_df_dict[clone_from].copy()
        st.session_state.customizations[ent_name] = {
            'tco': {cat: {gsi: st.session_state.customizations[clone_from]['tco'][cat][gsi] for gsi in GSIs} for cat in TCO_CATEGORIES},
            'license': {lic: st.session_state.customizations[clone_from]['license'][lic] for lic in LICENSES},
            'use_uplift': st.session_state.customizations[clone_from]['use_uplift'],
            'uplift_val': st.session_state.customizations[clone_from]['uplift_val']
        }
    else:
        init_data = {'Category': TCO_CATEGORIES}
        asset_costs = [287540.0, 432711.0, 815031.0, 68187.2, 40928.5, 335563.0, 156179.0, 308172.0, 0.0, 0.0]
        for i, gsi in enumerate(GSIs):
            init_data[gsi] = [asset_costs[i], 858990.0, 230000.0]
        st.session_state.tco_df_dict[ent_name] = pd.DataFrame(init_data)
        st.session_state.customizations[ent_name] = {
            'tco': {cat: {gsi: True for gsi in GSIs} for cat in TCO_CATEGORIES},
            'license': {lic: True for lic in LICENSES},
            'use_uplift': False, 'uplift_val': 40.0
        }
    
    if 'asset_uplift_pct' not in st.session_state or isinstance(st.session_state.asset_uplift_pct, dict):
        st.session_state.asset_uplift_pct = 40.0
    if 'manual_overrides_dict' not in st.session_state: st.session_state.manual_overrides_dict = {}
    st.session_state.manual_overrides_dict[ent_name] = {}
    
    return True

# --- 5. TABS ---
tab1, tab2 = st.tabs(["➕ Create / Clone Entity", "⚙️ Manage Portfolio"])

# ==========================================
# TAB 1: ADD NEW ENTITY
# ==========================================
with tab1:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    
    col_name, col_clone = st.columns(2)
    with col_clone:
        clone_options = ["None (Start Fresh)"] + st.session_state.entities
        target_clone = st.selectbox("🧬 Clone Settings from Existing Entity?", clone_options)
        
    with col_name:
        # Auto-fill name and warning if cloning
        default_name = f"{target_clone} (Clone)" if target_clone != "None (Start Fresh)" else ""
        new_ent_name = st.text_input("New Entity Code (e.g., EMEA, APAC , Global)", value=default_name, max_chars=30)
        
        if target_clone != "None (Start Fresh)":
            st.markdown("<p style='color:#D32F2F; font-size:13px; font-weight:bold; margin-top:-10px;'>⚠️ Please change the name for this clone.</p>", unsafe_allow_html=True)

    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Base Volumes</div>', unsafe_allow_html=True)
    
    with st.expander("⚡ Quick Paste Base Volumes (7 Values)", expanded=False):
        pasted = st.text_area("Paste 7 values column here:", height=100, label_visibility="collapsed")
        if st.button("Auto-Fill Fields"):
            try:
                lines = [line.strip().replace(',', '') for line in pasted.split('\n') if line.strip()]
                if len(lines) >= 7:
                    st.session_state.new_ent_vols = [int(float(l)) for l in lines[:7]]
                    st.session_state.flash_message = {'type': 'success', 'msg': 'Values Loaded! Review fields below.'}
                    st.rerun()
                else:
                    st.error("Format error. Expected 7 values.")
            except ValueError:
                st.error("Format error. Ensure numbers only.")
    
    st.write("")
    
    # 🧠 Determine which numbers to show in the input boxes
    if target_clone != "None (Start Fresh)":
        c_data = st.session_state.entity_data.get(target_clone, {})
        cv = [
            c_data.get('users', 0), c_data.get('priv_users', 0), c_data.get('accounts', 0),
            c_data.get('apps', 0), c_data.get('servers_win', 0), c_data.get('servers_linux', 0),
            c_data.get('servers_other', 0)
        ]
    else:
        cv = st.session_state.new_ent_vols
        
    c1, c2 = st.columns(2)
    with c1:
        n_users = st.number_input("Number of Users", value=cv[0], step=100)
        n_priv = st.number_input("Number of Privilege Users", value=cv[1], step=10)
        n_acc = st.number_input("Number of Accounts", value=cv[2], step=100)
        n_apps = st.number_input("Number of App / GSIs", value=cv[3], step=10)
    with c2:
        n_win = st.number_input("Windows Servers", value=cv[4], step=10)
        n_lin = st.number_input("Linux Servers", value=cv[5], step=10)
        n_oth = st.number_input("Other Servers", value=cv[6], step=10)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Create Entity Workspace", type="primary", use_container_width=True):
        new_ent_name = new_ent_name.strip().upper()
        
        if not new_ent_name:
            st.error("Entity name cannot be empty.")
        elif new_ent_name.endswith("(CLONE)"):
            st.error("Please provide a unique name for this clone before creating.")
        else:
            vols = {
                'users': n_users, 'priv_users': n_priv, 'accounts': n_acc,
                'apps': n_apps, 'servers_win': n_win, 'servers_linux': n_lin, 'servers_other': n_oth
            }
            clone_id = target_clone if target_clone != "None (Start Fresh)" else None
            
            if initialize_new_entity(new_ent_name, vols, clone_from=clone_id):
                update_all_results() 
                st.session_state.new_ent_vols = [0, 0, 0, 0, 0, 0, 0] 
                st.session_state.flash_message = {'type': 'success', 'msg': f"✅ New Entity '{new_ent_name}' successfully created!"}
                st.rerun()
            else:
                st.error(f"Entity '{new_ent_name}' already exists.")
            
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: MANAGE & EXPORT
# ==========================================
with tab2:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    
    col_head, col_btn = st.columns([3, 1])
    with col_head:
        st.markdown('<div class="section-title" style="border:none;">Active Portfolio</div>', unsafe_allow_html=True)
    with col_btn:
        df_export = pd.DataFrame.from_dict(st.session_state.entity_data, orient='index')
        df_export.index.name = 'Entity'
        csv = df_export.to_csv().encode('utf-8')
        st.download_button("📥 Export Portfolio (CSV)", data=csv, file_name="IAM_Entities_Export.csv", mime="text/csv", use_container_width=True)
        
    st.markdown("<hr style='margin-top: 0;'>", unsafe_allow_html=True)
    
    if len(st.session_state.entities) <= 1:
        st.warning("You must have at least one entity in the system. Deletion is disabled.")
        
    for ent in st.session_state.entities:
        c_name, c_action = st.columns([4, 1])
        with c_name:
            user_cnt = st.session_state.entity_data.get(ent, {}).get('users', 0)
            st.markdown(f'<div class="entity-row"><span class="entity-name">🏢 {ent}</span> <span style="color:#64748B; font-size:13px;">({user_cnt:,} Users)</span></div>', unsafe_allow_html=True)
        with c_action:
            st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
            if len(st.session_state.entities) > 1:
                if st.button("🗑️ Delete", key=f"del_{ent}", use_container_width=True):
                    st.session_state.entities.remove(ent)
                    st.session_state.entity_data.pop(ent, None)
                    st.session_state.calculated_results.pop(ent, None)
                    if 'tco_df_dict' in st.session_state: st.session_state.tco_df_dict.pop(ent, None)
                    if 'customizations' in st.session_state: st.session_state.customizations.pop(ent, None)
                    
                    if st.session_state.get('current_entity') == ent: st.session_state.current_entity = st.session_state.entities[0]
                    if st.session_state.get('current_tco_entity') == ent: st.session_state.current_tco_entity = st.session_state.entities[0]
                    if st.session_state.get('current_customize_entity') == ent: st.session_state.current_customize_entity = st.session_state.entities[0]
                        
                    update_all_results()
                    st.session_state.flash_message = {'type': 'success', 'msg': f"🗑️ Entity '{ent}' has been deleted."}
                    st.rerun()
            else:
                st.button("🔒 Locked", key=f"lock_{ent}", disabled=True, use_container_width=True)
                
    st.markdown('</div>', unsafe_allow_html=True)