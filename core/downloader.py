# core/downloader.py
import os
import threading
from queue import Queue
import yt_dlp
from .filename_cleaner import clean_filename

# Global download queue
download_queue = Queue()

class Downloader:
    def __init__(self, download_path=None, max_threads=4):
        self.download_path = download_path or os.getcwd()
        self.max_threads = max_threads
        self.threads = []
        self.active_workers = 0
        os.makedirs(self.download_path, exist_ok=True)

    def add_to_queue(self, url, format_id, callback=None):
        """
        Add a download job to the queue.
        callback: function(title, path) called after download completes
        """
        download_queue.put({"url": url, "format": format_id, "callback": callback})
        self._start_workers()

    def _start_workers(self):
        """
        Start worker threads up to max_threads
        """
        while self.active_workers < self.max_threads and not download_queue.empty():
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self.threads.append(t)
            self.active_workers += 1

    def _worker(self):
        while not download_queue.empty():
            job = download_queue.get()
            self._download(job["url"], job["format"], job.get("callback"))
            download_queue.task_done()
        self.active_workers -= 1

    def _download(self, url, format_id, callback=None):
        """
        Download a single video using yt-dlp
        """
        def progress_hook(d):
            status = d.get("status")
            if status == "downloading":
                percent = d["_percent_str"]
                speed = d.get("speed", 0)
                eta = d.get("eta", 0)
                print(f"{percent} | Speed: {speed/1024/1024:.2f} MB/s | ETA: {eta}s")
            elif status == "finished":
                print(f"Download finished: {d['filename']}")

        ydl_opts = {
            "format": format_id,
            "outtmpl": os.path.join(self.download_path, "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook]
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = clean_filename(ydl.prepare_filename(info))
                if callback:
                    callback(info.get("title"), filename)
        except Exception as e:
            print(f"Download error: {e}")