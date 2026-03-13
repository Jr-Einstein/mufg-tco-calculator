import streamlit as st
import json
import os
import pandas as pd

# Global database file
STORAGE_FILE = "data_storage.json"

def save_persistent_data(data=None):
    """
    Saves the entire workspace state including calculations and 
    custom TCO matrix data to the global JSON file.
    """
    # Capture the latest state from session_state
    state_to_save = {
        "user_name": st.session_state.get('user_name', 'Default User'),
        "entities": st.session_state.get('entities', []),
        "entity_data": st.session_state.get('entity_data', {}),
        "license_costs": st.session_state.get('license_costs', {}),
        "iam_op_costs": st.session_state.get('iam_op_costs', {}),
        "customizations": st.session_state.get('customizations', {}),
        # Save the actual math results so the summary page loads instantly
        "calculated_results": st.session_state.get('calculated_results', {}),
        # Convert TCO DataFrames to JSON strings for storage
        "tco_df_dict": {ent: df.to_json() for ent, df in st.session_state.get('tco_df_dict', {}).items()} if 'tco_df_dict' in st.session_state else {}
    }
    
    with open(STORAGE_FILE, "w") as f:
        json.dump(state_to_save, f, indent=4)

def load_persistent_data():
    """
    Loads all data from data_storage.json into the current session.
    """
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            try:
                data = json.load(f)
                st.session_state.user_name = data.get("user_name", "")
                st.session_state.entities = data.get("entities", ['MUBK', 'MUSA', 'BRAZIL', 'MEXICO', 'INTREPID', 'BRAZIL (SOW1)'])
                st.session_state.entity_data = data.get("entity_data", {})
                st.session_state.license_costs = data.get("license_costs", {})
                st.session_state.iam_op_costs = data.get("iam_op_costs", {})
                st.session_state.customizations = data.get("customizations", {})
                st.session_state.calculated_results = data.get("calculated_results", {})
                
                # Reconstruct DataFrames from saved JSON strings
                if "tco_df_dict" in data:
                    st.session_state.tco_df_dict = {
                        ent: pd.read_json(js) for ent, js in data["tco_df_dict"].items()
                    }
                return True
            except:
                return False
    return False

def check_login():
    """Forces the user to enter their name before seeing the app."""
    if 'user_name' not in st.session_state or not st.session_state.user_name:
        # Try to load existing session name from file first
        if load_persistent_data() and st.session_state.user_name:
            st.rerun()
            
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
                save_persistent_data() # Create file immediately on first login
                st.rerun()
            else:
                st.error("Name is required to proceed.")
        st.stop()

def init_session_state():
    """Initializes workspace by checking storage file first, then defaults."""
    
    # 1. Try to load EVERYTHING from the file FIRST (This handles the 'by default' requirement)
    file_exists = load_persistent_data()

    # 2. Defaults for Entities (Only if file loading didn't set them)
    if 'entities' not in st.session_state:
        st.session_state.entities = ['MUBK', 'MUSA', 'BRAZIL', 'MEXICO', 'INTREPID', 'BRAZIL (SOW1)']
    
    if 'current_entity' not in st.session_state:
        st.session_state.current_entity = 'MUBK'

    # 3. Defaults for Input Data (Only if file loading didn't set them)
    if 'entity_data' not in st.session_state:
        st.session_state.entity_data = {
            ent: {'users': 0, 'priv_users': 0, 'accounts': 0, 'apps': 0, 'servers_win': 0, 'servers_linux': 0, 'servers_other': 0}
            for ent in st.session_state.entities
        }

    # 4. Rate Defaults (Only if file loading didn't set them)
    if 'license_costs' not in st.session_state:
        st.session_state.license_costs = {'acat': 0.0, 'stealthbit': 22.5, 'iga': 43.5, 'cyberark': 510.0, 'centrify': 54.0, 'servicenow': 192.0}

    if 'iam_op_costs' not in st.session_state:
        st.session_state.iam_op_costs = {'per_gsi': 0.01, 'per_linux': 0.0023, 'per_windows': 0.0023, 'ad_support': 0.00132696, 'cert_audit_pct': 12.0}

    # 5. Calculation Results (Only if file loading didn't set them)
    if 'calculated_results' not in st.session_state:
        st.session_state.calculated_results = {}