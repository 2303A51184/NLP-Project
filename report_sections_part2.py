"""
===================================================================================
Module: report_sections_part2.py
Contents: Chapters 4 (System Requirements), 5 (Architecture & Design), 6 (Methodology)
===================================================================================
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from report_sections_part1 import (
    add_chapter_heading, add_section_heading, add_subsection_heading,
    add_figure_image, set_cell_background, set_table_borders, set_cell_margins
)

# ===================================================================================
# CHAPTER 4 – SYSTEM REQUIREMENTS
# ===================================================================================
def generate_chapter4(doc):
    add_chapter_heading(doc, "SYSTEM REQUIREMENTS", chap_num=4)
    
    add_section_heading(doc, "4.1 Hardware Requirements")
    doc.add_paragraph(
        "The computational architecture of the Warangal HealthRAG platform is engineered to balance neural inference efficiency "
        "with universal accessibility. Developing, vectorizing, and evaluating a dataset of 12,000 clinical records across dual sparse "
        "and dense vector spaces requires distinct hardware configurations for development and client-side access."
    )
    
    # Table 4.1: Hardware Specs
    t_hw = doc.add_table(rows=1, cols=3)
    t_hw.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_hw.columns[0].width = Inches(1.8)
    t_hw.columns[1].width = Inches(2.2)
    t_hw.columns[2].width = Inches(2.27)
    
    hdr = t_hw.rows[0].cells
    hdr[0].text = "Hardware Component"; hdr[1].text = "Minimum Specification"; hdr[2].text = "Recommended / Server Spec"
    for c in hdr:
        set_cell_background(c, "167D83")
        set_cell_margins(c, 100, 100, 140, 140)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"; r.font.size = Pt(10); r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    hw_specs = [
        ("Central Processor (CPU)", "Intel Core i5 / AMD Ryzen 5 (4 Cores)", "Intel Core i7 / AMD Ryzen 7 / Xeon (8+ Cores)"),
        ("System Memory (RAM)", "8 GB DDR4", "16 GB – 32 GB DDR4/DDR5"),
        ("Primary Storage", "256 GB SATA SSD", "512 GB NVMe M.2 SSD"),
        ("Dedicated GPU", "Not Required (CPU inference supported)", "NVIDIA RTX 3060 / T4 GPU (Google Colab 16GB VRAM)"),
        ("Network Interface", "Standard Broadband (10 Mbps)", "High-Speed Fiber (100+ Mbps) for Remote Tunneling"),
        ("Client Display", "1280 x 720 Resolution", "1920 x 1080 Full HD (Responsive light SaaS UI)")
    ]

    for comp, min_s, rec_s in hw_specs:
        row = t_hw.add_row()
        row.cells[0].text = comp; row.cells[1].text = min_s; row.cells[2].text = rec_s
        for idx, c in enumerate(row.cells):
            set_cell_margins(c, 50, 50, 100, 100)
            for r in c.paragraphs[0].runs:
                r.font.name = "Times New Roman"; r.font.size = Pt(9.5)
                if idx == 0: r.font.bold = True

    set_table_borders(t_hw)
    p_cap1 = doc.add_paragraph()
    p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c1 = p_cap1.add_run("Table 4.1: Minimum and Recommended Hardware Specifications")
    r_c1.font.name = "Times New Roman"; r_c1.font.size = Pt(10); r_c1.font.bold = True; r_c1.font.color.rgb = RGBColor(0x16, 0x7D, 0x83)

    add_section_heading(doc, "4.2 Software Requirements")
    doc.add_paragraph(
        "The software stack is built entirely on open-source, highly maintainable technologies. "
        "The operating system environment supports Windows 10/11, Ubuntu Linux (20.04/22.04 LTS), and cloud container runtimes such as Google Colab."
    )

    # Table 4.2: Software Environment
    t_sw = doc.add_table(rows=1, cols=3)
    t_sw.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sw.columns[0].width = Inches(1.8)
    t_sw.columns[1].width = Inches(2.2)
    t_sw.columns[2].width = Inches(2.27)
    
    h_sw = t_sw.rows[0].cells
    h_sw[0].text = "Software Layer"; h_sw[1].text = "Component Name"; h_sw[2].text = "Verified Version"
    for c in h_sw:
        set_cell_background(c, "167D83")
        set_cell_margins(c, 100, 100, 140, 140)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"; r.font.size = Pt(10); r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    sw_items = [
        ("Operating System", "Microsoft Windows / Ubuntu Linux", "Windows 11 (64-bit) / Linux 5.15 LTS"),
        ("Python Runtime", "CPython Python Interpreter", "Python 3.11.x / Python 3.12.x / 3.13.x"),
        ("Web Presentation Server", "Streamlit Framework", "Streamlit v1.38.0+"),
        ("Database Engine", "SQLite Embedded Relational DB", "SQLite 3.42.0+ (medical_system.db)"),
        ("IDE & Development", "Visual Studio Code / Cursor", "VS Code v1.93.0+ with Python Extension"),
        ("Cloud Notebook Runtime", "Google Colab", "Google Colab GPU Compute Environment"),
        ("Tunneling Utility", "Localtunnel / Ngrok", "localtunnel 2.0.2 for public endpoint hosting")
    ]
    for layer, cname, vver in sw_items:
        row = t_sw.add_row()
        row.cells[0].text = layer; row.cells[1].text = cname; row.cells[2].text = vver
        for idx, c in enumerate(row.cells):
            set_cell_margins(c, 50, 50, 100, 100)
            for r in c.paragraphs[0].runs:
                r.font.name = "Times New Roman"; r.font.size = Pt(9.5)
                if idx == 0: r.font.bold = True

    set_table_borders(t_sw)
    p_cap2 = doc.add_paragraph()
    p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c2 = p_cap2.add_run("Table 4.2: Software Environment and Execution Tooling")
    r_c2.font.name = "Times New Roman"; r_c2.font.size = Pt(10); r_c2.font.bold = True; r_c2.font.color.rgb = RGBColor(0x16, 0x7D, 0x83)

    add_section_heading(doc, "4.3 Programming Languages")
    doc.add_paragraph(
        "1. Python (v3.11+): Serves as the primary computational language powering backend logic, vector index construction, "
        "dense embedding generation, SQL database queries, and the Streamlit reactive UI. Python was selected for its rich ecosystem "
        "of high-performance numerical and NLP libraries."
    )
    doc.add_paragraph(
        "2. HTML5 & Custom CSS3: Embedded dynamically within Streamlit to enforce the enterprise Light SaaS design system, including custom card layouts, "
        "emergency red-flag banners, RAG Evidence Inspector drawers, and responsive table styling complying with clinical UI/UX standards."
    )
    doc.add_paragraph(
        "3. Structured Query Language (SQL): Used within Python's native sqlite3 module for relational schemas, transactional user management, "
        "query audit trails, and consultation history retrieval."
    )

    add_section_heading(doc, "4.4 Frameworks and Libraries")
    doc.add_paragraph(
        "The project relies on rigorously validated scientific and deep learning libraries:"
    )

    # Table 4.3: Frameworks & Libraries
    t_lib = doc.add_table(rows=1, cols=3)
    t_lib.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_lib.columns[0].width = Inches(1.8)
    t_lib.columns[1].width = Inches(1.5)
    t_lib.columns[2].width = Inches(2.97)
    
    h_lib = t_lib.rows[0].cells
    h_lib[0].text = "Library / Module"; h_lib[1].text = "Scope / Category"; h_lib[2].text = "Functional Responsibility in Platform"
    for c in h_lib:
        set_cell_background(c, "167D83")
        set_cell_margins(c, 100, 100, 140, 140)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"; r.font.size = Pt(10); r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    lib_items = [
        ("Streamlit", "Web Interface", "Reactive component rendering, session state management, and multi-page routing."),
        ("scikit-learn", "Machine Learning / IR", "TfidfVectorizer, sublinear TF scaling, n-gram extraction, and cosine_similarity."),
        ("faiss-cpu", "Vector Search", "IndexFlatIP construction, unit vector normalization, and L2 inner-product retrieval."),
        ("sentence-transformers", "Deep Learning / NLP", "all-MiniLM-L6-v2 neural bi-encoder model loading and 384-d dense embedding inference."),
        ("PyTorch (torch)", "Deep Learning Backend", "Underlying tensor computation and GPU/CPU matrix multiplication for Transformers."),
        ("pandas", "Data Manipulation", "Dataset ingestion, clinical record filtering, metadata slicing, and DataFrame operations."),
        ("numpy", "Numerical Computing", "High-performance vector operations, array reshaping, and dot-product calculations."),
        ("hashlib / binascii", "Security & Hashing", "PBKDF2-HMAC-SHA256 password hashing with random 16-byte cryptographic salts.")
    ]
    for lnam, lcat, lres in lib_items:
        row = t_lib.add_row()
        row.cells[0].text = lnam; row.cells[1].text = lcat; row.cells[2].text = lres
        for idx, c in enumerate(row.cells):
            set_cell_margins(c, 50, 50, 100, 100)
            for r in c.paragraphs[0].runs:
                r.font.name = "Times New Roman"; r.font.size = Pt(9.5)
                if idx == 0: r.font.bold = True

    set_table_borders(t_lib)
    p_cap3 = doc.add_paragraph()
    p_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c3 = p_cap3.add_run("Table 4.3: Python Frameworks, Libraries, and Core Dependencies")
    r_c3.font.name = "Times New Roman"; r_c3.font.size = Pt(10); r_c3.font.bold = True; r_c3.font.color.rgb = RGBColor(0x16, 0x7D, 0x83)

    add_section_heading(doc, "4.5 Dataset Requirements")
    doc.add_paragraph(
        "The knowledge foundation of the platform resides in 'cleaned_RAG_Warangal_medical_dataset.csv'. "
        "The dataset comprises exactly 12,000 synthetic clinical records structured across 91 attributes. Each record encapsulates "
        "a distinct clinical encounter containing patient demographic profile, primary presenting symptoms, secondary manifestations, "
        "provisional diagnosis, clinical department, assigned Warangal locality, recommended primary care facility, red-flag emergency status, "
        "and a consolidated RAG context text chunk."
    )

    # Table 4.4: Dataset Schema
    t_ds = doc.add_table(rows=1, cols=3)
    t_ds.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_ds.columns[0].width = Inches(1.8)
    t_ds.columns[1].width = Inches(1.5)
    t_ds.columns[2].width = Inches(2.97)
    
    h_ds = t_ds.rows[0].cells
    h_ds[0].text = "Feature Name"; h_ds[1].text = "Data Type"; h_ds[2].text = "Description and Clinical Role"
    for c in h_ds:
        set_cell_background(c, "167D83")
        set_cell_margins(c, 100, 100, 140, 140)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"; r.font.size = Pt(10); r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    ds_items = [
        ("patient_id", "String (Categorical)", "Unique record identifier (e.g., WP-SYN-010111) cited in Evidence Inspector."),
        ("condition", "String (Text)", "Provisional medical diagnosis (e.g., Dengue Fever, Asthma, Acute Gastroenteritis)."),
        ("department", "String (Categorical)", "One of 8 clinical specialties (General Medicine, Pediatrics, Cardiology, etc.)."),
        ("locality", "String (Categorical)", "One of 8 Warangal sub-districts (Hanamkonda, Kazipet, Parkal, Dharmasagar, etc.)."),
        ("care_facility_synthetic", "String (Text)", "Localized care centre (e.g., MGM Hospital, CHC Parkal, PHC Dharmasagar)."),
        ("red_flag", "Boolean / Integer", "Flag (0 or 1) indicating if symptoms require immediate casualty escalation."),
        ("retrieval_priority", "String (Categorical)", "Priority ranking tier (Critical, High, Medium, Routine)."),
        ("rag_context_text", "String (Free Text)", "Synthesized clinical narrative combining symptoms, diagnosis, and care advice.")
    ]
    for fnam, ftyp, fdes in ds_items:
        row = t_ds.add_row()
        row.cells[0].text = fnam; row.cells[1].text = ftyp; row.cells[2].text = fdes
        for idx, c in enumerate(row.cells):
            set_cell_margins(c, 50, 50, 100, 100)
            for r in c.paragraphs[0].runs:
                r.font.name = "Times New Roman"; r.font.size = Pt(9.5)
                if idx == 0: r.font.bold = True

    set_table_borders(t_ds)
    p_cap4 = doc.add_paragraph()
    p_cap4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c4 = p_cap4.add_run("Table 4.4: Warangal Medical Dataset Feature Schema and Clinical Mappings")
    r_c4.font.name = "Times New Roman"; r_c4.font.size = Pt(10); r_c4.font.bold = True; r_c4.font.color.rgb = RGBColor(0x16, 0x7D, 0x83)

    add_section_heading(doc, "4.6 Functional Requirements")
    doc.add_paragraph(
        "Functional requirements specify the operational capabilities and actions that the software system must perform:"
    )
    doc.add_paragraph(
        "- FR1 (User Registration & Authentication): The system shall permit citizens to register using name, email, phone, and password, storing password hashes via PBKDF2-HMAC-SHA256."
    )
    doc.add_paragraph(
        "- FR2 (Dual Vector Search Selection): The system shall enable users to toggle between Sparse TF-IDF Lexical Search and Dense FAISS Semantic Search at runtime."
    )
    doc.add_paragraph(
        "- FR3 (Emergency Red-Flag Interception): The system shall analyze queries prior to vector retrieval and instantly surface emergency hotlines (108 and MGM Hospital 0870-2441000) upon detecting critical triggers."
    )
    doc.add_paragraph(
        "- FR4 (Localized Clinical Filtering): The system shall allow users to restrict search context by medical specialty and Warangal geographic sub-districts."
    )
    doc.add_paragraph(
        "- FR5 (Grounded Response Synthesis): The system shall synthesize plain-English guidance strictly from the top-K retrieved records without speculating or hallucinating unverified treatments."
    )
    doc.add_paragraph(
        "- FR6 (Evidence Transparency): The system shall provide an expandable RAG Evidence Inspector exposing record IDs, similarity match percentages, and text snippets."
    )
    doc.add_paragraph(
        "- FR7 (Consultation Persistence): Authenticated users shall be able to save medical responses directly to their personal dashboard history."
    )
    doc.add_paragraph(
        "- FR8 (Administrative Telemetry): The system shall provide an isolated admin console displaying real-time usage metrics, latency distributions, and query audit trails."
    )
    doc.add_paragraph(
        "- FR9 (Role-Based Access Gate): The system shall restrict administrative views strictly to accounts possessing role='admin', returning an HTTP 403 Access Denied block for unauthorized attempts."
    )
    doc.add_paragraph(
        "- FR10 (Session State Continuity): The system shall maintain continuous chat history during active user sessions and allow one-click conversation clearing."
    )

    add_section_heading(doc, "4.7 Non-Functional Requirements")
    doc.add_paragraph(
        "Non-functional requirements define the architectural quality attributes, constraints, and performance benchmarks:"
    )
    doc.add_paragraph(
        "- Performance & Latency: The average retrieval latency shall not exceed 35 milliseconds for TF-IDF search and 65 milliseconds for FAISS dense search on standard multi-core CPUs."
    )
    doc.add_paragraph(
        "- Safety & Anti-Hallucination: The system must enforce a 100% strict context grounding constraint. If the maximum similarity score falls below 0.05 and no emergency is triggered, the system must decline to answer."
    )
    doc.add_paragraph(
        "- Security & Cryptography: Passwords must be hashed using PBKDF2 with 100,000 hashing rounds and unique 16-byte random salts. No plaintext passwords or administrative keys may appear in UI files."
    )
    doc.add_paragraph(
        "- Usability & Accessibility: The user interface must employ a clean Light Theme SaaS layout complying with WCAG AA contrast standards, avoiding dark mode text-inversion bugs."
    )
    doc.add_paragraph(
        "- Cross-Platform Reliability: The backend architecture must execute without modification across Windows workstation environments, local development servers, and remote Google Colab GPU instances."
    )
    doc.add_page_break()


# ===================================================================================
# CHAPTER 5 – SYSTEM ARCHITECTURE AND DESIGN
# ===================================================================================
def generate_chapter5(doc):
    add_chapter_heading(doc, "SYSTEM ARCHITECTURE AND DESIGN", chap_num=5)
    
    add_section_heading(doc, "5.1 Overall System Architecture")
    doc.add_paragraph(
        "The Warangal HealthRAG platform is engineered using a decoupled, layered software architecture designed for maximum reliability, "
        "transparency, and safety. The architecture divides into four distinct functional tiers: (1) the User Interaction Layer, "
        "(2) the Pre-Retrieval Safety and Triage Layer, (3) the Dual-Core Retrieval Engine, and (4) the Verified Knowledge and Persistence Layer. "
        "Figure 5.1 illustrates the end-to-end data flow and structural interactions between these components."
    )
    
    # Insert Figure 5.1
    add_figure_image(doc, "figures/fig_5_1_system_architecture.png", "Grounded Medical RAG Platform Architecture", "5.1")
    
    doc.add_paragraph(
        "When an inquiry is entered by a patient, it first passes through the Presentation Layer (Streamlit Light SaaS portal), where input "
        "normalization (lowercasing, whitespace trimming, and punctuation cleaning) occurs. Before invoking computationally expensive vector retrieval, "
        "the query is intercepted by the Pre-Retrieval Safety Guardrail. If life-threatening conditions are detected, an emergency alert is immediately dispatched. "
        "Concurrently, the query is dispatched to the chosen Vector Search Engine (sparse TF-IDF or dense FAISS), which performs similarity ranking against the "
        "pre-indexed 12,000 Warangal medical records. The top-K retrieved records are assembled into a structured prompt context and passed to the Grounded Response "
        "Synthesizer. Finally, the synthesized explanation, along with the RAG Evidence Inspector metadata, is rendered to the user and committed to the SQLite audit database."
    )

    add_section_heading(doc, "5.2 Data Flow Diagrams (DFD Level 0 & Level 1)")
    doc.add_paragraph(
        "Data Flow Diagrams provide a graphical representation of the flow of data through the information system. "
        "Figure 5.2 displays both the Level 0 Context Diagram and the Level 1 Process Decomposition."
    )

    # Insert Figure 5.2
    add_figure_image(doc, "figures/fig_5_2_dfd.png", "Data Flow Diagram (DFD Level 0 Context & Level 1 Process)", "5.2")

    doc.add_paragraph(
        "In the Level 0 Context Diagram, the external entities (Patient/Citizen and Emergency Services) interact with the central Warangal HealthRAG process. "
        "The patient inputs symptom queries and receives grounded medical guidance, while emergency triggers automatically route alerts to external healthcare providers. "
        "In the Level 1 Process Decomposition, the system breaks down into four sequential processes: Process 1.0 (Authentication & Session State), "
        "Process 2.0 (Pre-Retrieval Red-Flag Triage), Process 3.0 (Vector Index Retrieval over Data Store D1), and Process 4.0 (Grounded Synthesis & Audit Logging)."
    )

    add_section_heading(doc, "5.3 UML Use Case Diagram")
    doc.add_paragraph(
        "The Unified Modeling Language (UML) Use Case diagram defines the behavioral boundaries of the platform and the interactions between "
        "primary human actors and secondary services. As illustrated in Figure 5.3, the system models three primary actors: (1) Patient / Citizen, "
        "(2) Clinical Administrator, and (3) Emergency Medical Services (Telangana 108 / MGM Hospital Casualty)."
    )

    # Insert Figure 5.3
    add_figure_image(doc, "figures/fig_5_3_use_case.png", "UML Use Case Diagram for Patient and Administrative Actors", "5.3")

    doc.add_paragraph(
        "The Patient actor can register, authenticate, submit medical questions, apply locality/department filters, inspect grounded RAG evidence, "
        "and save consultations to their personal dashboard. The Clinical Administrator actor inherits all patient privileges while gaining exclusive access "
        "to the Administrative Telemetry Console to inspect system latency, active users, and complete query audit logs. The Emergency Medical Services actor "
        "serves as a recipient entity linked via automated hotlines."
    )

    add_section_heading(doc, "5.4 UML Sequence Diagram")
    doc.add_paragraph(
        "The UML Sequence Diagram captures the chronological order of method invocations and message passing across system lifecycles. "
        "Figure 5.4 outlines the step-by-step query execution lifecycle."
    )

    # Insert Figure 5.4
    add_figure_image(doc, "figures/fig_5_4_sequence.png", "UML Sequence Diagram of Query Triage and Vector Retrieval Flow", "5.4")

    doc.add_paragraph(
        "The sequence begins when the patient submits a query via the Streamlit interface. The UI immediately calls 'check_red_flags()' on the safety engine. "
        "If an emergency trigger is detected, the UI prepares the Emergency Alert Card. Next, the UI invokes 'get_relevant_chunks()' on the Dual RAG Engine. "
        "The engine computes vector similarities, extracts top-K records from the DataFrame, and returns ranked records. The UI executes grounded synthesis, "
        "commits the transaction to the SQLite database via 'auth_db.log_query()', and renders the final response to the user."
    )

    add_section_heading(doc, "5.5 Module Descriptions")
    doc.add_paragraph(
        "1. Authentication & Security Manager (auth_db.py): Responsible for user registration, case-insensitive email matching, PBKDF2 password hashing, "
        "session authorization, and role verification ('admin' vs 'user'). Prevents credential exposure in frontend templates."
    )
    doc.add_paragraph(
        "2. Emergency Red-Flag Triage Guardrail: A rule-based regex engine that evaluates incoming queries against high-acuity medical triggers (e.g., myocardial infarction, "
        "stroke, acute hemorrhage) and overrides standard retrieval with direct emergency hotlines."
    )
    doc.add_paragraph(
        "3. Dual-Core Vector Retrieval Engine (backend.py): Encapsulates both the sparse TF-IDF n-gram vectorizer and the dense FAISS IndexFlatIP vector index. "
        "Handles feature extraction, similarity scoring, locality filtering, and top-K chunk extraction."
    )
    doc.add_paragraph(
        "4. Grounded Response Synthesizer: Implements anti-hallucination prompt conditioning, synthesizing conversational explanations strictly from retrieved clinical chunks."
    )
    doc.add_paragraph(
        "5. RAG Evidence Inspector: An interactive UI component attached to every assistant response that displays mathematical similarity scores, synthetic patient IDs (WP-SYN-XXXX), "
        "department classifications, and raw source excerpts."
    )
    doc.add_paragraph(
        "6. Administrative Telemetry Console: A secured monitoring portal providing administrators with live query latency histograms, department distribution metrics, "
        "user status toggles, and system audit logs."
    )

    add_section_heading(doc, "5.6 Database and Dataset Structure")
    doc.add_paragraph(
        "The platform utilizes an embedded SQLite relational database ('medical_system.db') for persistent user management and compliance audit logging. "
        "The database schema is organized into four core relational tables:"
    )

    # Table 5.1: Users Table
    t_u = doc.add_table(rows=1, cols=4)
    t_u.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_u.columns[0].width = Inches(1.3); t_u.columns[1].width = Inches(1.2); t_u.columns[2].width = Inches(1.2); t_u.columns[3].width = Inches(2.57)
    
    h_u = t_u.rows[0].cells
    h_u[0].text = "Column Name"; h_u[1].text = "Data Type"; h_u[2].text = "Constraints"; h_u[3].text = "Description"
    for c in h_u:
        set_cell_background(c, "167D83")
        set_cell_margins(c, 80, 80, 100, 100)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    u_rows = [
        ("id", "INTEGER", "PRIMARY KEY AUTO", "Unique surrogate key for each registered user."),
        ("full_name", "TEXT", "NOT NULL", "Full legal name of the citizen or administrator."),
        ("email", "TEXT", "UNIQUE NOT NULL", "Unique normalized email address used for login."),
        ("phone", "TEXT", "NULLABLE", "Contact telephone number."),
        ("password_hash", "TEXT", "NOT NULL", "PBKDF2-HMAC-SHA256 salt and hash string."),
        ("role", "TEXT", "DEFAULT 'user'", "Authorization level ('user' or 'admin')."),
        ("status", "TEXT", "DEFAULT 'active'", "Account status ('active' or 'suspended')."),
        ("created_at", "TIMESTAMP", "DEFAULT CURRENT", "Timestamp of account creation.")
    ]
    for cnam, ctyp, ccon, cdes in u_rows:
        row = t_u.add_row()
        row.cells[0].text = cnam; row.cells[1].text = ctyp; row.cells[2].text = ccon; row.cells[3].text = cdes
        for idx, c in enumerate(row.cells):
            set_cell_margins(c, 40, 40, 80, 80)
            for r in c.paragraphs[0].runs:
                r.font.name = "Times New Roman"; r.font.size = Pt(9)
                if idx == 0: r.font.bold = True

    set_table_borders(t_u)
    p_cap5 = doc.add_paragraph()
    p_cap5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c5 = p_cap5.add_run("Table 5.1: Relational Database Schema: Users Table (users)")
    r_c5.font.name = "Times New Roman"; r_c5.font.size = Pt(10); r_c5.font.bold = True; r_c5.font.color.rgb = RGBColor(0x16, 0x7D, 0x83)

    # Table 5.2: Query Logs Table
    t_ql = doc.add_table(rows=1, cols=4)
    t_ql.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_ql.columns[0].width = Inches(1.3); t_ql.columns[1].width = Inches(1.2); t_ql.columns[2].width = Inches(1.2); t_ql.columns[3].width = Inches(2.57)
    
    h_ql = t_ql.rows[0].cells
    h_ql[0].text = "Column Name"; h_ql[1].text = "Data Type"; h_ql[2].text = "Constraints"; h_ql[3].text = "Description"
    for c in h_ql:
        set_cell_background(c, "167D83")
        set_cell_margins(c, 80, 80, 100, 100)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    ql_rows = [
        ("id", "INTEGER", "PRIMARY KEY AUTO", "Unique identifier for query transaction."),
        ("user_id", "INTEGER", "NULLABLE", "Foreign key reference to users.id."),
        ("user_email", "TEXT", "NOT NULL", "Email of requesting user or 'guest'."),
        ("query_text", "TEXT", "NOT NULL", "Raw natural language symptom query."),
        ("response_text", "TEXT", "NOT NULL", "Synthesized grounded medical response."),
        ("is_emergency", "INTEGER", "DEFAULT 0", "Flag (1 or 0) indicating emergency detection."),
        ("matched_triggers", "TEXT", "NULLABLE", "Comma-separated list of triggered red-flag keywords."),
        ("latency_ms", "REAL", "NOT NULL", "End-to-end retrieval and synthesis latency in ms."),
        ("engine_used", "TEXT", "NOT NULL", "Retrieval engine ('TF-IDF' or 'FAISS')."),
        ("department", "TEXT", "NULLABLE", "Top matched clinical specialty."),
        ("locality", "TEXT", "NULLABLE", "Top matched Warangal geographic locality."),
        ("timestamp", "TIMESTAMP", "DEFAULT CURRENT", "Exact UTC timestamp of query execution.")
    ]
    for cnam, ctyp, ccon, cdes in ql_rows:
        row = t_ql.add_row()
        row.cells[0].text = cnam; row.cells[1].text = ctyp; row.cells[2].text = ccon; row.cells[3].text = cdes
        for idx, c in enumerate(row.cells):
            set_cell_margins(c, 40, 40, 80, 80)
            for r in c.paragraphs[0].runs:
                r.font.name = "Times New Roman"; r.font.size = Pt(9)
                if idx == 0: r.font.bold = True

    set_table_borders(t_ql)
    p_cap6 = doc.add_paragraph()
    p_cap6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c6 = p_cap6.add_run("Table 5.2: Relational Database Schema: Clinical Query Logs (query_logs)")
    r_c6.font.name = "Times New Roman"; r_c6.font.size = Pt(10); r_c6.font.bold = True; r_c6.font.color.rgb = RGBColor(0x16, 0x7D, 0x83)
    doc.add_page_break()


# ===================================================================================
# CHAPTER 6 – METHODOLOGY
# ===================================================================================
def generate_chapter6(doc):
    add_chapter_heading(doc, "METHODOLOGY", chap_num=6)
    
    add_section_heading(doc, "6.1 Dataset Collection and Preparation")
    doc.add_paragraph(
        "The empirical validity of any Retrieval-Augmented Generation system depends entirely on the clinical accuracy, diversity, and structural "
        "integrity of its underlying knowledge base. For this research, a dedicated dataset of 12,000 synthetic patient records was curated to model "
        "realistic clinical presentations across the Warangal healthcare ecosystem. The dataset was designed to balance common acute infections, chronic non-communicable "
        "diseases, pediatric illnesses, and high-acuity cardiovascular and neurological emergencies."
    )
    doc.add_paragraph(
        "The dataset covers eight distinct clinical departments, ensuring comprehensive medical coverage. Table 6.1 delineates the record distribution across specialties:"
    )

    # Table 6.1: Department Distribution
    t_dept = doc.add_table(rows=1, cols=3)
    t_dept.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_dept.columns[0].width = Inches(2.2); t_dept.columns[1].width = Inches(1.8); t_dept.columns[2].width = Inches(2.27)
    
    h_dept = t_dept.rows[0].cells
    h_dept[0].text = "Medical Department"; h_dept[1].text = "Record Count"; h_dept[2].text = "Proportion (%)"
    for c in h_dept:
        set_cell_background(c, "167D83")
        set_cell_margins(c, 80, 80, 100, 100)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    dept_rows = [
        ("General Medicine", "2,400", "20.0%"),
        ("Pediatrics", "1,800", "15.0%"),
        ("Cardiology", "1,500", "12.5%"),
        ("Pulmonology", "1,500", "12.5%"),
        ("Gastroenterology", "1,400", "11.67%"),
        ("Orthopedics", "1,200", "10.0%"),
        ("Dermatology", "1,100", "9.17%"),
        ("ENT (Otolaryngology)", "1,100", "9.17%"),
        ("TOTAL VERIFIED RECORDS", "12,000", "100.0%")
    ]
    for dnam, dcnt, dpct in dept_rows:
        row = t_dept.add_row()
        row.cells[0].text = dnam; row.cells[1].text = dcnt; row.cells[2].text = dpct
        for idx, c in enumerate(row.cells):
            set_cell_margins(c, 40, 40, 80, 80)
            for r in c.paragraphs[0].runs:
                r.font.name = "Times New Roman"; r.font.size = Pt(9)
                if dnam.startswith("TOTAL") or idx == 0: r.font.bold = True

    set_table_borders(t_dept)
    p_cap7 = doc.add_paragraph()
    p_cap7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c7 = p_cap7.add_run("Table 6.1: Distribution of Clinical Records Across 8 Medical Departments")
    r_c7.font.name = "Times New Roman"; r_c7.font.size = Pt(10); r_c7.font.bold = True; r_c7.font.color.rgb = RGBColor(0x16, 0x7D, 0x83)

    doc.add_paragraph(
        "Similarly, patient records were mapped evenly across eight prominent geographical sub-districts and administrative mandals of Warangal. "
        "Table 6.2 outlines the geographic distribution of patient cohorts across Warangal district:"
    )

    # Table 6.2: Locality Distribution
    t_loc = doc.add_table(rows=1, cols=3)
    t_loc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_loc.columns[0].width = Inches(2.2); t_loc.columns[1].width = Inches(1.8); t_loc.columns[2].width = Inches(2.27)
    
    h_loc = t_loc.rows[0].cells
    h_loc[0].text = "Warangal Locality"; h_loc[1].text = "Record Count"; h_loc[2].text = "Representative Healthcare Centre"
    for c in h_loc:
        set_cell_background(c, "167D83")
        set_cell_margins(c, 80, 80, 100, 100)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    loc_rows = [
        ("Warangal Central", "1,850", "MGM Hospital / District Hospital"),
        ("Hanamkonda", "1,800", "Government Maternity & General Hospital"),
        ("Kazipet", "1,650", "Railway Hospital / Area Community Hospital"),
        ("Parkal", "1,450", "Parkal Community Health Centre (CHC)"),
        ("Dharmasagar", "1,350", "Dharmasagar Primary Health Centre (PHC)"),
        ("Geesugonda", "1,300", "Geesugonda Primary Health Centre (PHC)"),
        ("Hasanparthy", "1,350", "Hasanparthy Primary Health Centre (PHC)"),
        ("Wardhannapet", "1,250", "Wardhannapet Community Health Centre (CHC)"),
        ("TOTAL COHORT", "12,000", "District-Wide Health Network")
    ]
    for lnam, lcnt, lfac in loc_rows:
        row = t_loc.add_row()
        row.cells[0].text = lnam; row.cells[1].text = lcnt; row.cells[2].text = lfac
        for idx, c in enumerate(row.cells):
            set_cell_margins(c, 40, 40, 80, 80)
            for r in c.paragraphs[0].runs:
                r.font.name = "Times New Roman"; r.font.size = Pt(9)
                if lnam.startswith("TOTAL") or idx == 0: r.font.bold = True

    set_table_borders(t_loc)
    p_cap8 = doc.add_paragraph()
    p_cap8.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c8 = p_cap8.add_run("Table 6.2: Distribution of Patient Cohort Across 8 Warangal Localities")
    r_c8.font.name = "Times New Roman"; r_c8.font.size = Pt(10); r_c8.font.bold = True; r_c8.font.color.rgb = RGBColor(0x16, 0x7D, 0x83)

    add_section_heading(doc, "6.2 Data Cleaning and Validation")
    doc.add_paragraph(
        "Prior to indexing, raw clinical records underwent an automated validation and normalization pipeline. Records were audited for missing "
        "critical fields (patient ID, condition, department, locality). Redundant whitespace characters and inconsistent delimiters were removed. "
        "Categorical attributes were standardized to title-case strings to eliminate case-divergence errors during SQL and Pandas querying."
    )

    add_section_heading(doc, "6.3 Text Preprocessing Pipeline")
    doc.add_paragraph(
        "To maximize retrieval recall across both keyword-based and semantic queries, a consolidated search document ('search_text') was dynamically "
        "synthesized for each record. The search document concatenates the clinical condition, primary symptoms, medical department, geographical locality, "
        "recommended care facility, and explicit red-flag annotations into an information-dense passage:"
    )
    doc.add_paragraph(
        "search_text = f\"Condition: {condition} | Department: {dept} | Locality: {locality} | Symptoms: {symptoms} | Facility: {facility} | Notes: {context_text}\""
    )
    doc.add_paragraph(
        "This concatenation ensures that queries referencing symptoms alone ('wheezing and coughing'), localities alone ('hospitals in Parkal'), or composite expressions "
        "('child with fever in Kazipet') establish high semantic and lexical overlap with the target record."
    )

    add_section_heading(doc, "6.4 TF-IDF Retrieval and Sublinear Term Scaling")
    doc.add_paragraph(
        "The sparse retrieval engine constructs an n-gram TF-IDF matrix over the 12,000 document passages using scikit-learn's TfidfVectorizer. "
        "The vectorizer is configured with n-gram range (1, 2), capturing both unigrams ('asthma') and critical medical bigrams ('chest pain', 'blood pressure'). "
        "Sublinear term frequency scaling is enabled (sublinear_tf=True), replacing linear term frequency with logarithmic scaling (1 + log(TF)). "
        "This mathematical adjustment prevents repetitive mentions of common anatomical words from distorting the cosine similarity score."
    )

    add_section_heading(doc, "6.5 FAISS Index Construction")
    doc.add_paragraph(
        "The dense retrieval engine constructs a vector index using the Facebook AI Similarity Search (FAISS) library. Each of the 12,000 search text chunks "
        "is mapped into a 384-dimensional continuous dense vector using the all-MiniLM-L6-v2 neural bi-encoder. Each resulting embedding vector is L2 unit-normalized:"
    )
    doc.add_paragraph(
        "v_norm = v / ||v||_2  where ||v||_2 = sqrt(sum(v_i^2))"
    )
    doc.add_paragraph(
        "The normalized vectors are indexed into a FAISS 'IndexFlatIP' (Inner Product) structure. In unit-normalized space, the inner product is mathematically "
        "equivalent to cosine similarity: IP(u, v) = sum(u_i * v_i) = cos(theta). The IndexFlatIP structure guarantees exact nearest-neighbor retrieval without "
        "the quantization loss associated with inverted file (IVF) or hierarchical navigable small world (HNSW) approximations."
    )

    add_section_heading(doc, "6.6 Sentence Embedding Generation")
    doc.add_paragraph(
        "Sentence embeddings are computed using the sentence-transformers architecture. When a user submits an arbitrary natural language query q, "
        "it is tokenized with a maximum sequence length of 256 tokens and passed through the 6-layer MiniLM Transformer. Mean pooling is applied over the contextualized "
        "output token embeddings to derive a fixed-size 384-dimensional sentence representation. The embedding vector is normalized and passed directly to the FAISS search routine."
    )

    add_section_heading(doc, "6.7 Semantic Similarity Search")
    doc.add_paragraph(
        "Figure 6.1 illustrates the dual retrieval architecture. Queries are processed either through the sparse TF-IDF stream or the dense FAISS stream, "
        "yielding ranked candidate records sorted in descending order of similarity score."
    )

    # Insert Figure 6.1
    add_figure_image(doc, "figures/fig_6_1_dual_rag_pipeline.png", "Dual RAG Pipeline (Sparse Lexical vs. Dense Semantic Streams)", "6.1")

    add_section_heading(doc, "6.8 Top-K Document Retrieval")
    doc.add_paragraph(
        "The system extracts the top-K highest-scoring records (defaulting to K=5, adjustable from 3 to 8 via the UI slider). If the user has specified categorical "
        "filters for medical department or Warangal locality, metadata filtering is applied. If filtered candidates are insufficient, the engine gracefully falls back "
        "to global corpus ranking to prevent zero-result failures."
    )

    add_section_heading(doc, "6.9 Grounded Response Generation")
    doc.add_paragraph(
        "Response synthesis is strictly bounded by the retrieved clinical records. Rather than allowing an unconstrained language model to speculate on diagnoses, "
        "the synthesizer extracts verified clinical guidance, prescribed care actions, and facility recommendations directly from the top-scoring records. "
        "The explanation is structured in plain English according to a standard clinical format: (1) Understanding Your Symptoms, (2) Grounded Clinical Observations, "
        "(3) Recommended Local Action & Healthcare Facility, and (4) Mandatory Professional Consultation Advice."
    )

    add_section_heading(doc, "6.10 Emergency Red-Flag Detection Guardrail")
    doc.add_paragraph(
        "A cornerstone safety contribution of this project is the Pre-Retrieval Emergency Red-Flag Triage Guardrail. "
        "Figure 6.2 outlines the operational logic of the emergency detection filter."
    )

    # Insert Figure 6.2
    add_figure_image(doc, "figures/fig_6_2_emergency_workflow.png", "Rule-Based Emergency Red-Flag Triage Flowchart", "6.2")

    doc.add_paragraph(
        "Before vector retrieval executes, the user query is evaluated against a compiled regular expression dictionary of acute life-threatening medical indicators. "
        "Table 6.3 details the clinical categories, keyword triggers, and immediate escalations enforced by the guardrail:"
    )

    # Table 6.3: Red Flag Rules
    t_rf = doc.add_table(rows=1, cols=3)
    t_rf.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_rf.columns[0].width = Inches(1.8); t_rf.columns[1].width = Inches(2.2); t_rf.columns[2].width = Inches(2.27)
    
    h_rf = t_rf.rows[0].cells
    h_rf[0].text = "Clinical Emergency Category"; h_rf[1].text = "Regex Keyword Triggers"; h_rf[2].text = "Immediate Clinical Escalation"
    for c in h_rf:
        set_cell_background(c, "D9534F")
        set_cell_margins(c, 80, 80, 100, 100)
        for r in c.paragraphs[0].runs:
            r.font.name = "Times New Roman"; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    rf_rows = [
        ("Acute Coronary Syndrome", "chest pain, heart attack, radiating arm pain, cardiac arrest", "Surface 108 Ambulance + MGM Hospital Casualty (0870-2441000)"),
        ("Acute Respiratory Distress", "shortness of breath, cannot breathe, choking, severe asthma", "Surface 108 Ambulance + Emergency Oxygen Triage Alert"),
        ("Acute Neurological (Stroke)", "stroke, face drooping, slurred speech, paralysis, seizure", "Immediate Stroke Emergency Alert + Rapid MGM Casualty Transfer"),
        ("Unconsciousness & Trauma", "unconscious, fainted, unresponsive, severe head trauma", "Immediate 108 Ambulance Alert + Resuscitation Directive"),
        ("Acute Hemorrhage", "heavy bleeding, coughing blood, severe vomiting blood", "Direct Casualty Escalation + Hemorrhage Stabilization Alert")
    ]
    for ccat, ctrg, cesc in rf_rows:
        row = t_rf.add_row()
        row.cells[0].text = ccat; row.cells[1].text = ctrg; row.cells[2].text = cesc
        for idx, c in enumerate(row.cells):
            set_cell_margins(c, 40, 40, 80, 80)
            for r in c.paragraphs[0].runs:
                r.font.name = "Times New Roman"; r.font.size = Pt(9)
                if idx == 0: r.font.bold = True

    set_table_borders(t_rf, color="D9534F")
    p_cap9 = doc.add_paragraph()
    p_cap9.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c9 = p_cap9.add_run("Table 6.3: Emergency Red-Flag Regex Rule Definitions and Clinical Escalations")
    r_c9.font.name = "Times New Roman"; r_c9.font.size = Pt(10); r_c9.font.bold = True; r_c9.font.color.rgb = RGBColor(0xD9, 0x53, 0x4F)

    add_section_heading(doc, "6.11 Evidence Verification and Attribution")
    doc.add_paragraph(
        "To ensure radical transparency and counter the 'black-box' nature of AI systems, every synthesized answer is bound to its retrieved source evidence. "
        "The RAG Evidence Inspector reveals the exact synthetic record IDs (e.g., WP-SYN-010111), mathematical similarity percentages, retrieval priority tiers, "
        "and source text chunks. This allows patients to understand the factual basis of the guidance and enables supervising clinicians to audit the system's reasoning."
    )
    doc.add_page_break()

print("Part 2: Chapters 4, 5, 6 written successfully!")
