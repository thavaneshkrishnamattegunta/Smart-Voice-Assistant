# Smart Voice Assistant Quick Start

## 1) Install Python dependencies

Open PowerShell in this project folder and run:

```powershell
python -m pip install -r requirements.txt
```

## 2) Add your Gemini API key

Edit the `.env` file in this folder and set:

```env
GEMINI_API_KEY=your_actual_key_here
```

## 3) Run the assistant

Double-click `run_assistant.bat` or run:

```powershell
python .\main.py
```

## 4) Use it

- Put on your headset or earbuds
- Make sure Windows sees them as the default input device
- Speak clearly
- Say things like:
  - "What is the time?"
  - "Open YouTube"
  - "What is the weather?"
  - "Tell me the news"
  - "Exit"

## Notes

- If the microphone is not working, set the headset as the default input in Windows Sound settings.
- If the assistant says the Gemini key is missing, add it to `.env`.
