from pathlib import Path
import os
import runpy
import sys


ASSISTANT_DIR = (
    Path(__file__).resolve().parent
    / "Smart-Voice-Assistant-Internship-main"
    / "smart_voice_assistant-main"
    / "smart_voice_assistant-main"
)

if not (ASSISTANT_DIR / "main.py").exists():
    raise FileNotFoundError(f"Assistant entry point not found: {ASSISTANT_DIR / 'main.py'}")

sys.path.insert(0, str(ASSISTANT_DIR))
os.chdir(ASSISTANT_DIR)
runpy.run_path(str(ASSISTANT_DIR / "main.py"), run_name="__main__")
