"""
Agent: Orchestrates the full research pipeline.
  1. Decompose topic → sub-questions (Planner)
  2. For each sub-question:
     a. Web search (Tavily)
     b. Scrape top results (BeautifulSoup)
     c. Summarize each result (Groq)
     d. Store in memory
  3. Synthesize final report (Groq)
"""

import os
from dotenv import load_dotenv
from planner import decompose_query
from memory import AgentMemory
from tools.search import web_search
from tools.scraper import scrape_page
from tools.summarizer import summarize_page
from report import synthesize_report

load_dotenv()

MAX_RESULTS_PER_QUERY = 3

def run_agent(topic: str) -> dict:
    """
    Run the full research agent for a given topic.
    Returns dict with keys: topic, sub_questions, findings, report.
    """
    memory = AgentMemory(topic=topic)

    # Step 1: Plan
    print(f"[Agent] Planning sub-questions for: {topic}")
    memory.sub_questions = decompose_query(topic)
    print(f"[Agent] Sub-questions: {memory.sub_questions}")

    # Step 2: Research each sub-question
    for question in memory.sub_questions:
        print(f"[Agent] Researching: {question}")
        search_results = web_search(question, max_results=MAX_RESULTS_PER_QUERY)

        summaries = []
        for result in search_results:
            url = result["url"]
            # Use Tavily's snippet first; fall back to scraping
            raw_text = result.get("content") or scrape_page(url)
            summarized = summarize_page(raw_text, question, url)
            summaries.append(summarized)

        memory.add_finding(question, summaries)

    # Step 3: Synthesize report
    print("[Agent] Synthesizing final report...")
    report = synthesize_report(memory)

    return {
        "topic": topic,
        "sub_questions": memory.sub_questions,
        "findings": memory.findings,
        "report": report,
    }


if __name__ == "__main__":
    result = run_agent("The current state of quantum computing")
    print(result["report"])
