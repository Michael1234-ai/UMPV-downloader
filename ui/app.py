# ui/App.py
import tkinter as tk
from .main_window import MainWindow

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Ultimate Downloader")
        self.geometry("900x600")

        # Main window container
        self.main_window = MainWindow(self)
        self.main_window.pack(expand=1, fill="both")