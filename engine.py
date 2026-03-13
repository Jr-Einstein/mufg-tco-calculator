import streamlit as st
import pandas as pd

def calculate_entity_metrics(ent):
    """Calculates metrics for a SINGLE entity."""
    GSIs = ['AAD', 'AC2', 'ARK', 'CTF', 'IGA', 'Q03', 'R22', 'UDA', 'SNOW', 'Entra']

    # 0. ENGINE SELF-START
    if 'tco_df_dict' not in st.session_state:
        st.session_state.tco_df_dict = {}
        for entity in st.session_state.get('entities', ['MUBK', 'MUSA', 'BRAZIL']):
            init_data = {'Category': ['Asset Cost (HY)', 'Resource Cost - FTE', 'Managed Services - TCS PS']}
            asset_costs = [287540.0, 432711.0, 815031.0, 68187.2, 40928.5, 335563.0, 156179.0, 308172.0, 0.0, 0.0]
            for i, gsi in enumerate(GSIs):
                init_data[gsi] = [asset_costs[i], 858990.0, 230000.0]
            st.session_state.tco_df_dict[entity] = pd.DataFrame(init_data)

    # 1. RETRIEVE DATA
    vols = st.session_state.get('entity_data', {}).get(ent, {})
    users = vols.get('users', 0)
    priv_users = vols.get('priv_users', 0)
    std_users = max(users - priv_users, 0)
    apps = vols.get('apps', 0)
    win_servers = vols.get('servers_win', 0)
    linux_servers = vols.get('servers_linux', 0)
    other_servers = vols.get('servers_other', 0)

    iam_rates = st.session_state.get('iam_op_costs', {})
    cph = iam_rates.get('IAM Per Head Cost', 87578.82)
    fte_cost = iam_rates.get('Master Cost Per Body', 226050.0)
    r_gsi = iam_rates.get('Per GSI', 0.01)
    r_linux = iam_rates.get('Per Linux Server', 0.0023)
    r_win = iam_rates.get('Per Windows Server', 0.0023)
    r_ad = iam_rates.get('AD Support', 0.001327)
    cert_audit_pct = iam_rates.get('Cert & Audit (%)', 12.0)

    lic_costs = st.session_state.get('license_costs', {})
    def get_lic_val(name):
        val = lic_costs.get(name, lic_costs.get(f'LC ({name})', lic_costs.get(f'LC_{name}', 0.0)))
        return float(val) if val else 0.0

    cust = st.session_state.get('customizations', {}).get(ent, {})
    use_uplift = cust.get('use_uplift', False)
    uplift_val = cust.get('uplift_val', 0.0)
    tco_filters = cust.get('tco', {})
    lic_filters = cust.get('license', {})

    df = st.session_state.tco_df_dict.get(ent, pd.DataFrame())

    # 2. IAM OP COST
    cost_gsi = apps * r_gsi * cph
    cost_unix = (linux_servers + other_servers) * r_linux * cph
    cost_win = win_servers * r_win * cph
    cost_ad = users * r_ad * cph
    subtotal_iam = cost_gsi + cost_unix + cost_win + cost_ad
    total_iam_ops = subtotal_iam * (1 + (cert_audit_pct / 100))

    # 3. FILTERED TCO
    total_tco = 0.0
    if not df.empty:
        for idx, row in df.iterrows():
            cat = row['Category']
            cat_filters = tco_filters.get(cat, {}) if tco_filters else {}
            for gsi in GSIs:
                if cat_filters.get(gsi, True):
                    cell_val = float(row[gsi])
                    if cat == 'Asset Cost (HY)' and use_uplift:
                        cell_val += (uplift_val / 100.0) * fte_cost
                    total_tco += cell_val

    # 4. UNIT COSTS
    by_app = (total_tco / apps) if apps > 0 else 0.0
    
    c_centrify = get_lic_val('Centrify') if lic_filters.get('Centrify', True) else 0.0
    c_acat = get_lic_val('ACAT') if lic_filters.get('ACAT', True) else 0.0
    c_stealth = get_lic_val('StealthBit') if lic_filters.get('StealthBit', True) else 0.0
    c_iga = get_lic_val('IGA') if lic_filters.get('IGA', True) else 0.0
    c_snow = get_lic_val('ServiceNow') if lic_filters.get('ServiceNow', True) else 0.0
    c_cyberark = get_lic_val('CyberArk') if lic_filters.get('CyberArk', True) else 0.0

    by_app_lic = by_app + c_centrify
    by_std_user = (total_iam_ops / users) if users > 0 else 0.0
    std_lic_sum = c_acat + c_stealth + c_iga + c_snow
    by_std_user_lic = by_std_user + std_lic_sum
    by_priv_user_lic = by_std_user_lic + c_cyberark

    # 5. MULTIPLIED TOTALS
    total_cost_by_app_lic = by_app_lic * apps
    total_cost_std_user_lic = by_std_user_lic * std_users
    total_cost_priv_user_lic = by_priv_user_lic * priv_users
    grand_total = total_cost_by_app_lic + total_cost_std_user_lic + total_cost_priv_user_lic

    return {
        "iam_ops_total": total_iam_ops, "filtered_tco_total": total_tco,
        "unit_by_app": by_app, "unit_by_app_lic": by_app_lic,
        "unit_by_std": by_std_user, "unit_by_std_lic": by_std_user_lic, "unit_by_priv_lic": by_priv_user_lic,
        "tot_by_app_lic": total_cost_by_app_lic, "tot_std_lic": total_cost_std_user_lic, 
        "tot_priv_lic": total_cost_priv_user_lic, "grand_total": grand_total,
        
        # Raw Data needed for Global Aggregation
        "raw_apps": apps, "raw_users": users, "raw_priv_users": priv_users, "raw_std_users": std_users,
        "raw_c_centrify": c_centrify, "raw_std_lic_sum": std_lic_sum
    }

def calculate_global_metrics(all_results, entity_list):
    """Calculates the combined weighted average for the 'All Entities' view."""
    
    # CRASH-PROOF FIX: Only loop through valid dictionaries belonging to our entities
    valid_res = []
    mubk_tco = 0.0
    for ent in entity_list:
        if ent in all_results and isinstance(all_results[ent], dict):
            valid_res.append(all_results[ent])
            if ent == 'MUBK':
                mubk_tco = all_results[ent].get('filtered_tco_total', 0.0)
            
    if not valid_res:
        return {} # Failsafe if empty

    sum_apps = sum(res.get('raw_apps', 0) for res in valid_res)
    sum_iam = sum(res.get('iam_ops_total', 0.0) for res in valid_res)
    sum_users = sum(res.get('raw_users', 0) for res in valid_res)
    sum_priv = sum(res.get('raw_priv_users', 0) for res in valid_res)

    # Weighted Licenses (Excel Logic)
    sum_with_lic_all = sum(res.get('grand_total', 0.0) for res in valid_res)
    
    # 1. Global By App (MODIFIED: MUBK TCO / Global Apps)
    global_by_app = (mubk_tco / sum_apps) if sum_apps > 0 else 0.0
    
    # 2. Global By App + License (MODIFIED)
    sum_centrify_weighted = sum(res.get('raw_c_centrify', 0.0) * res.get('raw_apps', 0) for res in valid_res)
    global_by_app_lic = global_by_app + ((sum_centrify_weighted / sum_apps) if sum_apps > 0 else 0.0)

    # 3. Global Standard User
    global_by_std = (sum_iam / sum_users) if sum_users > 0 else 0.0
    
    # 4. Global Standard User + License
    sum_std_lic_weighted = sum(res.get('raw_std_lic_sum', 0.0) * res.get('raw_users', 0) for res in valid_res)
    global_by_std_lic = global_by_std + ((sum_std_lic_weighted / sum_users) if sum_users > 0 else 0.0)

    # 5. Global Privileged User + License
    sum_priv_weighted_cost = sum(res.get('unit_by_priv_lic', 0.0) * res.get('raw_priv_users', 0) for res in valid_res)
    global_by_priv_lic = (sum_priv_weighted_cost / sum_priv) if sum_priv > 0 else 0.0

    return {
        "iam_ops_total": sum_iam,
        "unit_by_app": global_by_app,
        "unit_by_app_lic": global_by_app_lic,
        "unit_by_std": global_by_std,
        "unit_by_std_lic": global_by_std_lic,
        "unit_by_priv_lic": global_by_priv_lic,
        
        "tot_by_app_lic": sum(res.get('tot_by_app_lic', 0.0) for res in valid_res),
        "tot_std_lic": sum(res.get('tot_std_lic', 0.0) for res in valid_res),
        "tot_priv_lic": sum(res.get('tot_priv_lic', 0.0) for res in valid_res),
        "grand_total": sum_with_lic_all
    }

def update_all_results():
    """Loops through all entities, saves their results, and creates a 'Global' profile."""
    if 'calculated_results' not in st.session_state or not isinstance(st.session_state.calculated_results, dict):
        st.session_state.calculated_results = {}
        
    entities = st.session_state.get('entities', [])
    for ent in entities:
        st.session_state.calculated_results[ent] = calculate_entity_metrics(ent)
        
    # Generate the combined "All Entities" view Safely
    st.session_state.calculated_results['ALL_ENTITIES_COMBINED'] = calculate_global_metrics(st.session_state.calculated_results, entities)