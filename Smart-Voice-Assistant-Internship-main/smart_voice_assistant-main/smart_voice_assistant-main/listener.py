# listener.py
import os
import speech_recognition as sr

_recognizer = sr.Recognizer()
_microphone = None
_calibrated = False


def get_microphone_index(preferred_name=None):
    try:
        devices = sr.Microphone.list_microphone_names()
    except Exception:
        return None

    env_name = (preferred_name or os.getenv("SMART_VOICE_MICROPHONE") or "").strip().lower()
    if env_name:
        for index, name in enumerate(devices):
            if env_name in name.lower():
                return index

    priority_terms = [
        "headset",
        "earphone",
        "earbud",
        "airpods",
        "bluetooth",
        "pod",
        "wireless",
        "microphone",
        "array",
    ]

    for term in priority_terms:
        for index, name in enumerate(devices):
            lowered = name.lower()
            if term in lowered and "output" not in lowered and "speaker" not in lowered:
                return index

    if devices:
        return 0
    return None


def listen():
    global _microphone, _calibrated
    device_index = get_microphone_index()
    if _microphone is None:
        _microphone = sr.Microphone(device_index=device_index) if device_index is not None else sr.Microphone()

    try:
        with _microphone as source:
            if not _calibrated:
                print("Calibrating microphone...")
                _recognizer.adjust_for_ambient_noise(source, duration=0.25)
                _recognizer.energy_threshold = max(_recognizer.energy_threshold, 300)
                _recognizer.dynamic_energy_threshold = True
                _recognizer.pause_threshold = 0.65
                _calibrated = True

            print("Listening...")
            try:
                audio = _recognizer.listen(source, timeout=3, phrase_time_limit=8)
                print("Processing audio...")

                try:
                    command = _recognizer.recognize_google(audio, language="en-US")
                    print("You said:", command)
                    return command.lower()
                except sr.UnknownValueError:
                    print("Sorry, I didn't understand. Please speak clearly.")
                    return ""
                except sr.RequestError:
                    print("Could not request results from Google.")
                    return ""
            except sr.WaitTimeoutError:
                print("No speech detected. Please try again.")
                return ""
    except Exception as exc:
        print(f"Microphone error: {exc}")
        return ""


def take_command():
    return listen()