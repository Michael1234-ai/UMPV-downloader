# ui/App.py
import tkinter as tk
from tkinter import ttk

from core.downloader import Downloader
from core.queue_manager import QueueManager
from .download_tab import DownloadTab
from .playlist_tab import PlaylistTab
from .history_tab import HistoryTab
from .settings_tab import SettingsTab

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Ultimate Downloader")
        self.geometry("900x600")

        # -------------------------
        # Initialize SettingsTab first
        # -------------------------
        self.settings_tab = SettingsTab(self)
        self.settings_tab.pack_forget()  # hidden until selected

        # -------------------------
        # Initialize Downloader & QueueManager
        # -------------------------
        download_path = self.settings_tab.settings.get("download_path", None)
        max_threads = self.settings_tab.settings.get("max_threads", 2)
        self.downloader = Downloader(download_path=download_path, max_threads=max_threads)
        self.queue_manager = QueueManager(self.downloader)

        # Let SettingsTab know about queue_manager (for future dynamic updates)
        self.settings_tab.set_queue_manager(self.queue_manager)

        # -------------------------
        # Create Notebook Tabs
        # -------------------------
        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=1, fill="both")

        # Initialize other tabs
        self.history_tab = HistoryTab(self.tab_control)
        self.download_tab = DownloadTab(
            self.tab_control,
            queue_manager=self.queue_manager,
            settings_tab=self.settings_tab,
            history_tab=self.history_tab
        )
        self.playlist_tab = PlaylistTab(
            self.tab_control,
            queue_manager=self.queue_manager,
            history_tab=self.history_tab
        )

        # Add tabs to Notebook
        self.tab_control.add(self.download_tab, text="Download")
        self.tab_control.add(self.playlist_tab, text="Playlist")
        self.tab_control.add(self.history_tab, text="History")
        self.tab_control.add(self.settings_tab, text="Settings")