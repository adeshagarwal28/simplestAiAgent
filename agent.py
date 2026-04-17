import os
import google.generativeai as genai
from dotenv import load_dotenv
from tools import web_search

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

INTENT_PROMPT = """You are an intent classifier. Given a user message, respond with ONLY one of these labels:
- search: the user wants to find information from the web or asks about recent/current events
- email: the user wants to write or draft an email
- chat: a general question, conversation, or anything else

User message: {message}

Respond with only the label, nothing else."""


def classify_intent(message: str) -> str:
    response = model.generate_content(INTENT_PROMPT.format(message=message))
    intent = response.text.strip().lower()
    if intent not in ["search", "email", "chat"]:
        return "chat"
    return intent


def run_agent(message: str, chat_history: list) -> tuple[str, str]:
    """
    Run the agent on a user message.
    Returns (response_text, intent) so the UI can show which mode was used.
    """
    intent = classify_intent(message)

    if intent == "search":
        results = web_search(message)
        if not results:
            return "I searched the web but couldn't find relevant results. Try rephrasing your query.", intent

        context = "\n\n".join(
            [f"Source: {r.get('href', '')}\nTitle: {r.get('title', '')}\n{r.get('body', '')}"
             for r in results]
        )
        prompt = f"""You are a helpful research assistant. Based on the web search results below,
answer the user's question with a clear, concise summary. Cite sources where relevant.

User question: {message}

Search results:
{context}

Provide a well-structured answer."""
        response = model.generate_content(prompt)
        return response.text, intent

    elif intent == "email":
        prompt = f"""You are a professional email writer. Draft a polished email body based on this request:

Request: {message}

Rules:
- Write only the email body (no subject line, no "Subject:" prefix)
- Start with an appropriate greeting
- Be professional, clear, and concise
- End with a professional sign-off (leave the name blank as [Your Name])"""
        response = model.generate_content(prompt)
        return response.text, intent

    else:
        # Build recent conversation context
        recent = chat_history[-6:] if len(chat_history) > 6 else chat_history
        history_text = "\n".join(
            [f"{m['role'].capitalize()}: {m['content']}" for m in recent]
        )
        prompt = f"""You are a helpful, friendly AI assistant.

{f"Conversation so far:{chr(10)}{history_text}{chr(10)}" if history_text else ""}
User: {message}
Assistant:"""
        response = model.generate_content(prompt)
        return response.text, intent
