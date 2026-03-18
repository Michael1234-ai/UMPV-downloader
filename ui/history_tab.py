# ui/history_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import webbrowser
from datetime import datetime

DB_PATH = os.path.join(os.getcwd(), "database", "history.db")

class HistoryTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Ensure database folder exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        # Connect to database
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_table()

        # Treeview setup
        columns = ("id", "title", "url", "path", "date", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            width = 250 if col in ("title", "url", "path") else 120
            self.tree.column(col, width=width)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Refresh button
        ttk.Button(self, text="Refresh History", command=self.load_history).pack(pady=5)

        # Load history initially
        self.load_history()

        # Bind double-click to open file
        self.tree.bind("<Double-1>", self.open_file)

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT,
                path TEXT,
                date TEXT,
                status TEXT
            )
        """)
        self.conn.commit()

    def add_entry(self, title, url, path=None, status="Completed"):
        """
        Add a download record to history.
        Used by QueueManager callbacks automatically.
        """
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO downloads(title, url, path, date, status) VALUES (?, ?, ?, ?, ?)",
            (title, url, path or "", date, status)
        )
        self.conn.commit()
        self.load_history()

    def load_history(self):
        # Clear tree
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Fetch and insert all history
        self.cursor.execute("SELECT * FROM downloads ORDER BY id DESC")
        for row in self.cursor.fetchall():
            self.tree.insert("", tk.END, values=row)

    def open_file(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            file_path = values[3]  # path column
            if os.path.exists(file_path):
                webbrowser.open(file_path)
            else:
                messagebox.showerror("Error", "File does not exist.")