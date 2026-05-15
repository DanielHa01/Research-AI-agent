"""
Report: Takes all findings in AgentMemory and synthesizes
a structured, cited Markdown report using the Groq LLM.
"""

import os
from groq import Groq
from memory import AgentMemory

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are a professional research writer.
Given a set of research findings with sources, write a comprehensive, well-structured Markdown report.

The report must follow this structure:
# [Topic Title]

## Executive Summary
(3-4 sentence overview)

## Key Findings
(One H3 section per sub-question researched, with analysis and insight)

## Sources
(Numbered list of all URLs cited)

## Conclusion
(2-3 sentences synthesizing the big picture)

Rules:
- Be factual, concise, and analytical
- Cite sources inline as [1], [2], etc.
- Do not invent facts not present in the findings
- Write in clear, professional English
"""

def synthesize_report(memory: AgentMemory) -> str:
    """
    Synthesize a final Markdown report from agent memory.
    Returns a Markdown string.
    """
    context = memory.to_context_string()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Research findings:\n\n{context}"},
        ],
        max_tokens=2000,
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()
