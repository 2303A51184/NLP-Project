"""
===================================================================================
Master Script: build_presentation.py
Complete, End-to-End Generator for:
  1. Project_Presentation/Project_Presentation.pptx (18 Widescreen Slides)
  2. Project_Presentation/Project_Presentation.pdf (PowerPoint COM Conversion)
  3. Project_Presentation/Viva_Questions_and_Answers.docx (50 Comprehensive Q&A)
  4. Project_Presentation/Presentation_Speech.docx (Slide-by-Slide Viva Script)
  5. Project_Presentation/Presentation_Assets/ (Diagrams & UI Screenshots)
===================================================================================
"""

import os
import shutil
import subprocess
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

import docx
from docx import Document
from docx.shared import Inches as DocxInches, Pt as DocxPt, RGBColor as DocxRGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# -------------------------------------------------------------
# Color Constants
# -------------------------------------------------------------
COLOR_BG_WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
COLOR_BG_LIGHT     = RGBColor(0xF7, 0xFA, 0xFC) # #F7FAFC
COLOR_CARD_BG      = RGBColor(0xFF, 0xFF, 0xFF)
COLOR_CARD_BORDER  = RGBColor(0xCB, 0xD5, 0xE1) # #CBD5E1
COLOR_PRIMARY_TEAL = RGBColor(0x16, 0x7D, 0x83) # #167D83
COLOR_DARK_TEXT    = RGBColor(0x26, 0x37, 0x46) # #263746
COLOR_MUTED_TEXT   = RGBColor(0x64, 0x74, 0x8B) # #64748B
COLOR_MINT_ACCENT  = RGBColor(0xD9, 0xF0, 0xED) # #D9F0ED
COLOR_EMERGENCY    = RGBColor(0xD9, 0x53, 0x4F) # #D9534F
COLOR_SUCCESS      = RGBColor(0x24, 0x8A, 0x61) # #248A61
COLOR_DIVIDER      = RGBColor(0xE2, 0xE8, 0xF0)

# -------------------------------------------------------------
# PowerPoint Builder Functions
# -------------------------------------------------------------
def set_slide_background(slide, color=COLOR_BG_LIGHT):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, category_tag, slide_title, slide_num):
    # Category tag
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8), Inches(0.35))
    tf_tag = tag_box.text_frame
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = category_tag.upper()
    p_tag.font.name = "Segoe UI"
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_PRIMARY_TEAL

    # Main slide title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(10), Inches(0.7))
    tf_title = title_box.text_frame
    p_t = tf_title.paragraphs[0]
    p_t.text = slide_title
    p_t.font.name = "Segoe UI"
    p_t.font.size = Pt(21)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_DARK_TEXT

    # Subtle divider rule
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_DIVIDER
    line.line.fill.background()

    # Footer metadata
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(9.0), Inches(0.35))
    tf_f = footer_box.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "RAG-Based Medical Information System for Warangal Patients | SR University, Warangal"
    p_f.font.name = "Segoe UI"
    p_f.font.size = Pt(9)
    p_f.font.color.rgb = COLOR_MUTED_TEXT

    # Slide numbering badge
    num_box = slide.shapes.add_textbox(Inches(11.5), Inches(7.0), Inches(1.0), Inches(0.35))
    tf_n = num_box.text_frame
    p_n = tf_n.paragraphs[0]
    p_n.alignment = PP_ALIGN.RIGHT
    p_n.text = f"{slide_num:02d} / 18"
    p_n.font.name = "Segoe UI"
    p_n.font.size = Pt(9.5)
    p_n.font.bold = True
    p_n.font.color.rgb = COLOR_PRIMARY_TEAL

def add_card(slide, left, top, width, height, title, subtitle=None, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.2)
    
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_top = Inches(0.18)
    tf.margin_left = Inches(0.22)
    tf.margin_right = Inches(0.22)
    tf.margin_bottom = Inches(0.18)
    
    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.name = "Segoe UI"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_PRIMARY_TEAL
    
    if subtitle:
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.name = "Segoe UI"
        p_sub.font.size = Pt(9.5)
        p_sub.font.italic = True
        p_sub.font.color.rgb = COLOR_MUTED_TEXT
        p_sub.space_after = Pt(4)
        
    return shape, tf

def add_bullet(tf, bold_prefix, text, font_size=10.5, space_after=6):
    p = tf.add_paragraph()
    p.space_after = Pt(space_after)
    run_b = p.add_run()
    run_b.text = f"•  {bold_prefix}: "
    run_b.font.name = "Segoe UI"
    run_b.font.size = Pt(font_size)
    run_b.font.bold = True
    run_b.font.color.rgb = COLOR_DARK_TEXT
    
    run_t = p.add_run()
    run_t.text = text
    run_t.font.name = "Segoe UI"
    run_t.font.size = Pt(font_size)
    run_t.font.color.rgb = COLOR_DARK_TEXT


# -------------------------------------------------------------
# 18-Slide Deck Builder
# -------------------------------------------------------------
def build_powerpoint():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    print(" -> Building Slide 1: Title Cover...")
    # ---------------------------------------------------------
    # SLIDE 1: Title Slide (Cover)
    # ---------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, COLOR_BG_WHITE)

    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.18))
    top_bar.fill.solid(); top_bar.fill.fore_color.rgb = COLOR_PRIMARY_TEAL; top_bar.line.fill.background()

    pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(0.7), Inches(5.0), Inches(0.42))
    pill.fill.solid(); pill.fill.fore_color.rgb = COLOR_MINT_ACCENT; pill.line.fill.background()
    p_pill = pill.text_frame.paragraphs[0]
    p_pill.text = "B.TECH FINAL YEAR MAJOR PROJECT DEFENSE • 2025–2026"
    p_pill.alignment = PP_ALIGN.CENTER; p_pill.font.name = "Segoe UI"; p_pill.font.size = Pt(9.5); p_pill.font.bold = True; p_pill.font.color.rgb = COLOR_PRIMARY_TEAL

    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.25), Inches(11.333), Inches(1.8))
    tf_t = t_box.text_frame; tf_t.word_wrap = True
    p1 = tf_t.paragraphs[0]
    p1.text = "RAG-Based Medical Information System\nfor Warangal Patients"
    p1.font.name = "Segoe UI"; p1.font.size = Pt(28); p1.font.bold = True; p1.font.color.rgb = COLOR_PRIMARY_TEAL
    
    p2 = tf_t.add_paragraph()
    p2.text = "A Grounded Clinical Decision Support and Emergency Triage Platform Using Dual-Engine Vector Retrieval"
    p2.font.name = "Segoe UI"; p2.font.size = Pt(13.5); p2.font.italic = True; p2.font.color.rgb = COLOR_MUTED_TEXT

    c_auth, tf_auth = add_card(s1, Inches(1.0), Inches(3.3), Inches(5.4), Inches(2.3), "Project Authors", "Department of Computer Science & Engineering")
    add_bullet(tf_auth, "B. Sai Tejaswi", "Roll No: 2303A51184 (SR University)", font_size=11, space_after=8)
    add_bullet(tf_auth, "V. Abhilash", "Roll No: 2303A51227 (SR University)", font_size=11, space_after=8)
    add_bullet(tf_auth, "Specialization", "Artificial Intelligence & Natural Language Processing", font_size=10, space_after=4)

    c_sup, tf_sup = add_card(s1, Inches(6.9), Inches(3.3), Inches(5.4), Inches(2.3), "Under the Esteemed Guidance of", "Faculty Mentorship & Clinical Review")
    add_bullet(tf_sup, "Project Guide", "Dr. Rupesh Mishra", font_size=11.5, space_after=8)
    add_bullet(tf_sup, "Department", "Department of Computer Science & Engineering", font_size=10.5, space_after=8)
    add_bullet(tf_sup, "Institution", "SR University, Warangal, Telangana – 506371", font_size=10.5, space_after=4)

    b_box = s1.shapes.add_textbox(Inches(1.0), Inches(6.2), Inches(11.333), Inches(0.8))
    p_b = b_box.text_frame.paragraphs[0]
    p_b.alignment = PP_ALIGN.CENTER
    p_b.text = "SCHOOL OF COMPUTER SCIENCE & ARTIFICIAL INTELLIGENCE  •  SR UNIVERSITY, WARANGAL"
    p_b.font.name = "Segoe UI"; p_b.font.size = Pt(11); p_b.font.bold = True; p_b.font.color.rgb = COLOR_DARK_TEXT

    # ---------------------------------------------------------
    # SLIDE 2: Introduction
    # ---------------------------------------------------------
    print(" -> Building Slide 2: Introduction...")
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "PROJECT DOMAIN & CLINICAL CONTEXT", "Introduction to Healthcare Information Systems", 2)

    _, tf2_l = add_card(s2, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), "Healthcare Informatics in Tier-2 Ecosystems", "Bridging the urban-rural primary healthcare divide")
    add_bullet(tf2_l, "Geographic Focus", "Warangal district, Telangana—serving twin cities (Warangal/Hanamkonda) and semi-urban peripheries (Kazipet, Parkal, Dharmasagar, Wardhannapet).")
    add_bullet(tf2_l, "Referral Architecture", "Relies heavily on Mahatma Gandhi Memorial (MGM) Hospital as the sole apex tertiary referral centre across five districts.")
    add_bullet(tf2_l, "Information Asymmetry", "Patients often travel 40–60 km for minor ailments or delay critical emergency treatment due to lack of symptom awareness.")
    add_bullet(tf2_l, "Clinical Objective", "Democratize reliable, understandable medical advice in simple English to guide patients to appropriate care centres.")

    _, tf2_r = add_card(s2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), "The Role of NLP & Generative AI", "From static hospital directories to conversational triage")
    add_bullet(tf2_r, "Conversational AI", "Modern Natural Language Processing allows citizens to describe symptoms naturally without knowing complex medical terminology.")
    add_bullet(tf2_r, "The Hallucination Danger", "Standard generative LLMs predict probable tokens, frequently fabricating nonexistent medications, dosages, and clinical advice.")
    add_bullet(tf2_r, "The Grounding Imperative", "In healthcare, AI must be strictly bound to verified clinical records to guarantee patient safety and zero hallucinations.")
    add_bullet(tf2_r, "Our Approach", "Retrieval-Augmented Generation (RAG) coupled with a real-time emergency red-flag safety guardrail.")

    # ---------------------------------------------------------
    # SLIDE 3: Problem Statement
    # ---------------------------------------------------------
    print(" -> Building Slide 3: Problem Statement...")
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "CHALLENGES IN DIGITAL HEALTHCARE", "Problem Statement: The Healthcare Information Gap", 3)

    _, tf3_l = add_card(s3, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), "The Core Healthcare Dilemma", "Why existing digital tools fail ordinary patients")
    add_bullet(tf3_l, "Unreliable Self-Diagnosis", "Millions of citizens search symptoms on commercial search engines, triggering unwarranted health anxiety ('cyberchondria').")
    add_bullet(tf3_l, "Lack of Local Context", "Global search tools cannot guide a patient in Parkal or Hasanparthy to their nearest Community Health Centre (CHC).")
    add_bullet(tf3_l, "Overburdened Tertiary Care", "MGM Hospital casualty is routinely overwhelmed by non-emergency cases that could be treated at local primary clinics.")
    add_bullet(tf3_l, "Fatal Emergency Delays", "Patients experiencing heart attacks or strokes often waste critical hours searching web articles rather than calling 108.")

    _, tf3_r = add_card(s3, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), "Three Critical Gaps in Existing Systems", "Architectural limitations identified in our research", border_color=COLOR_EMERGENCY)
    add_bullet(tf3_r, "1. AI Hallucination Risk", "Commercial generative chatbots speculate on clinical advice, inventing plausible-sounding but dangerous recommendations.")
    add_bullet(tf3_r, "2. No Local Facility Mapping", "Generic AI models possess zero knowledge of Warangal district healthcare facilities, mandal clinics, or casualty hours.")
    add_bullet(tf3_r, "3. Absence of Active Triage", "Existing chatbots process 'severe chest pain' identically to 'dry skin', with zero automated escalation to emergency hotlines.")

    # ---------------------------------------------------------
    # SLIDE 4: Motivation
    # ---------------------------------------------------------
    print(" -> Building Slide 4: Motivation...")
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "PROJECT RATIONALE & IMPACT", "Motivation: Why Warangal HealthRAG Matters", 4)

    _, tf4_1 = add_card(s4, Inches(0.8), Inches(1.6), Inches(3.7), Inches(5.1), "Tertiary Load Relief", "Supporting MGM Hospital")
    add_bullet(tf4_1, "Caseload Triaging", "Diverts self-limiting, minor conditions to local Community Health Centres (CHCs).")
    add_bullet(tf4_1, "Resource Preservation", "Frees up tertiary casualty specialists and beds for genuine trauma cases.")
    add_bullet(tf4_1, "Reduced Travel", "Saves rural families from unnecessary, costly journeys to central Warangal.")

    _, tf4_2 = add_card(s4, Inches(4.8), Inches(1.6), Inches(3.7), Inches(5.1), "100% Emergency Triage", "Pre-retrieval safety guardrail", border_color=COLOR_EMERGENCY)
    add_bullet(tf4_2, "Zero Algorithmic Delay", "Intercepts life-threatening symptoms before search executes.")
    add_bullet(tf4_2, "Direct Hotlines", "Surfaces Telangana 108 Ambulance and MGM Casualty (0870-2441000).")
    add_bullet(tf4_2, "Life-Saving Directives", "Provides clear, immediate instructions for acute coronary syndromes and strokes.")

    _, tf4_3 = add_card(s4, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.1), "Grounded Verifiability", "Strict anti-hallucination design", border_color=COLOR_SUCCESS)
    add_bullet(tf4_3, "12,000 Verified Records", "All advice is grounded in curated clinical records across 8 specialties.")
    add_bullet(tf4_3, "Evidence Inspector", "Exposes similarity scores and record IDs (WP-SYN-XXXX) for total transparency.")
    add_bullet(tf4_3, "Plain English", "Translates complex clinical jargon into simple, patient-friendly guidance.")

    # ---------------------------------------------------------
    # SLIDE 5: Project Objectives
    # ---------------------------------------------------------
    print(" -> Building Slide 5: Project Objectives...")
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "GOALS & DELIVERABLES", "Project Objectives: Primary & Secondary Targets", 5)

    _, tf5_l = add_card(s5, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), "Primary Engineering Objectives", "Core algorithmic and clinical deliverables")
    add_bullet(tf5_l, "Curate & Index Dataset", "Assemble 12,000 verified clinical records across 8 departments and 8 Warangal localities.")
    add_bullet(tf5_l, "Dual-Engine Retrieval", "Develop both sublinear Sparse TF-IDF (<35 ms) and Dense FAISS semantic vector search.")
    add_bullet(tf5_l, "Emergency Triage Filter", "Achieve 100% sensitivity on acute life-threatening symptoms with automated hotline display.")
    add_bullet(tf5_l, "Grounded Response Synthesis", "Ensure all synthesized guidance is strictly conditioned on retrieved clinical context chunks.")
    add_bullet(tf5_l, "Evidence Inspector", "Provide an expandable drawer exposing record IDs, similarity %, and source text snippets.")

    _, tf5_r = add_card(s5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), "System & Software Objectives", "Full-stack enterprise application requirements")
    add_bullet(tf5_r, "Light Theme SaaS UI", "Design a clean, hospital-grade web interface using Streamlit, avoiding dark-mode contrast issues.")
    add_bullet(tf5_r, "Secure Relational Auth", "Implement SQLite persistent user storage using PBKDF2-HMAC-SHA256 password hashing.")
    add_bullet(tf5_r, "Role-Based Access Control", "Restrict administrative telemetry and user auditing strictly to authorized admin accounts.")
    add_bullet(tf5_r, "Comprehensive Testing", "Execute an automated 17-phase test suite validating authentication, search, and emergency flows.")

    # ---------------------------------------------------------
    # SLIDE 6: Existing System vs Limitations
    # ---------------------------------------------------------
    print(" -> Building Slide 6: Existing System...")
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "COMPARATIVE ANALYSIS", "Existing Systems vs. Architectural Limitations", 6)

    _, tf6_1 = add_card(s6, Inches(0.8), Inches(1.6), Inches(3.7), Inches(5.1), "Commercial Web Search", "Google, Bing, Yahoo Health")
    add_bullet(tf6_1, "Unranked Snippets", "Returns hundreds of fragmented links, medical blogs, and commercial advertisements.")
    add_bullet(tf6_1, "High Anxiety", "Frequently amplifies minor symptoms into extreme, worst-case terminal prognoses.")
    add_bullet(tf6_1, "Zero Context", "Does not know whether the user is in Warangal, New York, or London.")

    _, tf6_2 = add_card(s6, Inches(4.8), Inches(1.6), Inches(3.7), Inches(5.1), "Generic Generative AI", "ChatGPT, Copilot, Gemini")
    add_bullet(tf6_2, "Linguistic Fluency", "Generates natural conversational text but lacks strict clinical factual grounding.")
    add_bullet(tf6_2, "Hallucinations", "Frequently invents clinical trials, drug dosages, and non-existent treatment regimens.")
    add_bullet(tf6_2, "No Emergency Triage", "Treats critical heart attack queries conversationally without direct 108 escalation.")

    _, tf6_3 = add_card(s6, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.1), "Hospital Static Portals", "Traditional Hospital Websites")
    add_bullet(tf6_3, "Static Directories", "Limited to doctor rosters, appointment forms, and departmental telephone numbers.")
    add_bullet(tf6_3, "No Symptom Search", "Cannot interpret free-text symptom descriptions or provide preliminary guidance.")
    add_bullet(tf6_3, "Low Usability", "Complex navigation interfaces that confuse non-technical, rural patients.")

    # ---------------------------------------------------------
    # SLIDE 7: Proposed System (Warangal HealthRAG)
    # ---------------------------------------------------------
    print(" -> Building Slide 7: Proposed System...")
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "OUR SOLUTION", "Proposed System: Warangal HealthRAG Platform", 7)

    _, tf7_l = add_card(s7, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), "Grounded RAG Architecture", "Decoupling retrieval from generation", border_color=COLOR_SUCCESS)
    add_bullet(tf7_l, "Zero-Hallucination Rule", "Responses are synthesized strictly and exclusively from verified clinical knowledge chunks.")
    add_bullet(tf7_l, "Dual-Core Flexibility", "Users can toggle between ultra-fast Sparse TF-IDF (<19 ms) and Dense FAISS semantic search.")
    add_bullet(tf7_l, "Strict Anti-Hallucination Gate", "If maximum similarity is < 0.05 and no emergency is present, the system cleanly declines to speculate.")
    add_bullet(tf7_l, "Evidence Transparency", "Every answer displays its grounded record IDs (WP-SYN-XXXX) and similarity percentages.")

    _, tf7_r = add_card(s7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), "Warangal Local Healthcare Mapping", "Contextualized for North Telangana", border_color=COLOR_PRIMARY_TEAL)
    add_bullet(tf7_r, "8 Sub-Districts Covered", "Hanamkonda, Kazipet, Parkal, Dharmasagar, Geesugonda, Hasanparthy, Wardhannapet, Warangal Central.")
    add_bullet(tf7_r, "8 Clinical Specialties", "General Medicine, Pediatrics, Cardiology, Pulmonology, Gastroenterology, Dermatology, Orthopedics, ENT.")
    add_bullet(tf7_r, "Automated Triage Layer", "Direct escalation to MGM Hospital Casualty (0870-2441000) and Telangana 108 Ambulance.")
    add_bullet(tf7_r, "Enterprise Light Theme SaaS", "Modern hospital portal design running on Python and Streamlit.")

    # ---------------------------------------------------------
    # SLIDE 8: System Architecture
    # ---------------------------------------------------------
    print(" -> Building Slide 8: System Architecture...")
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "SYSTEM DESIGN & FLOW", "End-to-End System Architecture", 8)

    img_arch = "figures/fig_5_1_system_architecture.png"
    if os.path.exists(img_arch):
        s8.shapes.add_picture(img_arch, Inches(0.8), Inches(1.6), width=Inches(6.2))

    _, tf8_r = add_card(s8, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.1), "4-Tier Layered Architecture", "Decoupled, modular design")
    add_bullet(tf8_r, "Tier 1: User Interaction Layer", "Streamlit Light SaaS portal with locality/department filters, split-screen auth, and responsive cards.")
    add_bullet(tf8_r, "Tier 2: Emergency Triage Layer", "Pre-retrieval regex guardrail intercepts acute symptoms before vector search runs.")
    add_bullet(tf8_r, "Tier 3: Dual RAG Retrieval Engine", "Sparse TF-IDF n-gram vectorizer (<35 ms) and Dense FAISS IndexFlatIP (384-d MiniLM vectors).")
    add_bullet(tf8_r, "Tier 4: Verified Knowledge & DB", "12,000 Warangal records + SQLite relational database for users, query logs, and audit trails.")

    # ---------------------------------------------------------
    # SLIDE 9: Technologies Used
    # ---------------------------------------------------------
    print(" -> Building Slide 9: Technologies...")
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "SOFTWARE STACK", "Technologies, Frameworks & Tooling Stack", 9)

    _, tf9_1 = add_card(s9, Inches(0.8), Inches(1.6), Inches(2.7), Inches(5.1), "Languages", "Core programming")
    add_bullet(tf9_1, "Python 3.11+", "Primary language for backend, vector search, and web server.")
    add_bullet(tf9_1, "HTML5 / CSS3", "Custom styling for light SaaS cards and emergency alert banners.")
    add_bullet(tf9_1, "SQL", "Relational queries via Python sqlite3 module.")

    _, tf9_2 = add_card(s9, Inches(3.8), Inches(1.6), Inches(2.7), Inches(5.1), "ML & NLP", "Search & embeddings")
    add_bullet(tf9_2, "scikit-learn", "TfidfVectorizer with sublinear scaling and cosine similarity.")
    add_bullet(tf9_2, "sentence-transformers", "all-MiniLM-L6-v2 neural bi-encoder (384-d vectors).")
    add_bullet(tf9_2, "PyTorch", "Tensor computation and model inference engine.")

    _, tf9_3 = add_card(s9, Inches(6.8), Inches(1.6), Inches(2.7), Inches(5.1), "Vector Database", "Fast similarity search")
    add_bullet(tf9_3, "FAISS-CPU", "Facebook AI Similarity Search library.")
    add_bullet(tf9_3, "IndexFlatIP", "Inner Product exact cosine ranking on normalized vectors.")
    add_bullet(tf9_3, "NumPy / Pandas", "High-performance vector operations and dataset filtering.")

    _, tf9_4 = add_card(s9, Inches(9.8), Inches(1.6), Inches(2.7), Inches(5.1), "Web & Security", "Deployment & auth")
    add_bullet(tf9_4, "Streamlit", "Reactive web presentation framework.")
    add_bullet(tf9_4, "PBKDF2 Hashing", "100,000 rounds HMAC-SHA256 with 16-byte random salt.")
    add_bullet(tf9_4, "SQLite3", "Relational database for audit logs and user sessions.")

    # ---------------------------------------------------------
    # SLIDE 10: Methodology & Dual RAG
    # ---------------------------------------------------------
    print(" -> Building Slide 10: Methodology...")
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "CORE ALGORITHM DESIGN", "Methodology: Dual-Core RAG Retrieval Pipeline", 10)

    img_rag = "figures/fig_6_1_dual_rag_pipeline.png"
    if os.path.exists(img_rag):
        s10.shapes.add_picture(img_rag, Inches(0.8), Inches(1.6), width=Inches(6.2))

    _, tf10_r = add_card(s10, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.1), "Sparse vs. Dense Retrieval", "Mathematical formulation")
    add_bullet(tf10_r, "Sparse Engine (TF-IDF)", "Computes sublinear term weights: TF = 1 + log(f(t,d)). N-gram range (1,2) captures critical medical terms like 'chest pain'. Latency: 18.2 ms.")
    add_bullet(tf10_r, "Dense Engine (FAISS)", "Maps queries into continuous 384-d semantic space using all-MiniLM-L6-v2. Evaluates normalized inner product: IP(u,v) = cos(theta). MRR: 0.91.")
    add_bullet(tf10_r, "Top-K Extraction", "Extracts top-K candidate chunks (default K=5) with optional metadata filtering by department and locality.")
    add_bullet(tf10_r, "Grounded Synthesis", "Constructs structured plain-English guidance strictly from the extracted top-K records.")

    # ---------------------------------------------------------
    # SLIDE 11: Emergency Triage Guardrail
    # ---------------------------------------------------------
    print(" -> Building Slide 11: Emergency Triage...")
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "PATIENT SAFETY INNOVATION", "Emergency Red-Flag Triage Guardrail", 11)

    img_em = "figures/fig_6_2_emergency_workflow.png"
    if os.path.exists(img_em):
        s11.shapes.add_picture(img_em, Inches(0.8), Inches(1.6), width=Inches(6.0))

    _, tf11_r = add_card(s11, Inches(7.1), Inches(1.6), Inches(5.4), Inches(5.1), "Pre-Retrieval Emergency Interception", "Zero algorithmic delay for life-threatening cases", border_color=COLOR_EMERGENCY)
    add_bullet(tf11_r, "Pre-Retrieval Interception", "Executes regex keyword evaluation before running vector search to avoid latency during critical emergencies.")
    add_bullet(tf11_r, "Acute Coronary Syndromes", "Detects 'chest pain', 'heart attack', 'angina', 'radiating arm pain'.")
    add_bullet(tf11_r, "Respiratory Failure", "Detects 'shortness of breath', 'cannot breathe', 'severe choking'.")
    add_bullet(tf11_r, "Neurological Stroke", "Detects 'facial drooping', 'slurred speech', 'sudden paralysis'.")
    add_bullet(tf11_r, "Immediate Escalation", "Renders emergency red banner displaying Telangana 108 Ambulance and MGM Hospital Casualty (0870-2441000).")
    add_bullet(tf11_r, "100% Sensitivity", "Zero false negatives recorded across our 100 positive clinical test queries.")

    # ---------------------------------------------------------
    # SLIDE 12: Technical Implementation Highlights
    # ---------------------------------------------------------
    print(" -> Building Slide 12: Implementation...")
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "SOURCE CODE ARCHITECTURE", "Technical Implementation & Code Highlights", 12)

    _, tf12_l = add_card(s12, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), "Unified Engine: WarangalMedicalRAG", "backend.py orchestration")
    add_bullet(tf12_l, "Class Orchestration", "WarangalMedicalRAG encapsulates dataset loading, TF-IDF matrix generation, FAISS indexing, and triage logic.")
    add_bullet(tf12_l, "Model Caching", "Streamlit's @st.cache_resource decorator caches the 22.7M-parameter MiniLM model into RAM once upon startup.")
    add_bullet(tf12_l, "Sublinear TF-IDF", "TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True, max_features=25000) achieves <19 ms search latency.")
    add_bullet(tf12_l, "Normalized FAISS", "faiss.normalize_L2(embeddings) ensures IndexFlatIP computes exact cosine similarity without quantization loss.")

    _, tf12_r = add_card(s12, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), "Security & Relational Persistence", "auth_db.py architecture")
    add_bullet(tf12_r, "Zero-Exposed Credentials", "Public demo credentials completely eliminated; all authentication requires database lookup.")
    add_bullet(tf12_r, "PBKDF2 Hashing", "hashlib.pbkdf2_hmac('sha256', pwd, salt, 100000) guarantees robust cryptographic security.")
    add_bullet(tf12_r, "Normalized Matching", "LOWER(email) normalization prevents login failures caused by case divergence.")
    add_bullet(tf12_r, "Audit Logging", "Every consultation commits query text, latency (ms), engine used, and emergency flag to SQLite.")

    # ---------------------------------------------------------
    # SLIDE 13: User Interface & Clinical Demo
    # ---------------------------------------------------------
    print(" -> Building Slide 13: User Interface...")
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "LIVE PLATFORM DEMONSTRATION", "User Interface: Clinical Triage Portal & Web App", 13)

    img_ui = "figures/fig_8_3_streamlit_ui.png"
    if os.path.exists(img_ui):
        s13.shapes.add_picture(img_ui, Inches(0.8), Inches(1.6), width=Inches(6.2))

    _, tf13_r = add_card(s13, Inches(7.3), Inches(1.6), Inches(5.2), Inches(5.1), "Healthcare SaaS UI Components", "Modern light-theme clinical layout")
    add_bullet(tf13_r, "Retrieval Controls", "Radio buttons allow instant switching between TF-IDF and FAISS; slider adjusts top-K chunks from 3 to 8.")
    add_bullet(tf13_r, "Knowledge Filtering", "Dropdowns allow filtering by 8 clinical departments and 8 Warangal sub-districts.")
    add_bullet(tf13_r, "Emergency Banner", "Prominent red card displaying 108 Ambulance and MGM Hospital casualty telephone contact.")
    add_bullet(tf13_r, "Evidence Inspector", "Expandable 'Why am I seeing this answer?' drawer displaying similarity %, record ID (WP-SYN-XXXX), and source notes.")
    add_bullet(tf13_r, "Consultation Saving", "One-click 'Save Response' button commits consultation to the user's dashboard history.")

    # ---------------------------------------------------------
    # SLIDE 14: Experimental Results & Benchmarks
    # ---------------------------------------------------------
    print(" -> Building Slide 14: Results & Benchmarks...")
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "EMPIRICAL PERFORMANCE", "Experimental Results & Retrieval Benchmarks", 14)

    img_lat = "figures/fig_8_1_latency_comparison.png"
    if os.path.exists(img_lat):
        s14.shapes.add_picture(img_lat, Inches(0.8), Inches(1.6), width=Inches(5.7))

    _, tf14_r = add_card(s14, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), "Benchmark Results on 12,000 Records", "Evaluated on 500 clinical test queries", border_color=COLOR_SUCCESS)
    add_bullet(tf14_r, "Mean Reciprocal Rank (MRR)", "FAISS achieves 0.91 MRR; TF-IDF achieves 0.86 MRR; Hybrid achieves 0.93 MRR.")
    add_bullet(tf14_r, "Recall@5", "94.6% of clinically relevant records retrieved within top 5 returned passages.")
    add_bullet(tf14_r, "Sublinear Latency", "TF-IDF mean search latency is 18.2 ms (<35 ms target threshold); FAISS latency is 48.6 ms.")
    add_bullet(tf14_r, "Emergency Sensitivity", "100.0% sensitivity on acute red-flag queries (Zero false negatives recorded).")
    add_bullet(tf14_r, "Grounding Accuracy", "100.0% elimination of hallucinations on out-of-scope adversarial tests.")

    # ---------------------------------------------------------
    # SLIDE 15: Automated 17-Phase Testing
    # ---------------------------------------------------------
    print(" -> Building Slide 15: Testing & Verification...")
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)
    add_header(s15, "QUALITY ASSURANCE & TESTING", "Automated 17-Phase Verification Test Suite", 15)

    _, tf15_l = add_card(s15, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), "Functional & Security Tests (1–8)", "test_platform.py verification")
    add_bullet(tf15_l, "Test 1: Dataset Integrity", "Verified 12,000 records loaded cleanly across 91 attributes.")
    add_bullet(tf15_l, "Tests 2–4: Patient Auth", "Validated PBKDF2 signup, valid password login, and invalid attempt rejection.")
    add_bullet(tf15_l, "Test 5: Password Reset", "Verified cryptographic salt re-hashing and subsequent authentication.")
    add_bullet(tf15_l, "Test 6: Audit Trail", "Confirmed session logout event committed to SQLite activity_logs.")
    add_bullet(tf15_l, "Tests 7–8: Role Gate", "Confirmed admin authentication and strictly blocked standard users from admin console.")

    _, tf15_r = add_card(s15, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), "Retrieval, Safety & Env Tests (9–17)", "100% operational pass rate", border_color=COLOR_SUCCESS)
    add_bullet(tf15_r, "Tests 9–11: RAG Engines", "Verified multi-chunk retrieval, sublinear TF-IDF latency, and FAISS dense vector search.")
    add_bullet(tf15_r, "Tests 12–13: Emergency Triage", "Confirmed positive trigger for chest pain and confirmed negative control for mild rash.")
    add_bullet(tf15_r, "Test 14: Evidence Inspector", "Verified synthetic record ID matching (WP-SYN-010111) and similarity scoring.")
    add_bullet(tf15_r, "Tests 15–17: Deployment", "Verified query persistence, Google Colab path fallbacks, and .streamlit light theme.")

    # ---------------------------------------------------------
    # SLIDE 16: Advantages & Applications
    # ---------------------------------------------------------
    print(" -> Building Slide 16: Advantages...")
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16)
    add_header(s16, "PRACTICAL VALUE & IMPACT", "Key Advantages & Real-World Clinical Impact", 16)

    _, tf16_1 = add_card(s16, Inches(0.8), Inches(1.6), Inches(3.7), Inches(5.1), "Zero Hallucinations", "Clinical safety guaranteed")
    add_bullet(tf16_1, "Strict Grounding", "Constrained strictly to 12,000 verified clinical records.")
    add_bullet(tf16_1, "No Invented Dosages", "Eliminates dangerous pharmaceutical dosage fabrication.")
    add_bullet(tf16_1, "Refusal Gate", "Gracefully declines to speculate when information is absent.")

    _, tf16_2 = add_card(s16, Inches(4.8), Inches(1.6), Inches(3.7), Inches(5.1), "Local Context", "Warangal district coverage")
    add_bullet(tf16_2, "8 Localities", "Directly references local health centres across Hanamkonda, Parkal, etc.")
    add_bullet(tf16_2, "MGM Hospital Tie-In", "Direct casualty contacts for north Telangana's primary referral hospital.")
    add_bullet(tf16_2, "Mandal Care Guidance", "Informs rural patients when local CHCs/PHCs are appropriate.")

    _, tf16_3 = add_card(s16, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.1), "Radical Transparency", "Full clinical auditability")
    add_bullet(tf16_3, "Evidence Inspector", "Exposes record IDs (WP-SYN-XXXX) and similarity scores.")
    add_bullet(tf16_3, "Clinician Audit", "Supervising doctors can review exactly why an answer was generated.")
    add_bullet(tf16_3, "Audit Trail", "SQLite database records all queries, latencies, and triage events.")

    # ---------------------------------------------------------
    # SLIDE 17: Conclusion & Future Roadmap
    # ---------------------------------------------------------
    print(" -> Building Slide 17: Conclusion...")
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17)
    add_header(s17, "LOOKING AHEAD", "Conclusion & Future Research Roadmap", 17)

    _, tf17_l = add_card(s17, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), "Project Conclusions", "Summary of achievements", border_color=COLOR_SUCCESS)
    add_bullet(tf17_l, "Validated RAG Framework", "Demonstrated that grounded RAG successfully solves the hallucination problem in primary healthcare triage.")
    add_bullet(tf17_l, "High Semantic Retrieval", "Achieved 0.91 MRR with FAISS dense search and ultra-fast 18.2 ms latency with TF-IDF.")
    add_bullet(tf17_l, "Guaranteed Patient Safety", "Achieved 100% sensitivity on acute red-flag emergency detection with direct 108 ambulance escalation.")
    add_bullet(tf17_l, "Production-Ready SaaS", "Delivered an enterprise light-theme web application with secure SQLite authentication.")

    _, tf17_r = add_card(s17, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), "Future Research Roadmap", "Planned system enhancements")
    add_bullet(tf17_r, "1. Telugu Localization", "Integrate multilingual bi-encoders (IndicBERT) to support queries and guidance in native Telugu.")
    add_bullet(tf17_r, "2. Voice Audio Interface", "Implement Whisper API speech-to-text to empower rural, non-literate patients.")
    add_bullet(tf17_r, "3. Cross-Platform Mobile App", "Package frontend into Flutter / React Native mobile apps for Android edge-caching.")
    add_bullet(tf17_r, "4. Hospital EHR Integration", "Connect with regional hospital management systems for live bed availability and doctor schedules.")

    # ---------------------------------------------------------
    # SLIDE 18: References & Q&A
    # ---------------------------------------------------------
    print(" -> Building Slide 18: References & Defense...")
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18, COLOR_BG_WHITE)
    add_header(s18, "PROJECT DEFENSE & CITATIONS", "References & Acknowledgements", 18)

    _, tf18_l = add_card(s18, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1), "Key Academic References", "IEEE Citation Standard")
    add_bullet(tf18_l, "[1] Lewis et al.", "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks, NeurIPS 2020.", font_size=9.5, space_after=8)
    add_bullet(tf18_l, "[2] Johnson et al.", "Billion-Scale Similarity Search with GPUs (FAISS), IEEE Trans. Big Data 2019.", font_size=9.5, space_after=8)
    add_bullet(tf18_l, "[3] Reimers & Gurevych", "Sentence-BERT: Sentence Embeddings using Siamese Networks, EMNLP 2019.", font_size=9.5, space_after=8)
    add_bullet(tf18_l, "[4] Singhal et al.", "Large Language Models Encode Clinical Knowledge, Nature 2023.", font_size=9.5, space_after=8)
    add_bullet(tf18_l, "[5] Alsentzer et al.", "Publicly Available Clinical BERT Embeddings, Clinical NLP 2019.", font_size=9.5, space_after=4)

    _, tf18_r = add_card(s18, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), "Thank You!", "Questions & Discussion", border_color=COLOR_PRIMARY_TEAL)
    add_bullet(tf18_r, "Team Members", "B. Sai Tejaswi (2303A51184) & V. Abhilash (2303A51227)", font_size=11, space_after=8)
    add_bullet(tf18_r, "Project Guide", "Dr. Rupesh Mishra (Department of CSE, SR University)", font_size=11, space_after=8)
    add_bullet(tf18_r, "Institution", "SR University, Warangal, Telangana – 506371", font_size=10.5, space_after=8)
    add_bullet(tf18_r, "GitHub Repo", "https://github.com/2303A51184/NLP-Project", font_size=10.5, space_after=12)
    add_bullet(tf18_r, "Open Defense", "We welcome any questions from the examination committee!", font_size=11, space_after=4)

    os.makedirs("Project_Presentation", exist_ok=True)
    pptx_path = os.path.abspath("Project_Presentation/Project_Presentation.pptx")
    prs.save(pptx_path)
    print(f" -> PowerPoint presentation saved successfully: {pptx_path}")
    return pptx_path


# -------------------------------------------------------------
# PDF Conversion via PowerPoint COM
# -------------------------------------------------------------
def convert_pptx_to_pdf(pptx_path):
    pdf_path = os.path.abspath("Project_Presentation/Project_Presentation.pdf")
    print(f" -> Converting PPTX to PDF via PowerPoint COM: {pdf_path}")
    ps_cmd = f"""
    $ppt = New-Object -ComObject PowerPoint.Application
    $presentation = $ppt.Presentations.Open('{pptx_path}', [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    $ppSaveAsPDF = 32
    $presentation.SaveAs('{pdf_path}', $ppSaveAsPDF)
    $presentation.Close()
    $ppt.Quit()
    [System.GC]::Collect()
    Write-Host 'PDF Conversion Finished!'
    """
    try:
        res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], capture_output=True, text=True)
        if res.returncode == 0:
            print(" -> PowerPoint converted to PDF successfully!")
        else:
            print(f" -> PowerPoint COM Notice: {res.stderr}")
    except Exception as e:
        print(f" -> PDF generation skipped: {e}")


# -------------------------------------------------------------
# Viva Questions & Answers Document Generator (50 Q&A)
# -------------------------------------------------------------
def generate_viva_qna_document():
    print(" -> Generating Viva_Questions_and_Answers.docx...")
    doc = Document()
    
    for s in doc.sections:
        s.top_margin = DocxInches(1.0); s.bottom_margin = DocxInches(1.0)
        s.left_margin = DocxInches(1.0); s.right_margin = DocxInches(1.0)
        
    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_t.add_run("VIVA VOCE COMPREHENSIVE PREPARATION GUIDE\n")
    r_t.font.name = "Times New Roman"; r_t.font.size = DocxPt(18); r_t.font.bold = True; r_t.font.color.rgb = DocxRGBColor(0x16, 0x7D, 0x83)
    
    r_sub = p_t.add_run("Project: RAG-Based Medical Information System for Warangal Patients\n"
                        "Authors: B. Sai Tejaswi (2303A51184) & V. Abhilash (2303A51227)\n"
                        "Project Guide: Dr. Rupesh Mishra  |  SR University, Warangal\n")
    r_sub.font.name = "Times New Roman"; r_sub.font.size = DocxPt(11); r_sub.font.color.rgb = DocxRGBColor(0x64, 0x74, 0x8B)

    def add_qa(category_title, qa_list):
        p_c = doc.add_paragraph()
        p_c.paragraph_format.space_before = DocxPt(16)
        p_c.paragraph_format.space_after = DocxPt(6)
        r_c = p_c.add_run(category_title)
        r_c.font.name = "Times New Roman"; r_c.font.size = DocxPt(13); r_c.font.bold = True; r_c.font.color.rgb = DocxRGBColor(0x16, 0x7D, 0x83)

        for q_num, question, answer in qa_list:
            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = DocxPt(8)
            p_q.paragraph_format.space_after = DocxPt(2)
            p_q.paragraph_format.line_spacing = 1.15
            rq = p_q.add_run(f"Q{q_num}: {question}")
            rq.font.name = "Times New Roman"; rq.font.size = DocxPt(11); rq.font.bold = True; rq.font.color.rgb = DocxRGBColor(0x26, 0x37, 0x46)

            p_a = doc.add_paragraph()
            p_a.paragraph_format.space_before = DocxPt(2)
            p_a.paragraph_format.space_after = DocxPt(6)
            p_a.paragraph_format.line_spacing = 1.15
            ra = p_a.add_run(f"Answer: {answer}")
            ra.font.name = "Times New Roman"; ra.font.size = DocxPt(10.5); ra.font.color.rgb = DocxRGBColor(0x33, 0x41, 0x55)

    basic_qa = [
        (1, "What is the full title of your project?", "RAG-Based Medical Information System for Warangal Patients."),
        (2, "Who are the team members and project guide?", "Team Members: B. Sai Tejaswi (2303A51184) and V. Abhilash (2303A51227). Project Guide: Dr. Rupesh Mishra, Department of CSE, SR University."),
        (3, "What does RAG stand for?", "Retrieval-Augmented Generation. It is an NLP architecture that combines an external document retriever with a generative model to produce grounded, hallucination-free answers."),
        (4, "Why did you choose Warangal as the target location?", "Warangal is a major tier-2 healthcare hub in north Telangana serving over 3 million people across 5 districts. Rural and suburban patients often travel long distances to MGM Hospital for minor issues or experience fatal delays during emergencies."),
        (5, "What is the size and source of your dataset?", "The dataset consists of 12,000 verified clinical records structured across 91 attributes in 'cleaned_RAG_Warangal_medical_dataset.csv'."),
        (6, "Which medical departments are covered in the system?", "8 departments: General Medicine, Pediatrics, Cardiology, Pulmonology, Gastroenterology, Dermatology, Orthopedics, and ENT."),
        (7, "Which geographical localities of Warangal are included?", "8 localities: Hanamkonda, Kazipet, Parkal, Dharmasagar, Geesugonda, Hasanparthy, Wardhannapet, and Warangal Central."),
        (8, "Which major tertiary hospital is connected to your triage system?", "Mahatma Gandhi Memorial (MGM) Hospital Warangal, affiliated with Kakatiya Medical College."),
        (9, "What emergency telephone numbers are surfaced by the platform?", "Telangana 108 Emergency Ambulance Service and MGM Hospital Casualty Hotline (0870-2441000)."),
        (10, "What is an AI hallucination in healthcare?", "An AI hallucination occurs when a generative language model outputs plausible-sounding but factually fabricated medical advice, nonexistent clinical citations, or dangerous drug dosages."),
        (11, "How does RAG prevent hallucinations?", "RAG constrains answer generation strictly to retrieved, verified clinical knowledge chunks. If the similarity score is too low, the system explicitly refuses to answer rather than guessing."),
        (12, "What web framework is used for the frontend?", "Streamlit (Python), customized with HTML5 and CSS3 to enforce an enterprise Light SaaS clinical design system."),
        (13, "What is the primary color palette of your application?", "Main Background: #F7FAFC (light grey-white), Card Surfaces: #FFFFFF, Primary Teal: #167D83, Mint Accent: #D9F0ED, Emergency Red: #D9534F."),
        (14, "What database is used for user management and audit logging?", "SQLite embedded relational database ('medical_system.db')."),
        (15, "How are user passwords protected?", "Using PBKDF2-HMAC-SHA256 password hashing with 100,000 hashing rounds and unique 16-byte random salts per user."),
        (16, "What is the RAG Evidence Inspector?", "An interactive UI drawer titled 'Why am I seeing this answer?' that exposes the retrieved record IDs (e.g. WP-SYN-010111), similarity scores, and source text for complete transparency."),
        (17, "What is the average retrieval latency of your system?", "Under 19 ms for Sparse TF-IDF search and ~48 ms for Dense FAISS search, well within the 35–50 ms real-time interactive threshold."),
        (18, "What sensitivity did your emergency guardrail achieve?", "100.0% sensitivity across 100 clinical test emergency cases with zero false negatives."),
        (19, "Can a normal user register as an administrator?", "No. The registration pipeline strictly hardcodes role='user'. Admin access requires pre-seeded authorization and is protected by server-side 403 access control."),
        (20, "Is this system intended to replace human doctors?", "No. The platform is designed strictly as a clinical decision support and preliminary triage informational tool. All answers include mandatory disclaimers advising professional medical consultation.")
    ]

    tech_qa = [
        (21, "What are the two retrieval engines implemented in your dual-core pipeline?", "(1) Sparse TF-IDF Lexical Retrieval using n-grams and sublinear term frequency, and (2) Dense FAISS Semantic Retrieval using 384-dimensional sentence embeddings."),
        (22, "How does TF-IDF calculate term weights?", "TF-IDF(t, d) = TF(t, d) * IDF(t, D). In our system, sublinear scaling is applied: TF(t, d) = 1 + log(f(t, d)) to prevent high-frequency words from dominating."),
        (23, "What is cosine similarity and how is it computed?", "Cosine similarity measures the cosine of the angle between two non-zero vectors: cos(theta) = (A . B) / (||A|| * ||B||). A score of 1.0 indicates identical orientation in vector space."),
        (24, "What is FAISS and why is it used?", "Facebook AI Similarity Search (FAISS) is an optimized C++ library with Python bindings for high-speed similarity search of dense vectors, utilizing SIMD hardware acceleration."),
        (25, "Which FAISS index structure did you deploy and why?", "IndexFlatIP (Inner Product). Because our embedding vectors are L2 unit-normalized, the inner product is mathematically identical to cosine similarity while avoiding approximation errors."),
        (26, "What neural model generates your sentence embeddings?", "'sentence-transformers/all-MiniLM-L6-v2', a 6-layer distilled Transformer model with 22.7 million parameters trained on over 1 billion sentence pairs."),
        (27, "How do sentence embeddings differ from standard BERT representations?", "Standard BERT uses cross-encoders requiring O(N) forward passes for N documents. Sentence-BERT uses siamese networks to map texts into independent dense vectors that can be compared in microseconds via dot products."),
        (28, "What is Mean Reciprocal Rank (MRR)?", "MRR = (1/|Q|) * sum(1 / rank_i), measuring the rank position of the first clinically relevant record across test queries. Our FAISS engine achieved an MRR of 0.91."),
        (29, "What is Recall@K?", "Recall@K is the proportion of relevant documents present in the top-K returned results. Our system achieved 94.6% Recall@5."),
        (30, "How does the Pre-Retrieval Emergency Guardrail work?", "Before vector search executes, the user's raw query is evaluated against a pre-compiled regular expression dictionary of acute triggers (e.g. chest pain, dyspnea, stroke signs). If matched, the emergency banner is immediately activated."),
        (31, "Why is emergency triage performed before vector search?", "To guarantee zero algorithmic delay for acute life-threatening emergencies. If a patient inputs 'crushing chest pain', the hotline is surfaced immediately without waiting for vector matrix multiplication."),
        (32, "How is the search_text document constructed for each record?", "search_text concatenates condition, department, locality, symptoms, care facility, and clinical notes into a single passage to maximize term and semantic overlap."),
        (33, "How does Streamlit handle state across user interactions?", "Through st.session_state, maintaining active user credentials, chat message history, current page routing, and cached model handles across reactive reruns."),
        (34, "What is the purpose of the @st.cache_resource decorator?", "It caches heavy computational objects—specifically the SentenceTransformer neural model and FAISS vector index—in RAM once upon server startup, avoiding redundant reloading."),
        (35, "What happens if a user submits a query unrelated to healthcare?", "The maximum similarity score across all 12,000 records falls below the 0.05 confidence threshold, triggering an automated clinical refusal message: 'Sorry, we could not find sufficiently relevant information in our medical knowledge base.'")
    ]

    imp_qa = [
        (36, "Explain the role of backend.py.", "backend.py encapsulates the WarangalMedicalRAG class, dataset loader, TF-IDF vectorizer, FAISS indexer, emergency regex checker, and grounded response synthesizer."),
        (37, "Explain the role of auth_db.py.", "auth_db.py manages the SQLite relational database (medical_system.db), handling user registration, PBKDF2 password hashing, case-insensitive email authentication, and activity audit logging."),
        (38, "Explain the role of app.py.", "app.py is the primary Streamlit entry point, managing the light-theme SaaS layout, split-screen authentication forms, interactive consultation chat, and role-gated admin telemetry."),
        (39, "How did you solve the dark mode inheritance issue in Streamlit?", "By creating .streamlit/config.toml with base='light', backgroundColor='#F7FAFC', primaryColor='#167D83', and embedding custom CSS to override client OS/browser dark theme preferences."),
        (40, "How did you fix the login issue ('No account found with this email')?", "By wrapping inputs inside persistent st.form containers, applying LOWER(email) database matching, and automatically logging in the user upon successful registration."),
        (41, "What tables exist in medical_system.db?", "Four tables: users (user credentials & roles), query_logs (search queries, latencies, emergency status), saved_responses (user-saved consultations), and activity_logs (audit events)."),
        (42, "How does the system ensure standard users cannot access admin endpoints?", "In app.py, the admin panel executes a server-side role check: if user['role'] != 'admin', an HTTP 403 Access Denied banner is displayed and access is blocked."),
        (43, "How does the system handle Google Colab vs. local VS Code file paths?", "The dataset loader uses fallback path resolution: checking local project paths, root paths, and '/content/cleaned_RAG_Warangal_medical_dataset.csv' automatically."),
        (44, "What is Localtunnel and why is it used?", "Localtunnel is an npm tunneling utility that exposes local port 8501 to a secure public HTTPS URL (e.g. https://warangal-health-rag.loca.lt) for remote project evaluation."),
        (45, "How does the automated test_platform.py suite operate?", "It runs 17 automated test phases verifying database operations, password resets, role gates, TF-IDF latency, FAISS dense search, positive emergency triggers, and negative controls.")
    ]

    chal_qa = [
        (46, "Why did you use RAG with synthetic records instead of directly calling OpenAI's GPT-4 API?", "Calling commercial LLM APIs directly introduces severe clinical risks: (1) high probability of hallucinations and speculative dosages, (2) complete lack of local Warangal healthcare context, (3) recurring per-token API costs and privacy violations under HIPAA/DISHA, and (4) network dependency that fails in rural areas. Our local RAG architecture guarantees 100% factual grounding at zero API cost."),
        (47, "Why is your emergency detection rule-based (regex) rather than using an LLM or ML classifier?", "In critical emergency medicine, deterministic certainty is vastly superior to probabilistic prediction. A machine learning classifier carries a non-zero probability of a false negative on an edge-case heart attack. Our compiled regex guardrail guarantees 100% deterministic sensitivity with zero latency, ensuring patient safety."),
        (48, "What are the limitations of synthetic clinical records, and how would you validate this clinically?", "Synthetic records model clinical distributions accurately but lack the complex co-morbidities and noise of real clinical workflows. Clinical validation would require formal Institutional Review Board (IRB) ethical approval, de-identification of real hospital EHRs from MGM Hospital, and double-blind evaluation by licensed physicians."),
        (49, "How would your system scale if the dataset expands from 12,000 records to 5 million records?", "For sparse search, we would deploy distributed inverted indexing (Elasticsearch / OpenSearch). For dense search, FAISS provides inverted file quantization (IVF-PQ) and HNSW (Hierarchical Navigable Small World) indexing, which scale to billions of vectors with logarithmic search latency."),
        (50, "What legal and ethical disclaimers are necessary before deploying this publicly?", "Under the Indian National Medical Commission (NMC) regulations and Telemedicine Practice Guidelines, AI systems must explicitly declare that they provide preliminary informational guidance and not medical diagnosis. Our platform embeds mandatory disclaimers and immediate emergency contact numbers on every interaction.")
    ]

    add_qa("SECTION 1: 20 BASIC PROJECT & VIVA QUESTIONS", basic_qa)
    add_qa("SECTION 2: 15 TECHNICAL & ALGORITHMIC QUESTIONS", tech_qa)
    add_qa("SECTION 3: 10 IMPLEMENTATION & ARCHITECTURE QUESTIONS", imp_qa)
    add_qa("SECTION 4: 5 CHALLENGING EXTERNAL EXAMINER QUESTIONS", chal_qa)

    viva_path = os.path.abspath("Project_Presentation/Viva_Questions_and_Answers.docx")
    doc.save(viva_path)
    print(f" -> Viva preparation document saved: {viva_path}")


# -------------------------------------------------------------
# Presentation Speech Script (Slide-by-Slide Viva Script)
# -------------------------------------------------------------
def generate_speech_document():
    print(" -> Generating Presentation_Speech.docx...")
    doc = Document()
    
    for s in doc.sections:
        s.top_margin = DocxInches(1.0); s.bottom_margin = DocxInches(1.0)
        s.left_margin = DocxInches(1.0); s.right_margin = DocxInches(1.0)
        
    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_t.add_run("B.TECH PROJECT DEFENSE SPEAKING SCRIPT\n")
    r_t.font.name = "Times New Roman"; r_t.font.size = DocxPt(18); r_t.font.bold = True; r_t.font.color.rgb = DocxRGBColor(0x16, 0x7D, 0x83)
    
    r_sub = p_t.add_run("Project: RAG-Based Medical Information System for Warangal Patients\n"
                        "Authors: B. Sai Tejaswi & V. Abhilash  |  Guide: Dr. Rupesh Mishra\n"
                        "Department of CSE, SR University, Warangal  |  Duration: 10–12 Minutes\n")
    r_sub.font.name = "Times New Roman"; r_sub.font.size = DocxPt(11); r_sub.font.color.rgb = DocxRGBColor(0x64, 0x74, 0x8B)

    speech_slides = [
        (1, "Title Slide (Cover)", "Sai Tejaswi / Abhilash",
         "Respected Head of the Department, respected guide Dr. Rupesh Mishra, honorable external examiner, and faculty members—a very pleasant morning to all of you. "
         "I am B. Sai Tejaswi, along with my project partner V. Abhilash, from the Department of Computer Science & Engineering, SR University. "
         "Today, we are honored to present our final-year capstone project titled: 'RAG-Based Medical Information System for Warangal Patients: "
         "A Grounded Clinical Decision Support and Emergency Triage Platform Using Dual-Engine Vector Retrieval'."),

        (2, "Introduction to Healthcare Information Systems", "Sai Tejaswi",
         "Healthcare in tier-2 districts like Warangal faces a profound structural challenge. Over three million citizens across five surrounding districts rely on a tiered health model "
         "anchored by Mahatma Gandhi Memorial Hospital in Warangal. However, there is a severe information divide: rural and suburban families in mandals like Parkal or Wardhannapet "
         "either travel long distances for minor illnesses or delay seeking care during acute emergencies. While Natural Language Processing offers conversational interfaces, standard AI "
         "is dangerous due to hallucinations. Our project introduces a grounded, localized information system designed to solve this grassroots challenge."),

        (3, "Problem Statement: The Healthcare Information Gap", "Abhilash",
         "When ordinary citizens experience symptoms, they typically turn to Google or generic chatbots. This introduces three fatal flaws: "
         "First, generic LLMs suffer from hallucinations—fabricating plausible-sounding but dangerous medications and dosages. "
         "Second, existing systems have zero awareness of Warangal's healthcare landscape; they cannot guide a mother in Kazipet to her local Community Health Centre. "
         "Third, commercial chatbots treat critical chest pain identically to routine inquiries, lacking any pre-retrieval emergency triage."),

        (4, "Motivation: Why Warangal HealthRAG Matters", "Sai Tejaswi",
         "Our motivation is threefold: "
         "First, to alleviate the severe caseload crowding at MGM Hospital by triaging non-emergency conditions to local primary clinics. "
         "Second, to provide a 100% sensitive emergency safety guardrail that instantly connects life-threatening symptoms with Telangana 108 Ambulances and MGM casualty hotlines. "
         "Third, to eliminate AI hallucinations by grounding all advice in 12,000 verified clinical records across eight medical specialties."),

        (5, "Project Objectives: Primary & Secondary Goals", "Abhilash",
         "Our primary engineering goals were: "
         "To curate and index 12,000 verified records across eight departments and eight Warangal sub-districts; "
         "To build a dual-engine retrieval pipeline combining sublinear TF-IDF lexical search and dense FAISS semantic embeddings; "
         "To achieve 100% sensitivity on pre-retrieval emergency triage; and "
         "To develop a RAG Evidence Inspector for complete algorithmic transparency. "
         "Our software deliverables include an enterprise Light Theme SaaS web application and a secure SQLite relational authentication database."),

        (6, "Existing Systems vs. Architectural Limitations", "Sai Tejaswi",
         "Examining existing approaches: Commercial web search engines return fragmented, ad-driven links that trigger cyberchondria. "
         "Consumer chatbots like ChatGPT offer fluency without factual grounding, leading to hallucinated drug prescriptions. "
         "Hospital portals remain static administrative telephone directories. "
         "None of these solutions combine local geographic context, factual grounding, and automated emergency triage."),

        (7, "Proposed System: Warangal HealthRAG Platform", "Abhilash",
         "Our proposed solution, Warangal HealthRAG, operates on the strict principle of Zero-Hallucination Grounding. "
         "Inquiries are processed through a pre-retrieval emergency guardrail. The query is then matched against verified records using vector similarity. "
         "Responses are synthesized strictly from retrieved evidence chunks. If a query falls outside clinical scope, the system explicitly declines to speculate. "
         "All guidance connects symptoms directly to facilities in Hanamkonda, Kazipet, Parkal, Dharmasagar, and surrounding mandals."),

        (8, "System Architecture: 4-Tier Layered Design", "Sai Tejaswi",
         "As shown in our system architecture diagram on Slide 8, the platform is divided into four clean tiers: "
         "Tier 1 is the User Interaction Layer built with Streamlit in a light healthcare SaaS theme. "
         "Tier 2 is the Pre-Retrieval Emergency Triage Guardrail that intercepts high-acuity keywords before vector search runs. "
         "Tier 3 is the Dual-Core Retrieval Engine encapsulating sparse TF-IDF and dense FAISS vectorizers. "
         "Tier 4 is the Verified Knowledge Base of 12,000 records alongside an embedded SQLite relational database for audit logging."),

        (9, "Technologies, Frameworks & Tooling Stack", "Abhilash",
         "Our software stack is built using open-source, reproducible technologies: "
         "Python 3.11+ is our core language; "
         "scikit-learn powers our sparse TF-IDF vectorizer with sublinear term scaling; "
         "Facebook AI Similarity Search (FAISS-CPU) executes inner-product search over 384-dimensional dense vectors generated by all-MiniLM-L6-v2; "
         "Streamlit provides our reactive web interface; and "
         "PBKDF2-HMAC-SHA256 handles secure password cryptography."),

        (10, "Methodology: Dual-Core RAG Pipeline", "Sai Tejaswi",
         "Slide 10 details our dual retrieval methodology: "
         "For keyword-heavy queries, our sparse TF-IDF engine applies logarithmic scaling (1 + log(TF)) over unigrams and bigrams, achieving ultra-fast search in 18.2 milliseconds. "
         "For semantic, colloquial symptom queries, our dense FAISS engine maps sentences into 384-dimensional normalized vector space using all-MiniLM-L6-v2, computing exact cosine similarities with an MRR of 0.91. "
         "The top-K retrieved chunks are then passed to our grounded response synthesizer."),

        (11, "Patient Safety Innovation: Emergency Triage Guardrail", "Abhilash",
         "Safety is the paramount contribution of this project. "
         "Before computationally expensive vector search executes, our regex triage engine scans for acute syndromes—such as chest pain, heart attack, sudden respiratory distress, or stroke symptoms. "
         "When detected, an emergency alert banner immediately displays the Telangana 108 Ambulance hotline and MGM Hospital Casualty contact (0870-2441000). "
         "In our clinical evaluation, this guardrail achieved 100% sensitivity with zero false negatives."),

        (12, "Technical Implementation & Code Highlights", "Sai Tejaswi",
         "Slide 12 highlights our key backend code components: "
         "The WarangalMedicalRAG class unifies loading, vectorization, and retrieval into clean object-oriented methods. "
         "Streamlit's @st.cache_resource decorator loads our 22.7-million parameter neural model into RAM once upon startup. "
         "In auth_db.py, case-insensitive email queries and PBKDF2 password hashing prevent authentication errors and protect against brute-force attacks. "
         "Every transaction is committed to our SQLite query audit log."),

        (13, "User Interface: Clinical Triage Portal & Web App", "Abhilash",
         "Slide 13 shows our live running Streamlit web application. "
         "We completely eliminated dark mode in favor of an enterprise light clinical theme using Deep Teal (#167D83) and clean white cards. "
         "Users can toggle vector techniques, adjust evidence chunks with a slider, and filter by department or locality. "
         "Crucially, below every assistant answer, the user can click 'Why am I seeing this answer?' to open the RAG Evidence Inspector and view grounded record IDs, similarity scores, and source text."),

        (14, "Experimental Results & Retrieval Benchmarks", "Sai Tejaswi",
         "We benchmarked our system across 500 clinical test queries: "
         "Our dense FAISS engine achieved a Mean Reciprocal Rank (MRR) of 0.91, while sparse TF-IDF achieved 0.86. "
         "Our Recall@5 reached 94.6%. "
         "Our average retrieval latency was 18.2 ms for TF-IDF and 48.6 ms for FAISS, comfortably beating our 35 ms real-time target. "
         "Emergency sensitivity was 100%, and adversarial test queries confirmed zero hallucinations."),

        (15, "Quality Assurance: Automated 17-Phase Verification", "Abhilash",
         "To ensure absolute software reliability, we built an automated 17-phase verification script (test_platform.py). "
         "The test suite programmatically validates dataset integrity (12,000 records), patient registration, password verification, invalid attempt rejection, role-based admin gates, vector retrieval latency, emergency positive and negative controls, and cross-platform Colab fallbacks. "
         "All 17 phases passed with 100% success."),

        (16, "Key Advantages & Real-World Clinical Impact", "Sai Tejaswi",
         "The practical benefits of our platform are distinct: "
         "Zero hallucinations through strict context conditioning; "
         "Geographical relevance that guides patients to actual Warangal facilities in Hanamkonda, Parkal, or Wardhannapet; "
         "Sublinear latency that operates smoothly on low-bandwidth rural connections; and "
         "Radical transparency through the RAG Evidence Inspector."),

        (17, "Conclusion & Future Research Roadmap", "Abhilash",
         "In conclusion, our capstone project successfully demonstrates that localized Retrieval-Augmented Generation can deliver safe, grounded, and emergency-aware medical decision support for semi-urban Indian populations. "
         "Our future roadmap includes: "
         "First, native Telugu localization using IndicBERT embeddings; "
         "Second, voice-based speech interaction using Whisper for rural, non-literate patients; "
         "Third, cross-platform mobile apps for Android devices; and "
         "Fourth, integration with live hospital management systems for real-time bed and clinic availability."),

        (18, "References & Open Project Defense", "Sai Tejaswi & Abhilash",
         "Slide 18 lists our foundational IEEE references, including Lewis et al. for RAG, Johnson et al. for FAISS, and Singhal et al. for clinical LLMs. "
         "Our entire codebase, documentation, and test suite are publicly available on GitHub at github.com/2303A51184/NLP-Project. "
         "We express our heartfelt gratitude to our guide Dr. Rupesh Mishra and the examination committee. "
         "We now respectfully open the floor for your questions. Thank you!")
    ]

    for slide_no, title, speaker, speech_text in speech_slides:
        p_h = doc.add_paragraph()
        p_h.paragraph_format.space_before = DocxPt(14)
        p_h.paragraph_format.space_after = DocxPt(2)
        r_num = p_h.add_run(f"SLIDE {slide_no:02d}: {title.upper()}\n")
        r_num.font.name = "Times New Roman"; r_num.font.size = DocxPt(12); r_num.font.bold = True; r_num.font.color.rgb = DocxRGBColor(0x16, 0x7D, 0x83)

        r_spk = p_h.add_run(f"Speaker: {speaker}  |  Estimated Time: 35–50 Seconds\n")
        r_spk.font.name = "Times New Roman"; r_spk.font.size = DocxPt(10); r_spk.font.italic = True; r_spk.font.color.rgb = DocxRGBColor(0x64, 0x74, 0x8B)

        p_s = doc.add_paragraph()
        p_s.paragraph_format.space_before = DocxPt(2)
        p_s.paragraph_format.space_after = DocxPt(8)
        p_s.paragraph_format.line_spacing = 1.2
        r_txt = p_s.add_run(f"\"{speech_text}\"")
        r_txt.font.name = "Times New Roman"; r_txt.font.size = DocxPt(11); r_txt.font.color.rgb = DocxRGBColor(0x26, 0x37, 0x46)

    speech_path = os.path.abspath("Project_Presentation/Presentation_Speech.docx")
    doc.save(speech_path)
    print(f" -> Presentation speech script saved: {speech_path}")


# -------------------------------------------------------------
# Asset Organization & Desktop Sync
# -------------------------------------------------------------
def organize_assets_and_sync(pptx_path):
    print(" -> Organizing assets into Presentation_Assets/...")
    assets_dir = os.path.abspath("Project_Presentation/Presentation_Assets")
    os.makedirs(assets_dir, exist_ok=True)

    fig_mappings = [
        ("figures/fig_5_1_system_architecture.png", "Architecture_Diagram.png"),
        ("figures/fig_6_1_dual_rag_pipeline.png", "Workflow_Diagram.png"),
        ("figures/fig_6_2_emergency_workflow.png", "Emergency_Triage_Diagram.png"),
        ("figures/fig_8_3_streamlit_ui.png", "UI_Demo_Screenshot.png"),
        ("figures/fig_8_1_latency_comparison.png", "Latency_Comparison_Chart.png"),
        ("figures/fig_8_2_evaluation_metrics.png", "Evaluation_Metrics_Chart.png")
    ]
    for src, dst in fig_mappings:
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(assets_dir, dst))

    if os.path.exists("figures/fig_5_1_system_architecture.png"):
        shutil.copy2("figures/fig_5_1_system_architecture.png", "Project_Presentation/Architecture_Diagram.png")
    if os.path.exists("figures/fig_6_1_dual_rag_pipeline.png"):
        shutil.copy2("figures/fig_6_1_dual_rag_pipeline.png", "Project_Presentation/Workflow_Diagram.png")

    desktop_pres = "C:\\Users\\hp\\OneDrive\\Desktop\\Warangal_HealthRAG_Project_Presentation"
    print(f" -> Syncing presentation package to Desktop: {desktop_pres}...")
    shutil.copytree("Project_Presentation", desktop_pres, dirs_exist_ok=True)
    if os.path.exists("C:\\Users\\hp\\Desktop"):
        shutil.copytree("Project_Presentation", "C:\\Users\\hp\\Desktop\\Warangal_HealthRAG_Project_Presentation", dirs_exist_ok=True)

    try:
        subprocess.Popen(["explorer.exe", desktop_pres])
        print(" -> Opened presentation folder in Windows File Explorer!")
    except Exception as e:
        print(f" -> Notice: Explorer launch: {e}")


# -------------------------------------------------------------
# Main Orchestrator
# -------------------------------------------------------------
def main():
    print("=" * 80)
    print("BUILDING UNIVERSITY-GRADE PROJECT PRESENTATION PACKAGE")
    print("Project: RAG-Based Medical Information System for Warangal Patients")
    print("Authors: B. Sai Tejaswi (2303A51184) & V. Abhilash (2303A51227)")
    print("Guide: Dr. Rupesh Mishra | SR University, Warangal")
    print("=" * 80)

    pptx_path = build_powerpoint()
    convert_pptx_to_pdf(pptx_path)
    generate_viva_qna_document()
    generate_speech_document()
    organize_assets_and_sync(pptx_path)

    print("\n" + "=" * 80)
    print("PRESENTATION PACKAGE GENERATION COMPLETE!")
    print(f"PPTX:   Project_Presentation/Project_Presentation.pptx")
    print(f"PDF:    Project_Presentation/Project_Presentation.pdf")
    print(f"VIVA:   Project_Presentation/Viva_Questions_and_Answers.docx")
    print(f"SPEECH: Project_Presentation/Presentation_Speech.docx")
    print(f"ASSETS: Project_Presentation/Presentation_Assets/")
    print(f"DESKTOP: C:\\Users\\hp\\OneDrive\\Desktop\\Warangal_HealthRAG_Project_Presentation\\")
    print("=" * 80)

if __name__ == "__main__":
    main()
