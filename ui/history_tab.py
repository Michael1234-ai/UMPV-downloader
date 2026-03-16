# ui/history_tab.py
import tkinter as tk
from tkinter import ttk
import sqlite3
import os
import webbrowser
from datetime import datetime

DB_PATH = os.path.join(os.getcwd(), "database", "history.db")

class HistoryTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Connect/create database
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_table()

        # Treeview for history
        columns = ("id", "title", "url", "path", "date")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("url", text="URL")
        self.tree.heading("path", text="File Path")
        self.tree.heading("date", text="Date")

        self.tree.column("id", width=30)
        self.tree.column("title", width=250)
        self.tree.column("url", width=250)
        self.tree.column("path", width=250)
        self.tree.column("date", width=120)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Refresh button
        self.refresh_btn = ttk.Button(self, text="Refresh History", command=self.load_history)
        self.refresh_btn.pack(pady=5)

        # Load history on startup
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

    def add_entry(self, title, url, path, status="Completed"):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO downloads(title,url,path,date,status) VALUES(?,?,?,?,?)",
            (title, url, path, date, status)
        )
        self.conn.commit()
        self.load_history()

    def load_history(self):
        # Clear current rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.cursor.execute("SELECT * FROM downloads ORDER BY id DESC")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def open_file(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            file_path = values[3]  # Path column
            if os.path.exists(file_path):
                webbrowser.open(file_path)
            else:
                tk.messagebox.showerror("Error", "File does not exist.")