# 🏥 RAG-Based Medical Information System for Warangal Patients

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/2303A51184/NLP-Project/blob/main/RAG_Warangal_Medical_Colab.ipynb)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**B.Tech Computer Science & Engineering Final-Year Mini Project**  
**Department of Computer Science & Engineering, SR University, Warangal, Telangana, India**

### 👥 Authors
- **B. Sai Tejaswi** (`2303A51184@sru.edu.in`)
- **V. Abhilash** (`2303A51227@sru.edu.in`)

---

## 📌 Project Overview
The **RAG-Based Medical Information System for Warangal Patients** is an AI-powered healthcare guidance and clinical triage platform. Specially developed for patients across the Warangal district (Hanamkonda, Kazipet, Parkal, Dharmasagar, Geesugonda, Hasanparthy, Wardhannapet), the system leverages **Retrieval-Augmented Generation (RAG)** strictly grounded in a verified local knowledge dataset of **12,000 clinical records**.

The architecture decouples the **Core Backend Engine (`backend.py`)** from the **Interactive Frontend (`app.py`)**, allowing the system to run seamlessly in:
1. **VS Code / Local Terminal** (CLI backend execution and local Streamlit dashboard).
2. **Google Colab** (Interactive notebook testing and public tunnel deployment).

---

## 🏗️ System Architecture & Modularity

```
+-----------------------------------------------------------------------------------+
|                            WARANGAL MEDICAL RAG SYSTEM                            |
+-----------------------------------------------------------------------------------+
                                         |
            +----------------------------+----------------------------+
            |                                                         |
            v                                                         v
   [ 💻 FRONTEND: app.py ]                                   [ 🧠 BACKEND: backend.py ]
   - Streamlit Dashboard UI                                  - WarangalMedicalRAG Class
   - Sidebar Metrics & KPI Cards                             - TF-IDF Sparse Engine (<35 ms)
   - Locality & Dept Filter Dropdowns                        - FAISS Dense Vector Engine (MiniLM)
   - Chat History Session State                              - Red-Flag Safety Guardrail
   - Grounded RAG Evidence Inspector                         - Grounded Response Synthesizer
            |                                                         |
            +----------------------------+----------------------------+
                                         |
                                         v
                 [ 📂 DATASET: cleaned_RAG_Warangal_medical_dataset.csv ]
                                  (12,000 Verified Records)
```

---

## 🌟 Key Features

1. **Decoupled Backend Engine (`backend.py`)**:
   - `WarangalMedicalRAG`: High-level class providing a single `.query(...)` method.
   - Dual retrieval: **TF-IDF + Cosine Similarity** (instant, <35 ms) and **FAISS + SentenceTransformers (`all-MiniLM-L6-v2`)**.
   - Standalone CLI execution: Can be executed directly with `python backend.py --query "..."`.

2. **Emergency Red-Flag Guardrails**:
   - Automated rule-based triage layer scanning for life-threatening symptoms (*acute chest pain, dyspnea, stroke indicators, fainting, heavy trauma*).
   - Prominently routes emergencies to local facilities:
     - **MGM Hospital Warangal Casualty Hotline**: `0870-2441000 / 0870-2441001`
     - **Telangana Emergency Ambulance**: `108`
     - **District Hospital Warangal**: `0870-2577772`

3. **Interactive Streamlit Web Dashboard (`app.py`)**:
   - Real-time dataset statistics (12,000 total records, verified entries, high-priority counts).
   - Expandable **RAG Evidence Inspector** displaying similarity score percentages, record IDs (`WP-SYN-XXXX`), matched condition, department, and locality.

---

## 🚀 How to Run in VS Code (Local Environment)

### Step 1: Clone Repository & Open in VS Code
```bash
git clone https://github.com/2303A51184/NLP-Project.git
cd NLP-Project
```
Open the folder in **VS Code**:
```bash
code .
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run in VS Code

#### Option A: Run the Backend directly (CLI / Python script)
You can test the RAG engine directly in the VS Code terminal without launching a browser:
```bash
python backend.py --query "Child in Parkal having severe asthma and wheezing"
```
Or test an emergency query:
```bash
python backend.py --query "Severe chest pain and sweating in Kazipet"
```

#### Option B: Launch the Streamlit Web Application
```bash
python -m streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## ☁️ How to Run in Google Colab

You can run the entire project in **Google Colab** with zero local setup:

### Method 1: One-Click Colab Notebook
1. Open the included notebook: **[`RAG_Warangal_Medical_Colab.ipynb`](RAG_Warangal_Medical_Colab.ipynb)**
2. Click the **Open in Colab** badge:  
   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/2303A51184/NLP-Project/blob/main/RAG_Warangal_Medical_Colab.ipynb)
3. Run the cells in order:
   - Cell 1 clones the repository and installs dependencies.
   - Cell 2 initializes the backend `WarangalMedicalRAG`.
   - Cell 3 runs interactive test queries.
   - Cell 4 launches the Streamlit web app using `localtunnel` and gives you a public URL.

### Method 2: Manual Commands in Colab
In any new Colab notebook, simply run:
```python
# 1. Clone repository
!git clone https://github.com/2303A51184/NLP-Project.git
%cd NLP-Project

# 2. Install dependencies
!pip install -r requirements.txt

# 3. Test backend in Python
from backend import WarangalMedicalRAG
rag = WarangalMedicalRAG()
result = rag.query("Child in Parkal having severe asthma and wheezing")
print(result['response_text'])

# 4. Launch Streamlit UI
!curl -s https://loca.lt/mytunnelpassword
!streamlit run app.py & npx localtunnel --port 8501
```

---

## 📂 Repository Structure

```
NLP-Project/
├── backend.py                                          # Decoupled core RAG & safety engine
├── app.py                                              # Streamlit web dashboard
├── RAG_Warangal_Medical_Colab.ipynb                    # Complete Google Colab notebook
├── requirements.txt                                    # Project dependencies
├── cleaned_RAG_Warangal_medical_dataset.csv            # 12,000 clinical records dataset (39.2 MB)
├── create_ieee_paper.py                                # Script generating IEEE Word paper
├── IEEE_Research_Paper_RAG_Warangal_Medical_System.docx# Formatted IEEE two-column paper (.docx)
├── RAG-Based Medical Information System.pptx           # Mini-project presentation slides
├── Summary of Created Files.docx                       # Project overview summary
├── dataset code.txt                                    # Data preprocessing script
├── .gitignore                                          # Git ignore rules
└── README.md                                           # Comprehensive documentation
```

---

## 📄 IEEE Research Paper Reference
The project includes a publication-standard, two-column IEEE formatted research paper:
- **File**: `IEEE_Research_Paper_RAG_Warangal_Medical_System.docx`
- **Authors**: B. Sai Tejaswi & V. Abhilash (SR University, Warangal)
- **Title**: *Design and Implementation of a Grounded RAG-Based Medical Information Triage System for Rural and Suburban Patients in Warangal District*
