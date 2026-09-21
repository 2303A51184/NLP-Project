# 🏥 RAG-Based Medical Information System for Warangal Patients

**B.Tech Computer Science & Engineering Final-Year Mini Project**  
**Department of Computer Science & Engineering, SR University, Warangal, Telangana, India**

### 👥 Authors
- **B. Sai Tejaswi** (`2303A51184@sru.edu.in`)
- **V. Abhilash** (`2303A51227@sru.edu.in`)

---

## 📌 Project Overview
The **RAG-Based Medical Information System for Warangal Patients** is an intelligent AI-driven healthcare guidance and emergency triage platform. Designed specifically for patients in the Warangal district (Hanamkonda, Kazipet, Parkal, Dharmasagar, Geesugonda, Hasanparthy, Wardhannapet), the system leverages **Retrieval-Augmented Generation (RAG)** strictly grounded in a verified local dataset of **12,000 clinical records**.

The platform eliminates AI hallucination risks by anchoring answers directly in retrieved context and features an automated **Red-Flag Emergency Triage Guardrail** to instantly escalate critical symptoms (acute chest pain, dyspnea, stroke indicators, fainting) to local emergency facilities such as **MGM Hospital Warangal** casualty hotlines (`0870-2441000` / `108`).

---

## 🌟 Key Application Features

1. **Interactive Streamlit Medical Dashboard**:
   - Live KPI metric tiles displaying Total Records (12,000), Verified Records, High Priority Chunks, and Localities Served.
   - Context filters for Medical Departments (*Pulmonology, Gastroenterology, Cardiology, Orthopedics, ENT, Dermatology, Neurology, General Medicine*) and Warangal Localities.
   - Quick-click sample patient queries for one-touch testing.

2. **Dual Similarity Search Engine**:
   - **TF-IDF + Cosine Similarity**: Ultra-fast sparse term matching (<35 ms latency).
   - **FAISS + SentenceTransformers (`all-MiniLM-L6-v2`)**: Dense 384-dimensional vector embedding search for complex colloquial symptom queries.

3. **Emergency Red-Flag Guardrails**:
   - Automated pattern-matching safety layer scanning user queries and retrieved chunks for life-threatening symptoms.
   - Immediate red alert banner rendering local emergency escalation details:
     - **MGM Hospital Warangal Casualty Hotline**: `0870-2441000` / `0870-2441001`
     - **Telangana Emergency Ambulance**: `108`
     - **District Hospital Warangal**: `0870-2577772`

4. **Grounded Guidance & RAG Inspector**:
   - Grounded recommendations outlining primary care advice, local Warangal healthcare facilities, and precautionary steps.
   - Interactive **RAG Evidence Inspector** expander detailing matched similarity scores %, record IDs (`WP-SYN-XXXX`), department, locality, and raw grounded text chunks.

---

## 🛠️ Technical Stack
- **Frontend / UI**: Streamlit (Python)
- **Data Handling**: Pandas, NumPy
- **Retrieval & Vector Search**: Scikit-Learn (TF-IDF Vectorizer), FAISS, SentenceTransformers (`all-MiniLM-L6-v2`), PyTorch
- **Paper Generator**: Python-Docx (IEEE Standard Two-Column Format)

---

## 🚀 How to Run the Application Locally

### 1. Clone the Repository
```bash
git clone https://github.com/2303A51184/NLP-Project.git
cd NLP-Project
```

### 2. Install Required Dependencies
```bash
pip install streamlit pandas numpy scikit-learn sentence-transformers faiss-cpu torch python-docx
```

### 3. Launch the Streamlit Web App
```bash
python -m streamlit run app.py
```
Open your browser and navigate to **`http://localhost:8501`**.

---

## 📄 IEEE Research Paper & Project Assets
- **[IEEE_Research_Paper_RAG_Warangal_Medical_System.docx](IEEE_Research_Paper_RAG_Warangal_Medical_System.docx)**: Full IEEE two-column paper formatted for B.Tech project submission.
- **[RAG-Based Medical Information System.pptx](RAG-Based%20Medical%20Information%20System.pptx)**: Project presentation slides.
- **[cleaned_RAG_Warangal_medical_dataset.csv](cleaned_RAG_Warangal_medical_dataset.csv)**: Preprocessed Warangal medical dataset (12,000 records).

---

## 📂 Repository Structure
```
├── app.py                                              # Main Streamlit application
├── cleaned_RAG_Warangal_medical_dataset.csv            # 12,000 clinical records dataset
├── create_ieee_paper.py                                # Script generating IEEE Word paper
├── IEEE_Research_Paper_RAG_Warangal_Medical_System.docx# Formatted IEEE paper (.docx)
├── RAG-Based Medical Information System.pptx           # Presentation slides
├── Summary of Created Files.docx                       # Project overview summary
├── dataset code.txt                                    # Data preprocessing script
├── .gitignore                                          # Git ignore file
└── README.md                                           # Repository documentation
```
