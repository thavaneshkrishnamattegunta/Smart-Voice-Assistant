try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

def get_latest_news():
    if requests is None or BeautifulSoup is None:
        return ["News support is not installed. Run: python -m pip install -r requirements.txt"]

    url = "https://www.bbc.com/news"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = []

        for item in soup.select(".gs-c-promo-heading__title"):
            if item.text.strip():
                headlines.append(item.text.strip())
            if len(headlines) >= 5:
                break

        return headlines
    except Exception:
        return ["Sorry, I couldn't fetch the news right now."]

def get_weather_data():
    try:
        url = "https://wttr.in/?format=3"
        response = requests.get(url)
        return response.text
    except Exception as e:
        return "Sorry, I couldn't fetch the weather right now."
