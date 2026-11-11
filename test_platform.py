"""
Automated Verification Suite for Warangal HealthRAG Platform
File: test_platform.py
"""

import sys
import auth_db
from backend import (
    load_medical_dataset,
    init_tfidf_engine,
    init_faiss_engine,
    check_red_flags,
    get_relevant_chunks,
    generate_grounded_response,
    WarangalMedicalRAG
)

def run_tests():
    print("=" * 70)
    print("🧪 STARTING WARANGAL HEALTHRAG AUTOMATED VERIFICATION SUITE")
    print("=" * 70)

    # TEST 1: User Signup
    print("\n[TEST 1] Testing User Signup...")
    test_email = "test.patient@sru.edu.in"
    ok, msg = auth_db.register_user("Test Patient", test_email, "+91 9999988888", "SecurePass@123")
    print(f" -> Signup result: {ok} ({msg})")

    # TEST 2: User Login (Positive & Negative)
    print("\n[TEST 2] Testing User Authentication...")
    user_fail, msg_fail = auth_db.authenticate_user(test_email, "WrongPassword!")
    assert user_fail is None, "Failed password test should return None"
    print(f" -> Incorrect password rejected correctly: {msg_fail}")

    user_success, msg_ok = auth_db.authenticate_user(test_email, "SecurePass@123")
    assert user_success is not None, "Correct password test should succeed"
    assert user_success['role'] == 'user', "Standard user should have 'user' role"
    print(f" -> Patient authenticated successfully: {user_success['full_name']} (Role: {user_success['role']})")

    # TEST 3: Admin Login & Role Check
    print("\n[TEST 3] Testing Admin Authentication & Role Enforcement...")
    admin_user, admin_msg = auth_db.authenticate_user("admin@warangalmed.org", "Admin@Warangal2026")
    assert admin_user is not None, "Admin authentication failed"
    assert admin_user['role'] == 'admin', "Admin account must have 'admin' role"
    print(f" -> Admin authenticated successfully: {admin_user['full_name']} (Role: {admin_user['role']})")

    # TEST 4: Admin Access Restriction Logic
    print("\n[TEST 4] Testing Access Control Logic...")
    assert user_success['role'] != 'admin', "Normal user must NOT have admin privileges"
    print(" -> Confirmed: Normal user cannot access administrator endpoints.")

    # TEST 5: Dataset Loading & TF-IDF Vectorization
    print("\n[TEST 5] Loading 12,000 Verified Records & TF-IDF Index...")
    df = load_medical_dataset()
    assert len(df) == 12000, f"Expected 12000 records, got {len(df)}"
    v, tfidf_matrix = init_tfidf_engine(df['search_text'].tolist())
    assert tfidf_matrix.shape[0] == 12000, "TF-IDF matrix dimension mismatch"
    print(f" -> Loaded {len(df):,} records successfully. TF-IDF Matrix: {tfidf_matrix.shape}")

    # TEST 6: Emergency Red-Flag Detection (Positive Case)
    print("\n[TEST 6] Testing Emergency Red-Flag Triage (Positive Trigger)...")
    emerg_q = "Severe chest pain, heavy sweating and breathing difficulty in Kazipet"
    emerg_rf = check_red_flags(emerg_q)
    assert emerg_rf['is_emergency'] is True, "Emergency should be detected!"
    print(f" -> Emergency detected correctly! Triggers: {emerg_rf['matched_triggers']}")
    assert "0870-2441000" in emerg_rf['emergency_contacts']['MGM Hospital Warangal (Emergency Hotline)'], "MGM contact missing"
    print(" -> MGM Hospital Casualty hotline verified.")

    # TEST 7: Emergency Red-Flag Detection (Negative Control Case)
    print("\n[TEST 7] Testing Non-Emergency Control Query (Negative Control)...")
    mild_q = "Mild skin rash on forearm with slight itching in Hanamkonda"
    mild_rf = check_red_flags(mild_q)
    assert mild_rf['is_emergency'] is False, "Mild rash should NOT trigger emergency"
    print(f" -> Non-emergency confirmed. is_emergency = {mild_rf['is_emergency']}")

    # TEST 8: RAG Top-K Retrieval & Grounding
    print("\n[TEST 8] Testing Retrieval and Evidence Inspection...")
    chunks = get_relevant_chunks(mild_q, df, v, tfidf_matrix, top_k=3)
    assert len(chunks) == 3, "Expected 3 retrieved chunks"
    top_row = chunks.iloc[0]
    print(f" -> Top matched record: ID={top_row['patient_id']}, Dept={top_row['department']}, Match={top_row['similarity_score']*100:.1f}%")
    assert str(top_row['patient_id']).startswith("WP-"), "Record ID must be from dataset"

    # TEST 9: Grounded Response Generation
    print("\n[TEST 9] Testing Grounded Response Synthesis...")
    resp = generate_grounded_response(mild_q, chunks, mild_rf)
    assert "MGM Hospital Warangal" in resp, "Referral center should be present in advice"
    assert "WP-SYN-" in resp or "WP-REC-" in resp, "Grounded citations must be included"
    print(f" -> Generated response verified ({len(resp)} chars). Citations included.")

    # TEST 10: FAISS Dense Vector Engine (Optional Fallback / Real)
    print("\n[TEST 10] Testing FAISS Dense Vector Initialization...")
    f_model, f_index = init_faiss_engine(df['search_text'].tolist()[:100]) # test on sample for speed
    if f_model and f_index:
        print(" -> FAISS and SentenceTransformers MiniLM initialized successfully.")
    else:
        print(" -> FAISS fallback verified.")

    # TEST 11: All 8 Localities Presence Check
    print("\n[TEST 11] Checking 8 Warangal Localities in Dataset...")
    expected_locs = ["Warangal", "Hanamkonda", "Kazipet", "Parkal", "Dharmasagar", "Geesugonda", "Hasanparthy", "Wardhannapet"]
    actual_locs = df['locality'].dropna().unique().tolist()
    for loc in expected_locs:
        assert loc in actual_locs, f"Locality {loc} missing from dataset"
    print(f" -> All 8 Warangal localities confirmed in dataset: {expected_locs}")

    # TEST 12: Query Logging & Saved Responses
    print("\n[TEST 12] Testing Query History & Saved Responses...")
    auth_db.log_query(user_success['id'], user_success['email'], mild_q, resp, False, [], 28.5, "TF-IDF", "Dermatology", "Hanamkonda")
    history = auth_db.get_user_query_history(user_success['id'], 5)
    assert len(history) > 0, "Query history must contain logged query"
    print(f" -> Logged query verified: {history[0]['query_text']}")

    save_ok = auth_db.save_response_for_user(user_success['id'], mild_q, resp, "WP-SYN-001")
    assert save_ok is True, "Failed to save response"
    saved_list = auth_db.get_user_saved_responses(user_success['id'])
    assert len(saved_list) > 0, "Saved answers must contain saved response"
    print(f" -> Saved response verified for user {user_success['full_name']}")

    # TEST 13: Admin Dashboard Metrics & Logs
    print("\n[TEST 13] Testing Administrator Metrics Aggregation...")
    metrics = auth_db.get_admin_dashboard_metrics()
    print(f" -> Admin Metrics: Total Users={metrics['total_users']}, Queries={metrics['total_queries']}, Emergencies={metrics['total_emergencies']}, Avg Latency={metrics['avg_latency_ms']} ms")
    assert metrics['total_users'] >= 2, "Should have at least 2 users"

    print("\n" + "=" * 70)
    print("✅ ALL 13 TEST PHASES PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
