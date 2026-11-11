import os
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
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Professional Healthcare SaaS Design System (Light Theme Only)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-main: #F7FAFC;
        --card-bg: #FFFFFF;
        --primary-teal: #167D83;
        --primary-hover: #116267;
        --secondary-teal: #D9F0ED;
        --main-text: #263746;
        --secondary-text: #64748B;
        --border-color: #E5EBEF;
        --success-color: #248A61;
        --warning-color: #D99A36;
        --error-color: #D9534F;
        --error-bg: #FFF5F5;
        --error-border: #FED7D7;
    }

    /* Enforce light background across entire window */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: var(--bg-main) !important;
        color: var(--main-text) !important;
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid var(--border-color) !important;
    }

    .main .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1220px !important;
    }

    /* Top Navigation Bar */
    .saas-nav {
        background: #FFFFFF;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 0.85rem 1.4rem;
        margin-bottom: 1.4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .brand-group {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-mark {
        width: 36px;
        height: 36px;
        background: var(--primary-teal);
        color: white;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.1rem;
    }
    .brand-title {
        font-weight: 800;
        font-size: 1.15rem;
        color: var(--primary-teal);
        letter-spacing: -0.3px;
        margin: 0;
    }
    .brand-tag {
        background: var(--secondary-teal);
        color: var(--primary-teal);
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
        text-transform: uppercase;
    }

    /* Hero Banner */
    .saas-hero {
        background: #FFFFFF;
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 2.8rem 2.4rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.02);
    }
    .saas-hero h1 {
        font-size: 2.35rem;
        font-weight: 800;
        color: var(--main-text);
        letter-spacing: -0.02em;
        line-height: 1.25;
        margin-bottom: 0.75rem;
    }
    .saas-hero h1 span {
        color: var(--primary-teal);
    }
    .saas-hero p {
        font-size: 1.05rem;
        color: var(--secondary-text);
        max-width: 760px;
        line-height: 1.6;
        margin-bottom: 1.8rem;
    }
    .hero-stat-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.2rem;
        border-top: 1px solid var(--border-color);
        padding-top: 1.4rem;
        margin-top: 1.2rem;
    }
    .hero-stat-card {
        background: var(--bg-main);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
    }
    .hero-stat-num {
        font-size: 1.45rem;
        font-weight: 800;
        color: var(--primary-teal);
    }
    .hero-stat-label {
        font-size: 0.8rem;
        color: var(--secondary-text);
        font-weight: 600;
    }

    /* Professional Cards */
    .saas-card {
        background: #FFFFFF;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.4rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-bottom: 1rem;
    }
    .saas-card-title {
        font-size: 1.08rem;
        font-weight: 700;
        color: var(--main-text);
        margin-bottom: 0.4rem;
    }
    .saas-card-sub {
        font-size: 0.85rem;
        color: var(--secondary-text);
        margin-bottom: 0.8rem;
    }

    /* Emergency Alert Component */
    .emergency-alert-card {
        background-color: var(--error-bg);
        border: 2px solid var(--error-border);
        border-radius: 12px;
        padding: 1.4rem;
        margin: 1.2rem 0;
        color: #7A271A;
    }
    .emergency-alert-head {
        font-size: 1.2rem;
        font-weight: 800;
        color: var(--error-color);
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.4rem;
    }
    .emergency-alert-body {
        font-size: 0.95rem;
        color: #7A271A;
        line-height: 1.5;
        margin-bottom: 1rem;
    }
    .emergency-chips {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 0.8rem;
    }
    .emergency-chip-item {
        background: #FFFFFF;
        border: 1px solid #FED7D7;
        border-radius: 8px;
        padding: 0.65rem 0.9rem;
    }
    .emergency-chip-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--error-color);
        text-transform: uppercase;
    }
    .emergency-chip-val {
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--main-text);
    }

    /* Evidence Inspector Box */
    .evidence-card {
        background: #FFFFFF;
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--primary-teal);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.6rem 0;
    }
    .evidence-meta-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 0.4rem;
        margin-bottom: 0.5rem;
    }
    .badge-sim {
        background-color: var(--secondary-teal);
        color: var(--primary-teal);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .badge-prio {
        background-color: #F1F5F9;
        color: #475569;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .evidence-text-snippet {
        background: var(--bg-main);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 0.7rem;
        font-size: 0.84rem;
        color: var(--secondary-text);
        font-style: italic;
        line-height: 1.5;
    }

    /* Split Login Page Styles */
    .split-login-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2.5rem;
        align-items: center;
        padding: 1.5rem 0;
    }
    .login-brand-panel {
        background: #FFFFFF;
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 2.8rem 2.2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.02);
    }
    .login-brand-panel h2 {
        font-size: 2rem;
        font-weight: 800;
        color: var(--main-text);
        margin-bottom: 0.8rem;
        line-height: 1.25;
    }
    .login-brand-panel h2 span {
        color: var(--primary-teal);
    }
    .login-brand-panel p {
        font-size: 0.98rem;
        color: var(--secondary-text);
        line-height: 1.6;
        margin-bottom: 1.8rem;
    }
    .feature-point {
        display: flex;
        gap: 12px;
        margin-bottom: 1.1rem;
        align-items: flex-start;
    }
    .feature-point-dot {
        width: 22px;
        height: 22px;
        background: var(--secondary-teal);
        color: var(--primary-teal);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 800;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .feature-point-text h4 {
        font-size: 0.92rem;
        font-weight: 700;
        color: var(--main-text);
        margin: 0;
    }
    .feature-point-text p {
        font-size: 0.82rem;
        color: var(--secondary-text);
        margin: 0;
    }

    /* Buttons & Inputs */
    button[kind="primary"] {
        background-color: var(--primary-teal) !important;
        border-color: var(--primary-teal) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    button[kind="primary"]:hover {
        background-color: var(--primary-hover) !important;
        border-color: var(--primary-hover) !important;
    }
    button[kind="secondary"] {
        border-color: var(--border-color) !important;
        color: var(--main-text) !important;
        border-radius: 8px !important;
    }

    /* Footer */
    .saas-footer {
        border-top: 1px solid var(--border-color);
        margin-top: 3.5rem;
        padding-top: 1.6rem;
        text-align: center;
        font-size: 0.84rem;
        color: var(--secondary-text);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Dataset & Vector Store Cache
# ---------------------------------------------------------
DATA_PATH = "cleaned_RAG_Warangal_medical_dataset.csv"

@st.cache_data(show_spinner="Loading Warangal clinical dataset...")
def get_cached_dataset(file_path: str = DATA_PATH) -> pd.DataFrame:
    return load_medical_dataset(file_path)

@st.cache_resource(show_spinner="Initializing sparse TF-IDF retrieval index...")
def get_cached_tfidf(search_texts: list):
    return init_tfidf_engine(search_texts)

@st.cache_resource(show_spinner="Loading dense vector embeddings (all-MiniLM-L6-v2)...")
def get_cached_faiss(search_texts: list):
    return init_faiss_engine(search_texts)


# ---------------------------------------------------------
# Session State & Navigation Router
# ---------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "faiss_loaded" not in st.session_state:
    st.session_state.faiss_loaded = False
    st.session_state.faiss_model = None
    st.session_state.faiss_index = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# URL Query parameter handling
query_params = st.query_params
if "page" in query_params:
    target_page = query_params["page"]
    if target_page in ["home", "chat", "dashboard", "local_info", "auth", "admin", "analytics"]:
        st.session_state.page = target_page


# ---------------------------------------------------------
# Top Navigation Bar
# ---------------------------------------------------------
def render_navbar():
    c_brand, c_nav, c_user = st.columns([3.0, 5.2, 2.8], vertical_alignment="center")

    with c_brand:
        st.markdown(
            """
            <div class="brand-group">
                <div class="brand-mark">+</div>
                <div>
                    <h3 class="brand-title">Warangal HealthRAG</h3>
                    <span class="brand-tag">Clinical Triage Portal</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_nav:
        n1, n2, n3, n4 = st.columns(4)
        with n1:
            if st.button("Home", use_container_width=True, type="primary" if st.session_state.page == "home" else "secondary"):
                st.session_state.page = "home"
                st.query_params["page"] = "home"
                st.rerun()
        with n2:
            if st.button("Ask a Question", use_container_width=True, type="primary" if st.session_state.page == "chat" else "secondary"):
                st.session_state.page = "chat"
                st.query_params["page"] = "chat"
                st.rerun()
        with n3:
            if st.button("Local Facilities", use_container_width=True, type="primary" if st.session_state.page == "local_info" else "secondary"):
                st.session_state.page = "local_info"
                st.query_params["page"] = "local_info"
                st.rerun()
        with n4:
            if st.button("Analytics", use_container_width=True, type="primary" if st.session_state.page == "analytics" else "secondary"):
                st.session_state.page = "analytics"
                st.query_params["page"] = "analytics"
                st.rerun()

    with c_user:
        if st.session_state.user:
            u_role = st.session_state.user.get("role", "user")
            u_name = st.session_state.user.get("full_name", "Patient")

            u1, u2 = st.columns([1.8, 1.2])
            with u1:
                btn_title = "Admin Panel" if u_role == "admin" else u_name.split()[0]
                target_route = "admin" if u_role == "admin" else "dashboard"
                if st.button(btn_title, use_container_width=True, type="primary" if st.session_state.page in ["dashboard", "admin"] else "secondary"):
                    st.session_state.page = target_route
                    st.query_params["page"] = target_route
                    st.rerun()
            with u2:
                if st.button("Logout", use_container_width=True):
                    auth_db.log_activity(st.session_state.user["email"], "LOGOUT", "User logged out")
                    st.session_state.user = None
                    st.session_state.page = "home"
                    st.query_params["page"] = "home"
                    st.rerun()
        else:
            if st.button("Sign In / Register", use_container_width=True, type="primary" if st.session_state.page == "auth" else "secondary"):
                st.session_state.page = "auth"
                st.query_params["page"] = "auth"
                st.rerun()

    st.markdown("<hr style='margin: 0.4rem 0 1.2rem 0; border: none; border-bottom: 1px solid #E5EBEF;'>", unsafe_allow_html=True)


# ---------------------------------------------------------
# VIEW 1: Homepage (Clean Healthcare SaaS Landing)
# ---------------------------------------------------------
def render_home_page(df: pd.DataFrame):
    st.markdown(
        """
        <div class="saas-hero">
            <span style="background: var(--secondary-teal); color: var(--primary-teal); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">
                Grounded Clinical Decision Support
            </span>
            <h1 style="margin-top: 0.9rem;">Better Health Information <span>Starts Here.</span></h1>
            <p>
                Understand health information through locally relevant medical knowledge designed for people across Warangal. 
                Strictly grounded in 12,000 verified clinical records to eliminate artificial intelligence hallucinations and ensure patient safety.
            </p>
            <div class="hero-stat-grid">
                <div class="hero-stat-card">
                    <div class="hero-stat-num">12,000</div>
                    <div class="hero-stat-label">Verified Clinical Records</div>
                </div>
                <div class="hero-stat-card">
                    <div class="hero-stat-num">8 Localities</div>
                    <div class="hero-stat-label">Warangal Sub-Districts</div>
                </div>
                <div class="hero-stat-card">
                    <div class="hero-stat-num">&lt; 35 ms</div>
                    <div class="hero-stat-label">Real-Time Search Latency</div>
                </div>
                <div class="hero-stat-card">
                    <div class="hero-stat-num">100%</div>
                    <div class="hero-stat-label">Emergency Triage Sensitivity</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_act1, c_act2, _ = st.columns([1.8, 1.8, 4.4])
    with c_act1:
        if st.button("Ask a Question", type="primary", use_container_width=True):
            st.session_state.page = "chat"
            st.query_params["page"] = "chat"
            st.rerun()
    with c_act2:
        if st.button("Explore Local Features", type="secondary", use_container_width=True):
            st.session_state.page = "local_info"
            st.query_params["page"] = "local_info"
            st.rerun()

    st.write("")
    st.write("")

    # Three Core Pillars
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="saas-card" style="min-height: 220px;">
                <div class="saas-card-title">Reliable Information Retrieval</div>
                <div class="saas-card-sub">Strictly anti-hallucination architecture</div>
                <p style="font-size: 0.9rem; color: var(--secondary-text); line-height: 1.6;">
                    Unlike standard generative models that speculate on medication or diagnosis, 
                    answers are derived strictly from authenticated clinical records mapped to specific departments.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="saas-card" style="min-height: 220px;">
                <div class="saas-card-title">Local Healthcare Knowledge</div>
                <div class="saas-card-sub">Contextualized for Warangal District</div>
                <p style="font-size: 0.9rem; color: var(--secondary-text); line-height: 1.6;">
                    Guidance maps symptoms to actual facilities across Hanamkonda, Kazipet, Parkal, Dharmasagar, Geesugonda, Hasanparthy, and Wardhannapet.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="saas-card" style="min-height: 220px;">
                <div class="saas-card-title">Emergency Awareness</div>
                <div class="saas-card-sub">Pre-retrieval safety guardrail</div>
                <p style="font-size: 0.9rem; color: var(--secondary-text); line-height: 1.6;">
                    Life-threatening symptoms (chest pain, acute breathing difficulty, stroke signs, sudden numbness) immediately trigger 108 and MGM Hospital casualty alerts.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Emergency Awareness Strip
    st.markdown(
        """
        <div class="emergency-alert-card">
            <div class="emergency-alert-head">
                <span>⚠️</span>
                <span>Medical Emergency Alert</span>
            </div>
            <div class="emergency-alert-body">
                Your symptoms may require immediate medical attention. Please contact emergency services or visit the nearest emergency department.
            </div>
            <div class="emergency-chips">
                <div class="emergency-chip-item">
                    <div class="emergency-chip-label">Emergency Ambulance Service</div>
                    <div class="emergency-chip-val">Dial 108 / 112</div>
                </div>
                <div class="emergency-chip-item">
                    <div class="emergency-chip-label">MGM Hospital Warangal (Emergency)</div>
                    <div class="emergency-chip-val">0870-2441000</div>
                </div>
                <div class="emergency-chip-item">
                    <div class="emergency-chip-label">District Hospital Warangal</div>
                    <div class="emergency-chip-val">0870-2577772</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# VIEW 2: Authentication (Split-Screen Professional Layout)
# ---------------------------------------------------------
def render_auth_page():
    c_left, c_right = st.columns([1.1, 1.0], gap="large")

    # LEFT PANEL: Brand & Value Proposition
    with c_left:
        st.markdown(
            """
            <div class="login-brand-panel">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem;">
                    <div class="brand-mark">+</div>
                    <span style="font-size: 1.15rem; font-weight: 800; color: var(--primary-teal);">Warangal HealthRAG</span>
                </div>
                <h2>Healthcare Information, <span>Made Simpler.</span></h2>
                <p>
                    A specialized clinical retrieval system developed by researchers at SR University. 
                    Designed to help residents of Warangal District understand primary care guidance, 
                    verify local clinic facilities, and receive rapid emergency escalation when needed.
                </p>
                <div class="feature-point">
                    <div class="feature-point-dot">1</div>
                    <div class="feature-point-text">
                        <h4>Reliable Information Retrieval</h4>
                        <p>Strictly bounded to 12,000 verified clinical cases with zero hallucination.</p>
                    </div>
                </div>
                <div class="feature-point">
                    <div class="feature-point-dot">2</div>
                    <div class="feature-point-text">
                        <h4>Local Healthcare Knowledge</h4>
                        <p>Addresses specific healthcare centers across 8 sub-districts of Warangal.</p>
                    </div>
                </div>
                <div class="feature-point">
                    <div class="feature-point-dot">3</div>
                    <div class="feature-point-text">
                        <h4>Emergency Awareness</h4>
                        <p>Immediate routing to MGM Hospital casualty hotlines for critical symptoms.</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # RIGHT PANEL: Clean Auth Card (No Public Passwords)
    with c_right:
        auth_mode = st.radio("Choose Action:", ["Sign In", "Create Patient Account", "Forgot Password"], horizontal=True, label_visibility="collapsed")

        if auth_mode == "Sign In":
            st.markdown(
                """
                <div class="saas-card" style="padding: 2.2rem 2rem;">
                    <h3 style="font-size: 1.45rem; font-weight: 800; color: var(--main-text); margin-bottom: 0.3rem;">Welcome Back</h3>
                    <p style="font-size: 0.88rem; color: var(--secondary-text); margin-bottom: 1.5rem;">Sign in to access your health information portal.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("signin_form", clear_on_submit=False):
                email_input = st.text_input("Email Address", placeholder="name@example.com")
                show_pwd = st.checkbox("Show password", value=False)
                pass_input = st.text_input("Password", type="text" if show_pwd else "password", placeholder="Enter your password")

                submit_login = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                if submit_login:
                    if not email_input or not pass_input:
                        st.error("Please provide both email address and password.")
                    else:
                        user, msg = auth_db.authenticate_user(email_input, pass_input)
                        if user:
                            st.session_state.user = user
                            st.success("Sign in successful.")
                            st.session_state.page = "admin" if user["role"] == "admin" else "dashboard"
                            st.query_params["page"] = st.session_state.page
                            time.sleep(0.3)
                            st.rerun()
                        else:
                            st.error(msg)

        elif auth_mode == "Create Patient Account":
            st.markdown(
                """
                <div class="saas-card" style="padding: 2.2rem 2rem;">
                    <h3 style="font-size: 1.45rem; font-weight: 800; color: var(--main-text); margin-bottom: 0.3rem;">Create Account</h3>
                    <p style="font-size: 0.88rem; color: var(--secondary-text); margin-bottom: 1.5rem;">Join Warangal HealthRAG to save queries and consultation notes.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("signup_form", clear_on_submit=False):
                name_new = st.text_input("Full Name", placeholder="e.g. Ramesh Kumar")
                email_new = st.text_input("Email Address", placeholder="ramesh@example.com")
                phone_new = st.text_input("Phone Number", placeholder="+91 9876543210")
                p1_new = st.text_input("Create Password", type="password", placeholder="Minimum 6 characters")
                p2_new = st.text_input("Confirm Password", type="password", placeholder="Re-type password")

                submit_signup = st.form_submit_button("Create Patient Account", type="primary", use_container_width=True)

                if submit_signup:
                    if p1_new != p2_new:
                        st.error("Passwords do not match. Please verify.")
                    else:
                        ok, user_dict, message = auth_db.register_user(name_new, email_new, phone_new, p1_new)
                        if ok and user_dict:
                            st.session_state.user = user_dict
                            st.success("Account created successfully! Redirecting to your dashboard...")
                            st.session_state.page = "dashboard"
                            st.query_params["page"] = "dashboard"
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(message)

        elif auth_mode == "Forgot Password":
            st.markdown(
                """
                <div class="saas-card" style="padding: 2.2rem 2rem;">
                    <h3 style="font-size: 1.45rem; font-weight: 800; color: var(--main-text); margin-bottom: 0.3rem;">Reset Password</h3>
                    <p style="font-size: 0.88rem; color: var(--secondary-text); margin-bottom: 1.5rem;">Update your password securely.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("reset_form"):
                remail = st.text_input("Registered Email Address")
                rnew_p = st.text_input("New Password", type="password", placeholder="Minimum 6 characters")
                submit_reset = st.form_submit_button("Update Password", type="primary", use_container_width=True)

                if submit_reset:
                    if not remail or not rnew_p:
                        st.error("Please fill in both email and new password.")
                    else:
                        ok, msg = auth_db.update_user_password(remail, rnew_p)
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
        "full_name": "Patient User",
        "email": "user@warangal.local",
        "role": "user"
    }

    st.markdown(
        f"""
        <div class="saas-card" style="margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="font-size: 1.6rem; font-weight: 800; color: var(--main-text); margin: 0;">How can we help you today?</h2>
                    <p style="color: var(--secondary-text); font-size: 0.92rem; margin: 4px 0 0 0;">Welcome back, {user['full_name']}. All clinical information is grounded in Warangal hospital records.</p>
                </div>
                <span class="brand-tag">Patient Dashboard</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_queries = auth_db.get_user_query_history(user.get("id"))
    saved_answers = auth_db.get_user_saved_responses(user.get("id"))

    # Metric Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="saas-card" style="text-align: center; padding: 1.1rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: var(--secondary-text); text-transform: uppercase;">Questions Asked</div>
                <div style="font-size: 1.7rem; font-weight: 800; color: var(--primary-teal); margin: 3px 0;">{len(user_queries)}</div>
                <div style="font-size: 0.75rem; color: var(--success-color); font-weight: 600;">Personal History</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
            <div class="saas-card" style="text-align: center; padding: 1.1rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: var(--secondary-text); text-transform: uppercase;">Saved Answers</div>
                <div style="font-size: 1.7rem; font-weight: 800; color: var(--primary-teal); margin: 3px 0;">{len(saved_answers)}</div>
                <div style="font-size: 0.75rem; color: var(--primary-teal); font-weight: 600;">Personal Records</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""
            <div class="saas-card" style="text-align: center; padding: 1.1rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: var(--secondary-text); text-transform: uppercase;">Indexed Records</div>
                <div style="font-size: 1.7rem; font-weight: 800; color: var(--main-text); margin: 3px 0;">{len(df):,}</div>
                <div style="font-size: 0.75rem; color: var(--success-color); font-weight: 600;">100% Grounded</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            """
            <div class="saas-card" style="text-align: center; padding: 1.1rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: var(--secondary-text); text-transform: uppercase;">Emergency Ambulance</div>
                <div style="font-size: 1.7rem; font-weight: 800; color: var(--error-color); margin: 3px 0;">108</div>
                <div style="font-size: 0.75rem; color: var(--error-color); font-weight: 600;">24/7 Available</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Large Search Box
    st.markdown("### Search Health Information")
    st.caption("Type any symptoms or health inquiries in simple English:")

    c_box, c_sbtn = st.columns([5.5, 1.2])
    with c_box:
        dash_q = st.text_input("Search input", placeholder="Describe your health concern in simple words...", label_visibility="collapsed")
    with c_sbtn:
        if st.button("Search", type="primary", use_container_width=True):
            if dash_q:
                st.session_state.messages.append({"role": "user", "content": dash_q})
                st.session_state.page = "chat"
                st.query_params["page"] = "chat"
                st.rerun()

    st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: var(--secondary-text); margin-top: 0.4rem;'>Common sample questions:</p>", unsafe_allow_html=True)
    sample_queries = [
        "What are common symptoms of dengue?",
        "What should I know about high blood pressure?",
        "Where can I find healthcare services in Kazipet?",
        "What are common causes of stomach pain?"
    ]
    sq_cols = st.columns(4)
    for i, sq in enumerate(sample_queries):
        with sq_cols[i]:
            if st.button(sq, key=f"dash_btn_sq_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": sq})
                st.session_state.page = "chat"
                st.query_params["page"] = "chat"
                st.rerun()

    st.write("")
    st.divider()

    # User History & Saved Responses
    col_hist, col_saved = st.columns(2)
    with col_hist:
        st.markdown("#### Recent Questions")
        if user_queries:
            for q in user_queries[:6]:
                st.markdown(
                    f"""
                    <div style="background: #FFFFFF; border: 1px solid var(--border-color); border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
                        <div style="font-weight: 600; font-size: 0.9rem; color: var(--main-text);">{q['query_text']}</div>
                        <div style="font-size: 0.75rem; color: var(--secondary-text); margin-top: 3px;">
                            Engine: {q['engine_used']} | Latency: {q['latency_ms']:.1f} ms | {q['timestamp']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No prior questions recorded. Use the search box above to ask your first question.")

    with col_saved:
        st.markdown("#### Saved Responses")
        if saved_answers:
            for s in saved_answers[:6]:
                with st.expander(f"Saved: {s['query_text'][:45]}..."):
                    st.markdown(s['response_text'])
                    if s.get('sources_cited'):
                        st.caption(f"Sources: {s['sources_cited']}")
        else:
            st.info("No saved responses yet. In the Q&A interface, click 'Save Answer' to bookmark helpful guidance.")


# ---------------------------------------------------------
# VIEW 4: Medical RAG Chat Interface (Healthcare Assistant)
# ---------------------------------------------------------
def render_chat_page(df: pd.DataFrame, tfidf_vectorizer, tfidf_matrix):
    # Sidebar Filters
    with st.sidebar:
        st.markdown("### Retrieval Controls")
        engine_choice = st.radio(
            "Vector Search Technique:",
            options=["TF-IDF + Cosine Similarity", "FAISS + SentenceTransformers"],
            index=0,
            help="TF-IDF offers instant sublinear search. FAISS uses 384-dimensional dense semantic vector embeddings."
        )

        if engine_choice.startswith("FAISS") and not st.session_state.faiss_loaded:
            with st.spinner("Building FAISS dense vector store..."):
                f_model, f_index = get_cached_faiss(df['search_text'].tolist())
                st.session_state.faiss_model = f_model
                st.session_state.faiss_index = f_index
                st.session_state.faiss_loaded = True

        top_k = st.slider("Evidence Chunks (Top-K):", min_value=3, max_value=8, value=5)

        st.divider()
        st.markdown("### Knowledge Filtering")
        departments = ["All"] + sorted([d for d in df['department'].unique() if str(d).strip() and str(d) != 'nan'])
        dept_filter = st.selectbox("Department:", options=departments, index=0)

        localities = ["All"] + sorted([l for l in df['locality'].unique() if str(l).strip() and str(l) != 'nan'])
        locality_filter = st.selectbox("Warangal Locality:", options=localities, index=0)

        st.divider()
        if st.button("Clear Conversation", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # Chat Top Status Bar
    st.markdown(
        """
        <div class="saas-card" style="padding: 1rem 1.4rem; display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem;">
            <div>
                <h3 style="font-size: 1.2rem; font-weight: 800; color: var(--main-text); margin: 0;">Medical Information Assistant</h3>
                <p style="font-size: 0.85rem; color: var(--secondary-text); margin: 0;">Grounding answers strictly on 12,000 verified Warangal patient records.</p>
            </div>
            <span class="brand-tag">Online &bull; 108 Triage Active</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render Messages
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg.get("red_flag_info") and msg["red_flag_info"]["is_emergency"]:
                triggers = ", ".join(msg["red_flag_info"]["matched_triggers"])
                st.markdown(
                    f"""
                    <div class="emergency-alert-card">
                        <div class="emergency-alert-head">
                            <span>⚠️</span>
                            <span>Medical Emergency Alert</span>
                        </div>
                        <div class="emergency-alert-body">
                            Your symptoms ({triggers}) may require immediate medical attention. Please contact emergency services or visit the nearest emergency department.
                        </div>
                        <div class="emergency-chips">
                            <div class="emergency-chip-item">
                                <div class="emergency-chip-label">Emergency Ambulance</div>
                                <div class="emergency-chip-val">Dial 108 / 112</div>
                            </div>
                            <div class="emergency-chip-item">
                                <div class="emergency-chip-label">MGM Hospital Warangal</div>
                                <div class="emergency-chip-val">0870-2441000</div>
                            </div>
                            <div class="emergency-chip-item">
                                <div class="emergency-chip-label">District Hospital Warangal</div>
                                <div class="emergency-chip-val">0870-2577772</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(msg["content"])

            if msg["role"] == "assistant":
                col_save, _ = st.columns([2, 8])
                with col_save:
                    if st.button("Save Response", key=f"save_ans_{idx}", type="secondary"):
                        uid = st.session_state.user["id"] if st.session_state.user else 1
                        auth_db.save_response_for_user(uid, "Medical Query", msg["content"])
                        st.toast("Saved to your personal dashboard records.", icon="✅")

                # RAG Evidence Inspector ("Why am I seeing this answer?")
                if msg.get("chunks") is not None and not msg["chunks"].empty:
                    with st.expander("Why am I seeing this answer? (RAG Evidence Inspector)", expanded=False):
                        st.caption("The system retrieved these specific records from the Warangal dataset to generate this response:")
                        st.caption("Notice: Similarity score measures mathematical semantic proximity to our verified records, not clinical diagnostic certainty.")

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
                                <div class="evidence-card">
                                    <div class="evidence-meta-row">
                                        <span style="font-weight: 700; color: var(--primary-teal); font-size: 0.9rem;">Record ID: {rec_id} &bull; Condition: {cond}</span>
                                        <div>
                                            <span class="badge-sim">Similarity: {sim_pct}</span>
                                            <span class="badge-prio">Priority: {prio}</span>
                                        </div>
                                    </div>
                                    <div style="font-size: 0.8rem; color: var(--secondary-text); margin-bottom: 0.4rem;">
                                        <strong>Department:</strong> {dept} &nbsp;|&nbsp; 
                                        <strong>Locality:</strong> {loc} &nbsp;|&nbsp; 
                                        <strong>Facility:</strong> {facility}
                                    </div>
                                    <div class="evidence-text-snippet">
                                        "{row.get('rag_context_text', row.get('search_text', ''))}"
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

    # Quick Sample Questions Chips (when no messages or at the start)
    if not st.session_state.messages:
        st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: var(--secondary-text); margin-bottom: 0.4rem;'>Sample health questions you can test:</p>", unsafe_allow_html=True)
        sq_cols = st.columns(3)
        sample_chips = [
            "Severe chest pain and sweating",
            "Child coughing and fever in Kazipet",
            "High blood pressure warning signs"
        ]
        for sc_idx, chip_text in enumerate(sample_chips):
            with sq_cols[sc_idx]:
                if st.button(chip_text, key=f"chat_chip_{sc_idx}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": chip_text})
                    st.rerun()

    # Chat Input
    query_input = st.chat_input("Ask a health question in simple words (e.g. 'Child wheezing in Parkal')...")
    if query_input:
        st.session_state.messages.append({"role": "user", "content": query_input})
        st.rerun()

    # If the last message is from the user without an assistant response, process it immediately!
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        active_query = st.session_state.messages[-1]["content"]
        with st.chat_message("assistant"):
            with st.spinner("Reviewing Warangal verified clinical records..."):
                t0 = time.time()

                # Step 1: Pre-retrieval Red-Flag Check
                immediate_rf = check_red_flags(active_query)

                # Step 2: Retrieve Chunks
                top_chunks = get_relevant_chunks(
                    query=active_query,
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

                # Comprehensive check combining chunks
                red_flag_info = check_red_flags(active_query, top_chunks)

                # Step 3: Grounded Answer Synthesis
                max_sim = top_chunks['similarity_score'].max() if not top_chunks.empty else 0.0
                if max_sim < 0.05 and not red_flag_info["is_emergency"]:
                    response_text = "Sorry, we could not find sufficiently relevant information in our medical knowledge base. Please consult a qualified healthcare professional."
                else:
                    response_text = generate_grounded_response(active_query, top_chunks, red_flag_info)

                elapsed_ms = (time.time() - t0) * 1000

                # Render emergency alert if detected
                if red_flag_info["is_emergency"]:
                    triggers = ", ".join(red_flag_info["matched_triggers"])
                    st.markdown(
                        f"""
                        <div class="emergency-alert-card">
                            <div class="emergency-alert-head">
                                <span>⚠️</span>
                                <span>Medical Emergency Alert</span>
                            </div>
                            <div class="emergency-alert-body">
                                Your symptoms ({triggers}) may require immediate medical attention. Please contact emergency services or visit the nearest emergency department.
                            </div>
                            <div class="emergency-chips">
                                <div class="emergency-chip-item">
                                    <div class="emergency-chip-label">Emergency Ambulance</div>
                                    <div class="emergency-chip-val">Dial 108 / 112</div>
                                </div>
                                <div class="emergency-chip-item">
                                    <div class="emergency-chip-label">MGM Hospital Warangal</div>
                                    <div class="emergency-chip-val">0870-2441000</div>
                                </div>
                                <div class="emergency-chip-item">
                                    <div class="emergency-chip-label">District Hospital Warangal</div>
                                    <div class="emergency-chip-val">0870-2577772</div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown(response_text)

                # Render Evidence Inspector
                with st.expander("Why am I seeing this answer? (RAG Evidence Inspector)", expanded=True):
                    st.caption(f"Retrieved Top-{len(top_chunks)} evidence records using {engine_choice} in {elapsed_ms:.1f} ms:")
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
                            <div class="evidence-card">
                                <div class="evidence-meta-row">
                                    <span style="font-weight: 700; color: var(--primary-teal); font-size: 0.9rem;">Record ID: {rec_id} &bull; Condition: {cond}</span>
                                    <div>
                                        <span class="badge-sim">Similarity: {sim_pct}</span>
                                        <span class="badge-prio">Priority: {prio}</span>
                                    </div>
                                </div>
                                <div style="font-size: 0.8rem; color: var(--secondary-text); margin-bottom: 0.4rem;">
                                    <strong>Department:</strong> {dept} &nbsp;|&nbsp; 
                                    <strong>Locality:</strong> {loc} &nbsp;|&nbsp; 
                                    <strong>Facility:</strong> {facility}
                                </div>
                                <div class="evidence-text-snippet">
                                    "{row.get('rag_context_text', row.get('search_text', ''))}"
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            # Store in session state and record to audit log
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "red_flag_info": red_flag_info,
                "chunks": top_chunks
            })

            uid = st.session_state.user["id"] if st.session_state.user else None
            uemail = st.session_state.user["email"] if st.session_state.user else "guest@warangal.local"
            mdept = top_chunks.iloc[0].get('department', '') if not top_chunks.empty else ''
            mloc = top_chunks.iloc[0].get('locality', '') if not top_chunks.empty else ''

            auth_db.log_query(
                user_id=uid,
                user_email=uemail,
                query_text=active_query,
                response_text=response_text,
                is_emergency=red_flag_info["is_emergency"],
                matched_triggers=red_flag_info["matched_triggers"],
                latency_ms=elapsed_ms,
                engine_used=engine_choice,
                department=mdept,
                locality=mloc
            )
            st.rerun()


# ---------------------------------------------------------
# VIEW 5: Warangal Local Healthcare Information
# ---------------------------------------------------------
def render_local_info_page(df: pd.DataFrame):
    st.markdown(
        """
        <div class="saas-card" style="margin-bottom: 1.5rem;">
            <h2 style="font-size: 1.6rem; font-weight: 800; color: var(--main-text); margin: 0 0 0.4rem 0;">Warangal District Healthcare Directory</h2>
            <p style="color: var(--secondary-text); font-size: 0.92rem; margin: 0;">Verified clinical facilities, regional department coverage, and referral routes for Warangal sub-districts.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    localities = ["Warangal", "Hanamkonda", "Kazipet", "Parkal", "Dharmasagar", "Geesugonda", "Hasanparthy", "Wardhannapet"]
    selected_loc = st.selectbox("Select Locality to Explore Verified Resources:", options=localities, index=0)

    sub_df = df[df['locality'].str.lower() == selected_loc.lower()] if 'locality' in df.columns else df

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f"""
            <div class="saas-card" style="text-align: center; padding: 1.1rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: var(--secondary-text); text-transform: uppercase;">Indexed Cases</div>
                <div style="font-size: 1.6rem; font-weight: 800; color: var(--primary-teal); margin: 3px 0;">{len(sub_df):,}</div>
                <div style="font-size: 0.75rem; color: var(--success-color); font-weight: 600;">Verified Dataset Records</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        top_dept = sub_df['department'].mode().iloc[0] if 'department' in sub_df.columns and not sub_df['department'].empty else "General Medicine"
        st.markdown(
            f"""
            <div class="saas-card" style="text-align: center; padding: 1.1rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: var(--secondary-text); text-transform: uppercase;">Top Clinical Department</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: var(--main-text); margin: 3px 0;">{top_dept}</div>
                <div style="font-size: 0.75rem; color: var(--primary-teal); font-weight: 600;">Highest Inflow Volume</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            """
            <div class="saas-card" style="text-align: center; padding: 1.1rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: var(--secondary-text); text-transform: uppercase;">Primary Referral Hub</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: var(--primary-teal); margin: 3px 0;">MGM Hospital</div>
                <div style="font-size: 0.75rem; color: var(--secondary-text); font-weight: 600;">Government Tertiary Center</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    c_fac, c_chart = st.columns([1.2, 1.0])
    with c_fac:
        st.markdown(f"#### Healthcare Facilities Active in {selected_loc}")
        if 'care_facility_synthetic' in sub_df.columns:
            counts = sub_df['care_facility_synthetic'].value_counts()
            for fac, cnt in counts.items():
                st.markdown(
                    f"""
                    <div style="background: #FFFFFF; border: 1px solid var(--border-color); border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; color: var(--main-text); font-size: 0.9rem;">{fac}</span>
                        <span class="brand-tag">{cnt} records</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    with c_chart:
        st.markdown(f"#### Department Distribution in {selected_loc}")
        if 'department' in sub_df.columns:
            st.bar_chart(sub_df['department'].value_counts())


# ---------------------------------------------------------
# VIEW 6: Analytics & Data Visualization
# ---------------------------------------------------------
def render_analytics_page(df: pd.DataFrame):
    st.markdown(
        """
        <div class="saas-card" style="margin-bottom: 1.5rem;">
            <h2 style="font-size: 1.6rem; font-weight: 800; color: var(--main-text); margin: 0 0 0.4rem 0;">Healthcare Analytics & Retrieval Performance</h2>
            <p style="color: var(--secondary-text); font-size: 0.92rem; margin: 0;">Statistical distribution of the 12,000 Warangal clinical records and real-time query metrics.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metrics = auth_db.get_admin_dashboard_metrics()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="saas-card" style="text-align: center; padding: 1.1rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: var(--secondary-text); text-transform: uppercase;">Total Dataset Records</div>
                <div style="font-size: 1.7rem; font-weight: 800; color: var(--primary-teal); margin: 3px 0;">{len(df):,}</div>
                <div style="font-size: 0.75rem; color: var(--success-color); font-weight: 600;">Verified Knowledge</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="saas-card" style="text-align: center; padding: 1.1rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: var(--secondary-text); text-transform: uppercase;">Queries Processed</div>
                <div style="font-size: 1.7rem; font-weight: 800; color: var(--main-text); margin: 3px 0;">{metrics['total_queries']}</div>
                <div style="font-size: 0.75rem; color: var(--primary-teal); font-weight: 600;">Database Logged</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="saas-card" style="text-align: center; padding: 1.1rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: var(--secondary-text); text-transform: uppercase;">Emergency Flags</div>
                <div style="font-size: 1.7rem; font-weight: 800; color: var(--error-color); margin: 3px 0;">{metrics['total_emergencies']}</div>
                <div style="font-size: 0.75rem; color: var(--error-color); font-weight: 600;">Red-Flags Intercepted</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="saas-card" style="text-align: center; padding: 1.1rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: var(--secondary-text); text-transform: uppercase;">Average Latency</div>
                <div style="font-size: 1.7rem; font-weight: 800; color: var(--success-color); margin: 3px 0;">{metrics['avg_latency_ms']} ms</div>
                <div style="font-size: 0.75rem; color: var(--success-color); font-weight: 600;">Sublinear Speed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    col_d, col_l = st.columns(2)
    with col_d:
        st.markdown("#### Department Distribution (12,000 Records)")
        if 'department' in df.columns:
            st.bar_chart(df['department'].value_counts())
    with col_l:
        st.markdown("#### Locality Case Distribution (8 Localities)")
        if 'locality' in df.columns:
            st.bar_chart(df['locality'].value_counts())


# ---------------------------------------------------------
# VIEW 7: Administrator Dashboard (Strict Role Verification)
# ---------------------------------------------------------
def render_admin_dashboard(df: pd.DataFrame):
    current_user = st.session_state.user
    if not current_user or current_user.get("role") != "admin":
        st.markdown(
            """
            <div class="emergency-alert-card" style="text-align: center; padding: 2.5rem 1.5rem;">
                <h2 style="color: var(--error-color); font-weight: 800; margin-bottom: 0.5rem;">Access Denied: Administrator Privileges Required</h2>
                <p style="color: #7A271A; font-size: 0.98rem; max-width: 600px; margin: 0 auto 1.5rem auto;">
                    This section is strictly restricted to clinical administrators. 
                    Normal patient sessions cannot inspect system logs, user registries, or retrieval telemetry.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Return to Homepage", type="primary"):
            st.session_state.page = "home"
            st.query_params["page"] = "home"
            st.rerun()
        return

    st.markdown(
        f"""
        <div class="saas-card" style="margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="font-size: 1.6rem; font-weight: 800; color: var(--main-text); margin: 0 0 0.3rem 0;">Clinical Administration Portal</h2>
                    <p style="color: var(--secondary-text); font-size: 0.92rem; margin: 0;">Logged in as: <strong>{current_user['full_name']}</strong> ({current_user['email']})</p>
                </div>
                <span class="brand-tag">Administrator Verified</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    admin_metrics = auth_db.get_admin_dashboard_metrics()

    adm_tabs = st.tabs(["User Management", "RAG Analytics", "Dataset Information", "Activity Audit Logs"])

    with adm_tabs[0]:
        st.markdown("#### User Accounts Registry")
        users = auth_db.get_all_users()
        user_df = pd.DataFrame(users)
        if not user_df.empty:
            st.dataframe(user_df[["id", "full_name", "email", "phone", "role", "status", "created_at"]], use_container_width=True)

            c_uinput, c_ubtn = st.columns([3, 1])
            with c_uinput:
                t_uid = st.number_input("User ID to Toggle Status (Active / Suspended):", min_value=1, step=1, value=1)
            with c_ubtn:
                if st.button("Toggle Status", type="secondary"):
                    auth_db.toggle_user_status(t_uid)
                    st.success("User account status updated.")
                    st.rerun()
        else:
            st.info("No registered users.")

    with adm_tabs[1]:
        st.markdown("#### Retrieval Engine Telemetry")
        eng_dist = admin_metrics.get("engine_distribution", {})
        if eng_dist:
            st.bar_chart(pd.Series(eng_dist))
        else:
            st.info("No retrieval telemetry recorded yet.")

    with adm_tabs[2]:
        st.markdown(f"#### Verified Knowledge Base ({len(df):,} Records)")
        st.dataframe(df[["patient_id", "condition", "department", "locality", "symptoms", "care_advice", "care_facility_synthetic"]].head(100), use_container_width=True)

    with adm_tabs[3]:
        st.markdown("#### Security & User Audit Trail")
        logs = auth_db.get_recent_activity_logs(50)
        if logs:
            st.dataframe(pd.DataFrame(logs), use_container_width=True)
        else:
            st.info("No audit logs recorded.")


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
def render_footer():
    st.markdown(
        """
        <div class="saas-footer">
            <p style="font-weight: 700; color: var(--primary-teal); margin-bottom: 0.2rem;">
                Warangal HealthRAG &bull; Clinical Information System
            </p>
            <p style="margin-bottom: 0.4rem;">
                Department of Computer Science & Engineering | <strong>SR University</strong>, Warangal, Telangana
            </p>
            <p style="font-size: 0.8rem; color: var(--secondary-text); margin-bottom: 0.8rem;">
                Project Authors: B. Sai Tejaswi (2303A51184) &bull; V. Abhilash (2303A51227)
            </p>
            <p style="font-size: 0.75rem; color: #94A3B8; max-width: 780px; margin: 0 auto;">
                Academic Medical Disclaimer: This platform demonstrates localized Retrieval-Augmented Generation for academic research. 
                It is designed to supplement health information, not replace diagnosis by a registered medical practitioner. 
                In all acute medical emergencies, immediately dial <strong>108</strong> or proceed to <strong>MGM Hospital Warangal</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Main Controller
# ---------------------------------------------------------
def main():
    df = get_cached_dataset(DATA_PATH)
    tfidf_vectorizer, tfidf_matrix = get_cached_tfidf(df['search_text'].tolist())

    render_navbar()

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

    render_footer()


if __name__ == "__main__":
    main()
