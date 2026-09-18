import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CUSTOM_COMMANDS_PATH = BASE_DIR / "custom_commands.json"


def load_custom_commands():
    if CUSTOM_COMMANDS_PATH.exists():
        with CUSTOM_COMMANDS_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_custom_command(trigger, action):
    if CUSTOM_COMMANDS_PATH.exists():
        with CUSTOM_COMMANDS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    data[trigger] = action

    with CUSTOM_COMMANDS_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def run_custom_command(command):
    commands = load_custom_commands()
    if command in commands:
        import pyautogui
        import time
        pyautogui.hotkey("win", "r")
        time.sleep(1)
        pyautogui.write(commands[command])
        pyautogui.press("enter")
        return True
    return False
