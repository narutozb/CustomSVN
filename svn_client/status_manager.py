# status_manager.py

import threading

class StatusManager:
    def __init__(self):
        self.uploading = False
        self.lock = threading.Lock()

    def start_upload(self):
        with self.lock:
            self.uploading = True

    def end_upload(self):
        with self.lock:
            self.uploading = False

    def is_uploading(self):
        with self.lock:
            return self.uploading
