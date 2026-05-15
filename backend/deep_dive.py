"""
Deep Dive: A focused mini-agent that researches a single sub-question in depth.

Differences from the main agent:
  - Takes ONE specific question (not a broad topic)
  - Generates 3 drill-down angles on that question via LLM
  - Searches with more results per query (5 vs 3)
  - Synthesizes an expert-level, detailed section (not a high-level summary)
  - Returns structured data: { question, angles, findings, deep_report }

Reuses existing tools (search, scraper, summarizer) from tools/.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv
from tools.search import web_search
from tools.scraper import scrape_page
from tools.summarizer import summarize_page

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

MAX_SOURCES_PER_ANGLE = 5
MAX_ANGLES = 3


# ── Step 1: Generate drill-down angles ──────────────────────────────────────

ANGLE_SYSTEM_PROMPT = """You are a research specialist.
Given a specific research question, generate 3 drill-down angles that go deeper into it.
Each angle should be a focused, specific sub-query that explores a distinct facet:
  - Mechanisms / how it works technically
  - Real-world examples, case studies, or data
  - Challenges, open problems, or expert debates

Return ONLY a JSON array of 3 strings. No explanation. No preamble.
Example: ["How does X work at a molecular level?", "What are documented case studies of X?", "What are the unresolved challenges in X?"]
"""

def generate_drill_angles(question: str) -> list[str]:
    """
    Generate 3 focused drill-down angles for a given research question.
    Returns list of 3 angle query strings.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ANGLE_SYSTEM_PROMPT},
            {"role": "user", "content": f"Research question: {question}"},
        ],
        max_tokens=250,
        temperature=0.3,
    )
    content = response.choices[0].message.content.strip()
    content = content.replace("```json", "").replace("```", "").strip()
    angles = json.loads(content)
    if not isinstance(angles, list):
        raise ValueError("Angle generator did not return a list")
    return angles[:MAX_ANGLES]

def research_angle(angle: str, parent_question: str) -> list[dict]:
    """
    Search and summarize sources for a single drill-down angle.
    Returns list of {summary, url} dicts.
    """
    results = web_search(angle, max_results=MAX_SOURCES_PER_ANGLE)
    summaries = []
    for result in results:
        url = result["url"]
        raw_text = result.get("content") or scrape_page(url)
        context_query = f"{parent_question} — specifically: {angle}"
        summarized = summarize_page(raw_text, context_query, url)
        summaries.append(summarized)
    return summaries

DEEP_REPORT_SYSTEM_PROMPT = """You are an expert research analyst writing a deep-dive section for a research report.

You will receive a research question and detailed findings from multiple angles.
Write a comprehensive, expert-level Markdown section that:

1. Starts with ## Deep Dive: [question]
2. Has one ### subsection per angle explored
3. Synthesizes findings analytically — draw connections, note tensions, highlight significance
4. Cites sources inline as [1], [2], etc.
5. Ends with a ### Key Takeaways bullet list (3-5 bullets)
6. Ends with a ### Sources list of all URLs

Rules:
- Be substantive and analytical, not just descriptive
- Minimum 400 words
- Do not invent facts not present in the findings
- Write for an intelligent reader who already read the surface-level report
"""

def synthesize_deep_report(question: str, angles: list[str], findings: list[dict]) -> str:
    """
    Synthesize all angle findings into a detailed Markdown deep dive section.

    Args:
        question: The original sub-question being deep-dived.
        angles:   The drill-down angle queries explored.
        findings: List of {angle, summaries: [{summary, url}]} dicts.

    Returns:
        Markdown string of the deep dive section.
    """
    context_lines = [f"Original question: {question}", ""]
    for i, finding in enumerate(findings):
        context_lines.append(f"Angle {i+1}: {finding['angle']}")
        for j, s in enumerate(finding["summaries"], 1):
            context_lines.append(f"  Source {j}: {s['summary']} (URL: {s['url']})")
        context_lines.append("")

    context = "\n".join(context_lines)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": DEEP_REPORT_SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
        max_tokens=2000,
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()

def run_deep_dive(question: str) -> dict:
    """
    Run a full deep dive on a single research question.

    Args:
        question: The specific sub-question to deep dive.

    Returns:
        Dict with keys:
          - question:    The original question
          - angles:      List of drill-down angle strings
          - findings:    List of {angle, summaries} dicts
          - deep_report: Full Markdown deep dive section string
    """
    print(f"[DeepDive] Starting deep dive on: {question}")

    angles = generate_drill_angles(question)
    print(f"[DeepDive] Angles: {angles}")

    findings = []
    for angle in angles:
        print(f"[DeepDive] Researching angle: {angle}")
        summaries = research_angle(angle, question)
        findings.append({"angle": angle, "summaries": summaries})

    print("[DeepDive] Synthesizing deep report...")
    deep_report = synthesize_deep_report(question, angles, findings)

    return {
        "question": question,
        "angles": angles,
        "findings": findings,
        "deep_report": deep_report,
    }
