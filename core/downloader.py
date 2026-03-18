# core/downloader.py
import os
import threading
import shutil
import yt_dlp
from .filename_cleaner import clean_filename

class Downloader:
    def __init__(self, download_path=None, max_threads=4):
        self.download_path = download_path or os.getcwd()
        self.max_threads = max_threads
        os.makedirs(self.download_path, exist_ok=True)

        # --- Node.js detection for JS runtime ---
        node_path = shutil.which("node")
        if node_path:
            self.js_runtime = f"node:{node_path}"
        else:
            print("[WARNING] Node.js not found in PATH. Some YouTube formats may be missing.")
            self.js_runtime = "deno"  # fallback to Deno

    def _download(self, url, format_id="best", callback=None):
        """
        Download a single video using yt-dlp
        Returns (file_path, title)
        """
        file_path = None
        title = None

        def progress_hook(d):
            nonlocal file_path
            nonlocal title
            status = d.get("status")
            if status == "downloading":
                percent = d.get("_percent_str", "0.0%")
                speed = d.get("speed", 0)
                eta = d.get("eta", 0)
                speed_mb = speed / 1024 / 1024 if speed else 0
                print(f"{percent} | Speed: {speed_mb:.2f} MB/s | ETA: {eta}s")
            elif status == "finished":
                file_path = clean_filename(d["filename"])
                print(f"Download finished: {file_path}")

        ydl_opts = {
            "format": format_id,
            "outtmpl": os.path.join(self.download_path, "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "quiet": True,
            "jsruntimes": [self.js_runtime]  # automatically use Node or Deno
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "Unknown Title")
                file_path = clean_filename(ydl.prepare_filename(info))
                if callback:
                    callback(title, file_path)
                return file_path, title

        except Exception as e:
            print(f"[ERROR] Download failed: {e}")
            if callback:
                callback(title or "Unknown", None)
            return None, title or "Unknown"

    def download_async(self, url, format_id="best", callback=None):
        """
        Download in a separate thread
        """
        thread = threading.Thread(target=self._download, args=(url, format_id, callback))
        thread.start()
        return thread