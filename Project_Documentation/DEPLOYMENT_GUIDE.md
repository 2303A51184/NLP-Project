# Deployment Guide: Warangal HealthRAG Clinical Information System

This guide outlines how to deploy the **RAG-Based Medical Information System for Warangal Patients** to live cloud platforms for your university presentation, viva demonstration, or public access.

---

## 🌟 Method 1: Streamlit Community Cloud (Recommended & 100% Free)

Streamlit Community Cloud is the official, zero-configuration cloud hosting platform provided by Snowflake/Streamlit. It builds directly from your GitHub repository.

### Step-by-Step Instructions:

1. **Open Streamlit Cloud:**
   - Navigate to [https://share.streamlit.io](https://share.streamlit.io).
   - Sign in using your GitHub account (`2303A51184`).

2. **Alternatively, Click "Deploy" directly from your browser:**
   - If running locally at `http://localhost:8501`, look at the top-right corner of the browser window.
   - Click the **`Deploy`** button next to the three-dots menu.

3. **Configure Deployment Settings:**
   - **Repository:** `2303A51184/NLP-Project`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL (optional custom subdomain):** `warangal-healthrag` (or `warangal-medical-rag`)

4. **Click "Deploy!":**
   - Streamlit Cloud will automatically detect:
     - `requirements.txt` (Python packages)
     - `packages.txt` (`libgomp1` for FAISS vector search)
     - `.streamlit/config.toml` (Healthcare Light Theme and server configurations)
     - `cleaned_RAG_Warangal_medical_dataset.csv` (12,000 clinical records)
   - Within 2 to 3 minutes, your live web application will be live at:
     ```text
     https://warangal-healthrag.streamlit.app
     ```

---

## 🚀 Method 2: Hugging Face Spaces (Free Cloud Hosting with 16 GB RAM)

Hugging Face Spaces offers a generous 16 GB RAM free tier, ideal for dense SentenceTransformer vector embeddings.

### Step-by-Step Instructions:

1. Go to [https://huggingface.co/spaces](https://huggingface.co/spaces) and log in.
2. Click **"Create new Space"**.
3. Choose a Space Name: `warangal-medical-rag`.
4. License: `mit` or `apache-2.0`.
5. Select Space SDK: **Streamlit**.
6. Hardware: Free (2 vCPU · 16 GB RAM).
7. Under Repository options, link to GitHub `https://github.com/2303A51184/NLP-Project` or push via Git remote.
8. The Space will build and launch automatically.

---

## 🐳 Method 3: Docker Container Deployment (Render, Railway, Cloud Run, AWS)

A production-ready `Dockerfile` and `Procfile` are included in the repository.

### Run with Docker Locally or on a Server:
```bash
# Build the Docker image
docker build -t warangal-healthrag:latest .

# Run the container mapping port 8501
docker run -d -p 8501:8501 --name warangal-healthrag-app warangal-healthrag:latest
```
Access at `http://localhost:8501` or your server's public IP.

### Deploy on Render.com:
1. Create a free account at [https://render.com](https://render.com).
2. Click **"New +"** → **"Web Service"**.
3. Connect your GitHub repository `2303A51184/NLP-Project`.
4. Runtime: **Python 3** (or **Docker**).
5. Build Command: `pip install -r requirements.txt`.
6. Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`.
7. Instance Type: Free.
8. Click **"Create Web Service"**.

---

## 📶 Method 4: Local Wi-Fi / College Presentation Demonstration

If you are presenting in an auditorium or laboratory and want the examination panel or audience to test the app on their own mobile phones or laptops on the same Wi-Fi network:

1. Keep the Streamlit server running on your laptop.
2. Note your laptop's local IPv4 address (e.g. `192.168.1.35`).
3. Any mobile device or laptop connected to the same Wi-Fi router can open:
   ```text
   http://192.168.1.35:8501
   ```
4. The full application, login, triage, and RAG search will work seamlessly across all connected devices without requiring any external internet connection!

---

## 📋 Included Cloud Configuration Files

| File | Purpose |
| :--- | :--- |
| `packages.txt` | Installs `libgomp1` on Debian/Ubuntu cloud containers for FAISS CPU vector index |
| `requirements.txt` | Python library versions (`streamlit`, `sentence-transformers`, `faiss-cpu`, etc.) |
| `.streamlit/config.toml` | Production light theme and server flags (`headless = true`, `maxUploadSize = 50`) |
| `Dockerfile` | Multi-stage production container build for cloud VM deployment |
| `Procfile` | Dyno web process binding for PaaS platforms (Render, Heroku, Koyeb) |
| `auth_db.py` | Auto-initializes SQLite schema (`medical_system.db`) and default test accounts on startup |
