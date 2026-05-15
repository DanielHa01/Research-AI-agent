"""
Planner: Takes a high-level research topic and breaks it into
3-5 targeted sub-questions that, when answered together,
give a comprehensive overview of the topic.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are a research planner.
Given a research topic, decompose it into 3-5 specific sub-questions.
Each sub-question should target a distinct angle (definition, current state, challenges, examples, future outlook).
Return ONLY a JSON array of strings. No explanation, no preamble.
Example output: ["What is X?", "How does X work?", "What are the main challenges with X?"]
"""

def decompose_query(topic: str) -> list[str]:
    """
    Decompose a research topic into sub-questions.
    Returns list of question strings.
    Raises ValueError if LLM output cannot be parsed.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Research topic: {topic}"},
        ],
        max_tokens=300,
        temperature=0.3,
    )
    content = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    content = content.replace("```json", "").replace("```", "").strip()
    questions = json.loads(content)
    if not isinstance(questions, list):
        raise ValueError("Planner did not return a list")
    return questions[:5]
