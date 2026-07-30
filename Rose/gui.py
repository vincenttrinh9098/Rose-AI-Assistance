"""
gui.py

Settings GUI for Rose - separate process from main.py.
Run manually with: python3 gui.py
"""
from tkinter import filedialog
import customtkinter as ctk
import pyttsx3
import json
import tkinter
import threading 
import random
import traceback
import math
import time
from core.audio_io import speak,stop_speaking


GUI_ERROR_LOG = "logs/gui_error.log"
SETTINGS_PATH = "config/settings.json"
ENV_PATH = "../.env"

STATUS_COLORS = {
    "idle": "#4FC3F7",
    "listening": "#4ADE80",
    "speaking": "#FBBF24",
}

systemWidth = 500
systemHeight= 550

import os
import subprocess

PLIST_PATH = os.path.expanduser("~/Library/LaunchAgents/com.vincenttrinh.rose.plist")




customtkinter_appearance = ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")  # different accent entirely
ctk.set_default_color_theme("blue")


def load_settings() -> dict:
    try:
        with open(SETTINGS_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_settings(settings: dict) -> None:
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)


class RoseSettingsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.report_callback_exception = self._log_callback_exception
        self.title("Rose Settings")
        self.geometry("700x600")

        self.settings = load_settings()

        # top navigation bar
        nav_bar = ctk.CTkFrame(self, height=50, fg_color="#0d1520", corner_radius=0)
        nav_bar.pack(fill="x", side="top")

        ctk.CTkLabel(nav_bar, text="Rose.AI", font=ctk.CTkFont(size=16, weight="bold"), text_color="#F8FAFC").pack(side="left", padx=15)

        self.nav_dropdown = ctk.CTkOptionMenu(
            nav_bar,
            values=["Home", "Voice", "Hotkey", "Config Files", "Conversation", "Gui Error Logs", "API Keys"],
            command=self._switch_screen,
            fg_color="#111827",
            button_color="#2563EB",
            button_hover_color="#3B82F6",
        )
        self.nav_dropdown.pack(side="right", padx=15, pady=8)

        # main content container - all screens live here, only one visible at a time
        self.content_container = ctk.CTkFrame(self, fg_color="#151E2E", corner_radius=0)
        self.content_container.pack(fill="both", expand=True)

        # build each screen as its own frame inside content_container
        self._launchctl_check_counter = 0
        self.screens = {}
        self.screens["Home"] = ctk.CTkFrame(self.content_container, fg_color="#0d1520", corner_radius=0)
        self.screens["Voice"] = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.screens["Hotkey"] = ctk.CTkFrame(self.content_container, fg_color="#151E2E")
        self.screens["Config Files"] = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.screens["Conversation"] = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.screens["Gui Error Logs"] = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.screens["API Keys"] = ctk.CTkFrame(self.content_container, fg_color="transparent")

        self._build_home_tab(self.screens["Home"])
        self._build_voice_tab(self.screens["Voice"])
        self._build_hotkey_tab(self.screens["Hotkey"])
        self._build_config_tab(self.screens["Config Files"])
        self._build_conversation_tab(self.screens["Conversation"])
        self._build_error_log_tab(self.screens["Gui Error Logs"])
        self._build_api_keys_tab(self.screens["API Keys"])

        self._switch_screen("Home")



        
    def _switch_screen(self, screen_name):
        for frame in self.screens.values():
            frame.pack_forget()
        self.screens[screen_name].pack(fill="both", expand=True)
        

    def _log_callback_exception(self, exc, val, tb):
        with open(GUI_ERROR_LOG, "a") as f:
            f.write("".join(traceback.format_exception(exc, val, tb)) + "\n")
        print("".join(traceback.format_exception(exc, val, tb)))

#VOICE TAB
    def _build_voice_tab(self, tab):
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        self.voice_map = {v.name: v.id for v in voices}

        self.voice_dropdown = ctk.CTkOptionMenu(tab, values=list(self.voice_map.keys()))
        self.voice_dropdown.pack(pady=10)

        # find the display name matching the currently saved voice, and select it
        current_voice_name = self.settings.get("say_voice_name")
        if current_voice_name and current_voice_name in self.voice_map:
            self.voice_dropdown.set(current_voice_name)
            

        save_button = ctk.CTkButton(tab, text="Save Voice", command=self._save_voice)
        save_button.pack(pady=10)
            
    def _save_voice(self):
        selected_name = self.voice_dropdown.get()
        selected_id = self.voice_map[selected_name]
        self.settings["voice_id"] = selected_id
        self.settings["say_voice_name"] = selected_name
        speak(f"Hello, I am {selected_name}")
        save_settings(self.settings)
        print(f"Saved voice: {selected_name}")

    #HOTKEY TAB

    def _build_hotkey_tab(self,tab):

        current_hotkey = self.settings.get("hotkey", "<cmd>+<shift>+0")
        current_modifiers, current_key = self._parse_hotkey(current_hotkey)

        # --- Modifiers group ---
        modifier_frame = ctk.CTkFrame(tab, fg_color="#1F2937")
        modifier_frame.pack(pady=(15, 5), padx=20, fill="x")

        ctk.CTkLabel(modifier_frame, text="Modifiers", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))

        self.cmd_var = ctk.BooleanVar(value="<cmd>" in current_modifiers)
        self.shift_var = ctk.BooleanVar(value="<shift>" in current_modifiers)
        self.ctrl_var = ctk.BooleanVar(value="<ctrl>" in current_modifiers)
        self.alt_var = ctk.BooleanVar(value="<alt>" in current_modifiers)

        ctk.CTkCheckBox(modifier_frame, text="⌘ Command", variable=self.cmd_var).pack(pady=3, anchor="w", padx=30)
        ctk.CTkCheckBox(modifier_frame, text="⇧ Shift", variable=self.shift_var).pack(pady=3, anchor="w", padx=30)
        ctk.CTkCheckBox(modifier_frame, text="⌃ Control", variable=self.ctrl_var).pack(pady=3, anchor="w", padx=30)
        ctk.CTkCheckBox(modifier_frame, text="⌥ Option", variable=self.alt_var).pack(pady=(3, 10), anchor="w", padx=30)

        # --- Key group ---
        key_frame = ctk.CTkFrame(tab, fg_color="#1F2937")
        key_frame.pack(pady=5, padx=20, fill="x")


        ctk.CTkLabel(key_frame, text="Key", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))

        key_options = list("0123456789") + list("abcdefghijklmnopqrstuvwxyz")
        self.key_dropdown = ctk.CTkOptionMenu(key_frame, values=key_options)
        self.key_dropdown.pack(pady=(0, 10))
        if current_key in key_options:
            self.key_dropdown.set(current_key)

        # --- Preview ---
        self.preview_label = ctk.CTkLabel(tab, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.preview_label.pack(pady=10)
        self._update_preview()

        for var in (self.cmd_var, self.shift_var, self.ctrl_var, self.alt_var):
            var.trace_add("write", lambda *args: self._update_preview())
        self.key_dropdown.configure(command=lambda *_: self._update_preview())

        # --- Test + Save ---
        self.test_result_label = ctk.CTkLabel(tab, text="", text_color="gray")
        self.test_result_label.pack(pady=(0, 5))

        button_row = ctk.CTkFrame(tab, fg_color="transparent")
        button_row.pack(pady=5)

        test_button = ctk.CTkButton(button_row, text="Test Hotkey (5s)", command=self._test_hotkey)
        test_button.grid(row=0, column=0, padx=5)

        save_button = ctk.CTkButton(button_row, text="Save Hotkey", command=self._save_hotkey)
        save_button.grid(row=0, column=1, padx=5)

        note = ctk.CTkLabel(
            tab,
            text="Note: some key combinations are reserved by macOS or other apps.\nUse Test to confirm before saving.",
            text_color="gray", font=ctk.CTkFont(size=11), justify="center",
        )
        note.pack(pady=(10, 0))


    def _test_hotkey(self):
        combo = self._build_combo_string()
        self.test_result_label.configure(text=f"Press {combo} within 5 seconds...", text_color="orange")

        import subprocess

        def run_test():
            script = (
                "from pynput import keyboard\n"
                "import sys\n"
                "\n"
                "def on_activate():\n"
                "    print('DETECTED')\n"
                "    sys.exit(0)\n"
                "\n"
                f'hotkey = keyboard.GlobalHotKeys({{"{combo}": on_activate}})\n'
                "hotkey.start()\n"
                "hotkey.join(timeout=5)\n"
                "print('TIMEOUT')\n"
            )
            result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=7)
            detected = "DETECTED" in result.stdout
            self.after(0, self._show_test_result, detected)

        threading.Thread(target=run_test, daemon=True).start()
        
    def _show_test_result(self, detected: bool):
        if detected:
            self.test_result_label.configure(text="✓ Hotkey detected successfully!", text_color="green")
        else:
            self.test_result_label.configure(text="✗ Not detected - this combo may be reserved. Try another.", text_color="red")

    def _parse_hotkey(self, hotkey_str: str) -> tuple[list, str]:
        """Splits a stored hotkey string like '<cmd>+<shift>+r' into modifiers and the key."""
        parts = hotkey_str.split("+")
        modifiers = [p for p in parts if p.startswith("<")]
        key = next((p for p in parts if not p.startswith("<")), "")
        return modifiers, key


    def _build_combo_string(self) -> str:
        modifiers = []
        if self.cmd_var.get():
            modifiers.append("<cmd>")
        if self.shift_var.get():
            modifiers.append("<shift>")
        if self.ctrl_var.get():
            modifiers.append("<ctrl>")
        if self.alt_var.get():
            modifiers.append("<alt>")
        key = self.key_dropdown.get()
        return "+".join(modifiers + [key])


    def _update_preview(self, *args):
        combo = self._build_combo_string()
        self.preview_label.configure(text=f"Your hotkey: {combo}")


    def _save_hotkey(self):
        combo = self._build_combo_string()

        if not any([self.cmd_var.get(), self.shift_var.get(), self.ctrl_var.get(), self.alt_var.get()]):
            print("Select at least one modifier key")
            return

        self.settings["hotkey"] = combo
        save_settings(self.settings)
        print(f"Saved hotkey: {combo}")

#CONFIG TAB

    def _build_config_tab(self,tab):

        self.config_files = {
            "Apps": "config/apps.json",
            "Steam Games": "config/steam_games.json",
            "VS Code Projects": "config/projects.json",
            "GitHub Repos": "config/github_repos.json",
            "Search Sites": "config/search_sites.json",
        }

        # Which config file
        self.config_selector = ctk.CTkOptionMenu(
            tab, values=list(self.config_files.keys()), command=self._on_config_selected
        )
        self.config_selector.pack(pady=(10, 5))

        # Existing entries dropdown - lets you pick one to edit, or "New Entry" to add one
        self.entry_selector = ctk.CTkComboBox(
            tab, values=["New Entry"], command=self._on_entry_selected
        )
        self.entry_selector.pack(pady=5)

        # Container frame that gets rebuilt depending on simple vs detailed form
        self.form_frame = ctk.CTkFrame(tab)
        self.form_frame.pack(pady=10, fill="x", padx=20)

        save_button = ctk.CTkButton(tab, text="Save Entry", command=self._save_entry)
        save_button.pack(pady=5)

        delete_button = ctk.CTkButton(tab, text="Delete Entry", fg_color="darkred", command=self._delete_entry)
        delete_button.pack(pady=5)

        self._on_config_selected(self.config_selector.get())


    def _on_config_selected(self, selected_label):
        path = self.config_files[selected_label]
        with open(path) as f:
            self._current_config_data = json.load(f)
        self._current_config_path = path

        entry_names = ["New Entry"] + list(self._current_config_data.keys())
        self.entry_selector.configure(values=entry_names)
        self.entry_selector.set("New Entry")
        self._on_entry_selected("New Entry")


    def _on_entry_selected(self, selected_entry):
        for widget in self.form_frame.winfo_children():
            widget.destroy()

        is_apps_file = self._current_config_path.endswith("apps.json")
        is_search_sites_file = self._current_config_path.endswith("search_sites.json")
        is_known_entry = selected_entry in self._current_config_data
        existing = self._current_config_data.get(selected_entry, {}) if is_known_entry else {}

        self.entry_name_field = ctk.CTkEntry(self.form_frame, placeholder_text="Name (e.g. 'youtube')")
        self.entry_name_field.pack(pady=5, fill="x")
        if is_known_entry:
            self.entry_name_field.insert(0, selected_entry)

        if is_apps_file:
            self.type_field = ctk.CTkOptionMenu(self.form_frame, values=["url", "native_app"])
            self.type_field.pack(pady=5, fill="x")
            if existing.get("type"):
                self.type_field.set(existing["type"])

            self.target_field = ctk.CTkEntry(self.form_frame,     placeholder_text="Enter a website URL or application name (e.g., https://youtube.com)")
            self.target_field.pack(pady=5, fill="x")
            if existing.get("target"):
                self.target_field.insert(0, existing.get("target"))

            self.aliases_field = ctk.CTkEntry(self.form_frame, placeholder_text="Alternative names (comma-separated, e.g., youtube, yt)")
            self.aliases_field.pack(pady=5, fill="x")
            if existing.get("aliases"):
                self.aliases_field.insert(0, ", ".join(existing.get("aliases", [])))
    
        elif is_search_sites_file:
            self.value_field = ctk.CTkEntry(
                self.form_frame,
                placeholder_text="URL template with {query} placeholder, e.g. https://example.com/search?q={query}",
            )
            self.value_field.pack(pady=5, fill="x")
            if existing and isinstance(existing, str):
                self.value_field.insert(0, existing)
        else:
            self.value_field = ctk.CTkEntry(self.form_frame, placeholder_text="Identifier or path (e.g., 730 or /Applications/Steam.app)")
            self.value_field.pack(pady=5, fill="x")
            if existing and isinstance(existing, str):
                self.value_field.insert(0, existing)

    def _save_entry(self):
        name = self.entry_name_field.get().strip().lower()
        if not name:
            print("Name is required")
            return

        is_new = self.entry_selector.get() == "New Entry"
        already_exists = name in self._current_config_data

        if is_new and already_exists:
            print(f"An entry called '{name}' already exists. Select it from the dropdown to edit it instead.")
            return

        is_apps_file = self._current_config_path.endswith("apps.json")
        is_search_sites_file = self._current_config_path.endswith("search_sites.json")

        if is_apps_file:
            target = self.target_field.get().strip()
            if not target:
                print("Target cannot be empty")
                return

            entry_type = self.type_field.get()
            if entry_type == "url" and not (target.startswith("http://") or target.startswith("https://")):
                print(f"Warning: '{target}' doesn't look like a valid URL (should start with http:// or https://)")
                return

            aliases = [a.strip() for a in self.aliases_field.get().split(",") if a.strip()]
            self._current_config_data[name] = {
                "type": entry_type,
                "target": target,
                "aliases": aliases or [name],
            }
        else:
                value = self.value_field.get().strip()
                if not value:
                    print("Value cannot be empty")
                    return

                if is_search_sites_file and "{query}" not in value:
                    print("Warning: URL template must contain {query} as a placeholder")
                    return

                if self._current_config_path.endswith("steam_games.json") and not value.isdigit():
                    print(f"Warning: '{value}' doesn't look like a valid Steam App ID (should be a number)")
                    return

                if self._current_config_path.endswith("github_repos.json") and "/" not in value:
                    print(f"Warning: '{value}' doesn't look like a valid repo (should be 'owner/repo')")
                    return

                self._current_config_data[name] = value

        with open(self._current_config_path, "w") as f:
            json.dump(self._current_config_data, f, indent=2)

        print(f"Saved '{name}' to {self._current_config_path}")
        self._on_config_selected(self.config_selector.get())



        
    def _delete_entry(self):
        name = self.entry_selector.get()
        if name == "New Entry" or name not in self._current_config_data:
            return
        del self._current_config_data[name]
        with open(self._current_config_path, "w") as f:
            json.dump(self._current_config_data, f, indent=2)
        print(f"Deleted '{name}'")
        self._on_config_selected(self.config_selector.get())

#ERROR LOG TAB

    def _build_error_log_tab(self,tab):

        self.error_log_display = ctk.CTkTextbox(tab, width=440, height=300, fg_color="#1F2937")
        self.error_log_display.pack(pady=10, padx=10, fill="both", expand=True)

        refresh_button = ctk.CTkButton(tab, text="Refresh", command=self._load_error_log)
        refresh_button.pack(pady=5)
        clear_error_button = ctk.CTkButton(tab, text="Clear Log", fg_color="darkred", command=self._clear_error_log)
        clear_error_button.pack(pady=5)

        self._load_error_log()


    def _load_error_log(self):
        try:
            with open("logs/gui_error.log") as f:
                content = f.read()
        except FileNotFoundError:
            content = "(no error log yet)"

        self.error_log_display.delete("1.0", "end")
        self.error_log_display.insert("1.0", content or "{ log is empty :) }")
    def _clear_error_log(self):
        open("logs/gui_error.log", "w").close()
        self._load_error_log()
        print("Error log cleared")



#CONVERSATION LOG TAB
    def _build_conversation_tab(self,tab):

        self.conversation_scroll = ctk.CTkScrollableFrame(tab, width=440, height=260)
        self.conversation_scroll.pack(pady=5, padx=10, fill="both", expand=True)

        input_row = ctk.CTkFrame(tab, fg_color="transparent")
        input_row.pack(pady=5, padx=10, fill="x")

        self.text_input = ctk.CTkEntry(input_row, placeholder_text="Type a message to Rose...")
        self.text_input.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.text_input.bind("<Return>", lambda event: self._send_text_message())

        send_button = ctk.CTkButton(input_row, text="Send", width=70, command=self._send_text_message)
        send_button.pack(side="left")

        button_row = ctk.CTkFrame(tab, fg_color="transparent")
        button_row.pack(pady=5)
        ctk.CTkButton(button_row, text="Refresh", command=self._load_conversation_log).grid(row=0, column=0, padx=5)
        ctk.CTkButton(button_row, text="▲ Up", width=60, command=lambda: self._scroll_conversation(-1)).grid(row=0, column=1, padx=5)
        ctk.CTkButton(button_row, text="▼ Down", width=60, command=lambda: self._scroll_conversation(1)).grid(row=0, column=2, padx=5)
        clear_button = ctk.CTkButton(button_row, text="Clear History", fg_color="darkred", command=self._clear_conversation_log)
        clear_button.grid(row=0, column=3, padx=5)
        #test_error_button = ctk.CTkButton(button_row, text="Trigger Test Error", fg_color="gray", command=self._trigger_test_error)
        #test_error_button.grid(row=0, column=4, padx=5)
        self._load_conversation_log()



    def _trigger_test_error(self):
        raise ValueError("This is a deliberate test error to confirm gui_error.log works")


    def _scroll_conversation(self, direction: int):
        self.conversation_scroll._parent_canvas.yview_scroll(direction * 25, "units")


    def _send_text_message(self):
        text = self.text_input.get().strip()
        if not text:
            return

        self.text_input.delete(0, "end")
        self.text_input.configure(state="disabled")

        # show the user's message immediately
        self._add_message_bubble("user", text)

        buffering_responses = [
            "Thinking...",
            "Planning...",
            "Working on it...",
            "One moment...",
            "Just a second...",
            "Let me think...",
            "Looking into that...",
            "Checking...",
            "Analyzing...",
            "Processing...",
            "Gathering information...",
            "Searching my memory...",
            "Connecting the dots...",
            "Figuring that out...",
            "Almost there...",
            "Let's see...",
            "I'm on it...",
            "Calculating...",
            "Reviewing your request...",
            "Preparing a response..."
        ]
        response = random.choice(buffering_responses)
        self._typing_bubble_row = self._add_message_bubble("assistant", response)

        self.after(50, lambda: self.conversation_scroll._parent_canvas.yview_moveto(1.0))

        threading.Thread(target=self._process_text_message, args=(text,), daemon=True).start()


    def _process_text_message(self, text):
        from core.dispatcher import dispatch
        from core.conversation_log import log_exchange

        response = dispatch(text)
        log_exchange(text, response)

        self.after(0, self._on_text_message_done, response)


    def _on_text_message_done(self, response):
        # remove the placeholder "typing" bubble
        self._typing_bubble_row.destroy()

        self._add_message_bubble("assistant", response)
        self.text_input.configure(state="normal")
        self.after(50, lambda: self.conversation_scroll._parent_canvas.yview_moveto(1.0))


    def _load_conversation_log(self):
        for widget in self.conversation_scroll.winfo_children():
            widget.destroy()

        try:
            with open("logs/conversation.jsonl") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            self._add_message_bubble(entry.get("role"), entry.get("text", ""))

        self.after(50, lambda: self.conversation_scroll._parent_canvas.yview_moveto(1.0))
        

    def _add_message_bubble(self, role: str, text: str):
        is_user = role == "user"

        row = ctk.CTkFrame(self.conversation_scroll, fg_color="transparent")
        row.pack(fill="x", pady=4, padx=5)

        bubble = ctk.CTkLabel(
            row,
            text=text,
            wraplength=280,
            justify="left",
            fg_color=("#0B93F6" if is_user else "#3A3A3C"),
            text_color="white",
            corner_radius=12,
            padx=12, pady=8,
        )

        if is_user:
            bubble.pack(side="right", anchor="e")
        else:
            bubble.pack(side="left", anchor="w")

        for widget in (row, bubble):
            widget.bind("<MouseWheel>", self._on_conversation_scroll)

        return row 

    def _on_conversation_scroll(self, event):
        self.conversation_scroll._parent_canvas.yview_scroll(int(-1 * event.delta), "units")

    def _clear_conversation_log(self):
        open("logs/conversation.jsonl", "w").close()  # truncate the file
        for widget in self.conversation_scroll.winfo_children():
            widget.destroy()
        print("Conversation history cleared")
        


    def _build_api_keys_tab(self,tab):

        ctk.CTkLabel(tab, text="Anthropic API Key", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))

        self.anthropic_key_entry = ctk.CTkEntry(tab, placeholder_text="sk-ant-...", width=350)
        self.anthropic_key_entry.pack(pady=5)

        current_key = self._read_env_value("ANTHROPIC_API_KEY")
        if current_key:
            self.anthropic_key_entry.insert(0, current_key)

        save_anthropic_button = ctk.CTkButton(tab, text="Save Anthropic Key", command=self._save_anthropic_key)
        save_anthropic_button.pack(pady=5)

        ctk.CTkLabel(tab, text="Google Calendar (optional)", font=ctk.CTkFont(weight="bold")).pack(pady=(25, 5))

        google_status = "Connected" if self._google_credentials_exist() else "Not connected"
        self.google_status_label = ctk.CTkLabel(tab, text=f"Status: {google_status}")
        self.google_status_label.pack(pady=5)

        upload_button = ctk.CTkButton(tab, text="Upload Google Credentials File", command=self._upload_google_credentials)
        upload_button.pack(pady=5)

        connect_button = ctk.CTkButton(tab, text="Connect Google Calendar", command=self._connect_google_calendar)
        connect_button.pack(pady=5)

        test_button = ctk.CTkButton(tab, text="Test Connection", command=self._test_google_calendar)
        test_button.pack(pady=5)

        disconnect_button = ctk.CTkButton(tab, text="Disconnect", fg_color="darkred", command=self._disconnect_google_calendar)
        disconnect_button.pack(pady=5)

    def _read_env_value(self, key: str) -> str:
        try:
            with open(ENV_PATH) as f:
                for line in f:
                    if line.startswith(f"{key}="):
                        return line.strip().split("=", 1)[1]
        except FileNotFoundError:
            pass
        return ""


    def _write_env_value(self, key: str, value: str) -> None:
        lines = []
        found = False
        try:
            with open(ENV_PATH) as f:
                lines = f.readlines()
        except FileNotFoundError:
            pass

        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                found = True
                break

        if not found:
            lines.append(f"{key}={value}\n")

        with open(ENV_PATH, "w") as f:
            f.writelines(lines)


    def _save_anthropic_key(self):
        key = self.anthropic_key_entry.get().strip()
        if not key:
            print("API key cannot be empty")
            return
        self._write_env_value("ANTHROPIC_API_KEY", key)
        print("Saved Anthropic API key")





    def _google_credentials_exist(self) -> bool:
        import os
        return os.path.exists("config/google_credentials.json")


    def _upload_google_credentials(self):
        filepath = filedialog.askopenfilename(
            title="Select your Google credentials JSON file",
            filetypes=[("JSON files", "*.json")],
        )
        if not filepath:
            return

        import shutil
        shutil.copy(filepath, "config/google_credentials.json")
        print("Google credentials file uploaded")
        self.google_status_label.configure(text="Status: Credentials uploaded (not yet connected)")


    def _connect_google_calendar(self):
        if not self._google_credentials_exist():
            print("Please upload your Google credentials file first")
            return

        def run_oauth():
            try:
                from commands.google_calendar import _get_credentials
                _get_credentials()
                self.after(0, lambda: self.google_status_label.configure(text="Status: Connected"))
                
                print("Google Calendar connected successfully")
                return
            except Exception as e:
                print(f"Google Calendar connection failed: {e}",)

        threading.Thread(target=run_oauth, daemon=True).start()
        


    def _disconnect_google_calendar(self):
        import os
        try:
            os.remove("config/google_token.json")
            print("Disconnected from Google Calendar")
        except FileNotFoundError:
            print("Already disconnected")

        self.google_status_label.configure(text="Status: Not connected")

    def _test_google_calendar(self):
        self.google_status_label.configure(text="Status: Testing...")

        def run_test():
            try:
                from commands.google_calendar import list_todays_google_events
                from ai.event_parser import extract_date

                date_str = extract_date("today")
                result = list_todays_google_events(date_str)
                self.after(0, lambda: self.google_status_label.configure(text=f"Status: Connected ✓", text_color="green"))
                #print(f"Test result: {result}")
            except Exception as e:
                self.after(0, lambda: self.google_status_label.configure(text="Status: Connection failed", text_color="green"))
                print(f"Google Calendar test failed: {e}")

        threading.Thread(target=run_test, daemon=True).start()


    def _build_home_tab(self,tab):

        self.status_canvas = ctk.CTkCanvas(tab, bg="#0d1520", highlightthickness=0)
        self.status_canvas.pack(fill="both", expand=True, padx=0, pady=0)


        self._rotation_angle = 0
        self._pulse_phase = 0.0
        self._ring_items_created = False

        self.status_canvas.bind("<Configure>", self._on_canvas_resize)
        self._poll_status()


    def _check_main_process_running(self) -> bool:
        import subprocess
        result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
        return "com.vincenttrinh.rose" in result.stdout

    def _create_ring_items(self):
        self._main_ring_item = self.status_canvas.create_oval(0, 0, 0, 0, outline="#2a3a4a", width=1)
        self._arc_items = [
            self.status_canvas.create_arc(0, 0, 0, 0, start=0, extent=50, outline="#3a6a9a", width=3, style="arc")
            for _ in range(6)
        ]
        self._text_item = self.status_canvas.create_text(0, 0, text="ROSE", fill="#3a6a9a", font=("Helvetica", 16, "bold"))
        self._status_text_item = self.status_canvas.create_text(0, 0, text="", fill="#6a8aaa", font=("Helvetica", 11))
        self._running_status_item = self.status_canvas.create_text(0, 0, text="", fill="#22C55E", font=("Helvetica", 10))
        self._ring_items_created = True

        # make the ROSE label clickable, with a hand cursor to hint it's interactive
        self.status_canvas.tag_bind(self._text_item, "<Button-1>", self._toggle_rose)
        self.status_canvas.tag_bind(self._text_item, "<Enter>", lambda e: self.status_canvas.config(cursor="pointinghand"))
        self.status_canvas.tag_bind(self._text_item, "<Leave>", lambda e: self.status_canvas.config(cursor=""))
        


    def _draw_status_ring(self, state, is_running):
        if not hasattr(self, "_canvas_width"):
            return

        if not self._ring_items_created:
            self._create_ring_items()

        center_x = self._canvas_width / 2
        center_y = self._canvas_height / 2
        base_radius = min(self._canvas_width, self._canvas_height) * 0.2

        if not is_running:
            color = "#EF4444"  # red, overrides everything else when offline
        else:
            color = STATUS_COLORS.get(state, "#3a6a9a")


        # fixed-size faint background ring, always visible
        self.status_canvas.coords(
            self._main_ring_item,
            center_x - base_radius, center_y - base_radius,
            center_x + base_radius, center_y + base_radius,
        )

        if is_running:
            self._rotation_angle += 3
        # three arcs at different radii and speeds, each offset from the others

        arc_configs = [
            (base_radius + 8, 0.5, 0),
            (base_radius + 8,  0.5, 60),
            (base_radius + 8,  0.5, 120),
            (base_radius + 8,  0.5, 180),
            (base_radius + 8,  0.5, 240),
            (base_radius + 8,  0.5, 300),
        ]

        for i, (arc_r, speed_mult, offset) in enumerate(arc_configs):
            angle = (self._rotation_angle * speed_mult + offset) % 360
            self.status_canvas.coords(
                self._arc_items[i],
                center_x - arc_r, center_y - arc_r, center_x + arc_r, center_y + arc_r,
            )
            self.status_canvas.itemconfig(
                self._arc_items[i],
                start=angle, outline=color,
                state="normal",
            )

        self.status_canvas.coords(self._text_item, center_x, center_y)
        self.status_canvas.itemconfig(self._text_item, fill=color)

        self.status_canvas.coords(self._status_text_item, center_x, center_y + 30)  # positioned just below the ROSE label
        self.status_canvas.coords(self._running_status_item, center_x, self._canvas_height - 30)

        

    def _on_canvas_resize(self, event):
        self._canvas_width = event.width
        self._canvas_height = event.height
        self._draw_grid_background()


    def _draw_grid_background(self):
        self.status_canvas.delete("grid")
        w, h = self._canvas_width, self._canvas_height
        for x in range(0, w, 20):
            self.status_canvas.create_line(x, 0, x, h, fill="#16202e", width=1, tags="grid")
        for y in range(0, h, 20):
            self.status_canvas.create_line(0, y, w, y, fill="#16202e", width=1, tags="grid")
        self.status_canvas.tag_lower("grid")  # ensure grid stays behind the ring



    def _start_rose(self):
        result = subprocess.run(["launchctl", "load", PLIST_PATH], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to start Rose: {result.stderr.strip()}")
        else:
            print("Started Rose")
            
    def _stop_rose(self):
        subprocess.run(["launchctl", "unload", PLIST_PATH])
        print("Stopped Rose")


    def _toggle_rose(self, event=None):
        is_running = self._check_main_process_running()

        if is_running:
            from core.audio_io import stop_speaking
            stop_speaking()

            self._stop_rose()
            self._cached_is_running = False
        else:
            self._start_rose()
            self._cached_is_running = True
            threading.Thread(target=self._speak_greeting, daemon=True).start()
            

    def _speak_greeting(self):
        from core.audio_io import speak
        speak("Welcome back, how can I assist you today?")

    def _poll_status(self):
        from core.status import get_status
        state = get_status()
        self._last_known_state = state

        self._launchctl_check_counter += 1
        if self._launchctl_check_counter % 50 == 0:
            self._cached_is_running = self._check_main_process_running()

        is_running = getattr(self, "_cached_is_running", True)  # default to True until first real check completes

        self._draw_status_ring(state, is_running)

        running_text = "● Rose is running" if is_running else "○ Rose is not running"
        running_color = "#22C55E" if is_running else "#EF4444"
        if hasattr(self, "_running_status_item"):
            self.status_canvas.itemconfig(self._running_status_item, text=running_text, fill=running_color)

        self.after(20, self._poll_status)

        
        

    def _blend_color(self, color_hex, bg_hex, factor):
        """factor: 0.0 = full background, 1.0 = full color"""
        c = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
        bg = tuple(int(bg_hex[i:i+2], 16) for i in (1, 3, 5))
        blended = tuple(int(bg[j] + (c[j] - bg[j]) * factor) for j in range(3))
        return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"


if __name__ == "__main__":
    try:
        app = RoseSettingsApp()
        app.mainloop()
    except Exception:
        with open(GUI_ERROR_LOG, "a") as f:
            f.write(traceback.format_exc() + "\n")
        raise