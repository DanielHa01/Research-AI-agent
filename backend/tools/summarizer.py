"""
Tool: Summarizer
Takes a chunk of raw scraped text and a query context,
and returns a concise 3-5 sentence summary using the Groq LLM.
"""

import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are a precise research summarizer.
Given raw webpage text and a research query, extract the most relevant facts.
Return a concise summary of 3-5 sentences. Focus only on content relevant to the query.
Do not pad or speculate. If the content is irrelevant, say "No relevant content found."
"""

def summarize_page(text: str, query: str, source_url: str) -> dict:
    """
    Summarize a scraped page relative to a query.
    Returns dict with keys: summary, url.
    """
    if not text.strip():
        return {"summary": "No content could be extracted.", "url": source_url}

    user_msg = f"Query: {query}\n\nWebpage content:\n{text}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=300,
        temperature=0.2,
    )
    summary = response.choices[0].message.content.strip()
    return {"summary": summary, "url": source_url}
