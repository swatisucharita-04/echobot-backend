import requests
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# API keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# ---------------- Weather ----------------
def get_weather(city: str) -> str:
    logging.info(f"[SKILL] Weather triggered for city: {city}")
    if not OPENWEATHER_API_KEY:
        return "Weather API key is not set."
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        return f"Current weather in {city} is {weather} with temperature {temp}°C."
    except requests.exceptions.RequestException as e:
        logging.error(f"Weather API request error: {e}")
        return "Failed to get weather."
    except KeyError:
        logging.error("Unexpected weather API response structure")
        return "Could not parse weather data."


# ---------------- Web Search (Tavily) ----------------
def web_search(query: str) -> str:
    logging.info(f"[SKILL] Web Search triggered for query: {query}")
    if not TAVILY_API_KEY:
        return "Tavily API key is not set."
    try:
        url = "https://api.tavily.com/v1/search"
        headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
        params = {"q": query, "limit": 3}
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return "No results found."
        return "\n".join([r.get('title', 'No Title') for r in results])
    except requests.exceptions.RequestException as e:
        logging.error(f"Tavily API request error: {e}")
        return "Failed to fetch search results."
    except Exception as e:
        logging.error(f"Unexpected error in web search: {e}")
        return "Error occurred while fetching search results."


# ---------------- News ----------------
def get_news(topic: str = "technology") -> str:
    import requests, os, logging
    from dotenv import load_dotenv
    load_dotenv()
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    if not NEWS_API_KEY:
        return "News API key is not set."
    try:
        url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={NEWS_API_KEY}&pageSize=5"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        filtered = [a for a in articles if a.get("title")]
        if not filtered:
            return f"No news found for '{topic}'."
        return "\n".join([a['title'] for a in filtered])
    except Exception as e:
        logging.error(f"News fetch error: {e}")
        return "Failed to get news."

