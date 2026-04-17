from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 5) -> list:
    """Search the web using DuckDuckGo and return top results."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    return results
