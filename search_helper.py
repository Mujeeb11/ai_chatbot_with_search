import requests
from newspaper import Article

SERPER_API_KEY = "YOUR_SERPER_API_KEY"

def search_serper(query):
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY}
    data = {"q": query}
    res = requests.post(url, json=data, headers=headers)
    return res.json()

def fetch_and_summarize(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.title + ":\n" + article.text[:500] + "..."

def search_and_summarize(query):
    results = search_serper(query)
    if not results.get("organic"):
        return "No relevant data found online."
    top_result = results["organic"][0]
    return fetch_and_summarize(top_result["link"])