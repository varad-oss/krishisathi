<div align="center">
  <h1>🌱 KrishiSathi (कृषि साथी)</h1>
  
  <p><strong>A zero-billing, multimodal AI diagnostic platform and voice-first advisory network for Indian agriculture.</strong></p>

<h3>🔗 <a href="https://krishisathi-ai.vercel.app">Live Demo Website</a></h3>
</div>

---

## 📌 Overview

**KrishiSathi** is a highly scalable, serverless microservices platform engineered to deliver real-time, localized crop diagnostics and regenerative agricultural advisories to farmers in low-resource environments. 

Built for the **Google Build with AI Hackathon**, this project demonstrates modern AI architecture by integrating multimodal LLMs (Gemini 1.5 Flash), real-time geospatial data injection, and custom client-side audio processing—all operating under a strict **$0 infrastructure cost** (zero-billing) deployment model.

---

## 🚀 Technical Highlights

### 1. Multimodal AI Diagnostics
* **Architecture:** A `FastAPI` backend wrapper around the `Gemini 1.5 Flash` API processes base64-encoded crop images uploaded by farmers.
* **Context Injection:** The backend dynamically fetches real-time weather and soil data via the `Open-Meteo API` (based on the user's geolocation) and injects it directly into the LLM prompt, forcing the agent to consider hyper-local environmental factors before diagnosing diseases or recommending treatments.

### 2. Voice-First Accessibility (VAD & TTS)
* **Voice Activity Detection (VAD):** Engineered a custom client-side React hook utilizing the Web Audio API to detect microphone volume levels, automatically terminating recording after 2.5 seconds of silence.
* **Streaming Audio Pipeline:** Built a custom Text-to-Speech (TTS) fallback pipeline in the FastAPI backend that calculates byte-sizes in-memory and returns exact `Content-Length` headers, bypassing native browser `AbortError` race conditions and ensuring flawless audio playback in strict-mode React environments.

### 3. Strict Multilingual Localization
* **Non-Romanized Enforcement:** The system supports 10 regional Indian languages (Hindi, Marathi, Tamil, etc.). Prompt engineering strictly prohibits the LLM from outputting Romanized transliterations (e.g., Hinglish) and enforces native Indic numerals in all UI components.

### 4. Zero-Billing Edge Deployment
* **Infrastructure:** Both the `Next.js` frontend and `FastAPI` backend are deployed on **Vercel Edge/Serverless** functions. 
* **Cost Efficiency:** By utilizing Vercel's serverless Python runtime (`@vercel/python`) and free-tier API integrations, the entire production architecture scales down to zero cost when idle.

---

## 💻 Tech Stack

| Domain | Technology |
|---|---|
| **Frontend** | Next.js 14, React 18, Tailwind CSS, Web Audio API, Lucide Icons |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Google GenAI SDK |
| **AI / APIs** | Gemini 1.5 Flash, Open-Meteo, gTTS |
| **DevOps** | Vercel Serverless Functions (`vercel.json`), GitHub Actions |

---

## ⚙️ Local Development

### 1. Clone the Repository
```bash
git clone https://github.com/varad-oss/krishisathi.git
cd krishisathi
```

### 2. Run the Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create a .env file and add your GEMINI_API_KEY
echo 'GEMINI_API_KEY="your-api-key"' > .env

# Start the server
uvicorn main:app --reload --port 8000
```

### 3. Run the Frontend (Next.js)
In a new terminal tab:
```bash
cd frontend
npm install

# Point the frontend to the local backend
echo 'NEXT_PUBLIC_API_URL="http://localhost:8000"' > .env.local

npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000).

---
*Developed by Varad Pandare | IIT Kharagpur*
