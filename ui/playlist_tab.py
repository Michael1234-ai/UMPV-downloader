# ui/playlist_tab.py
import tkinter as tk
from tkinter import ttk
from queue import Queue
import threading
import yt_dlp
import os
from core.filename_cleaner import clean_filename
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Use the same global download queue as download_tab
from .download_tab import download_queue

class PlaylistTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Playlist URL input
        self.url_label = ttk.Label(self, text="Playlist URL:")
        self.url_label.pack(pady=5)
        self.url_entry = ttk.Entry(self, width=70)
        self.url_entry.pack(pady=5)

        # Fetch playlist button
        self.fetch_btn = ttk.Button(self, text="Fetch Playlist", command=self.fetch_playlist)
        self.fetch_btn.pack(pady=5)

        # Scrollable frame for playlist videos
        self.canvas = tk.Canvas(self)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Format selector
        self.format_label = ttk.Label(self, text="Select Format for All Videos:")
        self.format_label.pack(pady=5)
        self.format_combo = ttk.Combobox(self, state="readonly", width=30)
        self.format_combo.pack(pady=5)

        # Download button
        self.download_btn = ttk.Button(self, text="Download Selected", command=self.download_selected)
        self.download_btn.pack(pady=10)

        # Status label
        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(pady=5)

        # Store video checkbox widgets
        self.video_vars = []
        self.video_info_list = []

    def fetch_playlist(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.config(text="Enter a playlist URL.")
            return

        ydl_opts = {"extract_flat": True, "quiet": True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                data = ydl.extract_info(url, download=False)

            # Clear previous
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()
            self.video_vars.clear()
            self.video_info_list.clear()

            # Add videos
            for i, entry in enumerate(data["entries"]):
                var = tk.BooleanVar(value=False)
                cb = ttk.Checkbutton(self.scroll_frame, text=entry["title"], variable=var)
                cb.pack(anchor="w", pady=2)
                self.video_vars.append(var)
                self.video_info_list.append({"title": entry["title"], "url": entry["url"]})

            # Populate format selector with first video formats as example
            if self.video_info_list:
                first_url = self.video_info_list[0]["url"]
                formats = self.get_formats(first_url)
                self.format_combo['values'] = [f"{f['format_id']} - {f['resolution'] or f['format_note']} - {f['ext']}" for f in formats]
                if formats:
                    self.format_combo.current(0)

            self.status_label.config(text=f"Fetched {len(self.video_info_list)} videos.")

        except Exception as e:
            self.status_label.config(text=f"Error fetching playlist: {e}")

    def get_formats(self, url):
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
        formats = []
        for f in info["formats"]:
            formats.append({"format_id": f["format_id"], "resolution": f.get("resolution"), "ext": f["ext"]})
        return formats

    def download_selected(self):
        selected_videos = []
        for var, info in zip(self.video_vars, self.video_info_list):
            if var.get():
                selected_videos.append(info)

        if not selected_videos:
            self.status_label.config(text="No videos selected!")
            return

        selected_format = self.format_combo.get().split(' - ')[0] if self.format_combo.get() else None
        if not selected_format:
            self.status_label.config(text="Select a format first!")
            return

        for video in selected_videos:
            download_queue.put({"url": video["url"], "format": selected_format, "widget": self})
        
        self.status_label.config(text=f"Added {len(selected_videos)} videos to the queue.")

        # Start worker thread
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        while not download_queue.empty():
            job = download_queue.get()
            self.download(job["url"], job["format"])
            download_queue.task_done()

    def download(self, url, format_id):
        ydl_opts = {
            "format": format_id,
            "progress_hooks": [self.progress_hook],
            "outtmpl": os.path.join(os.getcwd(), "%(title)s.%(ext)s")
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            self.status_label.config(text=f"Download error: {e}")

    def progress_hook(self, d):
        if d["status"] == "downloading":
            percent = float(d["_percent_str"].replace('%',''))
            self.status_label.config(text=f"{percent:.1f}% | Downloading...")
        elif d["status"] == "finished":
            self.status_label.config(text="Video download completed!")