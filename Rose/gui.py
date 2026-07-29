"""
gui.py

Settings GUI for Rose - separate process from main.py.
Run manually with: python3 gui.py
"""

import customtkinter as ctk
import pyttsx3
import json
import tkinter

SETTINGS_PATH = "config/settings.json"

customtkinter_appearance = ctk.set_appearance_mode("system")
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
        self.title("Rose Settings")
        self.geometry("500x400")

        self.settings = load_settings()

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        self.tabview.add("Voice")
        self.tabview.add("Hotkey")
        self.tabview.add("Config Files")

        self._build_voice_tab()

    def _build_voice_tab(self):
        tab = self.tabview.tab("Voice")
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        self.voice_map = {v.name: v.id for v in voices}
        self.voice_dropdown = ctk.CTkOptionMenu(tab, values=list(self.voice_map.keys()))
        self.voice_dropdown.pack(pady=10)

        save_button = ctk.CTkButton(tab, text="Save Voice", command=self._save_voice)
        save_button.pack(pady=10)
    def _save_voice(self):
        selected_name = self.voice_dropdown.get()
        selected_id = self.voice_map[selected_name]
        self.settings["voice_id"] = selected_id
        self.settings["say_voice_name"] = selected_name
        save_settings(self.settings)
        print(f"Saved voice: {selected_name}")


if __name__ == "__main__":
    app = RoseSettingsApp()
    app.mainloop()