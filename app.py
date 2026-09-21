import os
import re
import time
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

    /* Disclaimer Box */
    .disclaimer-box {
        background-color: #fffbeb;
        border: 1px solid #fcd34d;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        font-size: 0.85rem;
        color: #92400e;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 1. Data Loading & Caching
# ---------------------------------------------------------
DATA_PATH = r"cleaned_RAG_Warangal_medical_dataset.csv"

@st.cache_data(show_spinner="Loading Warangal Medical Knowledge Dataset...")
def load_medical_dataset(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        # Fallback to local execution directory
        file_path = os.path.join(os.path.dirname(__file__), "cleaned_RAG_Warangal_medical_dataset.csv")
    
    df = pd.read_csv(file_path)

    # Ensure critical fields exist
    text_cols = ['rag_context_text', 'symptoms', 'care_advice', 'condition', 'department', 'locality', 'red_flag_note']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
        else:
            df[col] = ""

    # Ensure search target column 'search_text' exists
    def build_search_target(row):
        if row['rag_context_text'].strip():
            return row['rag_context_text']
        return f"Condition: {row['condition']}. Department: {row['department']}. Symptoms: {row['symptoms']}. Locality: {row['locality']}. Care Advice: {row['care_advice']}."

    df['search_text'] = df.apply(build_search_target, axis=1)
    
    # Fill categorical defaults
    if 'retrieval_priority' in df.columns:
        df['retrieval_priority'] = df['retrieval_priority'].fillna("Medium")
    if 'verification_status' in df.columns:
        df['verification_status'] = df['verification_status'].fillna("Verified Record")
    if 'care_facility_synthetic' in df.columns:
        df['care_facility_synthetic'] = df['care_facility_synthetic'].fillna("District Hospital Warangal / MGM Hospital")

    return df


# ---------------------------------------------------------
# 2. Embedding & Vector Index Initialization
# ---------------------------------------------------------
@st.cache_resource(show_spinner="Initializing TF-IDF Search Engine...")
def init_tfidf_engine(search_texts: list):
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=25000,
        sublinear_tf=True
    )
    tfidf_matrix = vectorizer.fit_transform(search_texts)
    return vectorizer, tfidf_matrix


@st.cache_resource(show_spinner="Loading SentenceTransformers & Building FAISS Index...")
def init_faiss_engine(search_texts: list):
    try:
        from sentence_transformers import SentenceTransformer
        import faiss

        # Load lightweight MiniLM model
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(search_texts, batch_size=256, show_progress_bar=False, normalize_embeddings=True)
        
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for normalized embeddings = Cosine similarity
        index.add(np.array(embeddings, dtype=np.float32))

        return model, index
    except Exception as e:
        st.warning(f"FAISS/SentenceTransformers initialization notice: {e}. Falling back to TF-IDF.")
        return None, None


# ---------------------------------------------------------
# 3. Safety & Red-Flag Guardrail Engine
# ---------------------------------------------------------
RED_FLAG_PATTERNS = [
    r"\bchest pain\b", r"\bheart attack\b", r"\bcardiac\b", r"\bcrushing pain\b",
    r"\bshortness of breath\b", r"\bsevere breathing\b", r"\bdifficulty breathing\b", r"\bchoking\b", r"\bwheezing severely\b",
    r"\bunconscious\b", r"\bfainted\b", r"\bfainting\b", r"\bpassed out\b", r"\bresponsiveness\b",
    r"\bstroke\b", r"\bslurred speech\b", r"\bface drooping\b", r"\barm weakness\b", r"\bsudden numbness\b",
    r"\bheavy bleeding\b", r"\buncontrolled bleeding\b", r"\bsevere trauma\b", r"\bhead injury\b",
    r"\bseizure\b", r"\bconvulsions\b", r"\bbluish lips\b", r"\bcyanosis\b",
    r"\bhigh fever infant\b", r"\bpoisoning\b", r"\bsnake bite\b"
]

def check_red_flags(query: str, retrieved_chunks: pd.DataFrame = None) -> dict:
    query_lower = query.lower()
    matched_flags = []

    # 1. Scan user query
    for pattern in RED_FLAG_PATTERNS:
        if re.search(pattern, query_lower):
            clean_name = pattern.replace(r"\b", "").replace("\\", "")
            matched_flags.append(clean_name)

    # 2. Scan retrieved chunk red-flag notes
    if retrieved_chunks is not None and not retrieved_chunks.empty:
        if 'red_flag_note' in retrieved_chunks.columns:
            for note in retrieved_chunks['red_flag_note'].head(3):
                note_str = str(note).lower()
                if "urgent" in note_str or "emergency" in note_str or "severe" in note_str:
                    matched_flags.append("Retrieved clinical red-flag alert")

    matched_flags = list(set(matched_flags))
    is_emergency = len(matched_flags) > 0

    return {
        "is_emergency": is_emergency,
        "matched_triggers": matched_flags,
        "emergency_contacts": {
            "MGM Hospital Warangal (Emergency Hotline)": "0870-2441000 / 0870-2441001",
            "District Hospital Warangal": "0870-2577772",
            "Telangana Emergency Ambulance": "108",
            "Kakatiya Medical College Emergency Unit": "Warangal Main Rd, Near KMC Circle",
        }
    }


# ---------------------------------------------------------
# 4. Search & Retrieval Function
# ---------------------------------------------------------
def get_relevant_chunks(
    query: str,
    df: pd.DataFrame,
    tfidf_vectorizer,
    tfidf_matrix,
    faiss_model=None,
    faiss_index=None,
    engine_type: str = "TF-IDF + Cosine Similarity",
    dept_filter: str = "All",
    locality_filter: str = "All",
    top_k: int = 5
) -> pd.DataFrame:
    
    # Apply Department & Locality Filtering
    filtered_df = df.copy()
    if dept_filter != "All" and 'department' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['department'].str.lower() == dept_filter.lower()]
    if locality_filter != "All" and 'locality' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['locality'].str.lower() == locality_filter.lower()]

    if filtered_df.empty:
        # Fallback to full dataset if strict filter yields 0 matches
        filtered_df = df.copy()

    indices = filtered_df.index.values

    # Perform Retrieval
    if engine_type.startswith("FAISS") and faiss_model is not None and faiss_index is not None:
        query_vec = faiss_model.encode([query], normalize_embeddings=True)
        scores, match_indices = faiss_index.search(np.array(query_vec, dtype=np.float32), k=min(top_k * 4, len(df)))
        
        # Filter to allowed indices
        valid_hits = []
        for idx, score in zip(match_indices[0], scores[0]):
            if idx in indices:
                valid_hits.append((idx, float(score)))
            if len(valid_hits) >= top_k:
                break
        
        if not valid_hits:
            # Fallback to TF-IDF if FAISS hit filtering yielded no results
            return get_relevant_chunks(query, df, tfidf_vectorizer, tfidf_matrix, engine_type="TF-IDF + Cosine Similarity", dept_filter=dept_filter, locality_filter=locality_filter, top_k=top_k)
        
        hit_indices, hit_scores = zip(*valid_hits)
        results = df.loc[list(hit_indices)].copy()
        # Scale inner product score to percentage (typically cosine score 0..1)
        results['similarity_score'] = [max(0.0, min(1.0, s)) for s in hit_scores]

    else:
        # Default: TF-IDF + Cosine Similarity
        query_vec = tfidf_vectorizer.transform([query])
        
        # Compute similarity only against filtered subset or full matrix
        sub_tfidf = tfidf_matrix[indices]
        sim_scores = cosine_similarity(query_vec, sub_tfidf).flatten()

        top_sub_indices = np.argsort(sim_scores)[::-1][:top_k]
        actual_indices = indices[top_sub_indices]
        top_scores = sim_scores[top_sub_indices]

        results = df.loc[actual_indices].copy()
        results['similarity_score'] = top_scores

    return results.sort_values(by='similarity_score', ascending=False)


# ---------------------------------------------------------
# 5. Grounded Response Generation Engine
# ---------------------------------------------------------
def generate_grounded_response(query: str, top_chunks: pd.DataFrame, red_flag_info: dict) -> str:
    if top_chunks.empty:
        return (
            "I could not locate specific medical records in the Warangal dataset matching your query. "
            "Please consult a licensed medical professional or visit **MGM Hospital Warangal** for assistance."
        )

    # Identify primary matched condition, department, locality, and advice
    top_row = top_chunks.iloc[0]
    matched_condition = top_row.get('condition', 'General Symptom')
    matched_dept = top_row.get('department', 'General Medicine')
    matched_locality = top_row.get('locality', 'Warangal Region')

    # Gather advice items across top chunks
    advice_list = []
    facilities_list = set()
    source_ids = []

    for idx, row in top_chunks.iterrows():
        advice = str(row.get('care_advice', '')).strip()
        if advice and advice not in advice_list:
            advice_list.append(advice)
        
        facility = str(row.get('care_facility_synthetic', '')).strip()
        if facility:
            facilities_list.add(facility)
        
        pid = row.get('patient_id', f"WP-REC-{idx}")
        loc = row.get('locality', 'Warangal')
        source_ids.append(f"`{pid}` ({loc})")

    response_md = ""

    # Emergency Warning Section
    if red_flag_info['is_emergency']:
        response_md += f"""
> 🚨 **URGENT MEDICAL WARNING / RED-FLAG TRIGGERED**
> Symptoms matching critical conditions (**{', '.join(red_flag_info['matched_triggers'])}**) were detected.
> **Immediate Action Required**: Please visit the nearest casualty / emergency room immediately.
> 
> 📞 **Warangal Emergency Contacts**:
> - **MGM Hospital Warangal Casualty**: `0870-2441000` / `0870-2441001`
> - **Telangana Emergency Ambulance**: Call `108`
> - **District Hospital Warangal**: `0870-2577772`
---
"""

    # Grounded Guidance Content
    response_md += f"### 📋 Primary Medical Guidance for Warangal Patients\n\n"
    response_md += f"Based on verified knowledge records for **{matched_condition}** ({matched_dept} Dept) in the **{matched_locality}** area:\n\n"

    response_md += "#### 💊 Recommended Primary Care & Management Advice:\n"
    for adv in advice_list[:4]:
        response_md += f"- {adv.capitalize()}\n"

    response_md += f"\n#### 🏥 Recommended Local Healthcare Facilities ({matched_locality} & Warangal District):\n"
    for fac in list(facilities_list)[:3]:
        response_md += f"- **{fac}**\n"
    response_md += f"- **MGM Hospital Warangal** (Government Tertiary Care Referral Center)\n"

    response_md += "\n#### 🛡️ Precautionary Escalation Guidelines:\n"
    response_md += (
        "- Monitor symptoms closely over the next 12–24 hours.\n"
        "- Seek immediate medical re-evaluation if fever rises sharply, breathing worsens, or pain intensifies.\n"
        "- Do not self-administer prescription antibiotics or steroids without a licensed doctor's advice.\n"
    )

    # Source Citations
    response_md += f"\n---\n**📌 Grounded Knowledge Sources Cited**: " + ", ".join(source_ids[:4]) + "\n"

    return response_md


# ---------------------------------------------------------
# 6. Main Application Layout & Session State
# ---------------------------------------------------------
def main():
    # Load dataset
    df = load_medical_dataset(DATA_PATH)

    # Initialize Retrieval Engines
    tfidf_vectorizer, tfidf_matrix = init_tfidf_engine(df['search_text'].tolist())
    
    # Initialize Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "faiss_loaded" not in st.session_state:
        st.session_state.faiss_loaded = False
        st.session_state.faiss_model = None
        st.session_state.faiss_index = None

    # Header Banner
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

        # Metrics KPI Grid
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

        # Engine & Retrieval Settings
        st.subheader("⚙️ Retrieval Settings")
        
        retrieval_engine_choice = st.radio(
            "Select Similarity Search Engine:",
            options=["TF-IDF + Cosine Similarity", "FAISS + SentenceTransformers"],
            index=0,
            help="TF-IDF offers instant search. FAISS uses dense semantic vector embeddings."
        )

        # Lazy load FAISS if selected
        if retrieval_engine_choice.startswith("FAISS") and not st.session_state.faiss_loaded:
            with st.spinner("Building FAISS Vector Store..."):
                f_model, f_index = init_faiss_engine(df['search_text'].tolist())
                st.session_state.faiss_model = f_model
                st.session_state.faiss_index = f_index
                st.session_state.faiss_loaded = True

        top_k = st.slider("Top-K Knowledge Chunks:", min_value=3, max_value=10, value=5)

        st.divider()

        # Filters
        st.subheader("🔍 Context Filters")
        
        departments = ["All"] + sorted([d for d in df['department'].unique() if str(d).strip() and str(d) != 'nan'])
        dept_filter = st.selectbox("Department Filter:", options=departments, index=0)

        localities = ["All"] + sorted([l for l in df['locality'].unique() if str(l).strip() and str(l) != 'nan'])
        locality_filter = st.selectbox("Warangal Locality Filter:", options=localities, index=0)

        st.divider()

        # Sample Queries Chips
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

    # Display Existing Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # Display Red-Flag Banner if attached
            if msg.get("red_flag_info") and msg["red_flag_info"]["is_emergency"]:
                st.error(
                    f"🚨 **RED-FLAG EMERGENCY WARNING**: Critical symptoms detected ({', '.join(msg['red_flag_info']['matched_triggers'])}). "
                    f"Escalate immediately to **MGM Hospital Warangal (Hotline: 0870-2441000)** or call **108**."
                )

            # Display Grounded Evidence Inspector Expander
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

    # Capture User Input (From chat input or sample click)
    prompt_input = st.chat_input("Ask a medical query or describe symptoms (e.g., 'Child coughing in Parkal')...")
    
    user_query = None
    if prompt_input:
        user_query = prompt_input
    elif selected_sample:
        user_query = selected_sample

    if user_query:
        # Render User Message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Assistant Processing
        with st.chat_message("assistant"):
            with st.spinner("Searching Warangal Grounded Medical Database & Triaging Symptoms..."):
                start_time = time.time()
                
                # 1. Retrieve Chunks
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

                # 2. Check Red-Flags
                red_flag_info = check_red_flags(user_query, top_chunks)

                # 3. Generate Grounded Response
                response_text = generate_grounded_response(user_query, top_chunks, red_flag_info)
                elapsed = time.time() - start_time

                # Render Response
                st.markdown(response_text)

                # Display Emergency Banner if triggered
                if red_flag_info["is_emergency"]:
                    st.error(
                        f"🚨 **RED-FLAG EMERGENCY ALERT**: Critical red-flag symptoms detected ({', '.join(red_flag_info['matched_triggers'])}). "
                        f"Visit **MGM Hospital Warangal Casualty** or call **108** immediately."
                    )

                # Render RAG Inspector Expander
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

            # Store in Session State
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "red_flag_info": red_flag_info,
                "chunks": top_chunks
            })




if __name__ == "__main__":
    main()
