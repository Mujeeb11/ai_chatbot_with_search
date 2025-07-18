import re
from search_helper import search_and_summarize

FACTUAL_KEYWORDS = ["latest", "news", "today", "current", "live", "update"]

def should_use_search_api(message: str):
    message = message.lower()
    return any(k in message for k in FACTUAL_KEYWORDS) or "search" in message or re.search(r'\d{4}', message)

def hybrid_response(user_message: str, llm_reply: str):
    if should_use_search_api(user_message):
        web_summary = search_and_summarize(user_message)
        return f"{llm_reply}\n\n🔎 Factual update:\n{web_summary}"
    return llm_reply