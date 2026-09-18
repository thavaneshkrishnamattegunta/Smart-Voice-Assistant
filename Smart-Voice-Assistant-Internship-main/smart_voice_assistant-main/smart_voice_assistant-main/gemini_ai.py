# gemini_ai.py
import os
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    genai = None


def _load_env_file():
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip().strip('"').strip("'")
            if name and name not in os.environ:
                os.environ[name] = value
    except OSError:
        pass


_load_env_file()
API_KEY = os.getenv("GEMINI_API_KEY")
model = None

if API_KEY and genai is not None:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        model = None


def ask_gemini(prompt):
    if not API_KEY:
        return "Gemini API key is not configured. Set the GEMINI_API_KEY environment variable."

    if genai is None:
        return "Gemini support is not installed. Built-in commands still work. Install requirements.txt for AI answers."

    if model is None:
        return "Gemini could not be initialized. Check the API key and installed dependencies."

    try:
        final_prompt = f"{prompt}\n\nPlease respond briefly in just 1 or 2 lines."
        response = model.generate_content(final_prompt)
        return response.text.strip()
    except Exception:
        return "Sorry, Gemini could not respond right now."
