import streamlit as st
from datetime import datetime
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="IAM Operation Cost", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SESSION STATE INITIALIZATION ---
if 'iam_op_costs' not in st.session_state:
    st.session_state.iam_op_costs = {
        'IAM Per Head Cost': 87578.82, # This is the "Total Cost Per Head"
        'Per GSI': 0.010000,
        'Per Linux Server': 0.002300,
        'Per Windows Server': 0.002300,
        'AD Support': 0.001327,
        'Cert & Audit (%)': 12.00
    }
if 'iam_op_last_updated' not in st.session_state:
    st.session_state.iam_op_last_updated = "Not updated yet"

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
    st.markdown("<h2 style='text-align: center; color: #333; font-weight: 800; margin: 0;'>IAM Operational Cost Administration</h2>", unsafe_allow_html=True)
with col_time:
    st.markdown(f"<div style='text-align: right; color: #666; font-weight: 600; font-size: 13px; margin-top: 15px;'>{datetime.now().strftime('%b %d, %Y | %H:%M')}</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 5px; margin-bottom: 25px; border: 0; height: 2px; background: #CCC;'>", unsafe_allow_html=True)

# --- 5. MAIN DASHBOARD LAYOUT ---
left_col, right_col = st.columns([1.3, 1], gap="large")

with left_col:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Global Operational Rates</div>', unsafe_allow_html=True)
    
    with st.expander("⚡ Bulk Paste Operation Costs", expanded=False):
        st.caption(f"Paste exactly {len(st.session_state.iam_op_costs)} numbers in order.")
        pasted_data = st.text_area("Paste values here:", height=100, label_visibility="collapsed")
        if st.button("Auto-Fill Fields", key="autofill_op"):
            try:
                lines = [line.strip().replace(',', '').replace('$', '').replace('%', '') for line in pasted_data.split('\n') if line.strip()]
                if len(lines) == len(st.session_state.iam_op_costs):
                    keys = list(st.session_state.iam_op_costs.keys())
                    for i in range(len(keys)):
                        st.session_state.iam_op_costs[keys[i]] = float(lines[i])
                    st.session_state.iam_op_last_updated = datetime.now().strftime('%b %d, %Y at %H:%M:%S')
                    st.rerun()
                else:
                    st.error(f"Format error. Expected {len(st.session_state.iam_op_costs)} values, got {len(lines)}.")
            except ValueError:
                st.error("Format error. Ensure numbers only.")
    
    st.write("")

    temp_costs = {}
    keys = list(st.session_state.iam_op_costs.keys())
    delete_key = None
    
    for i in range(0, len(keys), 2):
        cols = st.columns([5, 1, 5, 1], gap="small")
        
        def render_input(col_idx, key_name):
            is_pct = '%' in key_name
            is_master = 'Master' in key_name
            step_val = 1000.0 if is_master else (0.1 if is_pct else 0.0001)
            fmt = "%.2f" if (is_pct or is_master) else "%.6f"
            
            with cols[col_idx]:
                temp_costs[key_name] = st.number_input(key_name, value=float(st.session_state.iam_op_costs[key_name]), step=step_val, format=fmt)
            with cols[col_idx + 1]:
                st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{key_name}"):
                    return key_name
            return None

        del_1 = render_input(0, keys[i])
        if del_1: delete_key = del_1
                
        if i + 1 < len(keys):
            del_2 = render_input(2, keys[i + 1])
            if del_2: delete_key = del_2

    if delete_key:
        del st.session_state.iam_op_costs[delete_key]
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Update IAM Cost", type="primary", use_container_width=True):
        st.session_state.iam_op_costs = temp_costs
        st.session_state.iam_op_last_updated = datetime.now().strftime('%b %d, %Y at %H:%M:%S')
        st.success("Operational Costs Updated.")
        st.rerun() 
        
    st.markdown('</div>', unsafe_allow_html=True)

    # --- ADD NEW OPERATIONAL COST FEATURE ---
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">➕ Add Custom Operational Cost</div>', unsafe_allow_html=True)
    
    c_reason, c_val, c_type, c_btn = st.columns([3, 1.5, 1.5, 1.5])
    with c_reason:
        new_op_reason = st.text_input("Cost Reason/Name", placeholder="e.g., VPN Support")
    with c_val:
        new_op_val = st.number_input("Rate Value", value=0.00, step=0.01, format="%.4f")
    with c_type:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        is_percentage = st.checkbox("Is this a %?")
    with c_btn:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        if st.button("Add Cost", use_container_width=True):
            if new_op_reason:
                final_name = f"{new_op_reason} (%)" if is_percentage else new_op_reason
                if final_name not in st.session_state.iam_op_costs:
                    st.session_state.iam_op_costs[final_name] = new_op_val
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    rows_html = ""
    for name, cost in st.session_state.iam_op_costs.items():
        if '%' in name:
            display_val = f"{cost:,.2f}%"
        elif 'Master' in name:
            display_val = f"${cost:,.2f}" # Standard currency for Master Cost
        else:
            display_val = f"${cost:,.6f}"
            
        rows_html += f'<div class="list-row"><span class="list-label">{name}:</span><span class="list-val">{display_val}</span></div>'
        
    st.markdown(f'''
    <div class="result-box">
        <div class="red-header">Final Data Uploaded</div>
        <div class="list-content" style="margin-top: 10px;">
            {rows_html}
        </div>
        <div class="status-banner">Last Updated At: {st.session_state.iam_op_last_updated}</div>
    </div>
    ''', unsafe_allow_html=True)