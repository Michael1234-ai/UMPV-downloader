# ui/playlist_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from core.metadata import get_playlist_videos, get_video_info
from core.formats import list_video_formats, get_highest_quality

class PlaylistTab(ttk.Frame):
    def __init__(self, parent, queue_manager, history_tab=None):
        super().__init__(parent)

        self.queue_manager = queue_manager
        self.history_tab = history_tab

        # Playlist URL input
        ttk.Label(self, text="Playlist URL:").pack(pady=5, anchor="w")
        self.url_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.url_var, width=70).pack(pady=5, padx=10)

        # Fetch playlist button
        ttk.Button(self, text="Fetch Playlist", command=self.fetch_playlist).pack(pady=5)

        # Playlist tree
        columns = ("Title", "URL")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=400)
        self.tree.pack(pady=5, padx=10, fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Download selected button
        ttk.Button(self, text="Download Selected", command=self.download_selected).pack(pady=10)

    def fetch_playlist(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a playlist URL.")
            return

        try:
            videos = get_playlist_videos(url)
            # Clear existing entries
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Add videos to tree
            for video in videos:
                self.tree.insert("", "end", values=(video["title"], video["url"]))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch playlist: {e}")

    def download_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No selection", "Select at least one video to download.")
            return

        for item in selected_items:
            title, url = self.tree.item(item, "values")

            # Fetch best format
            try:
                best = get_highest_quality(url)
                fmt = best["format_id"] if best else "best"
            except:
                fmt = "best"

            # Callback after download
            def after_download(title=title, url=url, path=None):
                if self.history_tab:
                    self.history_tab.add_entry(title, url, path)

            # Add job to queue
            self.queue_manager.add_job(url, fmt, callback=after_download)

        messagebox.showinfo("Queued", f"{len(selected_items)} video(s) added to download queue.")