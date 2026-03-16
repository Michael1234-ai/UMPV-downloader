# core/queue_manager.py
from queue import Queue
from threading import Thread
from .downloader import Downloader

class QueueManager:
    def __init__(self, downloader: Downloader):
        """
        downloader: instance of core.downloader.Downloader
        """
        self.downloader = downloader
        self.queue = Queue()
        self.active_workers = 0
        self.max_workers = downloader.max_threads

    def add_job(self, url: str, format_id: str, callback=None):
        """
        Add a new download job to the queue.
        """
        self.queue.put({"url": url, "format": format_id, "callback": callback})
        self._start_workers()

    def _start_workers(self):
        """
        Start worker threads up to max_workers
        """
        while self.active_workers < self.max_workers and not self.queue.empty():
            t = Thread(target=self._worker, daemon=True)
            t.start()
            self.active_workers += 1

    def _worker(self):
        """
        Worker thread processing jobs from the queue
        """
        while not self.queue.empty():
            job = self.queue.get()
            self.downloader._download(job["url"], job["format"], job.get("callback"))
            self.queue.task_done()
        self.active_workers -= 1

    def get_queue_size(self):
        """
        Returns number of jobs in queue
        """
        return self.queue.qsize()

    def is_busy(self):
        """
        Returns True if there are active jobs
        """
        return self.get_queue_size() > 0 or self.active_workers > 0