import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="MUFG Journey - Tutorial", layout="wide", initial_sidebar_state="collapsed")

# --- 2. THEME & DIMMED BACKGROUND CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;800&display=swap');
    
    /* Dimmed Background Logic */
    .stApp {{
        background: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), 
                    url('background.logo');
        background-size: cover;
        background-attachment: fixed;
        font-family: 'Segoe UI', sans-serif;
        color: #333;
    }}

    .dialogue-box {{
        background: white;
        color: #1E293B;
        padding: 25px;
        border-radius: 12px;
        border-left: 8px solid #D32F2F;
        font-weight: 500;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
    }}

    .checkpoint-card {{
        background: rgba(255, 255, 255, 0.98);
        border: 1px solid #E2E8F0;
        padding: 35px;
        border-radius: 15px;
        margin-bottom: 50px;
        box-shadow: 15px 15px 35px rgba(0,0,0,0.08);
        transform: rotateX(5deg);
    }}

    .formula-display {{
        background: #F1F5F9;
        border: 1px dashed #64748B;
        padding: 15px;
        border-radius: 6px;
        color: #D32F2F;
        font-family: 'Consolas', monospace;
        font-weight: bold;
        margin: 15px 0;
        font-size: 15px;
    }}

    .aman-walker {{
        width: 100px;
        transition: all 0.8s ease-in-out;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE LOGIC ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'intro_done' not in st.session_state: st.session_state.intro_done = False
if 'active_tutorial_tab' not in st.session_state: st.session_state.active_tutorial_tab = 0

# --- 4. DATA RETRIEVAL ---
active_ent = st.session_state.get('current_entity', 'MUBK')
vols = st.session_state.get('entity_data', {}).get(active_ent, {})
res = st.session_state.get('calculated_results', {}).get(active_ent, {})

# --- 5. TABBED INTERFACE ---
tabs = st.tabs(["TCO Calculator Walkthrough", "Key Terminologies", "FAQ", " Contact Developer"])

# --- TAB 1: INTERACTIVE TOUR ---
with tabs[0]:
    if not st.session_state.intro_done:
        st.markdown("<div style='text-align:center; margin-top:50px;'>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/4086/4086679.png", width=150)
        
        intro_msgs = [
            "Hey I am Aman, I will be giving you MUFG IAM TCO Walkthrough.",
            "This application is a comprehensive financial engine designed to calculate the Total Cost of Ownership for Identity and Access Management. It aggregates infrastructure costs, operational labor, and software licensing into a granular 'cost-per-user' and 'cost-per-app' model.",
            "I will guide you through the calculation logic step-by-step. Let's begin."
        ]
        
        if 'msg_idx' not in st.session_state: st.session_state.msg_idx = 0
        st.markdown(f"<div class='dialogue-box'>{intro_msgs[st.session_state.msg_idx]}</div>", unsafe_allow_html=True)
        
        _, col_next = st.columns([4,1])
        with col_next:
            if st.session_state.msg_idx < len(intro_msgs) - 1:
                if st.button("Continue ➡️"):
                    st.session_state.msg_idx += 1
                    st.rerun()
            else:
                if st.button("Start Journey 🚀"):
                    st.session_state.intro_done = True
                    st.session_state.step = 1
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.progress(st.session_state.step / 7, text=f"Checkpoint {st.session_state.step} of 7")
        pos_offset = st.session_state.step * 10
        st.markdown(f'<div style="margin-left: {pos_offset}%;"><img src="https://cdn-icons-png.flaticon.com/512/4086/4086679.png" class="aman-walker"></div>', unsafe_allow_html=True)

        step = st.session_state.step

        if step == 1:
            st.markdown(f"<div class='checkpoint-card'><h3>Checkpoint 1: Volume Assessment</h3><p>We start with user-provided volumes for <b>{active_ent}</b>: <b>{vols.get('users', 0):,} users</b> and <b>{vols.get('apps', 0):,} apps</b>.</p></div>", unsafe_allow_html=True)
        elif step == 2:
            st.markdown(f"<div class='checkpoint-card'><h3>Checkpoint 2: TCO Matrix Summation</h3><p>Total Infrastructure Cost for {active_ent}: <b>${res.get('filtered_tco_total', 0):,.2f}</b>.</p><div class='formula-display'>Total TCO = Σ(Asset + Resource + Managed Services)</div></div>", unsafe_allow_html=True)
        elif step == 3:
            st.markdown(f"<div class='checkpoint-card'><h3>Checkpoint 3: The 1 FTE Master Cost</h3><p>Resource costs are driven by the <b>Master Cost Per Body</b>.</p><div class='formula-display'>GSI Resource Cost = (Total Employees * Master Cost) / 10</div></div>", unsafe_allow_html=True)
        elif step == 4:
            st.markdown(f"<div class='checkpoint-card'><h3>Checkpoint 4: IAM Operational Labor</h3><p>Operational costs based on server/user support: <b>${res.get('iam_ops_total', 0):,.2f}</b>.</p><div class='formula-display'>IAM Ops = (Support Rates) * 1.12 Buffer</div></div>", unsafe_allow_html=True)
        elif step == 5:
            st.markdown(f"<div class='checkpoint-card'><h3>Checkpoint 5: Unit Cost Derivation</h3><p>Converting totals into actionable units.</p><div class='formula-display'>By App = Total TCO / Apps</div><p>Result: <b>${res.get('unit_by_app', 0):,.2f} per Application</b></p></div>", unsafe_allow_html=True)
        elif step == 6:
            st.markdown(f"<div class='checkpoint-card'><h3>Checkpoint 6: License Layering</h3><p>We add <b>Centrify</b> to Apps and ACAT/IGA/SNOW to Users.</p><div class='formula-display'>App+Lic = Unit Cost + Centrify License Rate</div></div>", unsafe_allow_html=True)
        elif step == 7:
            st.markdown(f"<div class='checkpoint-card' style='border-left: 8px solid #059669;'><h3>Checkpoint 7: Final Portfolio Value</h3><h2 style='color: #D32F2F;'>Portfolio Grand Total: ${res.get('grand_total', 0):,.2f}</h2></div>", unsafe_allow_html=True)
            
            st.write("### Journey Complete! What's next?")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("Yes, Finish 🎉"): st.balloons()
            with c2:
                if st.button("No, Restart 🔄"):
                    st.session_state.step = 1
                    st.rerun()
            with c3:
                if st.button("Report Bug 🐞"):
                    st.session_state.active_tutorial_tab = 3 # Logic for redirect
                    st.info("Please navigate to the 'Contact Developer' tab below.")
            with c4:
                if st.button("Contact Me 📞"):
                    st.session_state.active_tutorial_tab = 3
                    st.info("Please navigate to the 'Contact Developer' tab below.")

        st.markdown("---")
        n1, n2, n3 = st.columns([1, 2, 1])
        with n1:
            if step > 1:
                if st.button("⬅️ Previous"):
                    st.session_state.step -= 1
                    st.rerun()
        with n3:
            if step < 7:
                if st.button("Next Step ➡️"):
                    st.session_state.step += 1
                    st.rerun()

# --- TAB 2: TERMINOLOGIES ---
with tabs[1]:
    st.markdown("""
    <div class='checkpoint-card'>
        <h3>📖 Key Terminologies</h3>
        <p><b>TCO:</b> Total Cost of Ownership (Asset + Resource + MS).</p>
        <p><b>GSI:</b> Global Strategic Instance (System instance like AAD or IGA).</p>
        <p><b>FTE:</b> Full-Time Equivalent (1 employee's cost burden).</p>
        <p><b>IAM Ops:</b> Operational labor cost to maintain IAM infrastructure.</p>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 3: FAQ ---
with tabs[2]:
    st.markdown("""
    <div class='checkpoint-card'>
        <h3>❓ FAQ</h3>
        <p><b>Q: How are licenses calculated?</b><br>Licenses are added on top of the base unit costs per user or per app.</p>
        <p><b>Q: Can I change the Master Cost?</b><br>Yes, in the IAM Operation Cost page.</p>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 4: CONTACT DEVELOPER ---
with tabs[3]:
    st.markdown(f"""
    <div class='checkpoint-card'>
        <h3>👨‍💻 Contact Developer / Report Bug</h3>
        <p>If you have encountered a bug or need specialized assistance with the <b>{active_ent}</b> calculation, please use the details below.</p>
        <hr>
        <p><b>Email:</b> AmanSingh@us.mufg.jp</p>
        <p><b>Team Contact:</b> IAM Production Support</p>
        <p><b>Developer:</b> Aman Kumar Singh</p>
    </div>
    """, unsafe_allow_html=True)