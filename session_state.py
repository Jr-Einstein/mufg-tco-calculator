import streamlit as st
import json
import os

# This is our local "database" file to bypass the corporate network block
DB_FILE = "tco_sessions.json"

def check_login():
    """Forces the user to enter their name before seeing the app."""
    if 'user_name' not in st.session_state or not st.session_state.user_name:
        st.markdown("""
            <div style='text-align: center; background-color: #D32F2F; padding: 20px; border-radius: 10px; color: white;'>
                <h1>MUFG IAM TCO Calculator</h1>
                <p>Please enter your name to access the workspace.</p>
            </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("Full Name:", key="login_name_input")
        if st.button("Enter Workspace", type="primary", use_container_width=True):
            if name:
                st.session_state.user_name = name
                st.rerun()
            else:
                st.error("Name is required to proceed.")
        st.stop() # Halts the rest of the page from loading

def init_session_state():
    # Dynamic Entities List (Can be appended to later!)
    if 'entities' not in st.session_state:
        st.session_state.entities = ['MUBK', 'MUSA', 'BRAZIL', 'MEXICO', 'INTREPID', 'BRAZIL (SOW1)']
    
    if 'current_entity' not in st.session_state:
        st.session_state.current_entity = 'MUBK'

    # Entity Data mapping (dynamically updates if entities are added)
    if 'entity_data' not in st.session_state:
        st.session_state.entity_data = {
            entity: {'users': 0, 'priv_users': 0, 'accounts': 0, 'apps': 0, 'servers_win': 0, 'servers_linux': 0, 'servers_other': 0}
            for entity in st.session_state.entities
        }

    if 'license_costs' not in st.session_state:
        st.session_state.license_costs = {'acat': 0.0, 'stealthbit': 22.5, 'iga': 43.5, 'cyberark': 510.0, 'centrify': 54.0, 'servicenow': 192.0}

    if 'iam_op_costs' not in st.session_state:
        st.session_state.iam_op_costs = {'per_gsi': 0.01, 'per_linux': 0.0023, 'per_windows': 0.0023, 'ad_support': 0.00132696, 'cert_audit_pct': 12.0}

def save_session_to_db(session_id):
    """Saves current state to local JSON so others can view it via link"""
    data = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
            
    # Package the user's data
    data[session_id] = {
        "author": st.session_state.user_name,
        "entities": st.session_state.entities,
        "entity_data": st.session_state.entity_data,
        "license_costs": st.session_state.license_costs,
        "iam_op_costs": st.session_state.iam_op_costs
    }
    
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)