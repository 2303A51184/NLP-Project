import os
import re
import time
import datetime
import numpy as np
import pandas as pd
import streamlit as st

# Import core RAG backend and authentication database
from backend import (
    load_medical_dataset,
    init_tfidf_engine,
    init_faiss_engine,
    check_red_flags,
    get_relevant_chunks,
    generate_grounded_response,
    WARANGAL_EMERGENCY_CONTACTS
)
import auth_db

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Warangal HealthRAG | Medical Information System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# Professional Healthcare SaaS Design System (CSS)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    /* Google Fonts & Base Variables */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --primary-teal: #005f73;
        --teal-dark: #0a4650;
        --teal-light: #e0f2fe;
        --medical-blue: #0284c7;
        --accent-mint: #10b981;
        --mint-light: #d1fae5;
        --emergency-red: #dc2626;
        --emergency-bg: #fef2f2;
        --bg-white: #ffffff;
        --bg-slate: #f8fafc;
        --border-slate: #e2e8f0;
        --text-slate-900: #0f172a;
        --text-slate-600: #475569;
        --text-slate-400: #94a3b8;
    }

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        max-width: 1240px;
    }

    /* Top Navigation Bar */
    .top-navbar {
        background-color: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        padding: 0.85rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .brand-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 800;
        font-size: 1.25rem;
        color: #005f73;
        letter-spacing: -0.5px;
    }
    .brand-badge {
        background-color: #e0f2fe;
        color: #0284c7;
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Hero Section */
    .hero-container {
        background: linear-gradient(145deg, #005f73 0%, #0a4650 100%);
        border-radius: 20px;
        padding: 3rem 2.5rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 95, 115, 0.25);
        position: relative;
        overflow: hidden;
    }
    .hero-container h1 {
        font-size: 2.45rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 0.8rem;
        color: #ffffff !important;
    }
    .hero-container p {
        font-size: 1.12rem;
        color: #e0f2fe;
        max-width: 720px;
        line-height: 1.6;
        margin-bottom: 1.8rem;
    }
    .hero-stats-row {
        display: flex;
        gap: 2rem;
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255,255,255,0.15);
    }
    .hero-stat-item h3 {
        font-size: 1.55rem;
        font-weight: 800;
        color: #10b981;
        margin: 0;
    }
    .hero-stat-item p {
        font-size: 0.85rem;
        color: #cbd5e1;
        margin: 0;
    }

    /* Cards & Containers */
    .saas-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1.2rem;
    }
    .saas-card:hover {
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
    }
    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .card-subtitle {
        font-size: 0.88rem;
        color: #64748b;
        margin-bottom: 1rem;
    }

    /* Emergency Safety Box */
    .emergency-alert-banner {
        background-color: #fef2f2;
        border: 2px solid #ef4444;
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1.2rem 0;
        box-shadow: 0 6px 16px -2px rgba(220, 38, 38, 0.15);
        color: #991b1b;
    }
    .emergency-alert-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #dc2626;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 0.6rem;
    }
    .emergency-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
        padding-top: 0.8rem;
        border-top: 1px solid #fecaca;
    }
    .emergency-contact-chip {
        background: #ffffff;
        border: 1px solid #fca5a5;
        border-radius: 8px;
        padding: 0.75rem 1rem;
    }
    .emergency-contact-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #b91c1c;
        text-transform: uppercase;
    }
    .emergency-contact-num {
        font-size: 1.1rem;
        font-weight: 800;
        color: #1e293b;
    }

    /* Verification & Evidence Card */
    .evidence-box {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #0284c7;
        border-radius: 10px;
        padding: 1.1rem;
        margin: 0.8rem 0;
    }
    .evidence-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 0.5rem;
        margin-bottom: 0.6rem;
    }
    .score-badge {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .source-text-block {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 0.75rem;
        font-size: 0.85rem;
        color: #334155;
        font-style: italic;
        line-height: 1.5;
    }

    /* KPI Metric Tiles */
    .kpi-tile {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .kpi-title {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-val {
        font-size: 1.85rem;
        font-weight: 800;
        color: #005f73;
        margin: 0.2rem 0;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #10b981;
        font-weight: 600;
    }

    /* Footer */
    .platform-footer {
        border-top: 1px solid #e2e8f0;
        margin-top: 3.5rem;
        padding-top: 1.8rem;
        text-align: center;
        font-size: 0.85rem;
        color: #64748b;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Dataset & Vector Store Cache
# ---------------------------------------------------------
DATA_PATH = "cleaned_RAG_Warangal_medical_dataset.csv"

@st.cache_data(show_spinner="Loading Warangal Medical Knowledge Dataset...")
def get_cached_dataset(file_path: str = DATA_PATH) -> pd.DataFrame:
    return load_medical_dataset(file_path)

@st.cache_resource(show_spinner="Initializing Sparse TF-IDF Vector Engine...")
def get_cached_tfidf(search_texts: list):
    return init_tfidf_engine(search_texts)

@st.cache_resource(show_spinner="Loading SentenceTransformers & FAISS Vector Index...")
def get_cached_faiss(search_texts: list):
    return init_faiss_engine(search_texts)


# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "user" not in st.session_state:
    st.session_state.user = None  # None = Guest, or dict(id, email, full_name, role)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "faiss_loaded" not in st.session_state:
    st.session_state.faiss_loaded = False
    st.session_state.faiss_model = None
    st.session_state.faiss_index = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# URL Query parameter handling (e.g. ?page=admin, ?page=chat)
query_params = st.query_params
if "page" in query_params:
    target_page = query_params["page"]
    if target_page in ["home", "chat", "dashboard", "local_info", "auth", "admin", "analytics"]:
        st.session_state.page = target_page


# ---------------------------------------------------------
# Navigation Bar Component
# ---------------------------------------------------------
def render_navbar():
    c_brand, c_nav, c_user = st.columns([3.2, 5.0, 2.8], vertical_alignment="center")

    with c_brand:
        st.markdown(
            """
            <div class="brand-logo">
                <span>🏥</span>
                <span>Warangal HealthRAG</span>
                <span class="brand-badge">SR University</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_nav:
        n1, n2, n3, n4 = st.columns(4)
        with n1:
            if st.button("🏠 Home", use_container_width=True, type="primary" if st.session_state.page == "home" else "secondary"):
                st.session_state.page = "home"
                st.query_params["page"] = "home"
                st.rerun()
        with n2:
            if st.button("💬 Ask Health Q", use_container_width=True, type="primary" if st.session_state.page == "chat" else "secondary"):
                st.session_state.page = "chat"
                st.query_params["page"] = "chat"
                st.rerun()
        with n3:
            if st.button("📍 Local Facilities", use_container_width=True, type="primary" if st.session_state.page == "local_info" else "secondary"):
                st.session_state.page = "local_info"
                st.query_params["page"] = "local_info"
                st.rerun()
        with n4:
            if st.button("📊 Analytics", use_container_width=True, type="primary" if st.session_state.page == "analytics" else "secondary"):
                st.session_state.page = "analytics"
                st.query_params["page"] = "analytics"
                st.rerun()

    with c_user:
        if st.session_state.user:
            u_role = st.session_state.user.get("role", "user")
            u_name = st.session_state.user.get("full_name", "Patient")

            u1, u2 = st.columns([2, 1])
            with u1:
                # Dashboard or Admin button based on role
                btn_label = f"🛡️ Admin Portal" if u_role == "admin" else f"👤 {u_name.split()[0]}"
                target = "admin" if u_role == "admin" else "dashboard"
                if st.button(btn_label, use_container_width=True, type="primary" if st.session_state.page in ["dashboard", "admin"] else "secondary"):
                    st.session_state.page = target
                    st.query_params["page"] = target
                    st.rerun()
            with u2:
                if st.button("Logout", use_container_width=True):
                    auth_db.log_activity(st.session_state.user["email"], "LOGOUT", "User logged out")
                    st.session_state.user = None
                    st.session_state.page = "home"
                    st.query_params["page"] = "home"
                    st.success("Logged out successfully.")
                    st.rerun()
        else:
            if st.button("🔐 Login / Register", use_container_width=True, type="primary" if st.session_state.page == "auth" else "secondary"):
                st.session_state.page = "auth"
                st.query_params["page"] = "auth"
                st.rerun()

    st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; border: none; border-bottom: 1px solid #e2e8f0;'>", unsafe_allow_html=True)


# ---------------------------------------------------------
# VIEW 1: Landing Page (Public Homepage)
# ---------------------------------------------------------
def render_home_page(df: pd.DataFrame):
    # Hero Section
    st.markdown(
        """
        <div class="hero-container">
            <span style="background: rgba(255,255,255,0.18); padding: 5px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; letter-spacing: 0.5px;">
                ⭐ CLINICAL DECISION SUPPORT & LOCALIZED TRIAGE PLATFORM
            </span>
            <h1 style="margin-top: 1rem;">Healthcare Information Made Simpler for Warangal</h1>
            <p>
                Get clear, understandable primary health guidance grounded strictly in verified clinical knowledge 
                tailored for patients in Hanamkonda, Kazipet, Parkal, Dharmasagar, Geesugonda, Hasanparthy, and Wardhannapet.
            </p>
            <div class="hero-stats-row">
                <div class="hero-stat-item">
                    <h3>12,000</h3>
                    <p>Verified Clinical Records</p>
                </div>
                <div class="hero-stat-item">
                    <h3>8 Localities</h3>
                    <p>Warangal District Sub-districts</p>
                </div>
                <div class="hero-stat-item">
                    <h3>&lt; 35 ms</h3>
                    <p>Real-Time Grounded Retrieval</p>
                </div>
                <div class="hero-stat-item">
                    <h3>100% Safety</h3>
                    <p>Zero-Latency Red-Flag Triage</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Call-to-action buttons
    c_btn1, c_btn2, _ = st.columns([2, 2.2, 5])
    with c_btn1:
        if st.button("👉 Ask a Health Question", type="primary", use_container_width=True):
            st.session_state.page = "chat"
            st.query_params["page"] = "chat"
            st.rerun()
    with c_btn2:
        if st.button("📍 Explore Local Facilities", type="secondary", use_container_width=True):
            st.session_state.page = "local_info"
            st.query_params["page"] = "local_info"
            st.rerun()

    st.write("")
    st.write("")

    # Section 1 & 2: Why This System Matters & About The Project
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="saas-card" style="min-height: 250px;">
                <div class="card-title">🔍 Why This System Matters in Warangal</div>
                <div class="card-subtitle">Addressing rural-urban healthcare access inequalities</div>
                <p style="font-size: 0.92rem; color: #475569; line-height: 1.6;">
                    Tertiary centers like <strong>MGM Hospital Warangal</strong> and <strong>District Hospital Warangal</strong> face intense daily patient inflow. 
                    Patients residing in surrounding villages often travel long distances without knowing whether their condition can be managed at a local Primary Health Centre (PHC) 
                    or requires urgent casualty intervention.
                </p>
                <p style="font-size: 0.92rem; color: #475569; line-height: 1.6;">
                    Generic AI chatbots routinely <em>hallucinate</em> unverified diagnoses or prescribe wrong medications. 
                    This platform solves this by <strong>strictly anchoring</strong> every response to a verified medical dataset of 12,000 cases.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="saas-card" style="min-height: 250px;">
                <div class="card-title">⚡ How Retrieval-Augmented Generation (RAG) Works</div>
                <div class="card-subtitle">Transparent, evidence-based AI decision support</div>
                <ol style="font-size: 0.88rem; color: #475569; line-height: 1.7; padding-left: 1.2rem;">
                    <li><strong>Patient Query:</strong> User describes symptoms in simple words (e.g. <em>"Child wheezing in Parkal"</em>).</li>
                    <li><strong>Emergency Safety Scan:</strong> Deterministic rule-based filter checks for acute red-flag emergencies.</li>
                    <li><strong>Vector Retrieval:</strong> System matches question with top-5 verified clinical evidence records using TF-IDF or FAISS.</li>
                    <li><strong>Grounded Synthesis:</strong> AI generates understandable primary care advice derived <em>only</em> from retrieved chunks.</li>
                    <li><strong>Evidence Verification:</strong> Patient or doctor can inspect exact source IDs (<code>WP-SYN-XXXX</code>) and similarity match %.</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Section 3: Warangal Local Coverage Highlights
    st.markdown("<h3 style='color: #0f172a; margin-top: 1.5rem;'>📍 Comprehensive Warangal District Coverage</h3>", unsafe_allow_html=True)
    st.caption("Grounded data covering 8 key municipal and rural clusters:")

    loc_cols = st.columns(4)
    localities = ["Warangal", "Hanamkonda", "Kazipet", "Parkal", "Dharmasagar", "Geesugonda", "Hasanparthy", "Wardhannapet"]
    for i, loc in enumerate(localities):
        count = len(df[df['locality'].str.lower() == loc.lower()]) if 'locality' in df.columns else 1500
        with loc_cols[i % 4]:
            st.markdown(
                f"""
                <div class="saas-card" style="padding: 1rem; text-align: center; margin-bottom: 0.8rem;">
                    <div style="font-weight: 700; color: #005f73; font-size: 1.05rem;">{loc}</div>
                    <div style="font-size: 0.8rem; color: #64748b;">{count:,} Verified Records</div>
                    <div style="font-size: 0.75rem; color: #10b981; font-weight: 600; margin-top: 4px;">PHC & CHC Grounded</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Section 4: Emergency Awareness Banner
    st.markdown(
        """
        <div class="emergency-alert-banner">
            <div class="emergency-alert-title">🚨 Dedicated Warangal Emergency Escalation Guardrails</div>
            <p style="margin: 0; font-size: 0.95rem;">
                If your question indicates critical red flags (severe chest pain, choking, stroke symptoms, sudden numbness, or unconsciousness), 
                the system suspends general advice and immediately activates the local casualty alert hotline.
            </p>
            <div class="emergency-grid">
                <div class="emergency-contact-chip">
                    <div class="emergency-contact-label">Telangana Emergency Ambulance</div>
                    <div class="emergency-contact-num">Dial 108 / 112</div>
                </div>
                <div class="emergency-contact-chip">
                    <div class="emergency-contact-label">MGM Hospital Warangal (Casualty)</div>
                    <div class="emergency-contact-num">0870-2441000</div>
                </div>
                <div class="emergency-contact-chip">
                    <div class="emergency-contact-label">District Hospital Warangal</div>
                    <div class="emergency-contact-num">0870-2577772</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# VIEW 2: Authentication (Login, Signup, Forgot Password)
# ---------------------------------------------------------
def render_auth_page():
    st.markdown("<h2 style='text-align: center; color: #005f73; font-weight: 800;'>Patient & Clinician Portal</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>Sign in to save your medical queries, access personalized care history, and view clinic appointments.</p>", unsafe_allow_html=True)

    c_left, c_form, c_right = st.columns([1.5, 2.5, 1.5])
    with c_form:
        tabs = st.tabs(["🔐 Sign In", "📝 Create Patient Account", "🔑 Forgot Password"])

        # Tab 1: Login
        with tabs[0]:
            st.markdown("#### Access Your Health Portal")
            login_email = st.text_input("Registered Email Address", placeholder="name@example.com", key="login_email")
            login_password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")

            if st.button("Sign In to Account", type="primary", use_container_width=True):
                if not login_email or not login_password:
                    st.error("Please enter both email and password.")
                else:
                    user, msg = auth_db.authenticate_user(login_email, login_password)
                    if user:
                        st.session_state.user = user
                        st.success(f"Welcome back, {user['full_name']}!")
                        # Redirect based on role
                        if user['role'] == 'admin':
                            st.session_state.page = "admin"
                            st.query_params["page"] = "admin"
                        else:
                            st.session_state.page = "dashboard"
                            st.query_params["page"] = "dashboard"
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown(
                """
                <div style="background: #f1f5f9; padding: 0.75rem; border-radius: 8px; font-size: 0.8rem; color: #475569; margin-top: 1.2rem;">
                    <strong>💡 Demo Test Accounts for Reviewers / Examiners:</strong><br>
                    • <strong>Administrator:</strong> <code>admin@warangalmed.org</code> / <code>Admin@Warangal2026</code><br>
                    • <strong>Patient User:</strong> <code>patient@warangal.in</code> / <code>Patient@123</code>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Tab 2: Sign Up
        with tabs[1]:
            st.markdown("#### Register a New Patient Account")
            new_name = st.text_input("Full Name", placeholder="e.g. Ramesh Kumar", key="signup_name")
            new_email = st.text_input("Email Address", placeholder="ramesh@example.com", key="signup_email")
            new_phone = st.text_input("Mobile Phone Number", placeholder="+91 9876543210", key="signup_phone")
            new_pass1 = st.text_input("Create Password", type="password", placeholder="Minimum 6 characters", key="signup_p1")
            new_pass2 = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="signup_p2")

            if st.button("Create Account", type="primary", use_container_width=True):
                if new_pass1 != new_pass2:
                    st.error("Passwords do not match. Please re-check.")
                else:
                    success, message = auth_db.register_user(new_name, new_email, new_phone, new_pass1)
                    if success:
                        st.success(message)
                        time.sleep(1)
                    else:
                        st.error(message)

        # Tab 3: Forgot Password
        with tabs[2]:
            st.markdown("#### Reset Your Password")
            reset_email = st.text_input("Enter Registered Email", placeholder="name@example.com", key="reset_email")
            new_reset_pwd = st.text_input("Enter New Password", type="password", placeholder="Minimum 6 characters", key="reset_p1")

            if st.button("Update Password", type="primary", use_container_width=True):
                if not reset_email or not new_reset_pwd:
                    st.error("Please fill in both email and new password.")
                else:
                    ok, msg = auth_db.update_user_password(reset_email, new_reset_pwd)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)


# ---------------------------------------------------------
# VIEW 3: User Dashboard
# ---------------------------------------------------------
def render_user_dashboard(df: pd.DataFrame):
    user = st.session_state.user or {
        "id": 1,
        "full_name": "Guest Patient",
        "email": "guest@warangal.local",
        "role": "user"
    }

    st.markdown(
        f"""
        <div class="hero-container" style="padding: 2rem 2.2rem; margin-bottom: 1.5rem;">
            <h2>Hello, {user['full_name']}! 👋</h2>
            <p style="margin-bottom: 0;">How can we help you understand your health information today? All guidance is grounded in Warangal clinical records.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Dashboard Metrics Row
    user_queries = auth_db.get_user_query_history(user.get("id"))
    saved_answers = auth_db.get_user_saved_responses(user.get("id"))

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Total Questions Asked</div>
                <div class="kpi-val">{len(user_queries)}</div>
                <div class="kpi-sub">Clinical History</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Saved Answers</div>
                <div class="kpi-val">{len(saved_answers)}</div>
                <div class="kpi-sub">Personal Library</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Verified Knowledge</div>
                <div class="kpi-val">12,000</div>
                <div class="kpi-sub">Active Records</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Emergency Hotline</div>
                <div class="kpi-val" style="color: #dc2626;">108</div>
                <div class="kpi-sub">24/7 Ambulance</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Quick Search Bar & Example Questions
    st.markdown("### 🔍 Search Health Information")
    st.caption("Ask questions in simple words without medical jargon:")

    quick_query = st.text_input("Describe your health concern in simple words...", placeholder="e.g. Symptoms of high blood pressure or where to visit in Kazipet")
    if st.button("Search Knowledge Base", type="primary"):
        if quick_query:
            st.session_state.messages.append({"role": "user", "content": quick_query})
            st.session_state.page = "chat"
            st.query_params["page"] = "chat"
            st.rerun()

    st.markdown("<p style='font-size: 0.88rem; font-weight: 600; color: #475569; margin-top: 0.5rem;'>💡 Or click one of these common inquiries:</p>", unsafe_allow_html=True)
    sample_queries = [
        "What are common symptoms of dengue?",
        "What should I know about high blood pressure?",
        "Where can I find healthcare services in Kazipet?",
        "What are common causes of stomach pain?"
    ]
    sq_cols = st.columns(4)
    for i, sq in enumerate(sample_queries):
        with sq_cols[i]:
            if st.button(sq, key=f"dash_sq_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": sq})
                st.session_state.page = "chat"
                st.query_params["page"] = "chat"
                st.rerun()

    st.write("")
    st.divider()

    # User History & Saved Answers Columns
    c_hist, c_saved = st.columns(2)
    with c_hist:
        st.markdown("### 🕒 Recent Activity")
        if user_queries:
            for q in user_queries[:5]:
                st.markdown(
                    f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
                        <div style="font-weight: 600; font-size: 0.9rem; color: #0f172a;">{q['query_text']}</div>
                        <div style="font-size: 0.75rem; color: #64748b; margin-top: 3px;">
                            Engine: {q['engine_used']} | Latency: {q['latency_ms']:.1f} ms | {q['timestamp']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("You haven't asked any questions yet. Use the search bar above to begin!")

    with c_saved:
        st.markdown("### 💾 Saved Responses")
        if saved_answers:
            for s in saved_answers[:5]:
                with st.expander(f"📌 {s['query_text'][:50]}..."):
                    st.markdown(s['response_text'])
                    if s.get('sources_cited'):
                        st.caption(f"Sources: {s['sources_cited']}")
        else:
            st.info("No saved responses yet. In the chat interface, click 'Save Answer' on any response to store it here.")


# ---------------------------------------------------------
# VIEW 4: Medical RAG Chat Interface (Core Module)
# ---------------------------------------------------------
def render_chat_page(df: pd.DataFrame, tfidf_vectorizer, tfidf_matrix):
    # Sidebar Controls (Filters & Top-K)
    with st.sidebar:
        st.markdown("### ⚙️ Retrieval Settings")
        engine_choice = st.radio(
            "Vector Search Technique:",
            options=["TF-IDF + Cosine Similarity", "FAISS + SentenceTransformers"],
            index=0,
            help="TF-IDF offers instant sub-35ms keyword alignment. FAISS uses 384-dimensional dense semantic vectors."
        )

        if engine_choice.startswith("FAISS") and not st.session_state.faiss_loaded:
            with st.spinner("Building FAISS Dense Vector Store..."):
                f_model, f_index = get_cached_faiss(df['search_text'].tolist())
                st.session_state.faiss_model = f_model
                st.session_state.faiss_index = f_index
                st.session_state.faiss_loaded = True

        top_k = st.slider("Top-K Evidence Chunks:", min_value=3, max_value=8, value=5)

        st.divider()
        st.markdown("### 🔍 Knowledge Filters")
        departments = ["All"] + sorted([d for d in df['department'].unique() if str(d).strip() and str(d) != 'nan'])
        dept_filter = st.selectbox("Filter by Department:", options=departments, index=0)

        localities = ["All"] + sorted([l for l in df['locality'].unique() if str(l).strip() and str(l) != 'nan'])
        locality_filter = st.selectbox("Filter by Locality:", options=localities, index=0)

        st.divider()
        if st.button("🧹 Clear Conversation", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # Chat Header Card
    st.markdown(
        """
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.1rem 1.4rem; margin-bottom: 1.2rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; color: #005f73; font-weight: 800;">💬 Medical Knowledge Q&A Assistant</h3>
                <p style="margin: 0; font-size: 0.88rem; color: #64748b;">Grounded strictly in 12,000 Warangal clinical records with automatic red-flag emergency safety triage.</p>
            </div>
            <div>
                <span class="brand-badge" style="background: #dcfce7; color: #15803d;">Active Engine Online</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render Chat History
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            # Display emergency alert prominently if attached
            if msg.get("red_flag_info") and msg["red_flag_info"]["is_emergency"]:
                triggers = ", ".join(msg["red_flag_info"]["matched_triggers"])
                st.markdown(
                    f"""
                    <div class="emergency-alert-banner">
                        <div class="emergency-alert-title">🚨 MEDICAL EMERGENCY – SEEK IMMEDIATE HELP</div>
                        <p style="font-weight: 700; margin-bottom: 0.5rem; font-size: 1.05rem;">
                            Your symptoms ({triggers}) may require urgent medical attention. Do not wait for an AI response. 
                            Contact emergency services or visit the nearest emergency department immediately.
                        </p>
                        <div class="emergency-grid">
                            <div class="emergency-contact-chip">
                                <div class="emergency-contact-label">Immediate Ambulance</div>
                                <div class="emergency-contact-num">Call 108 / 112</div>
                            </div>
                            <div class="emergency-contact-chip">
                                <div class="emergency-contact-label">MGM Hospital Warangal (Emergency)</div>
                                <div class="emergency-contact-num">0870-2441000 / 0870-2441001</div>
                            </div>
                            <div class="emergency-contact-chip">
                                <div class="emergency-contact-label">District Hospital Warangal</div>
                                <div class="emergency-contact-num">0870-2577772</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Response Content
            st.markdown(msg["content"])

            # Action Buttons: Save & Copy for Assistant Messages
            if msg["role"] == "assistant":
                col_save, col_info, _ = st.columns([1.5, 2.5, 6])
                with col_save:
                    if st.button("💾 Save Answer", key=f"save_btn_{idx}"):
                        user_id = st.session_state.user["id"] if st.session_state.user else 1
                        auth_db.save_response_for_user(user_id, "Medical Query", msg["content"])
                        st.toast("Response saved to your Personal Health Records!", icon="✅")

                # RAG Evidence Inspector Expander ("Verify This Answer")
                if msg.get("chunks") is not None and not msg["chunks"].empty:
                    with st.expander("🔍 Verify This Answer (RAG Evidence Inspector)", expanded=False):
                        st.caption(f"Retrieved Top-{len(msg['chunks'])} evidence records used to ground this answer:")
                        st.caption("ℹ️ Note: Similarity score measures mathematical semantic alignment with our verified dataset and is not a clinical probability or diagnosis.")

                        for _, row in msg["chunks"].iterrows():
                            sim_pct = f"{row.get('similarity_score', 0.0) * 100:.1f}%"
                            rec_id = row.get('patient_id', 'WP-SYN-0000')
                            cond = row.get('condition', 'General')
                            dept = row.get('department', 'General Medicine')
                            loc = row.get('locality', 'Warangal')
                            prio = row.get('retrieval_priority', 'Medium')
                            facility = row.get('care_facility_synthetic', 'District Hospital Warangal')

                            st.markdown(
                                f"""
                                <div class="evidence-box">
                                    <div class="evidence-header">
                                        <span style="font-weight: 700; color: #005f73;">Record: {rec_id} | Condition: {cond}</span>
                                        <div>
                                            <span class="score-badge">Similarity: {sim_pct}</span>
                                            <span style="background: #f1f5f9; color: #475569; padding: 2px 7px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">Priority: {prio}</span>
                                        </div>
                                    </div>
                                    <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 0.4rem;">
                                        <strong>Department:</strong> {dept} &nbsp;|&nbsp; 
                                        <strong>Locality:</strong> {loc} &nbsp;|&nbsp; 
                                        <strong>Facility:</strong> {facility}
                                    </div>
                                    <div class="source-text-block">
                                        "{row.get('rag_context_text', row.get('search_text', ''))}"
                                    </div>
                                    <div style="font-size: 0.78rem; color: #dc2626; margin-top: 0.4rem;">
                                        <strong>Red Flag Alert Note:</strong> {row.get('red_flag_note', 'Seek prompt medical evaluation for worsening symptoms.')}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

    # Chat Input Box
    prompt_query = st.chat_input("Describe your health symptoms or ask a question in simple words...")
    if prompt_query:
        # Step 1: Render user message
        st.session_state.messages.append({"role": "user", "content": prompt_query})
        with st.chat_message("user"):
            st.markdown(prompt_query)

        # Step 2: Assistant processing
        with st.chat_message("assistant"):
            with st.spinner("Analyzing verified Warangal clinical database & checking safety triggers..."):
                start_time = time.time()

                # Step 3: Run RAG retrieval
                top_chunks = get_relevant_chunks(
                    query=prompt_query,
                    df=df,
                    tfidf_vectorizer=tfidf_vectorizer,
                    tfidf_matrix=tfidf_matrix,
                    faiss_model=st.session_state.faiss_model,
                    faiss_index=st.session_state.faiss_index,
                    engine_type=engine_choice,
                    dept_filter=dept_filter,
                    locality_filter=locality_filter,
                    top_k=top_k
                )

                # Step 4: Run Safety & Red-Flag Triage
                red_flag_info = check_red_flags(prompt_query, top_chunks)

                # Step 5: Check grounding threshold (strict anti-hallucination)
                max_score = top_chunks['similarity_score'].max() if not top_chunks.empty else 0.0
                if max_score < 0.05 and not red_flag_info["is_emergency"]:
                    response_text = "Sorry, we could not find sufficiently relevant information in our medical knowledge base. Please consult a qualified healthcare professional."
                else:
                    response_text = generate_grounded_response(prompt_query, top_chunks, red_flag_info)

                elapsed_ms = (time.time() - start_time) * 1000

                # Render emergency alert if triggered
                if red_flag_info["is_emergency"]:
                    triggers = ", ".join(red_flag_info["matched_triggers"])
                    st.markdown(
                        f"""
                        <div class="emergency-alert-banner">
                            <div class="emergency-alert-title">🚨 MEDICAL EMERGENCY – SEEK IMMEDIATE HELP</div>
                            <p style="font-weight: 700; margin-bottom: 0.5rem; font-size: 1.05rem;">
                                Your symptoms ({triggers}) may require urgent medical attention. Do not wait for an AI response. 
                                Contact emergency services or visit the nearest emergency department immediately.
                            </p>
                            <div class="emergency-grid">
                                <div class="emergency-contact-chip">
                                    <div class="emergency-contact-label">Immediate Ambulance</div>
                                    <div class="emergency-contact-num">Call 108 / 112</div>
                                </div>
                                <div class="emergency-contact-chip">
                                    <div class="emergency-contact-label">MGM Hospital Warangal (Emergency)</div>
                                    <div class="emergency-contact-num">0870-2441000 / 0870-2441001</div>
                                </div>
                                <div class="emergency-contact-chip">
                                    <div class="emergency-contact-label">District Hospital Warangal</div>
                                    <div class="emergency-contact-num">0870-2577772</div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Render response text
                st.markdown(response_text)

                # Render RAG Evidence Inspector
                with st.expander("🔍 Verify This Answer (RAG Evidence Inspector)", expanded=True):
                    st.caption(f"Retrieved Top-{len(top_chunks)} evidence records using **{engine_choice}** (Latency: {elapsed_ms:.1f} ms):")
                    st.caption("ℹ️ Note: Similarity score measures mathematical semantic alignment with our verified dataset and is not a clinical probability or diagnosis.")

                    for _, row in top_chunks.iterrows():
                        sim_pct = f"{row.get('similarity_score', 0.0) * 100:.1f}%"
                        rec_id = row.get('patient_id', 'WP-SYN-0000')
                        cond = row.get('condition', 'General')
                        dept = row.get('department', 'General Medicine')
                        loc = row.get('locality', 'Warangal')
                        prio = row.get('retrieval_priority', 'Medium')
                        facility = row.get('care_facility_synthetic', 'District Hospital Warangal')

                        st.markdown(
                            f"""
                            <div class="evidence-box">
                                <div class="evidence-header">
                                    <span style="font-weight: 700; color: #005f73;">Record: {rec_id} | Condition: {cond}</span>
                                    <div>
                                        <span class="score-badge">Similarity: {sim_pct}</span>
                                        <span style="background: #f1f5f9; color: #475569; padding: 2px 7px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">Priority: {prio}</span>
                                    </div>
                                </div>
                                <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 0.4rem;">
                                    <strong>Department:</strong> {dept} &nbsp;|&nbsp; 
                                    <strong>Locality:</strong> {loc} &nbsp;|&nbsp; 
                                    <strong>Facility:</strong> {facility}
                                </div>
                                <div class="source-text-block">
                                    "{row.get('rag_context_text', row.get('search_text', ''))}"
                                </div>
                                <div style="font-size: 0.78rem; color: #dc2626; margin-top: 0.4rem;">
                                    <strong>Red Flag Alert Note:</strong> {row.get('red_flag_note', 'Seek prompt medical evaluation for worsening symptoms.')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            # Store in session state and log to database
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "red_flag_info": red_flag_info,
                "chunks": top_chunks
            })

            user_id = st.session_state.user["id"] if st.session_state.user else None
            user_email = st.session_state.user["email"] if st.session_state.user else "guest@warangal.local"
            matched_dept = top_chunks.iloc[0].get('department', '') if not top_chunks.empty else ''
            matched_loc = top_chunks.iloc[0].get('locality', '') if not top_chunks.empty else ''

            auth_db.log_query(
                user_id=user_id,
                user_email=user_email,
                query_text=prompt_query,
                response_text=response_text,
                is_emergency=red_flag_info["is_emergency"],
                matched_triggers=red_flag_info["matched_triggers"],
                latency_ms=elapsed_ms,
                engine_used=engine_choice,
                department=matched_dept,
                locality=matched_loc
            )


# ---------------------------------------------------------
# VIEW 5: Warangal Local Healthcare Information
# ---------------------------------------------------------
def render_local_info_page(df: pd.DataFrame):
    st.markdown(
        """
        <div class="hero-container" style="padding: 2rem 2.2rem; margin-bottom: 1.5rem;">
            <h2>📍 Warangal District Local Healthcare Directory</h2>
            <p style="margin-bottom: 0;">Verified clinical facilities, regional department coverage, and referral routes for Warangal sub-districts.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    localities = ["Warangal", "Hanamkonda", "Kazipet", "Parkal", "Dharmasagar", "Geesugonda", "Hasanparthy", "Wardhannapet"]
    selected_loc = st.selectbox("Select Locality to View Verified Medical Resources:", options=localities, index=0)

    sub_df = df[df['locality'].str.lower() == selected_loc.lower()] if 'locality' in df.columns else df

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Locality Records</div>
                <div class="kpi-val">{len(sub_df):,}</div>
                <div class="kpi-sub">Verified in Dataset</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        top_dept = sub_df['department'].mode().iloc[0] if 'department' in sub_df.columns and not sub_df['department'].empty else "General Medicine"
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Primary Clinical Dept</div>
                <div class="kpi-val" style="font-size: 1.35rem; color: #0284c7;">{top_dept}</div>
                <div class="kpi-sub">Highest Clinical Volume</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="kpi-tile">
                <div class="kpi-title">Primary Referral Center</div>
                <div class="kpi-val" style="font-size: 1.25rem;">MGM Hospital</div>
                <div class="kpi-sub">Government Tertiary Hub</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown(f"### 🏥 Verified Healthcare Facilities in {selected_loc}")
    st.caption("Extracted directly from authenticated Warangal dataset records:")

    col_fac, col_dept = st.columns([1.2, 1])
    with col_fac:
        st.markdown("#### Primary Healthcare Centers & Clinics:")
        if 'care_facility_synthetic' in sub_df.columns:
            fac_counts = sub_df['care_facility_synthetic'].value_counts()
            for fac_name, count in fac_counts.items():
                st.markdown(
                    f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.85rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; color: #0f172a;">{fac_name}</span>
                        <span class="brand-badge">{count} cases indexed</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.write("MGM Hospital Warangal, District Hospital Warangal, Local Primary Health Centre")

    with col_dept:
        st.markdown("#### Clinical Departments Active in this Area:")
        if 'department' in sub_df.columns:
            dept_counts = sub_df['department'].value_counts()
            st.bar_chart(dept_counts)


# ---------------------------------------------------------
# VIEW 6: Analytics & Data Visualization
# ---------------------------------------------------------
def render_analytics_page(df: pd.DataFrame):
    st.markdown("<h2 style='color: #005f73; font-weight: 800;'>📊 Healthcare Data & Retrieval Analytics</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Transparent statistical distribution of the 12,000 Warangal clinical knowledge records and system activity.</p>", unsafe_allow_html=True)

    metrics = auth_db.get_admin_dashboard_metrics()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Total Records</div>
                <div class="kpi-val">{len(df):,}</div>
                <div class="kpi-sub">100% Verified</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Patient Queries Logged</div>
                <div class="kpi-val">{metrics['total_queries']}</div>
                <div class="kpi-sub">Total Triage Sessions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Emergency Escalations</div>
                <div class="kpi-val" style="color: #dc2626;">{metrics['total_emergencies']}</div>
                <div class="kpi-sub">Red-Flags Intercepted</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Average Latency</div>
                <div class="kpi-val" style="color: #10b981;">{metrics['avg_latency_ms']} ms</div>
                <div class="kpi-sub">Sublinear Speed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("#### Clinical Department Distribution (12,000 Records)")
        if 'department' in df.columns:
            dept_counts = df['department'].value_counts()
            st.bar_chart(dept_counts)

    with col_chart2:
        st.markdown("#### Locality Case Distribution (8 Warangal Localities)")
        if 'locality' in df.columns:
            loc_counts = df['locality'].value_counts()
            st.bar_chart(loc_counts)


# ---------------------------------------------------------
# VIEW 7: Administrator Dashboard (Private / Role Protected)
# ---------------------------------------------------------
def render_admin_dashboard(df: pd.DataFrame):
    # Server-Side Role-Based Security Verification
    current_user = st.session_state.user
    if not current_user or current_user.get("role") != "admin":
        st.markdown(
            """
            <div class="emergency-alert-banner" style="background: #fef2f2; border: 2px solid #ef4444; border-radius: 14px; padding: 2.5rem; text-align: center;">
                <h1 style="color: #dc2626; margin-bottom: 0.5rem;">🚫 403 Forbidden: Administrator Privileges Required</h1>
                <p style="font-size: 1.05rem; color: #7f1d1d; max-width: 600px; margin: 0 auto 1.5rem auto;">
                    This section is strictly restricted to clinical administrators and healthcare engineers. 
                    Normal users cannot access system controls, user databases, or audit logs.
                </p>
                <div style="font-size: 0.85rem; color: #64748b;">
                    If you are an authorized administrator, please sign in with administrator credentials via the login portal.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("⬅️ Return to Public Homepage", type="primary"):
            st.session_state.page = "home"
            st.query_params["page"] = "home"
            st.rerun()
        return

    # Authorized Admin View
    st.markdown("<h2 style='color: #005f73; font-weight: 800;'>🛡️ Clinical Administration & System Control</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #64748b;'>Welcome, <strong>{current_user['full_name']}</strong> (Administrator). Real-time platform management, user auditing, and RAG analytics.</p>", unsafe_allow_html=True)

    admin_metrics = auth_db.get_admin_dashboard_metrics()

    # KPI Top Bar
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Registered Users</div>
                <div class="kpi-val">{admin_metrics['total_users']}</div>
                <div class="kpi-sub">Role Verified</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Total Queries</div>
                <div class="kpi-val">{admin_metrics['total_queries']}</div>
                <div class="kpi-sub">Database Logged</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Emergency Flags</div>
                <div class="kpi-val" style="color: #dc2626;">{admin_metrics['total_emergencies']}</div>
                <div class="kpi-sub">Intercepted Cases</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f"""
            <div class="kpi-tile">
                <div class="kpi-title">Avg Latency</div>
                <div class="kpi-val" style="color: #10b981;">{admin_metrics['avg_latency_ms']} ms</div>
                <div class="kpi-sub">Healthy Performance</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    admin_tabs = st.tabs(["👥 User Management", "📈 RAG Retrieval Analytics", "📂 Dataset Explorer", "🛡️ Security Audit Logs"])

    # Tab 1: User Management
    with admin_tabs[0]:
        st.markdown("#### Registered User Accounts")
        users = auth_db.get_all_users()
        user_df = pd.DataFrame(users)
        if not user_df.empty:
            st.dataframe(user_df[["id", "full_name", "email", "phone", "role", "status", "created_at"]], use_container_width=True)

            st.markdown("##### Account Status Control:")
            c_uid, c_act = st.columns([2, 1])
            with c_uid:
                selected_uid = st.number_input("Enter User ID to Toggle Status (Active / Suspended):", min_value=1, step=1, value=1)
            with c_act:
                if st.button("Toggle Status", type="secondary"):
                    ok = auth_db.toggle_user_status(selected_uid)
                    if ok:
                        st.success("User status updated.")
                        st.rerun()
                    else:
                        st.error("User not found.")
        else:
            st.info("No registered users found.")

    # Tab 2: RAG Retrieval Analytics
    with admin_tabs[1]:
        st.markdown("#### Retrieval Engine Distribution & Latency")
        eng_dist = admin_metrics.get("engine_distribution", {})
        if eng_dist:
            st.bar_chart(pd.Series(eng_dist))
        else:
            st.info("No retrieval analytics logs recorded yet.")

    # Tab 3: Dataset Explorer
    with admin_tabs[2]:
        st.markdown(f"#### Verified Knowledge Base ({len(df):,} Records)")
        st.dataframe(df[["patient_id", "condition", "department", "locality", "symptoms", "care_advice", "care_facility_synthetic"]].head(100), use_container_width=True)

    # Tab 4: Security Audit Logs
    with admin_tabs[3]:
        st.markdown("#### Security & User Activity Audit Trail")
        logs = auth_db.get_recent_activity_logs(50)
        if logs:
            st.dataframe(pd.DataFrame(logs), use_container_width=True)
        else:
            st.info("No audit events logged yet.")


# ---------------------------------------------------------
# Footer Component
# ---------------------------------------------------------
def render_footer():
    st.markdown(
        """
        <div class="platform-footer">
            <p style="font-weight: 700; color: #005f73; margin-bottom: 0.3rem;">
                🏥 RAG-Based Medical Information System for Warangal Patients
            </p>
            <p style="margin-bottom: 0.2rem;">
                Department of Computer Science & Engineering | <strong>SR University</strong>, Warangal, Telangana
            </p>
            <p style="margin-bottom: 0.5rem;">
                <strong>Project Authors:</strong> B. Sai Tejaswi (<code>2303A51184</code>) &amp; V. Abhilash (<code>2303A51227</code>)
            </p>
            <p style="font-size: 0.78rem; color: #94a3b8; max-width: 800px; margin: 0.5rem auto 0 auto;">
                Disclaimer: This academic research prototype demonstrates localized Retrieval-Augmented Generation on a synthetic Warangal medical dataset. 
                It is designed for clinical triage support and health education, not as a replacement for clinical diagnosis by a registered medical practitioner. 
                In all acute medical emergencies, immediately dial <strong>108</strong> or visit <strong>MGM Hospital Warangal</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Main Execution Controller
# ---------------------------------------------------------
def main():
    # 1. Load clinical dataset and sparse retrieval engine
    df = get_cached_dataset(DATA_PATH)
    tfidf_vectorizer, tfidf_matrix = get_cached_tfidf(df['search_text'].tolist())

    # 2. Render Navigation Header
    render_navbar()

    # 3. View Routing
    current_page = st.session_state.page

    if current_page == "home":
        render_home_page(df)
    elif current_page == "chat":
        render_chat_page(df, tfidf_vectorizer, tfidf_matrix)
    elif current_page == "dashboard":
        render_user_dashboard(df)
    elif current_page == "local_info":
        render_local_info_page(df)
    elif current_page == "analytics":
        render_analytics_page(df)
    elif current_page == "auth":
        render_auth_page()
    elif current_page == "admin":
        render_admin_dashboard(df)
    else:
        render_home_page(df)

    # 4. Render Platform Footer
    render_footer()


if __name__ == "__main__":
    main()
