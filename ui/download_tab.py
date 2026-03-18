# ui/download_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from core.metadata import get_video_info, get_formats
from core.formats import list_video_formats, get_highest_quality
from core.filename_cleaner import clean_filename

class DownloadTab(ttk.Frame):
    def __init__(self, parent, queue_manager, settings_tab=None, history_tab=None):
        super().__init__(parent)

        self.queue_manager = queue_manager
        self.settings_tab = settings_tab
        self.history_tab = history_tab

        # URL input
        ttk.Label(self, text="Video URL:").pack(pady=5, anchor="w")
        self.url_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.url_var, width=70).pack(pady=5, padx=10)

        # Fetch button
        ttk.Button(self, text="Fetch Video Info", command=self.fetch_info).pack(pady=5)

        # Video preview
        self.thumbnail_label = ttk.Label(self)
        self.thumbnail_label.pack(pady=5)
        self.info_label = ttk.Label(self, text="", wraplength=400)
        self.info_label.pack(pady=5)

        # Format selection
        ttk.Label(self, text="Select Format:").pack(pady=5, anchor="w")
        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(self, textvariable=self.format_var, state="readonly", width=40)
        self.format_combo.pack(pady=5)

        # Download button
        ttk.Button(self, text="Download", command=self.download_video).pack(pady=10)

        # Progress bar & status
        self.progress = ttk.Progressbar(self, length=400, mode='determinate')
        self.progress.pack(pady=5)
        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(pady=5)

    def fetch_info(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return
        try:
            info = get_video_info(url)
            self.info_label.config(text=f"{info['title']}\nChannel: {info['uploader']}\nDuration: {info['duration']}s")

            # Load thumbnail
            thumb_url = info.get("thumbnail")
            if thumb_url:
                response = requests.get(thumb_url)
                img = Image.open(BytesIO(response.content))
                img = img.resize((320, 180))
                self.thumbnail = ImageTk.PhotoImage(img)
                self.thumbnail_label.config(image=self.thumbnail)

            # Populate formats
            video_formats = list_video_formats(url)
            self.format_combo['values'] = [f"{f['format_id']} | {f['resolution']} | {f['ext']}" for f in video_formats]
            best = get_highest_quality(url)
            if best:
                self.format_var.set(f"{best['format_id']} | {best['resolution']} | {best['ext']}")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}")

    def download_video(self):
        url = self.url_var.get().strip()
        selected_format = self.format_var.get().split(" | ")[0] if self.format_var.get() else "best"
        if not url or not selected_format:
            self.status_label.config(text="URL or format missing!")
            return

        def after_download(title, path):
            if self.history_tab:
                self.history_tab.add_entry(title, url, path)
            self.status_label.config(text=f"Downloaded: {title}")

        self.queue_manager.add_job(url, selected_format, callback=after_download)
        self.status_label.config(text="Added to queue.")