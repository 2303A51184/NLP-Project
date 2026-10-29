import os
import time
import numpy as np
import pandas as pd
import streamlit as st

# Import decoupled, modular RAG logic from backend.py
from backend import (
    load_medical_dataset,
    init_tfidf_engine,
    init_faiss_engine,
    check_red_flags,
    get_relevant_chunks,
    generate_grounded_response,
    WARANGAL_EMERGENCY_CONTACTS
)

# Page Configuration
st.set_page_config(
    page_title="RAG Medical Info System | Warangal Patients",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (CSS)
st.markdown(
    """
    <style>
    /* Theme Colors & Typography */
    :root {
        --primary-teal: #005f73;
        --secondary-teal: #0a9396;
        --accent-mint: #94d2bd;
        --bg-light: #f8fafc;
        --card-border: #e2e8f0;
        --text-dark: #1e293b;
        --emergency-red: #dc2626;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }

    /* Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #005f73 0%, #0a9396 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 95, 115, 0.15);
    }
    .header-banner h1 {
        color: white !important;
        font-size: 1.95rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        padding-bottom: 0.3rem;
    }
    .header-banner p {
        color: #e0f2fe !important;
        font-size: 1.0rem !important;
        margin: 0 !important;
    }

    /* Metric Cards */
    .metric-card {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #005f73;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.4rem;
        color: #005f73;
        font-weight: 700;
    }

    /* Emergency Alert Card */
    .emergency-card {
        background-color: #fef2f2;
        border: 2px solid #ef4444;
        border-radius: 10px;
        padding: 1.25rem;
        margin: 1rem 0;
        color: #991b1b;
        box-shadow: 0 4px 6px -1px rgba(220, 38, 38, 0.1);
    }
    .emergency-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #dc2626;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.5rem;
    }

    /* Grounded Chunk Card in Inspector */
    .chunk-card {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    .chunk-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 0.4rem;
        margin-bottom: 0.5rem;
    }
    .badge-similarity {
        background-color: #e0f2fe;
        color: #0369a1;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .badge-priority-high {
        background-color: #fee2e2;
        color: #b91c1c;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    .badge-priority-med {
        background-color: #fef3c7;
        color: #b45309;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
    }

    /* Source Citation Tag */
    .citation-tag {
        display: inline-block;
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        color: #334155;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 0.82rem;
        margin-right: 6px;
        margin-top: 4px;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Streamlit Caching Wrappers for Backend Functions
# ---------------------------------------------------------
DATA_PATH = "cleaned_RAG_Warangal_medical_dataset.csv"

@st.cache_data(show_spinner="Loading Warangal Medical Knowledge Dataset...")
def get_cached_dataset(file_path: str = DATA_PATH) -> pd.DataFrame:
    return load_medical_dataset(file_path)

@st.cache_resource(show_spinner="Initializing TF-IDF Search Engine...")
def get_cached_tfidf(search_texts: list):
    return init_tfidf_engine(search_texts)

@st.cache_resource(show_spinner="Loading SentenceTransformers & Building FAISS Index...")
def get_cached_faiss(search_texts: list):
    return init_faiss_engine(search_texts)


# ---------------------------------------------------------
# Main Application Layout & Session State
# ---------------------------------------------------------
def main():
    # 1. Load dataset & TF-IDF matrix
    df = get_cached_dataset(DATA_PATH)
    tfidf_vectorizer, tfidf_matrix = get_cached_tfidf(df['search_text'].tolist())

    # 2. Session state initialization
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "faiss_loaded" not in st.session_state:
        st.session_state.faiss_loaded = False
        st.session_state.faiss_model = None
        st.session_state.faiss_index = None

    # 3. Header Banner
    st.markdown(
        """
        <div class="header-banner">
            <h1>🏥 RAG-Based Medical Information System</h1>
            <p>Localized Healthcare Guidance & Emergency Red-Flag Escalation for Warangal District Patients (Hanamkonda, Kazipet, Parkal, Dharmasagar)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # Sidebar Dashboard
    # -----------------------------------------------------
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/hospital-2.png", width=64)
        st.title("System Control & Metrics")
        st.markdown("**Warangal Medical RAG Dashboard**")
        st.divider()

        total_records = len(df)
        verified_count = len(df[df['verification_status'].str.contains("Verified", case=False, na=False)])
        high_priority_count = len(df[df['retrieval_priority'].str.lower() == "high"]) if 'retrieval_priority' in df.columns else 8146
        localities_count = df['locality'].nunique() if 'locality' in df.columns else 8

        st.subheader("📊 Dataset Statistics")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Total Records</div>
                    <div class="metric-value">{total_records:,}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">High Priority</div>
                    <div class="metric-value">{high_priority_count:,}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Verified QA</div>
                    <div class="metric-value">{verified_count:,}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Localities</div>
                    <div class="metric-value">{localities_count}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        st.subheader("⚙️ Retrieval Settings")
        retrieval_engine_choice = st.radio(
            "Select Similarity Search Engine:",
            options=["TF-IDF + Cosine Similarity", "FAISS + SentenceTransformers"],
            index=0,
            help="TF-IDF offers instant search. FAISS uses dense vector embeddings."
        )

        if retrieval_engine_choice.startswith("FAISS") and not st.session_state.faiss_loaded:
            with st.spinner("Building FAISS Vector Store..."):
                f_model, f_index = get_cached_faiss(df['search_text'].tolist())
                st.session_state.faiss_model = f_model
                st.session_state.faiss_index = f_index
                st.session_state.faiss_loaded = True

        top_k = st.slider("Top-K Knowledge Chunks:", min_value=3, max_value=10, value=5)

        st.divider()

        st.subheader("🔍 Context Filters")
        departments = ["All"] + sorted([d for d in df['department'].unique() if str(d).strip() and str(d) != 'nan'])
        dept_filter = st.selectbox("Department Filter:", options=departments, index=0)

        localities = ["All"] + sorted([l for l in df['locality'].unique() if str(l).strip() and str(l) != 'nan'])
        locality_filter = st.selectbox("Warangal Locality Filter:", options=localities, index=0)

        st.divider()

        st.subheader("💡 Sample Patient Queries")
        sample_queries = [
            "Child in Parkal having severe asthma and wheezing",
            "Skin rash and intense itching near Hanamkonda",
            "Severe chest pain and sweating in Kazipet - Emergency!",
            "Digestive issues and stomach ache after meals in Warangal",
            "High fever and persistent dry cough near Dharmasagar"
        ]

        selected_sample = None
        for q in sample_queries:
            if st.button(f"👉 {q}", key=f"btn_{q[:15]}"):
                selected_sample = q

        st.divider()

        if st.button("🧹 Clear Chat History", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # -----------------------------------------------------
    # Main Chat Area
    # -----------------------------------------------------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg.get("red_flag_info") and msg["red_flag_info"]["is_emergency"]:
                st.error(
                    f"🚨 **RED-FLAG EMERGENCY WARNING**: Critical symptoms detected ({', '.join(msg['red_flag_info']['matched_triggers'])}). "
                    f"Escalate immediately to **MGM Hospital Warangal (Hotline: 0870-2441000)** or call **108**."
                )

            if msg.get("chunks") is not None and not msg["chunks"].empty:
                with st.expander("🔍 View Grounded Knowledge Retrieval Evidence (RAG Inspector)", expanded=False):
                    st.caption(f"Retrieved Top-{len(msg['chunks'])} evidence chunks from `cleaned_RAG_Warangal_medical_dataset.csv`:")

                    for _, row in msg["chunks"].iterrows():
                        sim_pct = f"{row.get('similarity_score', 0.0) * 100:.1f}%"
                        p_priority = row.get('retrieval_priority', 'Medium')
                        p_badge_class = "badge-priority-high" if str(p_priority).lower() == "high" else "badge-priority-med"

                        st.markdown(
                            f"""
                            <div class="chunk-card">
                                <div class="chunk-header">
                                    <strong>Record ID: {row.get('patient_id', 'N/A')} | Condition: {row.get('condition', 'N/A')}</strong>
                                    <div>
                                        <span class="badge-similarity">Match Score: {sim_pct}</span>
                                        <span class="{p_badge_class}">Priority: {p_priority}</span>
                                    </div>
                                </div>
                                <div style="font-size: 0.88rem; color: #475569; margin-bottom: 0.3rem;">
                                    <strong>Department:</strong> {row.get('department', 'N/A')} | 
                                    <strong>Locality:</strong> {row.get('locality', 'N/A')} | 
                                    <strong>Care Facility:</strong> {row.get('care_facility_synthetic', 'District Hospital Warangal')}
                                </div>
                                <div style="font-size: 0.85rem; color: #334155; font-style: italic; background: #ffffff; padding: 0.5rem; border-radius: 4px; border: 1px solid #e2e8f0;">
                                    "{row.get('rag_context_text', row.get('search_text', ''))}"
                                </div>
                                <div style="font-size: 0.8rem; color: #dc2626; margin-top: 0.3rem;">
                                    <strong>Red Flag Note:</strong> {row.get('red_flag_note', 'Seek prompt care for severe symptoms.')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    prompt_input = st.chat_input("Ask a medical query or describe symptoms (e.g., 'Child coughing in Parkal')...")

    user_query = None
    if prompt_input:
        user_query = prompt_input
    elif selected_sample:
        user_query = selected_sample

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Searching Warangal Grounded Medical Database & Triaging Symptoms..."):
                start_time = time.time()

                top_chunks = get_relevant_chunks(
                    query=user_query,
                    df=df,
                    tfidf_vectorizer=tfidf_vectorizer,
                    tfidf_matrix=tfidf_matrix,
                    faiss_model=st.session_state.faiss_model,
                    faiss_index=st.session_state.faiss_index,
                    engine_type=retrieval_engine_choice,
                    dept_filter=dept_filter,
                    locality_filter=locality_filter,
                    top_k=top_k
                )

                red_flag_info = check_red_flags(user_query, top_chunks)
                response_text = generate_grounded_response(user_query, top_chunks, red_flag_info)
                elapsed = time.time() - start_time

                st.markdown(response_text)

                if red_flag_info["is_emergency"]:
                    st.error(
                        f"🚨 **RED-FLAG EMERGENCY ALERT**: Critical red-flag symptoms detected ({', '.join(red_flag_info['matched_triggers'])}). "
                        f"Visit **MGM Hospital Warangal Casualty** or call **108** immediately."
                    )

                with st.expander("🔍 View Grounded Knowledge Retrieval Evidence (RAG Inspector)", expanded=True):
                    st.caption(f"Retrieved Top-{len(top_chunks)} evidence chunks using **{retrieval_engine_choice}** (Latency: {elapsed*1000:.1f} ms):")

                    for _, row in top_chunks.iterrows():
                        sim_pct = f"{row.get('similarity_score', 0.0) * 100:.1f}%"
                        p_priority = row.get('retrieval_priority', 'Medium')
                        p_badge_class = "badge-priority-high" if str(p_priority).lower() == "high" else "badge-priority-med"

                        st.markdown(
                            f"""
                            <div class="chunk-card">
                                <div class="chunk-header">
                                    <strong>Record ID: {row.get('patient_id', 'N/A')} | Condition: {row.get('condition', 'N/A')}</strong>
                                    <div>
                                        <span class="badge-similarity">Match Score: {sim_pct}</span>
                                        <span class="{p_badge_class}">Priority: {p_priority}</span>
                                    </div>
                                </div>
                                <div style="font-size: 0.88rem; color: #475569; margin-bottom: 0.3rem;">
                                    <strong>Department:</strong> {row.get('department', 'N/A')} | 
                                    <strong>Locality:</strong> {row.get('locality', 'N/A')} | 
                                    <strong>Care Facility:</strong> {row.get('care_facility_synthetic', 'District Hospital Warangal')}
                                </div>
                                <div style="font-size: 0.85rem; color: #334155; font-style: italic; background: #ffffff; padding: 0.5rem; border-radius: 4px; border: 1px solid #e2e8f0;">
                                    "{row.get('rag_context_text', row.get('search_text', ''))}"
                                </div>
                                <div style="font-size: 0.8rem; color: #dc2626; margin-top: 0.3rem;">
                                    <strong>Red Flag Note:</strong> {row.get('red_flag_note', 'Seek prompt care for severe symptoms.')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "red_flag_info": red_flag_info,
                "chunks": top_chunks
            })


if __name__ == "__main__":
    main()
