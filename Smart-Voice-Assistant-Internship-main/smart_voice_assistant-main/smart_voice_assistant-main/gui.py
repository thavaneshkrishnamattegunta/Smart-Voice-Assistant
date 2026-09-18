import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import json
import os
from pathlib import Path
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import pyautogui
import webbrowser
import time
from datetime import datetime
import subprocess
import shutil
from PIL import Image, ImageTk
import cv2
import queue
import psutil
from main import get_local_response

BASE_DIR = Path(__file__).resolve().parent

# Initialize speech engine
engine = pyttsx3.init()

# Initialize Gemini AI
API_KEY = os.getenv("GEMINI_API_KEY")
model = None
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        model = None

class VideoPlayer:
    def __init__(self, canvas, video_path):
        self.canvas = canvas
        self.video_path = video_path
        self.cap = None
        self.is_playing = False
        self.current_frame = None
        self.photo = None
        self.play_thread = None
        self.stop_event = threading.Event()
        self.frame_buffer = None
        self.last_frame_time = 0
        
        # Bind canvas resize event
        self.canvas.bind('<Configure>', self._on_canvas_resize)
        
    def _on_canvas_resize(self, event):
        # Update frame size when canvas is resized
        if self.frame_buffer is not None:
            self._update_canvas()
        
    def play(self):
        if not self.is_playing:
            self.is_playing = True
            self.stop_event.clear()
            if self.play_thread is None or not self.play_thread.is_alive():
                self.play_thread = threading.Thread(target=self._play_video)
                self.play_thread.daemon = True
                self.play_thread.start()
        
    def pause(self):
        self.is_playing = False
        
    def _play_video(self):
        try:
            if self.cap is None:
                self.cap = cv2.VideoCapture(self.video_path)
                if not self.cap.isOpened():
                    raise Exception("Failed to open video file")
            
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frame_delay = 1.0 / fps if fps > 0 else 0.033
            
            while not self.stop_event.is_set():
                if self.is_playing:
                    ret, frame = self.cap.read()
                    if ret:
                        # Convert frame to RGB
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Store frame in buffer
                        self.frame_buffer = frame
                        
                        # Update canvas in the main thread
                        self.canvas.after(0, self._update_canvas)
                        
                        # Control playback speed
                        time.sleep(frame_delay)
                    else:
                        # Reset video when it reaches the end
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                else:
                    # If paused, just sleep briefly
                    time.sleep(0.1)
        except Exception as e:
            print(f"Video playback error: {e}")
            self.is_playing = False
            
    def _update_canvas(self):
        if self.frame_buffer is not None:
            try:
                # Get canvas dimensions
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                # Calculate aspect ratio
                frame_height, frame_width = self.frame_buffer.shape[:2]
                aspect_ratio = frame_width / frame_height
                
                # Calculate new dimensions while maintaining aspect ratio
                if canvas_width / canvas_height > aspect_ratio:
                    new_height = canvas_height
                    new_width = int(new_height * aspect_ratio)
                else:
                    new_width = canvas_width
                    new_height = int(new_width / aspect_ratio)
                
                # Resize frame to fit canvas
                resized_frame = cv2.resize(self.frame_buffer, (new_width, new_height))
                
                # Convert frame to PhotoImage
                self.current_frame = Image.fromarray(resized_frame)
                self.photo = ImageTk.PhotoImage(image=self.current_frame)
                
                # Update canvas
                self.canvas.delete("all")
                
                # Center the image in the canvas
                x = (canvas_width - new_width) // 2
                y = (canvas_height - new_height) // 2
                self.canvas.create_image(x, y, image=self.photo, anchor=tk.NW)
            except Exception as e:
                print(f"Canvas update error: {e}")
                
    def __del__(self):
        self.stop_event.set()
        if self.cap is not None:
            self.cap.release()

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print("You said:", command)
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn't understand.")
            return ""
        except sr.RequestError:
            print("Could not request results from Google.")
            return ""

def get_latest_news():
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
        return ["Could not fetch news right now."]

def get_weather_data(city="Guntur"):
    try:
        # If the city looks like coordinates, show a helpful message
        if city.startswith("~") or any(char.isdigit() for char in city):
            return "Please provide a city name, not coordinates."
        url = f"https://wttr.in/{city}?format=%l:+%c+%t,+%h+humidity,+%p+precipitation"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Sorry, I couldn't fetch the weather right now."
    except Exception as e:
        return "Sorry, I couldn't fetch the weather right now."

def get_current_time():
    current_time = datetime.now()
    return current_time.strftime("%I:%M %p")

def find_installed_executable(names):
    for name in names:
        resolved = shutil.which(name)
        if resolved:
            return resolved

    username = os.getenv('USERNAME') or os.getenv('USER') or ''
    roots = [
        os.path.join('C:\\', 'Program Files'),
        os.path.join('C:\\', 'Program Files (x86)'),
        os.path.join('C:\\', 'Users', username, 'AppData', 'Local', 'Programs'),
        os.path.join('C:\\', 'Users', username, 'AppData', 'Local', 'Microsoft', 'WindowsApps'),
        os.path.join('C:\\', 'Program Files', 'Steam', 'steamapps', 'common'),
        os.path.join('C:\\', 'Program Files (x86)', 'Steam', 'steamapps', 'common'),
        os.path.join('C:\\', 'Games'),
    ]

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


def open_application(app_name):
    app_name = (app_name or "").strip().lower()
    if not app_name:
        return False

    if app_name.startswith("open "):
        app_name = app_name.replace("open ", "", 1)

    if app_name in ["gmail", "google mail", "googlemail", "mail", "my gmail"]:
        webbrowser.open("https://mail.google.com")
        return True

    if app_name in ["maps", "google maps", "map"]:
        webbrowser.open("https://www.google.com/maps")
        return True

    if app_name in ["google", "search google"]:
        webbrowser.open("https://www.google.com")
        return True

    if "gmail" in app_name or "google mail" in app_name or "mail" in app_name:
        webbrowser.open("https://mail.google.com")
        return True

    if "maps" in app_name or "google maps" in app_name:
        webbrowser.open("https://www.google.com/maps")
        return True

    if "google" in app_name:
        webbrowser.open("https://www.google.com")
        return True

    if "youtube" in app_name:
        webbrowser.open("https://www.youtube.com")
        return True

    # Get the current user's username
    username = os.getenv('USERNAME')
    
    app_paths = {
        # Development Tools
        "vs code": [
            f"C:\\Users\\{username}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
            f"C:\\Users\\{username}\\AppData\\Local\\Programs\\Microsoft VS Code\\bin\\code.cmd",
            "C:\\Program Files\\Microsoft VS Code\\Code.exe",
            "C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe",
            "C:\\Program Files\\Microsoft VS Code\\bin\\code.cmd",
            "C:\\Program Files (x86)\\Microsoft VS Code\\bin\\code.cmd",
            "code",
            "code.cmd"
        ],
        "visual studio code": [
            f"C:\\Users\\{username}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
            f"C:\\Users\\{username}\\AppData\\Local\\Programs\\Microsoft VS Code\\bin\\code.cmd",
            "C:\\Program Files\\Microsoft VS Code\\Code.exe",
            "C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe",
            "C:\\Program Files\\Microsoft VS Code\\bin\\code.cmd",
            "C:\\Program Files (x86)\\Microsoft VS Code\\bin\\code.cmd",
            "code",
            "code.cmd"
        ],
        "visual studio": r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe",
        "sublime text": r"C:\Program Files\Sublime Text\sublime_text.exe",
        
        # Web Browsers
        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{username}\AppData\Local\Google\Chrome\Application\chrome.exe"
        ],
        "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
        "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "spotify": "spotify.exe",
        "steam": "steam.exe",
        "discord": "discord.exe",
        "gta vice city": ["gta-vc.exe", "gta_vc.exe"],
        "gta san andreas": ["gta-sa.exe", "gta_sa.exe"],
        "vice city": ["gta-vc.exe", "gta_vc.exe"],
        "san andreas": ["gta-sa.exe", "gta_sa.exe"],
        
        # System Applications
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "camera": "microsoft.windows.camera:",
        "file explorer": "explorer.exe",
        "task manager": "taskmgr.exe",
        "control panel": "control.exe",
        "settings": "ms-settings:",
        "snipping tool": "snippingtool.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
        
        # Microsoft Office
        "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        "outlook": r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
        
        # Media Applications
        "media player": "wmplayer.exe",
        "photos": "ms-photos:",
        "groove music": "mswindowsmusic:",
        "movies & tv": "mswindowsvideo:",
        
        # System Tools
        "disk cleanup": "cleanmgr.exe",
        "defragment": "dfrgui.exe",
        "registry editor": "regedit.exe",
        "system information": "msinfo32.exe",
        "device manager": "devmgmt.msc",
        "disk management": "diskmgmt.msc",
        
        # Common Folders
        "documents": f"C:\\Users\\{username}\\Documents",
        "downloads": f"C:\\Users\\{username}\\Downloads",
        "pictures": f"C:\\Users\\{username}\\Pictures",
        "music": f"C:\\Users\\{username}\\Music",
        "videos": f"C:\\Users\\{username}\\Videos",
        "desktop": f"C:\\Users\\{username}\\Desktop",
        
        # Web Applications
        "chatgpt": "https://chat.openai.com",
        "gmail": "https://mail.google.com",
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://github.com",
        "linkedin": "https://www.linkedin.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://twitter.com",
        "instagram": "https://www.instagram.com",
        "maps": "https://www.google.com/maps",
        "translate": "https://translate.google.com",
        "drive": "https://drive.google.com",
        "spotify": "https://open.spotify.com",
        "netflix": "https://www.netflix.com",
        "amazon": "https://www.amazon.com"
    }
    
    app_name = app_name.lower()

    for target in ["gta vice city", "vice city", "gta san andreas", "san andreas"]:
        if target in app_name:
            exe_path = find_installed_executable(["gta-vc.exe", "gta_vc.exe", "gta-sa.exe", "gta_sa.exe"])
            if exe_path:
                subprocess.Popen(exe_path)
                return True
            return False

    if app_name in ["spotify", "steam", "discord"]:
        exe_path = find_installed_executable([f"{app_name}.exe"])
        if exe_path:
            subprocess.Popen(exe_path)
            return True
        return False
    
    # Handle search commands
    if "search" in app_name:
        search_terms = app_name.replace("search", "").strip()
        if "youtube" in app_name:
            search_url = f"https://www.youtube.com/results?search_query={search_terms.replace(' ', '+')}"
        else:
            search_url = f"https://www.google.com/search?q={search_terms.replace(' ', '+')}"
        webbrowser.open(search_url)
        return True
    
    if app_name in app_paths:
        path = app_paths[app_name]
        
        # Handle VS Code paths (which is a list of possible paths)
        if app_name in ["vs code", "visual studio code"]:
            for vs_code_path in path:
                try:
                    # For command line versions (code or code.cmd)
                    if vs_code_path in ["code", "code.cmd"]:
                        subprocess.Popen([vs_code_path])
                        return True
                    
                    # For full paths
                    if os.path.exists(vs_code_path):
                        subprocess.Popen([vs_code_path])
                        return True
                except Exception as e:
                    print(f"Trying next VS Code path. Error: {e}")
                    continue
            
            # If all paths failed, try using the Windows Run dialog
            try:
                pyautogui.hotkey("win", "r")
                time.sleep(1)
                pyautogui.write("code")
                pyautogui.press("enter")
                return True
            except Exception as e:
                print(f"Failed to open VS Code through Run dialog: {e}")
                return False
            
        # Handle Chrome paths (which is a list of possible paths)
        if app_name == "chrome":
            for chrome_path in path:
                try:
                    if os.path.exists(chrome_path):
                        subprocess.Popen([chrome_path])
                        return True
                except Exception as e:
                    print(f"Trying next Chrome path. Error: {e}")
                    continue
            return False
            
        # Handle web URLs
        if isinstance(path, str) and path.startswith("http"):
            webbrowser.open(path)
            return True
            
        # Handle Windows Store apps (using URI scheme)
        if isinstance(path, str) and ":" in path:
            try:
                subprocess.Popen(["start", path], shell=True)
                return True
            except Exception as e:
                print(f"Error opening Windows Store app: {e}")
                return False
            
        # Handle folders
        if isinstance(path, str) and os.path.isdir(path):
            try:
                subprocess.Popen(["explorer", path])
                return True
            except Exception as e:
                print(f"Error opening folder: {e}")
                return False
            
        # Handle other applications
        try:
            if isinstance(path, str):
                path = os.path.expandvars(path)
            subprocess.Popen(path)
            return True
        except Exception as e:
            print(f"Error opening application: {e}")
            return False
    return False

def ask_gemini(prompt):
    if not API_KEY or model is None:
        return "Gemini API key is not configured. Set the GEMINI_API_KEY environment variable."

    try:
        final_prompt = f"{prompt}\n\nPlease respond briefly in just 1 or 2 lines."
        response = model.generate_content(final_prompt)
        return response.text.strip()
    except Exception:
        return "Sorry, Gemini could not respond right now."

def load_custom_commands():
    file_path = "custom_commands.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def save_custom_command(trigger, action):
    file_path = "custom_commands.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data[trigger] = action

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def run_custom_command(command):
    commands = load_custom_commands()
    if command in commands:
        pyautogui.hotkey("win", "r")
        time.sleep(1)
        pyautogui.write(commands[command])
        pyautogui.press("enter")
        return True
    return False

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Voice Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0A0A0A")

        # Configure ttk styles
        style = ttk.Style()
        style.configure("Dark.TFrame", background="#0A0A0A")
        style.configure("Dark.TLabel", background="#0A0A0A", foreground="#FFFFFF")
        style.configure("Dark.TButton", background="#1E1E1E", foreground="#FFFFFF")
        
        # Create main container with padding and 3D effect
        self.main_container = ttk.Frame(root, style="Dark.TFrame")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Create left and right frames with 3D effect
        self.left_frame = ttk.Frame(self.main_container, style="Dark.TFrame")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        self.right_frame = ttk.Frame(self.main_container, style="Dark.TFrame")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))

        # Create a container for the video and status
        self.video_container = ttk.Frame(self.left_frame, style="Dark.TFrame")
        self.video_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Add a decorative header above the video
        self.video_header = ttk.Label(
            self.video_container,
            text="Assistant Status",
            font=("Segoe UI", 12, "bold"),
            foreground="#2196F3",
            background="#0A0A0A",
            padding=5
        )
        self.video_header.pack(pady=(0, 10))

        # Video canvas with 3D effect - Fill the entire container
        self.video_canvas = tk.Canvas(
            self.video_container,
            bg="#0A0A0A",
            highlightthickness=2,
            highlightbackground="#1E1E1E"
        )
        self.video_canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Initialize video player
        video_path = BASE_DIR / "assets" / "6913754_Motion Graphics_Motion Graphic_1280x720.mp4"
        self.video_player = VideoPlayer(self.video_canvas, str(video_path))
        self.video_player.play()

        # Status indicators with modern design
        self.status_frame = ttk.Frame(self.video_container, style="Dark.TFrame")
        self.status_frame.pack(fill=tk.X, pady=(0, 20))

        # Microphone status with animation
        self.mic_status = ttk.Label(
            self.status_frame,
            text="● Microphone",
            font=("Segoe UI", 10, "bold"),
            foreground="#4CAF50",
            background="#0A0A0A",
            padding=5
        )
        self.mic_status.pack(side=tk.LEFT, padx=5)

        # AI status with animation
        self.ai_status = ttk.Label(
            self.status_frame,
            text="● AI Ready",
            font=("Segoe UI", 10, "bold"),
            foreground="#2196F3",
            background="#0A0A0A",
            padding=5
        )
        self.ai_status.pack(side=tk.LEFT, padx=5)

        # Browser-like assistant panel on the left side
        self.side_panel = ttk.Frame(self.left_frame, style="Dark.TFrame")
        self.side_panel.pack(fill=tk.BOTH, pady=(0, 20))

        self.side_panel_header = ttk.Label(
            self.side_panel,
            text="Listening Panel",
            font=("Segoe UI", 11, "bold"),
            foreground="#FFFFFF",
            background="#0A0A0A",
            padding=8
        )
        self.side_panel_header.pack(fill=tk.X)

        self.listening_box = tk.Canvas(
            self.side_panel,
            width=300,
            height=120,
            bg="#101010",
            highlightthickness=2,
            highlightbackground="#1E1E1E"
        )
        self.listening_box.pack(fill=tk.BOTH, expand=True)

        self.live_indicator = self.listening_box.create_oval(130, 18, 170, 58, fill="#4CAF50", outline="#4CAF50")
        self.live_text = self.listening_box.create_text(150, 82, text="Listening...", fill="#FFFFFF", font=("Segoe UI", 10, "bold"))

        # Chat area in right frame with modern design
        self.chat_frame = ttk.Frame(self.right_frame, style="Dark.TFrame")
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

        # Chat header with modern design
        self.chat_header = ttk.Label(
            self.chat_frame,
            text="Conversation",
            font=("Segoe UI", 14, "bold"),
            foreground="#FFFFFF",
            background="#0A0A0A",
            padding=10
        )
        self.chat_header.pack(pady=(0, 10))

        # Chat area with modern design
        self.chat_area = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#0A0A0A",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            highlightthickness=2,
            highlightbackground="#1E1E1E"
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)

        # Start the assistant thread
        self.listen_thread = threading.Thread(target=self.run_assistant)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def update_chat(self, sender, message):
        self.chat_area.config(state=tk.NORMAL)
        if sender == "You":
            self.chat_area.insert(tk.END, f"\n{sender}: ", "user")
            self.chat_area.insert(tk.END, f"{message}\n", "user_message")
        else:
            self.chat_area.insert(tk.END, f"\n{sender}: ", "assistant")
            self.chat_area.insert(tk.END, f"{message}\n", "assistant_message")
        
        # Configure tags for different message types with modern colors
        self.chat_area.tag_configure("user", foreground="#4CAF50", font=("Segoe UI", 11, "bold"))
        self.chat_area.tag_configure("user_message", foreground="#FFFFFF")
        self.chat_area.tag_configure("assistant", foreground="#2196F3", font=("Segoe UI", 11, "bold"))
        self.chat_area.tag_configure("assistant_message", foreground="#E0E0E0")
        
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def update_status(self, status, color="#00FF00"):
        if status == "Listening...":
            self.mic_status.config(foreground="#FFA500")
            self.ai_status.config(text="● AI Listening", foreground="#FFA500")
            self.listening_box.itemconfigure(self.live_indicator, fill="#FFA500", outline="#FFA500")
            self.listening_box.itemconfigure(self.live_text, text="Listening...", fill="#FFFFFF")
            self.video_player.play()
        elif status == "Processing...":
            self.mic_status.config(foreground="#2196F3")
            self.ai_status.config(text="● AI Thinking", foreground="#2196F3")
            self.listening_box.itemconfigure(self.live_indicator, fill="#2196F3", outline="#2196F3")
            self.listening_box.itemconfigure(self.live_text, text="Processing...", fill="#FFFFFF")
            self.video_player.pause()
        else:
            self.mic_status.config(foreground="#4CAF50")
            self.ai_status.config(text="● AI Ready", foreground="#2196F3")
            self.listening_box.itemconfigure(self.live_indicator, fill="#4CAF50", outline="#4CAF50")
            self.listening_box.itemconfigure(self.live_text, text="Ready", fill="#FFFFFF")
            self.video_player.play()

    def run_assistant(self):
        while True:
            self.update_status("Listening...")
            command = listen()
            if command:
                self.update_status("Processing...")
                self.update_chat("You", command)
                self.process_command(command.lower())
            self.update_status("Ready")

    def process_command(self, command):
        command = command.lower().strip()
        local_response = get_local_response(command)
        if local_response:
            self.update_chat("Assistant", local_response)
            speak(local_response)
            return

        # First check if it's a custom command
        if run_custom_command(command):
            self.update_chat("Assistant", "Running your custom command.")
            speak("Running your custom command.")
            return

        # Then check for command creation
        if "add a custom command" in command:
            self.update_chat("Assistant", "Okay! What should I listen for to trigger this command?")
            speak("Okay! What should I listen for to trigger this command?")
            trigger = listen()
            if trigger:
                self.update_chat("You", trigger)
                self.update_chat("Assistant", f"Got it! What action should I perform when I hear '{trigger}'?")
                speak(f"Got it! What action should I perform when I hear '{trigger}'?")
                action = listen()
                if action:
                    self.update_chat("You", action)
                    save_custom_command(trigger, action)
                    self.update_chat("Assistant", f"Custom command saved! Next time you say '{trigger}', I will perform '{action}'.")
                    speak(f"Custom command saved! Next time you say '{trigger}', I will perform '{action}'.")
                    return

        # Then handle other commands
        if "exit" in command or "quit" in command:
            self.update_chat("Assistant", "Goodbye!")
            speak("Goodbye!")
            self.root.quit()

        elif "time" in command:
            current_time = get_current_time()
            self.update_chat("Assistant", f"The current time is {current_time}")
            speak(f"The current time is {current_time}")

        elif "weather" in command:
            city = "Guntur"  # Default city
            if "in" in command:
                city = command.split("in")[-1].strip()
            weather = get_weather_data(city)
            self.update_chat("Assistant", f"Weather in {city}: {weather}")
            speak(f"Weather in {city}: {weather}")

        elif "open" in command or "launch" in command or "start" in command:
            app_name = command.replace("open", "", 1).replace("launch", "", 1).replace("start", "", 1).strip()
            app_name = app_name.replace("please", "").strip()
            display_name = app_name.replace("google mail", "Google Mail").replace("my gmail", "Gmail").replace("mail", "Mail").replace("google maps", "Google Maps").replace("maps", "Maps")
            spoken_name = display_name.title() if display_name else app_name.title()
            self.update_chat("Assistant", f"Opening {spoken_name}")
            speak(f"Opening {spoken_name}.")
            threading.Thread(target=open_application, args=(app_name,), daemon=True).start()

        elif "type" in command:
            text_to_type = command.replace("type", "").strip()
            self.update_chat("Assistant", f"Typing: {text_to_type}")
            speak(f"Typing: {text_to_type}")
            pyautogui.write(text_to_type)

        elif "news" in command:
            self.update_chat("Assistant", "Fetching the latest news...")
            speak("Fetching the latest news...")
            headlines = get_latest_news()
            for i, headline in enumerate(headlines[:5], 1):
                self.update_chat("Assistant", f"{i}. {headline}")
                speak(headline)

        else:
            reply = ask_gemini(command)
            self.update_chat("Assistant", reply)
            speak(reply)

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    
    # Function to show welcome message after UI is fully loaded
    def show_welcome():
        # Ensure all UI components are properly initialized
        root.update_idletasks()
        
        # Show welcome message
        welcome_message = "Hello! I'm your smart voice assistant. I can help you with:\n" \
                         "• Opening applications (VS Code, Chrome, etc.)\n" \
                         "• Checking weather and time\n" \
                         "• Reading news\n" \
                         "• Custom commands\n" \
                         "• And much more!\n\n" \
                         "How can I assist you today?"
        app.update_chat("Assistant", welcome_message)
        speak("Hello! I'm your smart voice assistant. How can I assist you today?")
    
    # Schedule the welcome message to appear after the GUI is fully loaded
    root.after(100, show_welcome)  # Reduced delay to 100ms
    
    # Start the main loop
    root.mainloop()
    