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
from core.audio_io import speak, stop_speaking


from core.paths import path_for


# gui.py
def _get_version():
    try:
        with open(path_for("VERSION")) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "dev"

ROSE_VERSION = _get_version()


GUI_ERROR_LOG = path_for("logs", "gui_error.log")
SETTINGS_PATH = path_for("config", "settings.json")
ENV_PATH = path_for(".env")  

STATUS_COLORS = {
    "idle": "#4FC3F7",
    "listening": "#4ADE80",
    "speaking": "#FBBF24",
}

CATEGORY_ICONS = {
    "identity": "◆", "goals": "◈", "interests": "♦", "technical": "◇",
    "preferences": "◉", "knowledge": "◐", "projects": "◧", "lifestyle": "◑",
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
        from core.paths import ensure_default_configs
        ensure_default_configs()

        self.report_callback_exception = self._log_callback_exception
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.title("Rose Settings")
        self.geometry("900x650")

        self.settings = load_settings()

        if self._is_first_run():
            self._build_onboarding_screen()
        else:
            self._build_main_interface()
            self._stop_rose()
            self._cached_is_running = False

    def _is_first_run(self) -> bool:
        key = self._read_env_value("ANTHROPIC_API_KEY")
        return not key


    def _build_main_interface(self):
        # top navigation bar
        nav_bar = ctk.CTkFrame(self, height=50, fg_color="#0d1520", corner_radius=0)
        nav_bar.pack(fill="x", side="top")

        ctk.CTkLabel(nav_bar, text="Rose.AI", font=ctk.CTkFont(size=16, weight="bold"), text_color="#F8FAFC").pack(side="left", padx=15)

        self.nav_dropdown = ctk.CTkOptionMenu(
            nav_bar,
            values=[
                "Rose",
                "Conversation",
                "Voice",
                "Hotkey",
                "Screenshots",
                "Config Files",
                "Memory",           
                "Capabilities",
                "API Keys",
                "Diagnostics",
                "Gui Error Logs",
            ],
            command=self._switch_screen,
            fg_color="#111827",
            button_color="#2563EB",
            button_hover_color="#3B82F6",
        )
        self.nav_dropdown.pack(side="right", padx=15, pady=8)

        # main content container
        self.content_container = ctk.CTkFrame(self, fg_color="#151E2E", corner_radius=0)
        self.content_container.pack(fill="both", expand=True)

        self.screens = {}
        self.screens["Rose"] = ctk.CTkFrame(self.content_container, fg_color="#0d1520", corner_radius=0)
        self.screens["Voice"] = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.screens["Hotkey"] = ctk.CTkFrame(self.content_container, fg_color="#151E2E")
        self.screens["Config Files"] = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.screens["Conversation"] = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.screens["Gui Error Logs"] = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.screens["API Keys"] = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.screens["Memory"] = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.screens["Diagnostics"] = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.screens["Screenshots"] = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.screens["Capabilities"] = ctk.CTkFrame(self.content_container, fg_color="transparent")

        self._build_home_tab(self.screens["Rose"])
        self._build_voice_tab(self.screens["Voice"])
        self._build_hotkey_tab(self.screens["Hotkey"])
        self._build_config_tab(self.screens["Config Files"])
        self._build_conversation_tab(self.screens["Conversation"])
        self._build_error_log_tab(self.screens["Gui Error Logs"])
        self._build_api_keys_tab(self.screens["API Keys"])
        self._build_memory_tab(self.screens["Memory"])
        self._build_diagnostics_tab(self.screens["Diagnostics"])
        self._build_screenshots_tab(self.screens["Screenshots"])
        self._build_capabilities_tab(self.screens["Capabilities"])

        self._switch_screen("Rose")

    def _build_onboarding_screen(self):
        self.onboarding_frame = ctk.CTkFrame(self, fg_color="#0d1520", corner_radius=0)
        self.onboarding_frame.pack(fill="both", expand=True)

        self.onboarding_step = 0
        self.onboarding_steps = [
            self._onboarding_welcome,
            self._onboarding_api_key,
            self._onboarding_permissions,
            self._onboarding_done,
        ]
        self._show_onboarding_step()


    def _show_onboarding_step(self):
        for widget in self.onboarding_frame.winfo_children():
            widget.destroy()
        self.onboarding_steps[self.onboarding_step]()


    def _onboarding_welcome(self):
        ctk.CTkLabel(self.onboarding_frame, text="Welcome to Rose", font=ctk.CTkFont(size=28, weight="bold"), text_color="#F8FAFC").pack(pady=(100, 10))
        ctk.CTkLabel(self.onboarding_frame, text="Let's get you set up in a few quick steps.", text_color="#8E9BAE", font=ctk.CTkFont(size=14)).pack(pady=(0, 40))
        ctk.CTkButton(self.onboarding_frame, text="Get Started", width=200, command=self._onboarding_next).pack()


    def _onboarding_api_key(self):
        ctk.CTkLabel(self.onboarding_frame, text="Connect your Anthropic API key", font=ctk.CTkFont(size=22, weight="bold"), text_color="#F8FAFC").pack(pady=(80, 10))
        ctk.CTkLabel(self.onboarding_frame, text="Rose uses Claude to understand and respond to you.\nGet a key at console.anthropic.com", text_color="#8E9BAE", justify="center").pack(pady=(0, 20))

        self.onboarding_key_entry = ctk.CTkEntry(self.onboarding_frame, placeholder_text="sk-ant-...", width=350)
        self.onboarding_key_entry.pack(pady=10)

        ctk.CTkButton(self.onboarding_frame, text="Continue", width=200, command=self._onboarding_save_key).pack(pady=20)


    def _onboarding_save_key(self):
        key = self.onboarding_key_entry.get().strip()
        if not key:
            return
        self._write_env_value("ANTHROPIC_API_KEY", key)
        self._onboarding_next()


    def _onboarding_permissions(self):
        ctk.CTkLabel(self.onboarding_frame, text="Grant permissions", font=ctk.CTkFont(size=22, weight="bold"), text_color="#F8FAFC").pack(pady=(80, 10))
        ctk.CTkLabel(
            self.onboarding_frame,
            text="Rose needs a few permissions to work:\n\n"
                "• Microphone — to hear your voice commands\n"
                "• Input Monitoring — to detect your hotkey\n"
                "• Accessibility — to control apps like Calendar and Messages\n\n"
                "Click below to open System Settings, then come back here.",
            text_color="#8E9BAE", justify="center",
        ).pack(pady=(0, 20))

        ctk.CTkButton(self.onboarding_frame, text="Open System Settings", width=220, command=self._open_privacy_settings).pack(pady=10)
        ctk.CTkButton(self.onboarding_frame, text="I've granted permissions", width=220, command=self._onboarding_next).pack(pady=10)


    def _open_privacy_settings(self):
        subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent"])


    def _onboarding_done(self):
        ctk.CTkLabel(self.onboarding_frame, text="You're all set!", font=ctk.CTkFont(size=28, weight="bold"), text_color="#22C55E").pack(pady=(100, 10))
        ctk.CTkButton(self.onboarding_frame, text="Start Using Rose", width=200, command=self._finish_onboarding).pack(pady=20)


    def _onboarding_next(self):
        self.onboarding_step += 1
        self._show_onboarding_step()


    def _finish_onboarding(self):
        self.onboarding_frame.destroy()
        self._build_main_interface()


    def _generate_plist(self) -> str:
        """Builds the launchd .plist content, pointing at THIS app's embedded RoseMain."""
        import sys

        if getattr(sys, 'frozen', False):
            # running as the bundled .app - find our own bundle's path
            app_bundle_path = os.path.abspath(os.path.join(os.path.dirname(sys.executable), ".."))
            rosemain_path = os.path.join(app_bundle_path, "Resources", "RoseMain", "RoseMain")
        else:
            # running unbundled during development - point at the dist_gui test build
            rosemain_path = os.path.abspath("dist_gui/Rose.app/Contents/Resources/RoseMain/RoseMain")

        log_path = os.path.expanduser("~/Library/Application Support/Rose/logs/rose.log")
        error_log_path = os.path.expanduser("~/Library/Application Support/Rose/logs/rose_error.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        return f'''<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.vincenttrinh.rose</string>
        <key>ProgramArguments</key>
        <array>
            <string>{rosemain_path}</string>
        </array>
        <key>RunAtLoad</key>
        <true/>
        <key>KeepAlive</key>
        <true/>
        <key>StandardOutPath</key>
        <string>{log_path}</string>
        <key>StandardErrorPath</key>
        <string>{error_log_path}</string>
    </dict>
    </plist>
    '''


    def _install_plist(self):
        plist_content = self._generate_plist()
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.vincenttrinh.rose.plist")

        with open(plist_path, "w") as f:
            f.write(plist_content)

        print(f"Installed plist at {plist_path}")
        return plist_path


    def _start_rose(self):
        plist_path = self._install_plist()
        result = subprocess.run(["launchctl", "load", plist_path], capture_output=True, text=True)
        from core.status import set_status
        set_status("idle")
        if result.returncode != 0:
            print(f"Failed to start Rose: {result.stderr.strip()}")
        else:


            print("Started Rose")

    def _on_close(self):
        from core.audio_io import stop_speaking, cancel_recording
        from core.status import set_status

        stop_speaking()
        cancel_recording()
        self._reset_all_voice_state()
        set_status("idle")

        if self._check_main_process_running():
            self._stop_rose()

        self.destroy()

        import os
        os._exit(0)
        
        
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
        from core.long_term_memory import load_memory

        ctk.CTkLabel(tab, text="Your Name", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))

        self.name_entry = ctk.CTkEntry(tab, placeholder_text="e.g. Vincent")
        self.name_entry.pack(pady=5)

        memory = load_memory()
        current_name = memory.get("identity", {}).get("name")
        if current_name:
            self.name_entry.insert(0, current_name)


        save_name_button = ctk.CTkButton(tab, text="Save Name", command=self._save_name)
        save_name_button.pack(pady=(5, 15))
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
        ctk.CTkLabel(
            tab,
            text="⚠ Restart Rose for voice changes to take effect",
            text_color="#F59E0B",
            font=ctk.CTkFont(size=11),
        ).pack(pady=(0, 10))


    def _save_name(self):
        from core.long_term_memory import remember_fact

        name = self.name_entry.get().strip()
        if not name:
            return
        remember_fact("identity", "name", name)
        print(f"Saved name: {name}")
        
                
    def _save_voice(self):
        selected_name = self.voice_dropdown.get()
        selected_id = self.voice_map[selected_name]
        self.settings["voice_id"] = selected_id
        self.settings["say_voice_name"] = selected_name
        save_settings(self.settings)

        import subprocess
        subprocess.Popen(["say", "-v", selected_name, f"Hello, I am the voice of {selected_name}..., thanks for selecting me"])
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
            text="Note: some key combinations are reserved by macOS or other apps.\nUse Test to confirm before saving.\n⚠ Restart Rose for hotkey changes to take effect",
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
            "Apps": path_for("config", "apps.json"),
            "Steam Games": path_for("config", "steam_games.json"),
            "VS Code Projects": path_for("config", "projects.json"),
            "GitHub Repos": path_for("config", "github_repos.json"),
            "Search Sites": path_for("config", "search_sites.json"),
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

    def _on_entry_selected(self, selected_entry):
        for widget in self.form_frame.winfo_children():
            widget.destroy()

        is_apps_file = self._current_config_path.endswith("apps.json")
        is_search_sites_file = self._current_config_path.endswith("search_sites.json")
        is_known_entry = selected_entry in self._current_config_data
        existing = self._current_config_data.get(selected_entry, {}) if is_known_entry else {}

        self.entry_name_field = ctk.CTkEntry(self.form_frame, placeholder_text="Name (e.g. 'spotify')")
        self.entry_name_field.pack(pady=5, fill="x")
        if is_known_entry:
            self.entry_name_field.insert(0, selected_entry)

        if is_apps_file:
            self.type_field = ctk.CTkOptionMenu(self.form_frame, values=["url", "native_app"])
            self.type_field.pack(pady=5, fill="x")
            if existing.get("type"):
                self.type_field.set(existing["type"])

            self.target_field = ctk.CTkEntry(self.form_frame, placeholder_text="Target (URL or exact app name)")
            self.target_field.pack(pady=5, fill="x")
            if existing.get("target"):
                self.target_field.insert(0, existing.get("target"))

            self.aliases_field = ctk.CTkEntry(self.form_frame, placeholder_text="Other ways to say this (comma-separated)")
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
                

    def _on_config_selected(self, selected_label):
        path = self.config_files[selected_label]
        with open(path) as f:
            self._current_config_data = json.load(f)
        self._current_config_path = path

        entry_names = ["New Entry"] + list(self._current_config_data.keys())
        self.entry_selector.configure(values=entry_names)
        self.entry_selector.set("New Entry")
        self._on_entry_selected("New Entry")


    def _on_enry_selected(self, selected_entry):
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
            from core.paths import path_for
            with open(path_for("logs", "conversation.jsonl")) as f:
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
            wraplength=400,
            justify="left",
            fg_color=("#0B93F6" if is_user else "#3A3A3C"),
            text_color="white",
            corner_radius=10,
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
        open(path_for("logs", "conversation.jsonl"), "w").close()
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
        ctk.CTkLabel(
            tab,
            text="⚠ Restart Rose after saving a new API key",
            text_color="#F59E0B",
            font=ctk.CTkFont(size=11),
        ).pack(pady=(0, 10))

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
        return os.path.exists(path_for("config", "google_credentials.json"))


    def _upload_google_credentials(self):
        filepath = filedialog.askopenfilename(
            title="Select your Google credentials JSON file",
            filetypes=[("JSON files", "*.json")],
        )
        if not filepath:
            return

        import shutil
        shutil.copy(filepath, path_for("config", "google_credentials.json"))
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
            os.remove(path_for("config", "google_token.json"))
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

                if "couldn't check your calendar" in result.lower() or "sorry" in result.lower():
                    raise Exception(result)

                self.after(0, lambda: self.google_status_label.configure(text="Status: Connected ✓", text_color="green"))
            except Exception as e:
                self.after(0, lambda: self.google_status_label.configure(text="Status: Connection failed", text_color="red"))
                print(f"Google Calendar test failed: {e}")

        threading.Thread(target=run_test, daemon=True).start()


    def _build_home_tab(self, tab):
        # split Home into two side-by-side sections
        left_panel = ctk.CTkFrame(tab, fg_color="#0d1520", corner_radius=0)
        left_panel.pack(side="left", fill="both", expand=True)

        right_panel = ctk.CTkFrame(tab, fg_color="#151E2E", corner_radius=0, width=400)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)  # keep the fixed width, don't let contents resize it

        # --- LEFT: the canvas, ring, buttons - all your existing code, just parented to left_panel ---
        self.status_canvas = ctk.CTkCanvas(left_panel, bg="#0d1520", highlightthickness=0)
        self.status_canvas.pack(fill="both", expand=True, padx=0, pady=0)

        self.speak_button = ctk.CTkButton(
            left_panel, text="◉  SPEAK", width=160, height=44, corner_radius=22,
            fg_color="transparent", border_width=2, border_color="#3B82F6",
            hover_color="#1a2938", text_color="#3B82F6",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_speak_button_click,
        )

        self.stop_talking_button = ctk.CTkButton(
            left_panel, text="✕  STOP TALKING", width=160, height=36, corner_radius=18,
            fg_color="transparent", border_width=2, border_color="#EF4444",
            hover_color="#3a1a1a", text_color="#EF4444",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_stop_talking_click,
        )

        # --- RIGHT: transcript panel ---
        ctk.CTkLabel(right_panel, text="Conversation Logs", font=ctk.CTkFont(size=25, weight="bold"), text_color="#F8FAFC").pack(pady=(15, 5), padx=15, anchor="w")

        self.home_transcript_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="#151E2E")
        self.home_transcript_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._rotation_angle = 0
        self._pulse_phase = 0.0
        self._ring_items_created = False
        self._launchctl_check_counter = 0
        self._gui_is_speaking = False
        self._floating_lines = [] 

        self.status_canvas.bind("<Configure>", self._on_canvas_resize)
        self._poll_status()
        self._load_home_transcript()
        

    def _load_home_transcript(self):
        for widget in self.home_transcript_scroll.winfo_children():
            widget.destroy()

        try:
            with open(path_for("logs", "conversation.jsonl")) as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        for line in lines[-15:]:  # only show the most recent 30 messages, since this panel is narrower
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            self._add_home_transcript_bubble(entry.get("role"), entry.get("text", ""))

        self.after(50, lambda: self.home_transcript_scroll._parent_canvas.yview_moveto(1.0))


    def _add_home_transcript_bubble(self, role: str, text: str):
        is_user = role == "user"

        row = ctk.CTkFrame(self.home_transcript_scroll, fg_color="transparent")
        row.pack(fill="x", pady=3, padx=3)

        bubble = ctk.CTkLabel(
            row, text=text, wraplength=190, justify="left",
            fg_color=("#0B93F6" if is_user else "#3A3A3C"),
            text_color="white", corner_radius=10, padx=10, pady=6,
            font=ctk.CTkFont(size=15),
        )

        if is_user:
            bubble.pack(side="right", anchor="e")
        else:
            bubble.pack(side="left", anchor="w")





    def _on_speak_button_click(self):
        if getattr(self, "_speak_button_locked", False):
            print("Rose is still starting up - please wait a moment")
            return

        if not self._check_main_process_running():
            print("Rose isn't running - start it first")
            return

        from core.status import get_status, set_status
        from core.audio_io import stop_speaking, cancel_recording,kill_any_speech

        was_interrupting = get_status() == "speaking" or self._gui_is_speaking or getattr(self, "_voice_thread_active", False)

        if was_interrupting:
            print(">>> calling stop_speaking")
            stop_speaking()
            print(">>> calling cancel_recording")
            cancel_recording()
            print(">>> cancel_recording done")
            self._gui_is_speaking = False
            self._gui_is_listening = False
            print(">>> calling pkill")
            import subprocess
            kill_any_speech()
            print(">>> pkill done")
            from core.status import request_cancel
            request_cancel()
            print(">>> request_cancel done")


        self._current_request_id = getattr(self, "_current_request_id", 0) + 1
        my_id = self._current_request_id

        self._gui_is_listening = True
        set_status("listening")
        self.speak_button.configure(
            text="◉ LISTENING", state="disabled",
            border_color="#22C55E", text_color="#22C55E",
        )

        threading.Thread(target=self._process_voice_message, args=(my_id, was_interrupting), daemon=True).start()
        

    def _on_stop_talking_click(self):
        from core.status import set_status
        from core.audio_io import stop_speaking, cancel_recording,kill_any_speech

        stop_speaking()
        cancel_recording()

        import subprocess
        kill_any_speech()
        self._gui_is_speaking = False
        self._gui_is_listening = False
        set_status("idle")

        self._current_request_id = getattr(self, "_current_request_id", 0) + 1

        self._reset_speak_button()


    def _set_speak_button_speaking_state(self, my_id):
        if my_id != self._current_request_id:
            return
        self.speak_button.configure(
            text="◉  SPEAKING (click to interrupt)", state="normal",
            border_color="#FBBF24", text_color="#FBBF24",
        )


    def _reset_speak_button(self):
        self.speak_button.configure(text="◉  SPEAK", state="normal", border_color="#3B82F6", text_color="#3B82F6")


    def _process_voice_message(self, my_id, was_interrupting=False):
        self._voice_thread_active = True
        try:
            import time
            if was_interrupting:
                time.sleep(0.15)

            from core.audio_io import record_and_transcribe, speak
            from core.dispatcher import dispatch
            from core.conversation_log import log_exchange
            from core.status import set_status, check_and_clear_cancel

            print(f">>> [{my_id}] starting, was_interrupting={was_interrupting}")

            self._gui_is_listening = True
            set_status("listening")
            result = record_and_transcribe()
            self._gui_is_listening = False

            check_and_clear_cancel()
            print(f">>> [{my_id}] recorded: '{result}' | current_request_id={self._current_request_id}")

            if my_id != self._current_request_id:
                print(f">>> [{my_id}] abandoned after recording (superseded)")
                self.after(0, self._reset_speak_button)
                return

            if not result:
                print(f">>> [{my_id}] no result, speaking fallback")
                set_status("speaking")
                self._gui_is_speaking = True
                self.after(0, lambda: self._set_speak_button_speaking_state(my_id))
                speak("I didn't catch that")
                self._gui_is_speaking = False
                set_status("idle")
                if my_id == self._current_request_id:
                    self.after(0, self._reset_speak_button)
                return

            buffering_responses = [
                "Let me think about that...", "Give me a moment...", "Let me take a look...",
                "I'm thinking...", "Let me work through that...", "Let me figure that out...",
                "One moment while I check...", "I'm looking into it...", "Let me see...",
                "Let me gather my thoughts...", "I'm putting that together...", "Let me think this through...",
                "Just a moment...", "I'm working on it...", "Let me check a few things...",
                "I'm going over that now...", "Let me find the best answer...", "Thinking it through...",
                "Let me look into that for you...",
            ]
            initial_response = random.choice(buffering_responses)

            self._gui_is_listening = True
            set_status("listening")
            print(f">>> [{my_id}] speaking buffering phrase")
            speak(initial_response)
            self._gui_is_listening = False

            check_and_clear_cancel()
            if my_id != self._current_request_id:
                print(f">>> [{my_id}] abandoned after buffering phrase (superseded)")
                self.after(0, self._reset_speak_button)
                return

            print(f">>> [{my_id}] dispatching")
            response = dispatch(result)
            print(f">>> [{my_id}] dispatch returned: {response[:50]}")

            check_and_clear_cancel()
            if my_id != self._current_request_id:
                print(f">>> [{my_id}] abandoned after dispatch (superseded)")
                self.after(0, self._reset_speak_button)
                return

            log_exchange(result, response)
            self.after(0, self._load_home_transcript)

            set_status("speaking")
            self._gui_is_speaking = True

            if my_id == self._current_request_id:
                self.after(0, lambda: self._set_speak_button_speaking_state(my_id))

            print(f">>> [{my_id}] speaking real response")
            speak(response)
            print(f">>> [{my_id}] real response done")

            self._gui_is_speaking = False
            set_status("idle")
            if my_id == self._current_request_id:
                self.after(0, self._reset_speak_button)

        finally:
            print(f">>> [{my_id}] thread finished")
            self._voice_thread_active = False
            

    def _check_main_process_running(self) -> bool:
        import subprocess
        result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            parts = line.split()
            if parts and parts[-1] == "com.vincenttrinh.rose":
                return True
        return False

    def _create_ring_items(self):
        self._main_ring_item = self.status_canvas.create_oval(
            0, 0, 0, 0,
            outline="#2a3a4a",
            width=1
        )

        self._arc_items = [
            self.status_canvas.create_arc(
                0, 0, 0, 0,
                start=0,
                extent=30,
                outline="#3a6a9a",
                width=3,
                style="arc",
            )
            for _ in range(20)
        ]

        self._text_item = self.status_canvas.create_text(0, 0, text="ROSE", fill="#3a6a9a", font=("Helvetica", 25, "bold"))
        self._status_text_item = self.status_canvas.create_text(0, 0, text="", fill="#6a8aaa", font=("Helvetica", 11))
        self._running_status_item = self.status_canvas.create_text(0, 0, text="", fill="#22C55E", font=("Helvetica", 10))
        self._ring_items_created = True

        # make the ROSE label clickable, with a hand cursor to hint it's interactive
        self.status_canvas.tag_bind(self._text_item, "<Button-1>", self._toggle_rose)
        self.status_canvas.tag_bind(self._text_item, "<Enter>", lambda e: self.status_canvas.config(cursor="pointinghand"))
        self.status_canvas.tag_bind(self._text_item, "<Leave>", lambda e: self.status_canvas.config(cursor=""))
        

    def _draw_gradient_background(self):
        """Draws a vertical gradient from dark navy to a slightly different dark blue."""
        top_color = (13, 21, 32)      # #0d1520
        bottom_color = (20, 30, 48)   # a bit lighter/bluer

        steps = 60
        band_height = self._canvas_height / steps

        for i in range(steps):
            factor = i / steps
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * factor)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * factor)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * factor)
            color = f"#{r:02x}{g:02x}{b:02x}"

            y1 = i * band_height
            y2 = y1 + band_height + 1  # +1 avoids visible seams between bands
            self.status_canvas.create_rectangle(0, y1, self._canvas_width, y2, fill=color, outline="", tags="gradient")

        self.status_canvas.tag_lower("gradient")  # keep it behind everything else


    def _draw_status_ring(self, state, is_running):
        if not hasattr(self, "_canvas_width"):
            return

        if not self._ring_items_created:
            self._create_ring_items()

        center_x = self._canvas_width / 2
        center_y = self._canvas_height / 3
        base_radius = min(self._canvas_width, self._canvas_height) * 0.3

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


        self._arc_configs = [ 
            # Inner ring (18°) 6
            (base_radius + 8,  1.00,   0, 18),
            (base_radius + 8,  1.00,  60, 18),
            (base_radius + 8,  1.00, 120, 18),
            (base_radius + 8,  1.00, 180, 18),
            (base_radius + 8,  1.00, 240, 18),
            (base_radius + 8,  1.00, 300, 18),

            # Middle ring (30°)4
            (base_radius + 16, 0.75,   0, 30),
            (base_radius + 16, 0.75,  90, 30),
            (base_radius + 16, 0.75, 180, 30),
            (base_radius + 16, 0.75, 270, 30),

            # Third ring (45°) 4
            (base_radius + 24, 0.45,  45, 45),
            (base_radius + 24, 0.45, 135, 45),
            (base_radius + 24, 0.45, 225, 45),
            (base_radius + 24, 0.45, 315, 45),

            # Outer ring (60°) 6
            (base_radius + 30, 0.20,   0, 60),
            (base_radius + 30, 0.20,  60, 60),
            (base_radius + 30, 0.20, 120, 60),
            (base_radius + 30, 0.20, 180, 60),
            (base_radius + 30, 0.20, 240, 60),
            (base_radius + 30, 0.20, 300, 60),
        ]


        import math

        for item, (radius, speed, offset, base_extent) in zip(
            self._arc_items,
            self._arc_configs,
        ):
            angle = (self._rotation_angle * speed + offset) % 360

            pulse = 4 * math.sin(
                math.radians(self._rotation_angle * 2 + offset)
            )

            extent = base_extent + pulse

            self.status_canvas.coords(
                item,
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
            )

            self.status_canvas.itemconfig(
                item,
                start=angle,
                extent=extent,
                outline=color,
                state="normal",
            )
            


        self.status_canvas.coords(self._text_item, center_x, center_y)
        self.status_canvas.itemconfig(self._text_item, fill=color)

        self.status_canvas.coords(self._running_status_item, center_x, self._canvas_height - 15) # positioned just below the ROSE label
        self.status_canvas.coords(self._running_status_item, center_x, self._canvas_height - 30)


    def _init_floating_lines(self):
        import random
        LINE_COLORS = ["#1e3a5f", "#16283f", "#254a75", "#122236"]

        self._floating_lines = []
        for _ in range(50):
            self._floating_lines.append({
                "item": self.status_canvas.create_line(0, 0, 0, 0, fill=random.choice(LINE_COLORS), width=2),
                "y": random.uniform(0, self._canvas_height),
                "speed": random.uniform(1, 0.6),
                "length_fraction": random.uniform(0.4, 0.9),   # store as a fraction, not a pixel count
                "x_offset_fraction": random.uniform(0, 0.3),
            })


    def _update_floating_lines(self):
        #top_color = (30, 58, 95)     # #1e3a5f
        #bottom_color = (60, 30, 90)  # a purple-ish tone for contrast, adjust to taste

        # Option 1: Deep Cyber / Modern HUD (Cleanest overall)
        top_color = (10, 17, 40)  # #0a1128
        bottom_color = (16, 42, 67)  # #102a43

        # Option 2: Smooth Indigo / Blue-Purple
        # top_color = (15, 23, 42)    # #0f172a
        # bottom_color = (30, 27, 75)   # #1e1b4b

        for line in self._floating_lines:
            line["y"] += line["speed"]
            if line["y"] > self._canvas_height + 20:
                line["y"] = -20

            x1 = line["x_offset_fraction"] * self._canvas_width
            x2 = x1 + (line["length_fraction"] * self._canvas_width)
            self.status_canvas.coords(line["item"], x1, line["y"], x2, line["y"])

            # interpolate color based on vertical position
            factor = max(0, min(1, line["y"] / self._canvas_height))
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * factor)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * factor)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * factor)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.status_canvas.itemconfig(line["item"], fill=color)


    def _on_canvas_resize(self, event):
        self._canvas_width = event.width
        self._canvas_height = event.height
        self.status_canvas.delete("gradient")
        self._draw_gradient_background()
        self._draw_grid_background()

        if not hasattr(self, "_floating_lines") or not self._floating_lines:
            self._init_floating_lines()

    def _draw_grid_background(self):
        self.status_canvas.delete("grid")
        w, h = self._canvas_width, self._canvas_height
        for x in range(0, w, 20):
            self.status_canvas.create_line(x, 0, x, h, fill="#16202e", width=1, tags="grid")
        for y in range(0, h, 20):
            self.status_canvas.create_line(0, y, w, y, fill="#16202e", width=1, tags="grid")
        self.status_canvas.tag_lower("grid")  # ensure grid stays behind the ring



    def _reset_all_voice_state(self):
        self._gui_is_speaking = False
        self._gui_is_listening = False
        self._current_request_id = getattr(self, "_current_request_id", 0) + 1

        if hasattr(self, "speak_button"):
            self.speak_button.configure(
                text="◉  SPEAK", state="normal",
                border_color="#3B82F6", text_color="#3B82F6",
            )

            
    def _stop_rose(self):
        self._reset_all_voice_state()
        subprocess.run(["launchctl", "unload", PLIST_PATH])
        # backup: forcefully kill any lingering RoseMain process directly
        subprocess.run(["pkill", "-f", "RoseMain"])
        from core.audio_io import stop_speaking, cancel_recording
        from core.status import set_status
        stop_speaking()
        cancel_recording()
        set_status("idle")
        print("Stopped Rose")



    def _toggle_rose(self, event=None):
        is_running = self._check_main_process_running()

        if is_running:
            from core.audio_io import stop_speaking, cancel_recording
            stop_speaking()
            cancel_recording()

            self._reset_all_voice_state()

            self._stop_rose()
            self._cached_is_running = False
        else:
            self._reset_all_voice_state()

            self._speak_button_locked = True  # block Speak button temporarily
            self._start_rose()
            self._cached_is_running = True
            threading.Thread(target=self._speak_greeting, daemon=True).start()

            # unlock after 8 seconds
            self.after(5500, self._unlock_speak_button)


    def _unlock_speak_button(self):
        self._speak_button_locked = False
        if hasattr(self, "speak_button"):
            self.speak_button.configure(
                text="◉  SPEAK", state="normal",
                border_color="#3B82F6", text_color="#3B82F6",
            )


            
            
            

    def _speak_greeting(self):
        from core.audio_io import speak
        from core.long_term_memory import load_memory

        memory = load_memory()
        name = memory.get("identity", {}).get("name")

        if name:
            greeting = f"Welcome back, {name}. How can I assist you today?"
        else:
            greeting = "Welcome back, how can I assist you today?"

        speak(greeting)

    def _poll_status(self):
        from core.status import get_status
        file_state = get_status()

        if getattr(self, "_gui_is_listening", False):
            state = "listening"
        elif self._gui_is_speaking:
            state = "speaking"
        else:
            state = file_state

        self._last_known_state = state

        self._launchctl_check_counter += 1
        if self._launchctl_check_counter % 50 == 0:
            self._cached_is_running = self._check_main_process_running()

        is_running = getattr(self, "_cached_is_running", True)

        self._draw_status_ring(state, is_running)
        self._update_floating_lines()

        running_text = "● Rose is running" if is_running else "○ Rose is not running"
        running_color = "#22C55E" if is_running else "#EF4444"
        if hasattr(self, "_running_status_item"):
            self.status_canvas.itemconfig(self._running_status_item, text=running_text, fill=running_color)

        if is_running or self._gui_is_speaking or getattr(self, "_gui_is_listening", False):
            if not self.speak_button.winfo_ismapped():
                self.speak_button.place(relx=0.5, rely=0.85, anchor="center")

            if getattr(self, "_speak_button_locked", False):
                self.speak_button.configure(state="disabled", text="◉  Starting up...", border_color="#6B7280", text_color="#6B7280")
            elif not getattr(self, "_voice_thread_active", False):
                if state != getattr(self, "_last_polled_button_state", None):
                    self._last_polled_button_state = state
                    if state == "listening":
                        self.speak_button.configure(text="◉ LISTENING", state="disabled", border_color="#22C55E", text_color="#22C55E")
                    elif state == "speaking":
                        self.speak_button.configure(text="◉  SPEAKING (click to interrupt)", state="normal", border_color="#FBBF24", text_color="#FBBF24")
                    else:
                        self.speak_button.configure(text="◉  SPEAK", state="normal", border_color="#3B82F6", text_color="#3B82F6")
                       
        else:
            if self.speak_button.winfo_ismapped():
                self.speak_button.place_forget()

        is_speaking_now = (state == "speaking") or self._gui_is_speaking
        if is_speaking_now:
            if not self.stop_talking_button.winfo_ismapped():
                self.stop_talking_button.place(relx=0.5, rely=0.95, anchor="center")
        else:
            if self.stop_talking_button.winfo_ismapped():
                self.stop_talking_button.place_forget()

        self._transcript_refresh_counter = getattr(self, "_transcript_refresh_counter", 0) + 1
        if self._transcript_refresh_counter % 500 == 0:
            self._load_home_transcript()
            
        self.after(20, self._poll_status)




    def _blend_color(self, color_hex, bg_hex, factor):
        """factor: 0.0 = full background, 1.0 = full color"""
        c = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
        bg = tuple(int(bg_hex[i:i+2], 16) for i in (1, 3, 5))
        blended = tuple(int(bg[j] + (c[j] - bg[j]) * factor) for j in range(3))
        return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"



    def _build_memory_tab(self, tab):
        ctk.CTkLabel(tab, text="Long term memory storage", font=ctk.CTkFont(size=20, weight="bold"), text_color="#F8FAFC").pack(pady=(20, 5))
        ctk.CTkLabel(tab, text="Facts your assistant remembers about you", text_color="#8E9BAE", font=ctk.CTkFont(size=12)).pack(pady=(0, 15))
        self.memory_categories = ["identity", "goals", "interests", "technical", "preferences", "knowledge", "projects", "lifestyle"]

        self.memory_category_selector = ctk.CTkOptionMenu(
            tab, values=[c.capitalize() for c in self.memory_categories],
            command=self._on_memory_category_selected,
        )
        self.memory_category_selector.pack(pady=(15, 10))

        self.memory_list_frame = ctk.CTkScrollableFrame(tab, fg_color="#151E2E", height=250)
        self.memory_list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        add_frame = ctk.CTkFrame(tab, fg_color="transparent")
        add_frame.pack(pady=10, fill="x", padx=15)

        self.memory_key_field = ctk.CTkEntry(add_frame, placeholder_text="Label (e.g. 'school')")
        self.memory_key_field.pack(side="left", padx=(0, 5), fill="x", expand=True)

        self.memory_value_field = ctk.CTkEntry(add_frame, placeholder_text="Value (e.g. 'UCSD')")
        self.memory_value_field.pack(side="left", padx=5, fill="x", expand=True)

        add_button = ctk.CTkButton(add_frame, text="Add", width=60, command=self._add_memory_fact)
        add_button.pack(side="left", padx=(5, 0))

        self._on_memory_category_selected("Identity")

    def _on_memory_category_selected(self, selected_label):
        self._current_memory_category = selected_label.lower()
        self._load_memory_list()



    def _load_memory_list(self):
        from core.long_term_memory import load_memory

        for widget in self.memory_list_frame.winfo_children():
            widget.destroy()

        memory = load_memory()


        if not any(memory.get(c, {} if c != "projects" else []) for c in self.memory_categories):
            ctk.CTkLabel(
                self.memory_list_frame,
                text="I don't know much about you yet.\nTell me something and say 'remember that...'",
                text_color="#64748B", font=ctk.CTkFont(size=13), justify="center",
            ).pack(pady=40)
            return
    
        for category in self.memory_categories:
            contents = memory.get(category, {} if category != "projects" else [])
            if not contents:
                continue

            ctk.CTkLabel(
                self.memory_list_frame,
                text=f"{CATEGORY_ICONS.get(category, '•')}  {category.capitalize()}",
                font=ctk.CTkFont(size=14, weight="bold"), text_color="#3B82F6",
            ).pack(anchor="w", padx=5, pady=(16, 6))

            if category == "projects":
                for item in contents:
                    self._add_memory_row(category, None, item)
            else:
                for key, value in contents.items():
                    self._add_memory_row(category, key, value)



    def _add_memory_row(self, category, key, value):
        row = ctk.CTkFrame(self.memory_list_frame, fg_color="transparent")
        row.pack(fill="x", pady=2, padx=5)

        label_text = f"{key}: {value}" if key else value
        chip = ctk.CTkLabel(
            row, text=label_text, anchor="w",
            fg_color="#1a2938", corner_radius=14, padx=14, pady=6,
            text_color="#E2E8F0", font=ctk.CTkFont(size=12),
        )
        chip.pack(side="left", padx=(0, 6), pady=3)

        delete_button = ctk.CTkButton(
            row, text="✕", width=24, height=24, corner_radius=12,
            fg_color="transparent", hover_color="#3a1a1a", text_color="#EF4444",
            border_width=1, border_color="#EF4444",
            command=lambda c=category, k=key, v=value: self._delete_memory_fact(c, k, v),
        )
        delete_button.pack(side="left", padx=(0, 0))


    def _add_memory_fact(self):
        from core.long_term_memory import remember_fact

        value = self.memory_value_field.get().strip()
        if not value:
            return

        if self._current_memory_category == "projects":
            remember_fact("projects", None, value)
        else:
            key = self.memory_key_field.get().strip()
            if not key:
                print("Label is required for this category")
                return
            remember_fact(self._current_memory_category, key, value)

        self.memory_key_field.delete(0, "end")
        self.memory_value_field.delete(0, "end")
        self._load_memory_list()


    def _delete_memory_fact(self, category, key, value):
        from core.long_term_memory import load_memory, save_memory

        memory = load_memory()

        if category == "projects":
            if value in memory["projects"]:
                memory["projects"].remove(value)
        else:
            if key in memory.get(category, {}):
                del memory[category][key]

        save_memory(memory)
        self._load_memory_list()



    def _build_screenshots_tab(self, tab):
        ctk.CTkLabel(tab, text="Screenshots", font=ctk.CTkFont(size=20, weight="bold"), text_color="#F8FAFC").pack(pady=(20, 5))
        #ctk.CTkLabel(tab, text="Screenshots taken b", text_color="#8E9BAE", font=ctk.CTkFont(size=12)).pack(pady=(0, 15))

        refresh_button = ctk.CTkButton(tab, text="Refresh", command=self._load_screenshots)
        refresh_button.pack(pady=(0, 10))

        self.screenshots_scroll = ctk.CTkScrollableFrame(tab, fg_color="#151E2E")
        self.screenshots_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self._load_screenshots()


    def _load_screenshots(self):
        import os
        from PIL import Image

        for widget in self.screenshots_scroll.winfo_children():
            widget.destroy()

        screenshots_dir = "screenshots"

        if not os.path.exists(screenshots_dir):
            ctk.CTkLabel(
                self.screenshots_scroll, text="No screenshots yet.",
                text_color="#64748B", font=ctk.CTkFont(size=13),
            ).pack(pady=40)
            return

        files = sorted(os.listdir(screenshots_dir), reverse=True)  # most recent first
        files = [f for f in files if f.lower().endswith(".png")]

        if not files:
            ctk.CTkLabel(
                self.screenshots_scroll, text="No screenshots yet.",
                text_color="#64748B", font=ctk.CTkFont(size=13),
            ).pack(pady=40)
            return

        for filename in files[:30]:  # cap at 30 most recent, to avoid loading hundreds of images
            filepath = os.path.join(screenshots_dir, filename)
            self._add_screenshot_row(filepath, filename)

    def _add_screenshot_row(self, filepath, filename):
        from PIL import Image

        row = ctk.CTkFrame(self.screenshots_scroll, fg_color="#1a2938")
        row.pack(fill="x", pady=5, padx=5)

        try:
            pil_image = Image.open(filepath)
            pil_image.thumbnail((200, 150))
            ctk_image = ctk.CTkImage(light_image=pil_image, size=pil_image.size)

            image_label = ctk.CTkLabel(row, image=ctk_image, text="")
            image_label.pack(side="left", padx=10, pady=10)
        except Exception:
            ctk.CTkLabel(row, text="(couldn't load image)", text_color="#EF4444").pack(side="left", padx=10, pady=10)

        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(info_frame, text=filename, text_color="#F8FAFC", font=ctk.CTkFont(size=12)).pack(anchor="w")

        button_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        button_row.pack(anchor="w", pady=(8, 0))

        open_button = ctk.CTkButton(
            button_row, text="Open Full Size", width=120, height=28,
            command=lambda p=filepath: self._open_screenshot(p),
        )
        open_button.grid(row=0, column=0, padx=(0, 8))

        delete_button = ctk.CTkButton(
            button_row, text="Delete", width=80, height=28,
            fg_color="darkred", hover_color="#7f1d1d",
            command=lambda p=filepath: self._delete_screenshot(p),
        )
        delete_button.grid(row=0, column=1)


    def _delete_screenshot(self, filepath):
        import os
        try:
            os.remove(filepath)
            print(f"Deleted screenshot: {filepath}")
        except Exception as e:
            print(f"Failed to delete screenshot: {e}")
        self._load_screenshots()
        

    def _open_screenshot(self, filepath):
        import subprocess
        subprocess.run(["open", filepath])


    def _build_diagnostics_tab(self, tab):
        ctk.CTkLabel(tab, text= f"Diagnostics for Rose {ROSE_VERSION}", font=ctk.CTkFont(size=20, weight="bold"), text_color="#F8FAFC").pack(pady=(20, 5))
        ctk.CTkLabel(tab, text="Run functional tests against Rose's core systems", text_color="#8E9BAE", font=ctk.CTkFont(size=12)).pack(pady=(0, 15))

        self.run_tests_button = ctk.CTkButton(tab, text="Run All Tests", command=self._run_diagnostics)
        self.run_tests_button.pack(pady=(0, 10))

        self.diagnostics_summary = ctk.CTkLabel(tab, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.diagnostics_summary.pack(pady=(0, 10))

        self.diagnostics_output = ctk.CTkTextbox(tab, width=500, height=350)
        self.diagnostics_output.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # configure the color tags used by _append_diagnostic_line
        self.diagnostics_output.tag_config("success", foreground="#22C55E")
        self.diagnostics_output.tag_config("failure", foreground="#EF4444")


    def _run_diagnostics(self):
        self.run_tests_button.configure(state="disabled", text="Running...")
        self.diagnostics_output.delete("1.0", "end")
        self.diagnostics_summary.configure(text="")

        threading.Thread(target=self._run_diagnostics_thread, daemon=True).start()


    def _run_diagnostics_thread(self):
        from run_tests import run_all_tests

        def on_progress(name, success, error):
            line = f"{'✓' if success else '✗'} {name}"
            if error:
                line += f"\n    → {error}"
            self.after(0, self._append_diagnostic_line, line, success)

        passed, failed, failures = run_all_tests(progress_callback=on_progress)

        self.after(0, self._finish_diagnostics, passed, failed)


    def _append_diagnostic_line(self, line, success):
        self.diagnostics_output.insert(
            "end",
            line + "\n",
            "success" if success else "failure"
        )
        self.diagnostics_output.see("end")


    def _finish_diagnostics(self, passed, failed):
        color = "#22C55E" if failed == 0 else "#EF4444"
        self.diagnostics_summary.configure(
            text=f"Passed: {passed}   Failed: {failed}",
            text_color=color
        )
        self.run_tests_button.configure(state="normal", text="Run All Tests")


    def _build_capabilities_tab(self, tab):
        ctk.CTkLabel(tab, text="What Rose Can Do", font=ctk.CTkFont(size=20, weight="bold"), text_color="#F8FAFC").pack(pady=(20, 5))
        ctk.CTkLabel(tab, text="Every capability Rose has, and how to trigger it", text_color="#8E9BAE", font=ctk.CTkFont(size=12)).pack(pady=(0, 15))

        search_frame = ctk.CTkFrame(tab, fg_color="transparent")
        search_frame.pack(pady=(0, 10), padx=15, fill="x")

        self.capabilities_search = ctk.CTkEntry(search_frame, placeholder_text="Search capabilities...")
        self.capabilities_search.pack(fill="x")
        self.capabilities_search.bind("<KeyRelease>", lambda e: self._load_capabilities())

        self.capabilities_scroll = ctk.CTkScrollableFrame(tab, fg_color="#151E2E")
        self.capabilities_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self._load_capabilities()


    def _load_capabilities(self):
        from plugins.registry import ALL_PLUGINS

        for widget in self.capabilities_scroll.winfo_children():
            widget.destroy()

        search_term = self.capabilities_search.get().strip().lower() if hasattr(self, "capabilities_search") else ""

        for plugin in ALL_PLUGINS:
            name_display = plugin.name.replace("_", " ").title()
            description = plugin.user_facing_description or plugin.description

            if search_term and search_term not in name_display.lower() and search_term not in description.lower():
                continue

            self._add_capability_card(name_display, description)

    def _add_capability_card(self, name: str, description: str):
        card = ctk.CTkFrame(self.capabilities_scroll, fg_color="#1a2938", corner_radius=10)
        card.pack(fill="x", pady=6, padx=5)

        ctk.CTkLabel(
            card, text=name, font=ctk.CTkFont(size=14, weight="bold"), text_color="#3B82F6", anchor="w"
        ).pack(fill="x", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            card, text=description, font=ctk.CTkFont(size=12), text_color="#CBD5E1",
            anchor="w", justify="left", wraplength=650,
        ).pack(fill="x", padx=15, pady=(0, 12))




if __name__ == "__main__":
    try:
        app = RoseSettingsApp()
        app.mainloop()
    except Exception:
        with open(GUI_ERROR_LOG, "a") as f:
            f.write(traceback.format_exc() + "\n")
        raise