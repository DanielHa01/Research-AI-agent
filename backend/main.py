"""
FastAPI server exposing the research agent as a REST API.
Endpoints:
  POST /research  — run the agent, returns JSON with report
  GET  /health    — health check
"""

import os
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import traceback

load_dotenv()
from agent import run_agent
from chat import chat_with_report, format_history_for_gemini
from database import init_db, save_report, get_all_reports, get_report_by_id, delete_report, search_reports
from exporter import markdown_to_pdf
from deep_dive import run_deep_dive

init_db()

app = FastAPI(title="Research Agent API", version="1.0.0")

ALLOWED_ORIGINS = [
    "https://DanielHa01.github.io",
]

if os.getenv("ENVIRONMENT") == "dev":
    ALLOWED_ORIGINS += [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "GET", "DELETE"],
    allow_headers=["Content-Type"],
)

class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    topic: str
    sub_questions: list[str]
    report: str

class ReportSummary(BaseModel):
    id: int
    topic: str
    sub_questions: list[str]
    created_at: str

class ReportDetail(BaseModel):
    id: int
    topic: str
    sub_questions: list[str]
    report: str
    created_at: str

class ChatRequest(BaseModel):
    report: str
    history: list[dict] = []
    message: str 

class ChatResponse(BaseModel):
    reply: str
    history: list[dict]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/research", response_model=ResearchResponse)
def research(req: ResearchRequest):
    if not req.topic or len(req.topic.strip()) < 3:
        raise HTTPException(status_code=400, detail="Topic too short")
    try:
        result = run_agent(req.topic.strip())
        save_report(result["topic"], result["sub_questions"], result["report"])
        return ResearchResponse(
            topic=result["topic"],
            sub_questions=result["sub_questions"],
            report=result["report"],
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class DeepDiveRequest(BaseModel):
    question: str

class DeepDiveResponse(BaseModel):
    question: str
    angles: list[str]
    deep_report: str

@app.post("/deep-dive", response_model=DeepDiveResponse)
def deep_dive(req: DeepDiveRequest):
    """
    Run a deep dive on a specific sub-question.
    Searches more sources, explores multiple angles, and
    returns an expert-level Markdown section.
    """
    if not req.question or len(req.question.strip()) < 5:
        raise HTTPException(status_code=400, detail="Question too short")
    try:
        result = run_deep_dive(req.question.strip())
        return DeepDiveResponse(
            question=result["question"],
            angles=result["angles"],
            deep_report=result["deep_report"],
        )
    except Exception as e:
        print(f"DEEP DIVE ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=list[ReportSummary])
def get_history(limit: int = 50):
    """Return all saved report summaries, newest first."""
    return get_all_reports(limit=limit)

@app.get("/history/{report_id}", response_model=ReportDetail)
def get_report(report_id: int):
    """Return a single full report by ID."""
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@app.delete("/history/{report_id}")
def delete_history_entry(report_id: int):
    """Delete a report by ID."""
    deleted = delete_report(report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"deleted": True, "id": report_id}

@app.get("/history/search/{query}", response_model=list[ReportSummary])
def search_history(query: str):
    """Search reports by topic or content."""
    if len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    return search_reports(query.strip())

class ExportRequest(BaseModel):
    topic: str
    report: str

@app.post("/export/pdf")
def export_pdf(req: ExportRequest):
    """
    Convert a Markdown report to a styled PDF and return it as a file download.
    Accepts the topic and report text from the frontend (already generated).
    """
    if not req.report.strip():
        raise HTTPException(status_code=400, detail="Report content is empty")
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")

    try:
        pdf_bytes = markdown_to_pdf(req.topic, req.report)
    except RuntimeError as e:
        print(f"PDF EXPORT ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    safe_filename = req.topic.strip().lower()
    safe_filename = "".join(c if c.isalnum() or c in (" ", "-") else "" for c in safe_filename)
    safe_filename = safe_filename.replace(" ", "-")[:60]
    filename = f"research-{safe_filename}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if not req.report.strip():
        raise HTTPException(status_code=400, detail="No report provided to chat about")
    try:
        gemini_history = format_history_for_gemini(req.history)
        reply = chat_with_report(req.report, gemini_history, req.message)

        updated_history = req.history + [
            {"role": "user", "content": req.message},
            {"role": "assistant", "content": reply},
        ]
        return ChatResponse(reply=reply, history=updated_history)
    except RuntimeError as e:
        print(f"CHAT ERROR: {e}")
        raise HTTPException(status_code=502, detail=str(e))
