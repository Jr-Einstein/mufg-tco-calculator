import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="TCO Data", layout="wide", initial_sidebar_state="collapsed")

# --- 2. UNIFORM CSS (Matched to your IAM_Operation_Cost UI) ---
st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    .stApp { background-color: #F0F2F6; font-family: sans-serif; }
    
    .input-card { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;}
    .section-title { color: #333; font-size: 1.2rem; font-weight: bold; border-bottom: 2px solid #EEE; padding-bottom: 10px; margin-bottom: 15px; }
    
    .result-box { background-color: white; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.15); border: 1px solid #CCC; margin-top: 20px;}
    .red-header { background-color: #D32F2F; color: white; text-align: center; padding: 10px; font-weight: bold; font-size: 16px; }
    .status-banner { background-color: #FEE2E2; color: #D32F2F; text-align: center; padding: 8px; font-weight: bold; font-size: 13px; border-top: 1px solid #FCA5A5; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. BRANDING & HEADER ---
col_logo, col_title, col_time = st.columns([1, 3, 1])
with col_logo:
    st.markdown("<div style='margin-top: 5px;'>", unsafe_allow_html=True)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=240)
    else:
        st.markdown("<h3 style='color:#D32F2F; font-weight:900;'>MUFG</h3>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
with col_title:
    st.markdown("<h2 style='text-align: center; color: #333; font-weight: 800; margin: 0;'>Total Cost of Ownership (TCO) Data</h2>", unsafe_allow_html=True)
with col_time:
    st.markdown(f"<div style='text-align: right; color: #666; font-weight: 600; font-size: 13px; margin-top: 15px;'>{datetime.now().strftime('%b %d, %Y | %H:%M')}</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 5px; margin-bottom: 25px; border: 0; height: 2px; background: #CCC;'>", unsafe_allow_html=True)

# --- 4. GSIs & SESSION STATE SETUP ---
GSIs = ['AAD', 'AC2', 'ARK', 'CTF', 'IGA', 'Q03', 'R22', 'UDA', 'SNOW', 'Entra']

# Initialize inputs
if 'tco_emp' not in st.session_state: st.session_state.tco_emp = 38
if 'tco_cost' not in st.session_state: st.session_state.tco_cost = 226050.0

# Initialize Manual Overrides Dictionary
if 'manual_overrides' not in st.session_state:
    st.session_state.manual_overrides = {} 

# Calculate the base split cost
base_split_cost = (st.session_state.tco_emp * st.session_state.tco_cost) / 10

# Initialize Dataframe
if 'tco_df' not in st.session_state:
    initial_data = {'Category': ['Asset Cost (HY)', 'Resource Cost - FTE', 'Managed Services - TCS PS']}
    # Pre-load Asset Costs
    asset_costs = [287540.0, 432711.0, 815031.0, 68187.2, 40928.5, 335563.0, 156179.0, 308172.0, 0.0, 0.0]
    for i, gsi in enumerate(GSIs):
        # FIX: Ensure Resource Cost - FTE starts with the calculated base_split_cost instead of 0.0
        initial_data[gsi] = [asset_costs[i], base_split_cost, 230000.0]
    st.session_state.tco_df = pd.DataFrame(initial_data)

if 'tco_uploaded_data' not in st.session_state:
    st.session_state.tco_uploaded_data = None
if 'tco_last_updated' not in st.session_state:
    st.session_state.tco_last_updated = "Not updated yet"

# --- 5. TOP CONTROLS (FTE INPUTS) ---
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Resource Parameters</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    new_emp = st.number_input("Total Employees:", value=st.session_state.tco_emp, step=1)
with col2:
    new_cost = st.number_input("Employee Cost (1 FTE):", value=st.session_state.tco_cost, step=1000.0)

# --- THE MATH LOGIC ---
if new_emp != st.session_state.tco_emp or new_cost != st.session_state.tco_cost:
    st.session_state.tco_emp = new_emp
    st.session_state.tco_cost = new_cost
    st.session_state.manual_overrides = {} 
    base_split_cost = (new_emp * new_cost) / 10
    # Apply change immediately to sync
    for gsi in GSIs:
        st.session_state.tco_df.at[1, gsi] = base_split_cost

st.markdown('</div>', unsafe_allow_html=True)

# --- 6. DATA GRID ---
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">TCO Matrix</div>', unsafe_allow_html=True)

# Re-apply split logic for GSIs NOT in manual overrides to keep the grid synced
for gsi in GSIs:
    if gsi not in st.session_state.manual_overrides:
        st.session_state.tco_df.at[1, gsi] = base_split_cost

display_df = st.session_state.tco_df.copy()
display_df['Grand Total'] = display_df[GSIs].sum(axis=1)

# MODIFIED: disabled=False for Category to allow custom text entry
column_config = {
    "Category": st.column_config.TextColumn("Category", disabled=False),
    "Grand Total": st.column_config.NumberColumn("Grand Total", format="$%d", disabled=True) 
}
for gsi in GSIs: column_config[gsi] = st.column_config.NumberColumn(gsi, format="$%d")

# Render Grid
edited_df = st.data_editor(
    display_df, 
    use_container_width=True, 
    hide_index=True, 
    column_config=column_config,
    key="tco_grid"
)

# SYNC LOGIC: Capture edits and update Grand Total calculation
for gsi in GSIs:
    grid_value = edited_df.at[1, gsi]
    if grid_value != base_split_cost:
        st.session_state.manual_overrides[gsi] = grid_value

# Immediately update session state with edited values to keep totals live
st.session_state.tco_df = edited_df.drop(columns=['Grand Total'])

# --- 7. BUTTONS ---
st.write("")
bc1, bc2, bc3, bc4 = st.columns([1.5, 1.5, 3, 2])

with bc1:
    if st.button("➕ Add Custom Expense", use_container_width=True):
        # MODIFIED: Placeholder text to prompt user to enter reason
        new_row = {'Category': f'Type reason here...'}
        for gsi in GSIs: new_row[gsi] = 0.0
        st.session_state.tco_df = pd.concat([st.session_state.tco_df, pd.DataFrame([new_row])], ignore_index=True)
        st.rerun()

with bc2:
    if st.button("➖ Remove Last", use_container_width=True):
        if len(st.session_state.tco_df) > 3:
            st.session_state.tco_df = st.session_state.tco_df[:-1]
            st.rerun()
        else:
            st.warning("Cannot delete core categories.")

with bc4:
    if st.button("✅ Lock & Upload TCO Data", use_container_width=True, type="primary"):
        # Explicitly copy the edited dataframe to sync the upload
        final_sync_df = edited_df.copy()
        st.session_state.tco_uploaded_data = final_sync_df
        st.session_state.tco_last_updated = datetime.now().strftime('%b %d, %Y at %H:%M:%S')
        st.success("TCO Data Successfully Uploaded!")
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)


# --- 8. BOTTOM DISPLAY (UPLOADED DATA) ---
if st.session_state.tco_uploaded_data is not None:
    st.markdown(f'''
    <div class="result-box">
        <div class="red-header">Final TCO Data Uploaded</div>
        <div style="padding: 20px;">
    ''', unsafe_allow_html=True)
    
    st.dataframe(st.session_state.tco_uploaded_data, hide_index=True, use_container_width=True)
    
    # MODIFIED: sum() now dynamically totals all rows including newly named custom ones
    final_grand_total = st.session_state.tco_uploaded_data['Grand Total'].sum()
    st.markdown(f"<h3 style='text-align:right; color:#D32F2F; margin-top:10px;'>Total Overall TCO Cost: ${final_grand_total:,.2f}</h3>", unsafe_allow_html=True)
    
    st.markdown(f'''
        </div>
        <div class="status-banner">Data Last Updated At: {st.session_state.tco_last_updated}</div>
    </div>
    ''', unsafe_allow_html=True)