# ui/main_window.py
import tkinter as tk
from tkinter import ttk
from .download_tab import DownloadTab
from .playlist_tab import PlaylistTab
from .history_tab import HistoryTab
from .settings_tab import SettingsTab

class MainWindow(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Create tab control
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=1, fill="both")

        # Initialize tabs
        self.download_tab = DownloadTab(self.tabs)
        self.playlist_tab = PlaylistTab(self.tabs)
        self.history_tab = HistoryTab(self.tabs)
        self.settings_tab = SettingsTab(self.tabs)

        # Add tabs to notebook
        self.tabs.add(self.download_tab, text="Download")
        self.tabs.add(self.playlist_tab, text="Playlist")
        self.tabs.add(self.history_tab, text="History")
        self.tabs.add(self.settings_tab, text="Settings")