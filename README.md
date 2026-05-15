![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.1-orange)
![Gemini](https://img.shields.io/badge/Chat-Gemini%202.5%20Flash-blue?logo=google)
![Deployed on Render](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render)
![Frontend on GitHub Pages](https://img.shields.io/badge/Frontend-GitHub%20Pages-222?logo=github)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)

# Research Agent

An autonomous, multi-step research agent that decomposes complex queries into sub-questions, searches the web, and synthesizes structured, expert-level reports with citations.

## 🚀 Features

### 🔍 Core Research Engine
- **Autonomous Planning:** Uses LLM (Llama 3.1 8b instant via Groq) to decompose any topic into 5-8 targeted sub-questions.
- **Smart Search:** Leverages **Tavily Search API** for high-signal web results.
- **Deep Scraping:** Scrapes and summarizes multiple sources per sub-question using BeautifulSoup and Groq.
- **Structured Synthesis:** Produces a comprehensive Markdown report with inline citations and a full source list.

### 🔬 Deep Dive Mode
- **Recursive Research:** Click "Deep Dive" next to any sub-question to trigger a focused mini-agent.
- **Multi-Angle Exploration:** Decomposes a single question into 3 technical, practical, and critical angles.
- **Enhanced Depth:** Researches 5 sources per angle (15 total) for expert-level detail.
- **Inline Expansion:** Deep dive reports are rendered directly below the sub-question in a collapsible panel.

### 📄 PDF Export
- **Pro-Styled PDF:** Converts Markdown reports into print-optimized A4 PDFs via **WeasyPrint**.
- **Typography & Layout:** Georgia serif typography, styled headers, and automatic page numbering.
- **Live Downloads:** One-click export with sanitized filenames directly from the UI.

### 🗂 History & Persistence
- **SQLite Storage:** Every generated report is automatically saved to a local database.
- **Searchable Sidebar:** Browse, search, and load past research sessions instantly.
- **Snappy UX:** Optimized for speed with smooth scrolling and instant sidebar toggling.

### 💬 Chat Follow-Up
- **Grounded Chat:** Ask follow-up questions about the generated report using **Google Gemini 2.5 Flash**.
- **Context Awareness:** The assistant understands the full report context and provides precise, grounded answers.

## 🛠 Tech Stack

- **Backend:** Python, FastAPI, Groq (Llama 3), Google Gemini (Chat), SQLite.
- **Frontend:** Vanilla JS/HTML/CSS, Lucide Icons, Marked.js (Markdown rendering).
- **Tools:** Tavily Search, BeautifulSoup (Scraping), WeasyPrint (PDF).

## 🏁 Getting Started

### Prerequisites
- Python 3.10+
- API Keys: Groq, Tavily, Google Gemini.

### Setup

1. **Clone & Install:**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Configuration:**
   Create a `backend/.env` file based on `.env.example`:
   ```env
   GROQ_API_KEY=your_key
   TAVILY_API_KEY=your_key
   GOOGLE_API_KEY=your_key
   ```

3. **Run the API:**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

4. **Launch the UI:**
   Open `frontend/index.html` in your browser (or use a Live Server extension).

## 📊 Evaluation
Run the automated benchmark suite to see the agent's performance across 4 quality dimensions:
```bash
python backend/eval.py
```