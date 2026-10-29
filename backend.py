"""
===================================================================================
RAG-Based Medical Information System for Warangal Patients
Core Backend Engine (backend.py)
===================================================================================
Author: B. Sai Tejaswi & V. Abhilash (SR University, Warangal)
Purpose: Modular RAG retrieval pipeline, emergency red-flag safety guardrails,
         and grounded answer synthesizer for Warangal District patients.
Compatible with:
  - Local Python / VS Code (CLI & Script execution)
  - Streamlit UI (app.py)
  - Google Colab (interactive notebook execution & API calls)
===================================================================================
"""

import os
import re
import sys
import time
import argparse
from typing import Dict, List, Optional, Tuple, Any

# Ensure UTF-8 output encoding across Windows / VS Code / Colab consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Default dataset locations (checked in priority order)
DEFAULT_DATASET_PATHS = [
    "cleaned_RAG_Warangal_medical_dataset.csv",
    os.path.join(os.path.dirname(__file__), "cleaned_RAG_Warangal_medical_dataset.csv"),
    "/content/NLP-Project/cleaned_RAG_Warangal_medical_dataset.csv",  # Colab default clone
    "/content/cleaned_RAG_Warangal_medical_dataset.csv",             # Colab root
]

# Emergency contacts for Warangal District
WARANGAL_EMERGENCY_CONTACTS = {
    "MGM Hospital Warangal (Emergency Hotline)": "0870-2441000 / 0870-2441001",
    "District Hospital Warangal": "0870-2577772",
    "Telangana Emergency Ambulance": "108",
    "National Emergency Helpline": "112",
    "Kakatiya Medical College Emergency Unit": "Warangal Main Rd, Near KMC Circle",
}

# Regex patterns for clinical red flags
RED_FLAG_PATTERNS = [
    r"\bchest pain\b", r"\bheart attack\b", r"\bcardiac\b", r"\bcrushing pain\b",
    r"\bshortness of breath\b", r"\bsevere breathing\b", r"\bdifficulty breathing\b",
    r"\bchoking\b", r"\bwheezing severely\b",
    r"\bunconscious\b", r"\bfainted\b", r"\bfainting\b", r"\bpassed out\b", r"\bresponsiveness\b",
    r"\bstroke\b", r"\bslurred speech\b", r"\bface drooping\b", r"\barm weakness\b", r"\bsudden numbness\b",
    r"\bheavy bleeding\b", r"\buncontrolled bleeding\b", r"\bsevere trauma\b", r"\bhead injury\b",
    r"\bseizure\b", r"\bconvulsions\b", r"\bbluish lips\b", r"\bcyanosis\b",
    r"\bhigh fever infant\b", r"\bpoisoning\b", r"\bsnake bite\b"
]


# ===================================================================================
# 1. Dataset Loader & Preprocessor
# ===================================================================================
def load_medical_dataset(file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Loads and normalizes the Warangal Medical Knowledge dataset (12,000 records).
    Handles relative local paths, VS Code environment paths, and Google Colab paths.
    """
    resolved_path = None
    if file_path and os.path.exists(file_path):
        resolved_path = file_path
    else:
        for candidate in DEFAULT_DATASET_PATHS:
            if os.path.exists(candidate):
                resolved_path = candidate
                break

    if not resolved_path:
        raise FileNotFoundError(
            "Medical dataset 'cleaned_RAG_Warangal_medical_dataset.csv' not found. "
            "Ensure the CSV file is located in the working directory or Google Colab /content folder."
        )

    df = pd.read_csv(resolved_path)

    # Normalize critical text columns
    text_cols = [
        'rag_context_text', 'symptoms', 'care_advice', 'condition',
        'department', 'locality', 'red_flag_note'
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
        else:
            df[col] = ""

    # Build primary search target text
    def build_search_target(row):
        ctx = row.get('rag_context_text', '').strip()
        if ctx:
            return ctx
        return (
            f"Condition: {row.get('condition', '')}. "
            f"Department: {row.get('department', '')}. "
            f"Symptoms: {row.get('symptoms', '')}. "
            f"Locality: {row.get('locality', '')}. "
            f"Care Advice: {row.get('care_advice', '')}."
        )

    df['search_text'] = df.apply(build_search_target, axis=1)

    # Defaults for categorical columns
    if 'retrieval_priority' in df.columns:
        df['retrieval_priority'] = df['retrieval_priority'].fillna("Medium").astype(str)
    else:
        df['retrieval_priority'] = "Medium"

    if 'verification_status' in df.columns:
        df['verification_status'] = df['verification_status'].fillna("Verified Record").astype(str)
    else:
        df['verification_status'] = "Verified Record"

    if 'care_facility_synthetic' in df.columns:
        df['care_facility_synthetic'] = df['care_facility_synthetic'].fillna(
            "District Hospital Warangal / MGM Hospital"
        ).astype(str)
    else:
        df['care_facility_synthetic'] = "District Hospital Warangal / MGM Hospital"

    return df


# ===================================================================================
# 2. Embedding & Vector Index Initializers
# ===================================================================================
def init_tfidf_engine(search_texts: List[str]) -> Tuple[TfidfVectorizer, Any]:
    """
    Initializes a high-speed sublinear TF-IDF retrieval matrix over search texts.
    Offers <35ms latency on CPU without GPU requirements.
    """
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=25000,
        sublinear_tf=True
    )
    tfidf_matrix = vectorizer.fit_transform(search_texts)
    return vectorizer, tfidf_matrix


def init_faiss_engine(search_texts: List[str]) -> Tuple[Optional[Any], Optional[Any]]:
    """
    Initializes a dense semantic vector index with SentenceTransformer ('all-MiniLM-L6-v2')
    and FAISS IndexFlatIP (Cosine Similarity over normalized embeddings).
    """
    try:
        from sentence_transformers import SentenceTransformer
        import faiss

        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(
            search_texts,
            batch_size=256,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(np.array(embeddings, dtype=np.float32))

        return model, index
    except Exception as e:
        print(f"[backend] FAISS/SentenceTransformers initialization notice: {e}. Falling back to TF-IDF.")
        return None, None


# ===================================================================================
# 3. Rule-Based Red-Flag Safety Guardrail
# ===================================================================================
def check_red_flags(query: str, retrieved_chunks: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Scans patient query and retrieved context chunks for life-threatening symptoms.
    Returns boolean emergency flag, matched triggers, and local Warangal emergency hotlines.
    """
    query_lower = query.lower()
    matched_flags = []

    # 1. Scan query text
    for pattern in RED_FLAG_PATTERNS:
        if re.search(pattern, query_lower):
            clean_name = pattern.replace(r"\b", "").replace("\\", "")
            matched_flags.append(clean_name)

    # 2. Scan top retrieved chunks
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
        "emergency_contacts": WARANGAL_EMERGENCY_CONTACTS
    }


# ===================================================================================
# 4. Search & Retrieval Engine
# ===================================================================================
def get_relevant_chunks(
    query: str,
    df: pd.DataFrame,
    tfidf_vectorizer: Any,
    tfidf_matrix: Any,
    faiss_model: Optional[Any] = None,
    faiss_index: Optional[Any] = None,
    engine_type: str = "TF-IDF + Cosine Similarity",
    dept_filter: str = "All",
    locality_filter: str = "All",
    top_k: int = 5
) -> pd.DataFrame:
    """
    Retrieves the top-k most relevant clinical records matching the query.
    Applies optional department and Warangal locality filters.
    """
    filtered_df = df.copy()
    if dept_filter != "All" and 'department' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['department'].str.lower() == dept_filter.lower()]
    if locality_filter != "All" and 'locality' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['locality'].str.lower() == locality_filter.lower()]

    if filtered_df.empty:
        filtered_df = df.copy()

    indices = filtered_df.index.values

    # 1. FAISS Dense Retrieval
    if (
        ("faiss" in engine_type.lower() or "dense" in engine_type.lower())
        and faiss_model is not None
        and faiss_index is not None
    ):
        query_vec = faiss_model.encode([query], normalize_embeddings=True)
        scores, match_indices = faiss_index.search(
            np.array(query_vec, dtype=np.float32),
            k=min(top_k * 4, len(df))
        )

        valid_hits = []
        for idx, score in zip(match_indices[0], scores[0]):
            if idx in indices:
                valid_hits.append((idx, float(score)))
            if len(valid_hits) >= top_k:
                break

        if not valid_hits:
            # Fallback to TF-IDF
            return get_relevant_chunks(
                query, df, tfidf_vectorizer, tfidf_matrix,
                engine_type="TF-IDF + Cosine Similarity",
                dept_filter=dept_filter, locality_filter=locality_filter,
                top_k=top_k
            )

        hit_indices, hit_scores = zip(*valid_hits)
        results = df.loc[list(hit_indices)].copy()
        results['similarity_score'] = [max(0.0, min(1.0, s)) for s in hit_scores]

    # 2. TF-IDF Sparse Retrieval (Default)
    else:
        query_vec = tfidf_vectorizer.transform([query])
        sub_tfidf = tfidf_matrix[indices]
        sim_scores = cosine_similarity(query_vec, sub_tfidf).flatten()

        top_sub_indices = np.argsort(sim_scores)[::-1][:top_k]
        actual_indices = indices[top_sub_indices]
        top_scores = sim_scores[top_sub_indices]

        results = df.loc[actual_indices].copy()
        results['similarity_score'] = top_scores

    return results.sort_values(by='similarity_score', ascending=False)


# ===================================================================================
# 5. Grounded Response Synthesizer
# ===================================================================================
def generate_grounded_response(
    query: str,
    top_chunks: pd.DataFrame,
    red_flag_info: Dict[str, Any]
) -> str:
    """
    Synthesizes a medically grounded response strictly derived from retrieved records.
    Appends source citations and localized facility routing.
    """
    if top_chunks.empty:
        return (
            "I could not locate specific medical records in the Warangal dataset matching your query. "
            "Please consult a licensed medical professional or visit **MGM Hospital Warangal** for assistance."
        )

    top_row = top_chunks.iloc[0]
    matched_condition = top_row.get('condition', 'General Symptom')
    matched_dept = top_row.get('department', 'General Medicine')
    matched_locality = top_row.get('locality', 'Warangal Region')

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

    # Emergency escalation banner
    if red_flag_info['is_emergency']:
        triggers_str = ", ".join(red_flag_info['matched_triggers'])
        response_md += f"""
> 🚨 **URGENT MEDICAL WARNING / RED-FLAG TRIGGERED**
> Symptoms matching critical emergency conditions (**{triggers_str}**) were detected.
> **Immediate Action Required**: Please visit the nearest casualty / emergency room immediately.
> 
> 📞 **Warangal Emergency Contacts**:
> - **MGM Hospital Warangal Casualty**: `0870-2441000` / `0870-2441001`
> - **Telangana Emergency Ambulance**: Call `108`
> - **District Hospital Warangal**: `0870-2577772`
---
"""

    # Grounded Primary Guidance
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

    response_md += f"\n---\n**📌 Grounded Knowledge Sources Cited**: " + ", ".join(source_ids[:4]) + "\n"

    return response_md


# ===================================================================================
# 6. High-Level Class: WarangalMedicalRAG
# ===================================================================================
class WarangalMedicalRAG:
    """
    End-to-end interface for the Warangal Medical Information System.
    Designed for clean integration in:
      - VS Code (Python scripts / unit tests / REST API)
      - Google Colab (notebook cells & interactive queries)
      - Streamlit UI (app.py)
    """

    def __init__(self, dataset_path: Optional[str] = None, enable_faiss: bool = False):
        print("[WarangalMedicalRAG] Loading clinical knowledge base...")
        self.df = load_medical_dataset(dataset_path)
        print(f"[WarangalMedicalRAG] Successfully loaded {len(self.df):,} clinical records.")

        print("[WarangalMedicalRAG] Initializing TF-IDF sparse retrieval index...")
        self.tfidf_vectorizer, self.tfidf_matrix = init_tfidf_engine(self.df['search_text'].tolist())

        self.faiss_model = None
        self.faiss_index = None
        if enable_faiss:
            print("[WarangalMedicalRAG] Building FAISS dense semantic index...")
            self.faiss_model, self.faiss_index = init_faiss_engine(self.df['search_text'].tolist())

    def query(
        self,
        user_query: str,
        engine_type: str = "TF-IDF + Cosine Similarity",
        dept_filter: str = "All",
        locality_filter: str = "All",
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Processes a patient query through the RAG pipeline.
        Returns a dictionary containing:
          - response_text: Formatted grounded markdown response
          - is_emergency: Boolean flag for red-flag triggers
          - matched_triggers: List of detected emergency symptoms
          - retrieved_chunks: DataFrame of top-k retrieved evidence
          - latency_ms: Execution time in milliseconds
        """
        start_time = time.time()

        # Step 1: Top-K Evidence Retrieval
        top_chunks = get_relevant_chunks(
            query=user_query,
            df=self.df,
            tfidf_vectorizer=self.tfidf_vectorizer,
            tfidf_matrix=self.tfidf_matrix,
            faiss_model=self.faiss_model,
            faiss_index=self.faiss_index,
            engine_type=engine_type,
            dept_filter=dept_filter,
            locality_filter=locality_filter,
            top_k=top_k
        )

        # Step 2: Red-Flag Clinical Safety Triage
        red_flag_info = check_red_flags(user_query, top_chunks)

        # Step 3: Grounded Answer Synthesis
        response_text = generate_grounded_response(user_query, top_chunks, red_flag_info)

        elapsed_ms = (time.time() - start_time) * 1000

        return {
            "query": user_query,
            "response_text": response_text,
            "is_emergency": red_flag_info["is_emergency"],
            "matched_triggers": red_flag_info["matched_triggers"],
            "emergency_contacts": red_flag_info["emergency_contacts"],
            "retrieved_chunks": top_chunks,
            "latency_ms": elapsed_ms
        }


# ===================================================================================
# 7. CLI / Direct Terminal & Colab Execution
# ===================================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Warangal Medical RAG Backend Engine")
    parser.add_argument(
        "--query", "-q",
        type=str,
        default="Child in Parkal having severe asthma and wheezing",
        help="Patient symptom or health question"
    )
    parser.add_argument("--engine", "-e", type=str, default="TF-IDF", choices=["TF-IDF", "FAISS"])
    parser.add_argument("--dept", "-d", type=str, default="All", help="Department filter")
    parser.add_argument("--locality", "-l", type=str, default="All", help="Locality filter")
    parser.add_argument("--top_k", "-k", type=int, default=3, help="Number of retrieved chunks")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print(" [RAG-Based Medical Information System for Warangal Patients]")
    print("=" * 70)

    rag = WarangalMedicalRAG(enable_faiss=(args.engine == "FAISS"))
    result = rag.query(
        user_query=args.query,
        engine_type=f"{args.engine} + Cosine Similarity",
        dept_filter=args.dept,
        locality_filter=args.locality,
        top_k=args.top_k
    )

    print(f"\n[QUERY]: {args.query}")
    print(f"[EXECUTION TIME]: {result['latency_ms']:.2f} ms")
    status_str = "[ALERT: CRITICAL RED-FLAG]" if result['is_emergency'] else "[NORMAL: Standard Primary Triage]"
    print(f"[EMERGENCY STATUS]: {status_str}")
    if result['matched_triggers']:
        print(f"[TRIGGERED SYMPTOMS]: {', '.join(result['matched_triggers'])}")

    print("\n--- GROUNDED RESPONSE ---")
    print(result['response_text'])

    print("\n--- TOP RETRIEVED EVIDENCE CHUNKS ---")
    for i, (_, row) in enumerate(result['retrieved_chunks'].iterrows(), 1):
        score_val = row.get('similarity_score', 0.0)
        print(f"[{i}] Record ID: {row.get('patient_id', 'N/A')} | Condition: {row.get('condition', 'N/A')} | Locality: {row.get('locality', 'N/A')} | Match: {score_val*100:.1f}%")

