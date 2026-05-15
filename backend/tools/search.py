"""
Tool: Web Search
Uses Tavily API to return search results for a query.
Returns a list of {title, url, content} dicts (top N results).
"""

import os
from tavily import TavilyClient

def web_search(query: str, max_results: int = 3) -> list[dict]:
    """
    Search the web for a query using Tavily.
    Returns list of dicts with keys: title, url, content.
    Raises RuntimeError on API failure.
    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
        include_raw_content=False,
    )
    results = []
    for r in response.get("results", []):
        results.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
        })
    return results
