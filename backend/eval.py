"""
Eval: Benchmark the research agent on 10 test queries.
Scores each report on:
  - Completeness: Does it have all required sections? (0-3)
  - Source count: Are at least 3 sources cited? (0-2)
  - Length: Is the report substantive (>300 words)? (0-2)
  - No hallucination markers: Does it avoid "I don't know"? (0-3)

Total score: 0-10 per query. Prints a summary table.
"""

import time
from agent import run_agent

TEST_QUERIES = [
    "The current state of quantum computing",
    "How does CRISPR gene editing work",
    "The impact of remote work on productivity",
    "Recent advances in fusion energy",
    "How large language models are trained",
    "The state of electric vehicle adoption",
    "What is retrieval-augmented generation",
    "How does the US federal reserve set interest rates",
    "The environmental impact of cryptocurrency mining",
    "Recent developments in autonomous vehicles",
]

REQUIRED_SECTIONS = ["## Executive Summary", "## Key Findings", "## Sources", "## Conclusion"]

def score_report(report: str) -> dict:
    scores = {}

    # Completeness: check for required sections
    section_score = sum(1 for s in REQUIRED_SECTIONS if s in report)
    scores["completeness"] = min(section_score, 3)

    # Source count
    source_count = report.count("http")
    scores["sources"] = 2 if source_count >= 3 else (1 if source_count >= 1 else 0)

    # Length
    word_count = len(report.split())
    scores["length"] = 2 if word_count >= 300 else (1 if word_count >= 150 else 0)

    # No hallucination markers
    bad_phrases = ["i don't know", "i cannot", "i'm not sure", "as an ai"]
    has_bad = any(p in report.lower() for p in bad_phrases)
    scores["no_hallucination"] = 0 if has_bad else 3

    scores["total"] = sum(scores[k] for k in ["completeness", "sources", "length", "no_hallucination"])
    return scores

def run_eval():
    print("=" * 60)
    print("Research Agent Evaluation")
    print("=" * 60)
    results = []
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n[{i}/10] Testing: {query}")
        start = time.time()
        try:
            result = run_agent(query)
            elapsed = round(time.time() - start, 1)
            scores = score_report(result["report"])
            results.append({"query": query, "elapsed": elapsed, **scores, "error": None})
            print(f"  Score: {scores['total']}/10 | Time: {elapsed}s")
        except Exception as e:
            results.append({"query": query, "elapsed": None, "total": 0, "error": str(e)})
            print(f"  FAILED: {e}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    avg = sum(r["total"] for r in results) / len(results)
    for r in results:
        status = f"{r['total']}/10" if not r["error"] else f"ERROR: {r['error'][:40]}"
        print(f"  {r['query'][:45]:<45} {status}")
    print(f"\nAverage score: {avg:.1f}/10")

if __name__ == "__main__":
    run_eval()
