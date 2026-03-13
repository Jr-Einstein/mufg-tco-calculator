import streamlit as st
from datetime import datetime
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="License Cost", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SESSION STATE INITIALIZATION ---
if 'license_costs' not in st.session_state:
    st.session_state.license_costs = {
        'LC (ACAT)': 0.0,
        'LC (StealthBit)': 22.50,
        'LC (IGA)': 43.50,
        'LC (CyberArk)': 510.00,
        'LC (Centrify)': 54.00,
        'ServiceNow': 192.00
    }
if 'lc_last_updated' not in st.session_state:
    st.session_state.lc_last_updated = "Not updated yet"

# --- 3. UNIFORM CSS ---
st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    .stApp { background-color: #F0F2F6; font-family: sans-serif; }
    
    .input-card { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;}
    .section-title { color: #333; font-size: 1.2rem; font-weight: bold; border-bottom: 2px solid #EEE; padding-bottom: 10px; margin-bottom: 15px; }
    
    .result-box { background-color: white; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.15); border: 1px solid #CCC; }
    .red-header { background-color: #D32F2F; color: white; text-align: center; padding: 10px; font-weight: bold; font-size: 16px; }
    .status-banner { background-color: #FEE2E2; color: #D32F2F; text-align: center; padding: 8px; font-weight: bold; font-size: 13px; border-top: 1px solid #FCA5A5; }
    
    .list-content { padding: 5px 20px 20px 20px; }
    .list-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #EEE; font-size: 14px; color: #333;}
    .list-row:last-child { border-bottom: none; }
    .list-label { font-weight: 600; color: #555; }
    .list-val { font-weight: bold; background-color: #F8F9FA; padding: 2px 10px; border-radius: 4px; border: 1px solid #E5E7EB; }
    
    /* Tighten Input Fields */
    .stNumberInput > div { margin-bottom: -10px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. BRANDING & HEADER ---
col_logo, col_title, col_time = st.columns([1, 3, 1])
with col_logo:
    st.markdown("<div style='margin-top: 5px;'>", unsafe_allow_html=True)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=240)
    else:
        st.markdown("<h3 style='color:#D32F2F; font-weight:900;'>MUFG</h3>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
with col_title:
    st.markdown("<h2 style='text-align: center; color: #333; font-weight: 800; margin: 0;'>License Cost Administration</h2>", unsafe_allow_html=True)
with col_time:
    st.markdown(f"<div style='text-align: right; color: #666; font-weight: 600; font-size: 13px; margin-top: 15px;'>{datetime.now().strftime('%b %d, %Y | %H:%M')}</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 5px; margin-bottom: 25px; border: 0; height: 2px; background: #CCC;'>", unsafe_allow_html=True)

# --- 5. MAIN DASHBOARD LAYOUT ---
left_col, right_col = st.columns([1.3, 1], gap="large")

with left_col:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Global License Base Costs</div>', unsafe_allow_html=True)
    
    # Quick Paste Feature
    with st.expander("⚡ Bulk Paste License Costs", expanded=False):
        st.caption(f"Paste exactly {len(st.session_state.license_costs)} numbers in a column matching the order below.")
        pasted_data = st.text_area("Paste values here:", height=100, label_visibility="collapsed")
        if st.button("Auto-Fill Fields", key="autofill_lc"):
            try:
                lines = [line.strip().replace(',', '').replace('$', '') for line in pasted_data.split('\n') if line.strip()]
                if len(lines) == len(st.session_state.license_costs):
                    keys = list(st.session_state.license_costs.keys())
                    for i in range(len(keys)):
                        st.session_state.license_costs[keys[i]] = float(lines[i])
                    st.session_state.lc_last_updated = datetime.now().strftime('%b %d, %Y at %H:%M:%S')
                    st.rerun()
                else:
                    st.error(f"Format error. Expected {len(st.session_state.license_costs)} values, got {len(lines)}.")
            except ValueError:
                st.error("Format error. Ensure numbers only.")
    
    st.write("")

    temp_costs = {}
    keys = list(st.session_state.license_costs.keys())
    delete_key = None
    
    # Process licenses in pairs to avoid deep nesting
    for i in range(0, len(keys), 2):
        # Create a single row with 4 columns: [Input 1, Trash 1, Input 2, Trash 2]
        cols = st.columns([5, 1, 5, 1], gap="small")
        
        # --- First Item in the Pair ---
        key1 = keys[i]
        with cols[0]:
            temp_costs[key1] = st.number_input(key1, value=float(st.session_state.license_costs[key1]), step=1.00, format="%.2f")
        with cols[1]:
            st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{key1}", help=f"Delete {key1}"):
                delete_key = key1
                
        # --- Second Item in the Pair (If it exists) ---
        if i + 1 < len(keys):
            key2 = keys[i + 1]
            with cols[2]:
                temp_costs[key2] = st.number_input(key2, value=float(st.session_state.license_costs[key2]), step=1.00, format="%.2f")
            with cols[3]:
                st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{key2}", help=f"Delete {key2}"):
                    delete_key = key2

    # Execute deletion if a trash can was clicked
    if delete_key:
        del st.session_state.license_costs[delete_key]
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Update Button
    if st.button("Update LC Cost", type="primary", use_container_width=True):
        st.session_state.license_costs = temp_costs
        st.session_state.lc_last_updated = datetime.now().strftime('%b %d, %Y at %H:%M:%S')
        st.success("License Costs Updated Successfully.")
        st.rerun() 
        
    st.markdown('</div>', unsafe_allow_html=True)

    # Add Custom License Feature
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">➕ Add Custom License</div>', unsafe_allow_html=True)
    c_name, c_price, c_btn = st.columns([2, 1, 1])
    with c_name:
        new_lc_name = st.text_input("License Name (e.g., Okta)", placeholder="Enter Name")
    with c_price:
        new_lc_price = st.number_input("Base Price ($)", min_value=0.0, step=1.0)
    with c_btn:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        if st.button("Add License", use_container_width=True):
            if new_lc_name and new_lc_name not in st.session_state.license_costs:
                st.session_state.license_costs[new_lc_name] = new_lc_price
                st.rerun()
            elif new_lc_name in st.session_state.license_costs:
                st.warning("License already exists.")
            else:
                st.warning("Provide a valid name.")
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    # Single-line HTML generation prevents Streamlit from treating it like Markdown code blocks
    rows_html = ""
    for name, cost in st.session_state.license_costs.items():
        rows_html += f'<div class="list-row"><span class="list-label">{name} Value:</span><span class="list-val">${cost:,.2f}</span></div>'
        
    st.markdown(f'''
    <div class="result-box">
        <div class="red-header">Final Data Uploaded</div>
        <div class="list-content" style="margin-top: 10px;">
            {rows_html}
        </div>
        <div class="status-banner">Data Last Updated At: {st.session_state.lc_last_updated}</div>
    </div>
    ''', unsafe_allow_html=True)