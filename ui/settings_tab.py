# ui/settings_tab.py
import tkinter as tk
from tkinter import ttk, filedialog
import json
import os

SETTINGS_PATH = os.path.join(os.getcwd(), "settings.json")

class SettingsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.settings = {
            "download_path": os.getcwd(),
            "max_threads": 4,
            "preferred_format": "mp4",
            "auto_update": True
        }

        # Load saved settings if exist
        self.load_settings()

        # Download folder
        ttk.Label(self, text="Default Download Folder:").pack(pady=5, anchor="w")
        self.download_path_var = tk.StringVar(value=self.settings["download_path"])
        path_frame = ttk.Frame(self)
        path_frame.pack(fill="x", pady=5)
        self.path_entry = ttk.Entry(path_frame, textvariable=self.download_path_var, width=50)
        self.path_entry.pack(side="left", padx=5)
        ttk.Button(path_frame, text="Browse", command=self.browse_folder).pack(side="left")

        # Max threads
        ttk.Label(self, text="Max Concurrent Downloads:").pack(pady=5, anchor="w")
        self.threads_var = tk.IntVar(value=self.settings["max_threads"])
        ttk.Spinbox(self, from_=1, to=16, textvariable=self.threads_var, width=5).pack(pady=5, anchor="w")

        # Preferred format
        ttk.Label(self, text="Preferred Format:").pack(pady=5, anchor="w")
        self.format_var = tk.StringVar(value=self.settings["preferred_format"])
        formats = ["mp4", "webm", "mp3", "aac", "flac", "m4a"]
        ttk.Combobox(self, textvariable=self.format_var, values=formats, state="readonly", width=10).pack(pady=5, anchor="w")

        # Auto-update toggle
        self.auto_update_var = tk.BooleanVar(value=self.settings["auto_update"])
        ttk.Checkbutton(self, text="Enable Auto-Update", variable=self.auto_update_var).pack(pady=5, anchor="w")

        # Save button
        ttk.Button(self, text="Save Settings", command=self.save_settings).pack(pady=10)

        # Status label
        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path_var.set(folder)

    def save_settings(self):
        self.settings["download_path"] = self.download_path_var.get()
        self.settings["max_threads"] = self.threads_var.get()
        self.settings["preferred_format"] = self.format_var.get()
        self.settings["auto_update"] = self.auto_update_var.get()

        with open(SETTINGS_PATH, "w") as f:
            json.dump(self.settings, f, indent=4)

        self.status_label.config(text="Settings saved successfully!")

    def load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r") as f:
                    self.settings.update(json.load(f))
            except Exception:
                pass