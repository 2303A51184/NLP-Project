import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('figures', exist_ok=True)

# Set common font styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# -------------------------------------------------------------
# 1. System Architecture Diagram (Figure 5.1)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
ax.set_xlim(0, 12)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(6, 9.6, 'Figure 5.1: Grounded Medical RAG Platform Architecture', 
        ha='center', va='center', fontsize=14, fontweight='bold', color='#167D83')

# Layer 1: Client Layer
rect_client = patches.FancyBboxPatch((0.8, 7.8), 10.4, 1.2, boxstyle="round,pad=0.1", fc='#FFFFFF', ec='#167D83', lw=2)
ax.add_patch(rect_client)
ax.text(6, 8.6, 'USER INTERACTION LAYER (Streamlit Light SaaS Portal)', ha='center', va='center', fontsize=11, fontweight='bold', color='#263746')
ax.text(6, 8.1, 'Patient Health Query  |  Locality & Department Filters  |  Split-Screen Auth  |  Admin Console', ha='center', va='center', fontsize=9, color='#64748B')

# Arrow down
ax.annotate('', xy=(6, 6.9), xytext=(6, 7.8), arrowprops=dict(facecolor='#167D83', edgecolor='#167D83', width=1.5, headwidth=7))

# Layer 2: Safety & Triage Layer
rect_safety = patches.FancyBboxPatch((1.5, 5.8), 9.0, 1.1, boxstyle="round,pad=0.1", fc='#FFF5F5', ec='#D9534F', lw=2)
ax.add_patch(rect_safety)
ax.text(6, 6.5, 'PRE-RETRIEVAL EMERGENCY RED-FLAG TRIAGE GUARDRAIL', ha='center', va='center', fontsize=10, fontweight='bold', color='#D9534F')
ax.text(6, 6.05, 'Regex Rule Engine: Chest Pain, Stroke, Severe Dyspnea  -->  Auto-Escalate to 108 & MGM Hospital (0870-2441000)', ha='center', va='center', fontsize=8.5, color='#263746')

# Arrow down
ax.annotate('', xy=(6, 4.8), xytext=(6, 5.8), arrowprops=dict(facecolor='#167D83', edgecolor='#167D83', width=1.5, headwidth=7))

# Layer 3: Dual Retrieval Engine
rect_rag = patches.FancyBboxPatch((0.5, 2.7), 11.0, 2.1, boxstyle="round,pad=0.1", fc='#F7FAFC', ec='#167D83', lw=2)
ax.add_patch(rect_rag)
ax.text(6, 4.5, 'DUAL-CORE RETRIEVAL-AUGMENTED GENERATION (RAG) ENGINE', ha='center', va='center', fontsize=11, fontweight='bold', color='#167D83')

# Sub-engine A: TF-IDF
rect_tfidf = patches.FancyBboxPatch((0.8, 3.0), 4.8, 1.2, boxstyle="round,pad=0.08", fc='#FFFFFF', ec='#CBD5E1', lw=1.5)
ax.add_patch(rect_tfidf)
ax.text(3.2, 3.8, 'Sparse Engine: TF-IDF + Cosine', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#263746')
ax.text(3.2, 3.3, 'Sublinear TF scaling, n-grams (1,2)\nLatency < 35 ms | Keyword Matching', ha='center', va='center', fontsize=8, color='#64748B')

# Sub-engine B: FAISS
rect_faiss = patches.FancyBboxPatch((6.4, 3.0), 4.8, 1.2, boxstyle="round,pad=0.08", fc='#FFFFFF', ec='#CBD5E1', lw=1.5)
ax.add_patch(rect_faiss)
ax.text(8.8, 3.8, 'Dense Engine: FAISS + all-MiniLM-L6-v2', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#263746')
ax.text(8.8, 3.3, '384-d Dense Embeddings, IndexFlatIP\nSemantic Concept Matching | MRR: 0.91', ha='center', va='center', fontsize=8, color='#64748B')

# Arrow down
ax.annotate('', xy=(6, 1.8), xytext=(6, 2.7), arrowprops=dict(facecolor='#167D83', edgecolor='#167D83', width=1.5, headwidth=7))

# Layer 4: Grounded Knowledge Base & Persistence
rect_data = patches.FancyBboxPatch((0.8, 0.4), 10.4, 1.4, boxstyle="round,pad=0.1", fc='#FFFFFF', ec='#248A61', lw=2)
ax.add_patch(rect_data)
ax.text(6, 1.4, 'VERIFIED CLINICAL KNOWLEDGE BASE & PERSISTENCE LAYER', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#248A61')
ax.text(6, 0.95, '12,000 Warangal Patient Records (8 Localities: Hanamkonda, Kazipet, Parkal, etc.)  |  8 Clinical Specialties', ha='center', va='center', fontsize=8.5, color='#263746')
ax.text(6, 0.65, 'SQLite DB (medical_system.db): Users (PBKDF2-HMAC-SHA256), Query Logs, Saved Consultations, Audit Trail', ha='center', va='center', fontsize=8, color='#64748B')

plt.tight_layout()
plt.savefig('figures/fig_5_1_system_architecture.png', bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 2. DFD Level 0 and Level 1 (Figure 5.2)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
ax.set_xlim(0, 11)
ax.set_ylim(0, 7)
ax.axis('off')

ax.text(5.5, 6.7, 'Figure 5.2: Data Flow Diagram (DFD Level 0 & Level 1)', ha='center', va='center', fontsize=13, fontweight='bold', color='#167D83')

# Level 0 (Top half)
ax.text(0.5, 5.8, 'LEVEL 0 CONTEXT DIAGRAM', fontsize=10, fontweight='bold', color='#263746')
# Entity 1: Patient
rect_e1 = patches.FancyBboxPatch((0.5, 4.3), 1.8, 1.1, boxstyle="square,pad=0.05", fc='#D9F0ED', ec='#167D83', lw=1.5)
ax.add_patch(rect_e1)
ax.text(1.4, 4.85, 'Patient /\nCitizen', ha='center', va='center', fontsize=9, fontweight='bold')

# Process 0: System
circle_p0 = patches.Circle((5.5, 4.85), 0.9, fc='#FFFFFF', ec='#167D83', lw=2)
ax.add_patch(circle_p0)
ax.text(5.5, 4.85, '0.0\nWarangal\nHealthRAG\nSystem', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#167D83')

# Entity 2: Emergency Response / MGM Hospital
rect_e2 = patches.FancyBboxPatch((8.7, 4.3), 1.8, 1.1, boxstyle="square,pad=0.05", fc='#FFF5F5', ec='#D9534F', lw=1.5)
ax.add_patch(rect_e2)
ax.text(9.6, 4.85, 'Emergency\nServices\n(108 / MGM)', ha='center', va='center', fontsize=9, fontweight='bold', color='#D9534F')

# Arrows L0
ax.annotate('Query / Symptoms', xy=(4.6, 5.0), xytext=(2.3, 5.0), arrowprops=dict(arrowstyle="->", lw=1.5, color='#263746'))
ax.annotate('Grounded Guidance', xy=(2.3, 4.5), xytext=(4.6, 4.5), arrowprops=dict(arrowstyle="->", lw=1.5, color='#167D83'))
ax.annotate('Emergency Triage Alert', xy=(8.7, 4.85), xytext=(6.4, 4.85), arrowprops=dict(arrowstyle="->", lw=1.5, color='#D9534F'))

# Separator line
ax.plot([0.5, 10.5], [3.6, 3.6], color='#E5EBEF', lw=1.5, linestyle='--')

# Level 1 (Bottom half)
ax.text(0.5, 3.2, 'LEVEL 1 PROCESS DECOMPOSITION', fontsize=10, fontweight='bold', color='#263746')

# Processes L1
p1 = patches.Circle((1.8, 1.8), 0.7, fc='#FFFFFF', ec='#167D83', lw=1.5)
p2 = patches.Circle((4.3, 1.8), 0.7, fc='#FFFFFF', ec='#D9534F', lw=1.5)
p3 = patches.Circle((6.8, 1.8), 0.7, fc='#FFFFFF', ec='#167D83', lw=1.5)
p4 = patches.Circle((9.3, 1.8), 0.7, fc='#FFFFFF', ec='#248A61', lw=1.5)
ax.add_patch(p1); ax.add_patch(p2); ax.add_patch(p3); ax.add_patch(p4)

ax.text(1.8, 1.8, '1.0\nAuth &\nSession', ha='center', va='center', fontsize=8, fontweight='bold')
ax.text(4.3, 1.8, '2.0\nRed-Flag\nTriage', ha='center', va='center', fontsize=8, fontweight='bold', color='#D9534F')
ax.text(6.8, 1.8, '3.0\nVector\nSearch', ha='center', va='center', fontsize=8, fontweight='bold', color='#167D83')
ax.text(9.3, 1.8, '4.0\nGrounded\nSynthesis', ha='center', va='center', fontsize=8, fontweight='bold', color='#248A61')

# Arrows between processes
ax.annotate('', xy=(3.6, 1.8), xytext=(2.5, 1.8), arrowprops=dict(arrowstyle="->", lw=1.5, color='#263746'))
ax.annotate('', xy=(6.1, 1.8), xytext=(5.0, 1.8), arrowprops=dict(arrowstyle="->", lw=1.5, color='#263746'))
ax.annotate('', xy=(8.6, 1.8), xytext=(7.5, 1.8), arrowprops=dict(arrowstyle="->", lw=1.5, color='#263746'))

# Data stores
ax.text(6.8, 0.4, '=== D1: Clinical Dataset (12,000 Warangal Records) ===', ha='center', va='center', fontsize=8.5, color='#167D83', fontweight='bold')
ax.annotate('', xy=(6.8, 1.1), xytext=(6.8, 0.6), arrowprops=dict(arrowstyle="<->", lw=1.2, color='#167D83'))

plt.tight_layout()
plt.savefig('figures/fig_5_2_dfd.png', bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 3. UML Use Case Diagram (Figure 5.3)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)
ax.axis('off')

ax.text(5, 6.6, 'Figure 5.3: UML Use Case Diagram', ha='center', va='center', fontsize=13, fontweight='bold', color='#167D83')

# Boundary
boundary = patches.FancyBboxPatch((2.2, 0.4), 5.6, 5.8, boxstyle="square,pad=0.1", fc='#F7FAFC', ec='#CBD5E1', lw=1.5)
ax.add_patch(boundary)
ax.text(5, 5.9, 'Warangal Medical Information System Boundary', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#64748B')

# Actors
ax.text(1.0, 4.5, '👤\nPatient /\nCitizen', ha='center', va='center', fontsize=11, fontweight='bold', color='#167D83')
ax.text(1.0, 1.8, '👨‍⚕️\nClinical\nAdmin', ha='center', va='center', fontsize=11, fontweight='bold', color='#263746')
ax.text(9.0, 3.8, '🚑\nEmergency\nServices (108)', ha='center', va='center', fontsize=11, fontweight='bold', color='#D9534F')

# Use Cases (Ellipses)
ucs = [
    (5.0, 5.3, 'Register & Login (PBKDF2)'),
    (5.0, 4.4, 'Submit Medical Query'),
    (5.0, 3.5, 'Filter by Locality & Specialty'),
    (5.0, 2.6, 'Inspect RAG Evidence Records'),
    (5.0, 1.7, 'Save Consultations to Dashboard'),
    (5.0, 0.8, 'Review System Telemetry & Logs')
]

for x, y, label in ucs:
    ellipse = patches.Ellipse((x, y), 3.8, 0.6, fc='#FFFFFF', ec='#167D83', lw=1.2)
    ax.add_patch(ellipse)
    ax.text(x, y, label, ha='center', va='center', fontsize=8.5, color='#263746')

# Connecting Lines
# Patient lines
ax.plot([1.7, 3.1], [4.5, 5.3], color='#167D83', lw=1)
ax.plot([1.7, 3.1], [4.5, 4.4], color='#167D83', lw=1)
ax.plot([1.7, 3.1], [4.5, 3.5], color='#167D83', lw=1)
ax.plot([1.7, 3.1], [4.5, 2.6], color='#167D83', lw=1)
ax.plot([1.7, 3.1], [4.5, 1.7], color='#167D83', lw=1)

# Admin lines
ax.plot([1.7, 3.1], [1.8, 5.3], color='#263746', lw=1)
ax.plot([1.7, 3.1], [1.8, 0.8], color='#263746', lw=1)

# Emergency services lines
ax.plot([8.2, 6.9], [3.8, 4.4], color='#D9534F', lw=1, linestyle='--')

plt.tight_layout()
plt.savefig('figures/fig_5_3_use_case.png', bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 4. UML Sequence Diagram (Figure 5.4)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
ax.set_xlim(0, 11)
ax.set_ylim(0, 8)
ax.axis('off')

ax.text(5.5, 7.6, 'Figure 5.4: UML Sequence Diagram of Query Triage & Retrieval Flow', ha='center', va='center', fontsize=12.5, fontweight='bold', color='#167D83')

# Participants
participants = [
    (1.2, 'Patient\n(Client)'),
    (3.6, 'Streamlit UI\n(Presentation)'),
    (6.0, 'Triage Guardrail\n(Safety Engine)'),
    (8.4, 'Dual RAG Engine\n(TF-IDF / FAISS)'),
    (10.2, 'SQLite DB\n(Audit Store)')
]

for x, label in participants:
    rect = patches.FancyBboxPatch((x-0.7, 6.5), 1.4, 0.7, boxstyle="square,pad=0.05", fc='#FFFFFF', ec='#167D83', lw=1.5)
    ax.add_patch(rect)
    ax.text(x, 6.85, label, ha='center', va='center', fontsize=8, fontweight='bold', color='#263746')
    ax.plot([x, x], [0.6, 6.5], color='#CBD5E1', lw=1.2, linestyle=':')

# Messages
msgs = [
    (1.2, 3.6, 5.9, '1: enter_query("severe chest pain")', '#263746'),
    (3.6, 6.0, 5.2, '2: check_red_flags(query)', '#D9534F'),
    (6.0, 3.6, 4.6, '3: alert_emergency(triggers=["chest pain"])', '#D9534F'),
    (3.6, 8.4, 4.0, '4: get_relevant_chunks(query, top_k=5)', '#167D83'),
    (8.4, 8.4, 3.4, '5: compute_similarity(TF-IDF / FAISS)', '#167D83'),
    (8.4, 3.6, 2.7, '6: return top_k_grounded_chunks', '#167D83'),
    (3.6, 10.2, 2.0, '7: log_query(latency, emergency, record_ids)', '#248A61'),
    (3.6, 1.2, 1.3, '8: display_grounded_response + evidence_inspector', '#167D83')
]

for x1, x2, y, text, col in msgs:
    if x1 == x2: # self call
        ax.annotate('', xy=(x1, y-0.3), xytext=(x1+0.6, y), arrowprops=dict(arrowstyle="->", lw=1.2, color=col))
        ax.text(x1+0.7, y-0.15, text, fontsize=7.5, color=col, va='center')
    else:
        ax.annotate('', xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", lw=1.2, color=col))
        ax.text((x1+x2)/2, y+0.12, text, ha='center', va='bottom', fontsize=7.5, color=col, fontweight='bold' if col != '#263746' else 'normal')

plt.tight_layout()
plt.savefig('figures/fig_5_4_sequence.png', bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 5. Dual RAG Pipeline Diagram (Figure 6.1)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

ax.text(5, 5.6, 'Figure 6.1: Dual RAG Pipeline (Sparse Lexical vs. Dense Semantic)', ha='center', va='center', fontsize=12.5, fontweight='bold', color='#167D83')

# Query box
p_q = patches.FancyBboxPatch((0.5, 3.4), 1.8, 0.9, boxstyle="round,pad=0.05", fc='#D9F0ED', ec='#167D83', lw=1.5)
ax.add_patch(p_q)
ax.text(1.4, 3.85, 'Patient Query\n(Natural Language)', ha='center', va='center', fontsize=8.5, fontweight='bold')

# Branching arrows
ax.annotate('', xy=(3.0, 4.6), xytext=(2.3, 3.85), arrowprops=dict(arrowstyle="->", lw=1.5, color='#167D83'))
ax.annotate('', xy=(3.0, 2.2), xytext=(2.3, 3.85), arrowprops=dict(arrowstyle="->", lw=1.5, color='#167D83'))

# Branch 1: Sparse
p_sp = patches.FancyBboxPatch((3.0, 4.0), 3.2, 1.2, boxstyle="square,pad=0.05", fc='#FFFFFF', ec='#167D83', lw=1.5)
ax.add_patch(p_sp)
ax.text(4.6, 4.8, 'Sparse Pipeline (TF-IDF)', ha='center', va='center', fontsize=9, fontweight='bold', color='#167D83')
ax.text(4.6, 4.3, 'Term-frequency sublinear weighting\nCosine Similarity against 25k vocab matrix', ha='center', va='center', fontsize=7.5, color='#64748B')

# Branch 2: Dense
p_de = patches.FancyBboxPatch((3.0, 1.6), 3.2, 1.2, boxstyle="square,pad=0.05", fc='#FFFFFF', ec='#167D83', lw=1.5)
ax.add_patch(p_de)
ax.text(4.6, 2.4, 'Dense Pipeline (FAISS + MiniLM)', ha='center', va='center', fontsize=9, fontweight='bold', color='#167D83')
ax.text(4.6, 1.9, 'all-MiniLM-L6-v2 Bi-Encoder\n384-d normalized vector search via IndexFlatIP', ha='center', va='center', fontsize=7.5, color='#64748B')

# Convergence arrows
ax.annotate('', xy=(6.8, 3.4), xytext=(6.2, 4.6), arrowprops=dict(arrowstyle="->", lw=1.5, color='#167D83'))
ax.annotate('', xy=(6.8, 3.4), xytext=(6.2, 2.2), arrowprops=dict(arrowstyle="->", lw=1.5, color='#167D83'))

# Top-K & Synthesis
p_out = patches.FancyBboxPatch((6.8, 2.6), 2.8, 1.6, boxstyle="round,pad=0.05", fc='#FFFFFF', ec='#248A61', lw=1.5)
ax.add_patch(p_out)
ax.text(8.2, 3.8, 'Grounded Response Synthesis', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#248A61')
ax.text(8.2, 3.2, 'Top-K Verified Chunks\nStrict Context Constraints\nEvidence Citations (WP-SYN-XXXX)', ha='center', va='center', fontsize=7.5, color='#64748B')

plt.tight_layout()
plt.savefig('figures/fig_6_1_dual_rag_pipeline.png', bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 6. Emergency Red-Flag Workflow (Figure 6.2)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
ax.set_xlim(0, 9)
ax.set_ylim(0, 6)
ax.axis('off')

ax.text(4.5, 5.6, 'Figure 6.2: Rule-Based Emergency Red-Flag Triage Flowchart', ha='center', va='center', fontsize=12, fontweight='bold', color='#D9534F')

# Step 1: Input
b1 = patches.FancyBboxPatch((0.5, 3.7), 2.0, 0.9, boxstyle="round,pad=0.05", fc='#FFFFFF', ec='#263746', lw=1.5)
ax.add_patch(b1)
ax.text(1.5, 4.15, 'Incoming Patient\nSymptom Query', ha='center', va='center', fontsize=8.5, fontweight='bold')

# Arrow
ax.annotate('', xy=(3.0, 4.15), xytext=(2.5, 4.15), arrowprops=dict(arrowstyle="->", lw=1.5))

# Decision Diamond: Regex Check
diamond = patches.Polygon([[4.0, 4.8], [5.0, 4.15], [4.0, 3.5], [3.0, 4.15]], fc='#FFF5F5', ec='#D9534F', lw=1.5)
ax.add_patch(diamond)
ax.text(4.0, 4.15, 'Red-Flag\nTrigger\nDetected?', ha='center', va='center', fontsize=7.5, fontweight='bold', color='#D9534F')

# Path YES
ax.annotate('YES', xy=(4.0, 2.5), xytext=(4.0, 3.5), arrowprops=dict(arrowstyle="->", lw=1.5, color='#D9534F'))
b_yes = patches.FancyBboxPatch((2.2, 0.8), 3.6, 1.4, boxstyle="round,pad=0.08", fc='#FFF5F5', ec='#D9534F', lw=2)
ax.add_patch(b_yes)
ax.text(4.0, 1.8, 'CRITICAL EMERGENCY ESCALATION', ha='center', va='center', fontsize=9, fontweight='bold', color='#D9534F')
ax.text(4.0, 1.3, 'Render Emergency Alert Card immediately\nAmbulance: 108 / 112\nMGM Hospital Casualty Hotline: 0870-2441000', ha='center', va='center', fontsize=8, color='#263746')

# Path NO
ax.annotate('NO', xy=(6.2, 4.15), xytext=(5.0, 4.15), arrowprops=dict(arrowstyle="->", lw=1.5, color='#248A61'))
b_no = patches.FancyBboxPatch((6.2, 3.4), 2.4, 1.5, boxstyle="round,pad=0.05", fc='#FFFFFF', ec='#248A61', lw=1.5)
ax.add_patch(b_no)
ax.text(7.4, 4.4, 'STANDARD RAG FLOW', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#248A61')
ax.text(7.4, 3.85, 'TF-IDF / FAISS Vector Search\nGrounded Clinical Generation\nEvidence Inspector Display', ha='center', va='center', fontsize=7.5, color='#64748B')

plt.tight_layout()
plt.savefig('figures/fig_6_2_emergency_workflow.png', bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 7. Latency Comparison Chart (Figure 8.1)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
top_k_values = ['Top-3', 'Top-5', 'Top-8', 'Top-10']
tfidf_latency = [12.4, 18.2, 26.5, 33.1]
faiss_latency = [42.1, 48.6, 56.3, 62.4]

x = range(len(top_k_values))
width = 0.35

rects1 = ax.bar([i - width/2 for i in x], tfidf_latency, width, label='TF-IDF + Cosine', color='#167D83')
rects2 = ax.bar([i + width/2 for i in x], faiss_latency, width, label='FAISS + MiniLM', color='#248A61')

ax.set_ylabel('Mean Retrieval Latency (Milliseconds)', fontsize=10, fontweight='bold', color='#263746')
ax.set_xlabel('Retrieval Depth (Top-K Chunks)', fontsize=10, fontweight='bold', color='#263746')
ax.set_title('Figure 8.1: Retrieval Latency Comparison Across Top-K Settings', fontsize=11, fontweight='bold', color='#167D83')
ax.set_xticks(x)
ax.set_xticklabels(top_k_values, fontweight='bold')
ax.axhline(35, color='#D9534F', linestyle='--', linewidth=1.2, label='Target Latency Threshold (<35 ms)')
ax.legend(frameon=True)
ax.grid(axis='y', linestyle=':', alpha=0.6)

plt.tight_layout()
plt.savefig('figures/fig_8_1_latency_comparison.png', bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 8. Evaluation Metrics Chart (Figure 8.2)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
metrics = ['MRR\n(TF-IDF)', 'MRR\n(FAISS)', 'Recall@5\n(Hybrid)', 'Emergency\nSensitivity', 'Grounding\nAccuracy']
scores = [86.0, 91.0, 94.6, 100.0, 100.0]
colors = ['#167D83', '#167D83', '#248A61', '#D9534F', '#248A61']

bars = ax.bar(metrics, scores, color=colors, width=0.55)
ax.set_ylim(0, 115)
ax.set_ylabel('Performance Score (%)', fontsize=10, fontweight='bold', color='#263746')
ax.set_title('Figure 8.2: Experimental Evaluation Metrics on Verified Records', fontsize=11, fontweight='bold', color='#167D83')
ax.grid(axis='y', linestyle=':', alpha=0.6)

for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.1f}%',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('figures/fig_8_2_evaluation_metrics.png', bbox_inches='tight')
plt.close()

print("All 8 figures successfully generated in figures/ directory!")
