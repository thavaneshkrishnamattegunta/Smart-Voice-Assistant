# Smart Voice Assistant

A Windows voice assistant written in Python. It listens through the microphone, responds with speech, opens applications and websites, performs searches, reports time and weather, reads news, types text, and supports custom commands.

## Features

- Speech recognition with microphone input
- Text-to-speech responses
- Local replies for greetings, help, identity, time, date, and thanks
- Open Windows applications and websites
- Google web search by voice
- Weather and news lookup
- Type dictated text using `pyautogui`
- Custom commands stored in `custom_commands.json`
- Optional Gemini responses for general questions
- Text mode for testing without a microphone

## Requirements

- Windows 10 or later
- Python 3.11 or later recommended
- A working microphone and speakers or headphones
- Internet access for speech recognition, search, weather, news, and Gemini

## Installation

Open PowerShell in the repository folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run the project with the virtual-environment interpreter directly instead.

## Configuration

Gemini is optional. To enable AI answers for questions that are not built-in commands, create a `.env` file inside:

```text
Smart-Voice-Assistant-Internship-main\smart_voice_assistant-main\smart_voice_assistant-main\.env
```

Add:

```env
GEMINI_API_KEY=your_api_key_here
```

Never commit `.env` or expose your API key. It is excluded by `.gitignore`.

## Run

From the repository folder:

```powershell
python main.py
```

From any directory, use the project interpreter and absolute paths:

```powershell
& "C:\Users\mthav\Downloads\Smart-Voice-Assistant-Internship-main\.venv\Scripts\python.exe" "C:\Users\mthav\Downloads\Smart-Voice-Assistant-Internship-main\main.py"
```

You can also double-click `run_assistant.bat` in the repository folder.

## Text Mode

Text mode is useful for testing commands without a microphone:

```powershell
python main.py --text
```

Run one prompt and exit:

```powershell
python main.py --prompt "hello"
```

## Example Commands

- `Hello`
- `What time is it?`
- `What is today's date?`
- `Open YouTube`
- `Open Notepad`
- `Search for Python tutorials`
- `What is the weather in London?`
- `Tell me the latest news`
- `Type hello world`
- `Add a custom command`
- `Exit`

## Project Layout

```text
main.py                         Root launcher
run_assistant.bat               Windows launcher
requirements.txt                Dependency list
Smart-Voice-Assistant-Internship-main/
	smart_voice_assistant-main/
		smart_voice_assistant-main/
			main.py                   Assistant command loop
			listener.py               Microphone and speech recognition
			speech_engine.py          Text-to-speech
			gemini_ai.py              Optional Gemini integration
			custom_commands.json      User-defined commands
```

## Troubleshooting

### `ModuleNotFoundError`

Install dependencies into the same environment used to run the assistant:

```powershell
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

### Microphone is not detected

Check Windows microphone permissions and set the headset or microphone as the default input device. You can select a device by setting `SMART_VOICE_MICROPHONE` to part of its name.

### Gemini is unavailable

Built-in commands work without Gemini. Install the requirements and add `GEMINI_API_KEY` to `.env` to enable general AI answers.

## Testing

Run the included tests from the repository folder:

```powershell
python -m unittest discover -v
```