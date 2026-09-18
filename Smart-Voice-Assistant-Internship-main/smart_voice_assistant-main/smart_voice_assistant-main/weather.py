try:
    import requests
except ImportError:
    requests = None

def get_weather(city="Guntur"):
    if requests is None:
        return "Weather support is not installed. Run: python -m pip install -r requirements.txt"

    try:
        url = f"https://wttr.in/{city}?format=%l:+%c+%t,+%h+humidity,+%p+precipitation"
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and response.text.strip():
            return response.text.strip()
        else:
            return f"Sorry, I couldn't fetch the weather for {city} right now."
    except Exception as e:
        return f"Error getting weather information for {city}."