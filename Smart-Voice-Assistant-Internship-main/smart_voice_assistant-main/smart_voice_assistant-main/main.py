# main.py
import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from custom_command_handler import run_custom_command
from gemini_ai import ask_gemini
from scraper import get_latest_news
from listener import listen, take_command
from speech_engine import speak
import pyautogui
import webbrowser
import time
import threading
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent
CUSTOM_COMMANDS_PATH = BASE_DIR / "custom_commands.json"

APP_URLS = {
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "linkedin": "https://www.linkedin.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "maps": "https://www.google.com/maps",
    "drive": "https://drive.google.com",
    "spotify": "https://open.spotify.com",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.com",
    "chatgpt": "https://chat.openai.com",
    "duckduckgo": "https://duckduckgo.com",
}

APP_EXECUTABLES = {
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "paint": ["mspaint.exe"],
    "spotify": ["spotify.exe"],
    "discord": ["discord.exe"],
    "steam": ["steam.exe"],
    "chrome": ["chrome.exe"],
    "edge": ["msedge.exe"],
    "firefox": ["firefox.exe"],
    "file explorer": ["explorer.exe"],
    "command prompt": ["cmd.exe"],
    "powershell": ["powershell.exe"],
    "vs code": ["code.exe", "code.cmd", "code"],
    "visual studio code": ["code.exe", "code.cmd", "code"],
    "vscode": ["code.exe", "code.cmd", "code"],
    "gta vice city": ["gta-vc.exe", "gta_vc.exe"],
    "gta san andreas": ["gta-sa.exe", "gta_sa.exe", "gta-sa.exe"],
    "vice city": ["gta-vc.exe", "gta_vc.exe"],
    "san andreas": ["gta-sa.exe", "gta_sa.exe"],
    "gta": ["gta5.exe", "gta-vc.exe", "gta_sa.exe", "gta-sa.exe"],
}


def find_installed_executable(names):
    for name in names:
        resolved = shutil.which(name)
        if resolved:
            return resolved

    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    roots = [
        os.path.join("C:\\", "Program Files"),
        os.path.join("C:\\", "Program Files (x86)"),
        os.path.join("C:\\", "Users", username, "AppData", "Local", "Programs"),
        os.path.join("C:\\", "Users", username, "AppData", "Local", "Microsoft", "WindowsApps"),
        os.path.join("C:\\", "Program Files", "Steam", "steamapps", "common"),
        os.path.join("C:\\", "Program Files (x86)", "Steam", "steamapps", "common"),
        os.path.join("C:\\", "Games"),
    ]

    roots = [r for r in roots if r]
    for root in roots:
        if not os.path.exists(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                lower_name = filename.lower()
                for candidate in names:
                    if lower_name == candidate.lower():
                        return os.path.join(dirpath, filename)
    return None


def open_requested_target(target):
    target = normalize_command(target or "")
    if not target:
        return False

    if target.startswith("open "):
        target = target.replace("open ", "", 1)

    alias_map = {
        "gmail": ["gmail", "google mail", "googlemail", "mail", "my gmail"],
        "maps": ["maps", "google maps", "map"],
        "google": ["google", "search google"],
        "youtube": ["youtube", "you tube", "yt"],
        "drive": ["drive", "google drive"],
        "github": ["github", "git hub"],
        "spotify": ["spotify", "spotify music"],
        "chatgpt": ["chatgpt", "chat gpt", "openai"],
        "linkedin": ["linkedin"],
        "netflix": ["netflix"],
    }

    for canonical, keywords in alias_map.items():
        if any(keyword in target for keyword in keywords):
            if canonical == "spotify":
                exe_path = find_installed_executable(APP_EXECUTABLES["spotify"])
                if exe_path:
                    os.startfile(exe_path)
                    return True
            if canonical in APP_URLS:
                webbrowser.open(APP_URLS[canonical])
                return True
            exe_path = find_installed_executable(APP_EXECUTABLES.get(canonical, []))
            if exe_path:
                os.startfile(exe_path)
                return True

    if "google" in target and "mail" in target:
        webbrowser.open(APP_URLS["gmail"])
        return True

    if "gmail" in target or "google mail" in target or "mail" in target:
        webbrowser.open(APP_URLS["gmail"])
        return True

    if "maps" in target or "google maps" in target:
        webbrowser.open(APP_URLS["maps"])
        return True

    if "youtube" in target:
        webbrowser.open(APP_URLS["youtube"])
        return True

    if "google" in target:
        webbrowser.open(APP_URLS["google"])
        return True

    if target in APP_URLS:
        webbrowser.open(APP_URLS[target])
        return True

    for known_name, executable_names in APP_EXECUTABLES.items():
        if target == known_name or target.startswith(known_name):
            exe_path = find_installed_executable(executable_names)
            if exe_path:
                os.startfile(exe_path)
                return True
            return False

    if "google" in target:
        webbrowser.open("https://www.google.com")
        return True

    if "spotify" in target:
        exe_path = find_installed_executable(["spotify.exe"])
        if exe_path:
            os.startfile(exe_path)
            return True
        webbrowser.open("https://open.spotify.com")
        return True

    if "gta vice city" in target or "vice city" in target:
        exe_path = find_installed_executable(["gta-vc.exe", "gta_vc.exe"])
        if exe_path:
            os.startfile(exe_path)
            return True
        return False

    if "gta san andreas" in target or "san andreas" in target:
        exe_path = find_installed_executable(["gta-sa.exe", "gta_sa.exe"])
        if exe_path:
            os.startfile(exe_path)
            return True
        return False

    return False


def _ensure_custom_commands_file():
    if not CUSTOM_COMMANDS_PATH.exists():
        with CUSTOM_COMMANDS_PATH.open("w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)


def save_custom_command(trigger, action):
    _ensure_custom_commands_file()
    with CUSTOM_COMMANDS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    data[trigger] = action

    with CUSTOM_COMMANDS_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def normalize_command(command):
    if not command:
        return ""
    text = command.lower().strip()
    text = text.replace("?", " ").replace("!", " ").replace(".", " ")
    text = " ".join(text.split())
    return text


def get_local_response(command):
    """Return a response for common requests that do not need an AI service."""
    command = normalize_command(command)
    if not command:
        return None

    greetings = ("hello", "hi", "hey", "good morning", "good afternoon", "good evening")
    if command in greetings or any(command.startswith(f"{greeting} ") for greeting in greetings):
        hour = datetime.now().hour
        if hour < 12:
            period = "Good morning"
        elif hour < 18:
            period = "Good afternoon"
        else:
            period = "Good evening"
        return f"{period}! How can I help you?"

    if command in {"how are you", "how are you doing", "are you okay"}:
        return "I'm doing well and ready to help."

    if command in {"what is your name", "whats your name", "who are you"}:
        return "I'm your smart voice assistant."

    if command in {"thanks", "thank you", "thank you so much"}:
        return "You're welcome!"

    if command in {"what time is it", "tell me the time", "current time", "time"}:
        return f"The current time is {datetime.now().strftime('%I:%M %p').lstrip('0')}."

    if command in {"what is today's date", "what is the date", "today's date", "date"}:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    if command in {"help", "what can you do", "what can you help me with"}:
        return "I can open apps and websites, tell the time and weather, read the news, type text, and run custom commands."

    return None


def perform_task(command):
    command = normalize_command(command)
    local_response = get_local_response(command)
    if local_response:
        speak(local_response)
        return

    _ensure_custom_commands_file()
    # Check and run custom command if matched
    try:
        with CUSTOM_COMMANDS_PATH.open("r", encoding="utf-8") as f:
            custom_cmds = json.load(f)
        for trigger in custom_cmds:
            if trigger in command:
                speak("Running your custom command.")
                pyautogui.hotkey("win", "r")
                time.sleep(1)
                pyautogui.write(custom_cmds[trigger])
                pyautogui.press("enter")
                return
    except Exception:
        pass

    if run_custom_command(command):
        speak("Running your custom command.")
        return

    if "add a custom command" in command:
        speak("Okay! How should I save to run this command?")
        trigger = take_command()

        speak(f"Got it! What should I do when I hear '{trigger}'?")
        action = take_command()

        save_custom_command(trigger, action)
        speak(f"Custom command saved! Next time you say '{trigger}', I will run '{action}'.")
        return

    if "open " in command or command.startswith("launch ") or command.startswith("start "):
        target = command.replace("open", "", 1).replace("launch", "", 1).replace("start", "", 1).strip()
        if target:
            target = target.replace("please", "").strip()
            display_name = (
                target.replace("google mail", "Gmail")
                .replace("my gmail", "Gmail")
                .replace("mail", "Mail")
                .replace("google maps", "Google Maps")
                .replace("maps", "Maps")
                .replace("open ", "")
                .replace("launch ", "")
            )
            spoken_name = display_name.title() if display_name else target.title()
            speak(f"Opening {spoken_name}.")
            threading.Thread(target=open_requested_target, args=(target,), daemon=True).start()
            return

    if "type" in command:
        text_to_type = command.replace("type", "", 1).strip()
        if text_to_type:
            speak(f"Typing: {text_to_type}")
            pyautogui.write(text_to_type)
            return

    search_prefixes = ("search for ", "search ", "look up ", "find ")
    for prefix in search_prefixes:
        if command.startswith(prefix):
            query = command[len(prefix):].strip()
            if query:
                speak(f"Searching for {query}.")
                webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
                return

    if "news" in command:
        speak("Fetching the latest news...")
        headlines = get_latest_news()
        if headlines:
            for i, headline in enumerate(headlines[:5], 1):
                speak(f"News {i}: {headline}")
        else:
            speak("Sorry, I couldn't fetch the news.")
    elif "weather" in command:
        from weather import get_weather
        city = "Guntur"
        if " in " in command:
            city = command.split(" in ", 1)[1].strip() or city
        speak(f"Fetching the weather for {city}.")
        weather = get_weather(city)
        speak(weather)
        # add_chat(f"Assistant: {weather}")  # Removed or commented out as it is undefined

    else:
        
        reply = ask_gemini(command)
        speak(reply)

def handle_text_command(command):
    command = normalize_command(command)
    if not command:
        return
    if "exit" in command or "quit" in command:
        speak("Goodbye!")
        return "exit"
    perform_task(command)
    return "continue"


def main():
    _ensure_custom_commands_file()
    parser = argparse.ArgumentParser(description="Smart Voice Assistant")
    parser.add_argument("--text", action="store_true", help="type commands instead of using microphone input")
    parser.add_argument("--prompt", default="", help="single text prompt to process immediately")
    args = parser.parse_args()

    if args.prompt:
        speak("Processing your prompt.")
        return handle_text_command(args.prompt)

    if args.text:
        print("Type your command. Type 'exit' to quit.")
        while True:
            try:
                command = input("You: ").strip()
            except EOFError:
                break
            if not command:
                continue
            if handle_text_command(command) == "exit":
                break
        return

    speak("Welcome! I'm your smart assistant. How can I help you today?")
    while True:
        command = listen()
        if command:
            if "exit" in command or "quit" in command:
                speak("Goodbye!")
                break
            perform_task(command)


if __name__ == "__main__":
    main()
