import os
import time
import asyncio


class LogStream:
    def __init__(self, filepath):
        self.filepath = filepath
        self.last_line = False

    def __iter__(self):
        while not os.path.exists(self.filepath):
            time.sleep(0.1)

        with open(self.filepath, encoding="utf-8") as file:
            while True:
                line = file.readline()
                if not line:
                    self.last_line = True
                    time.sleep(0.1)  # Sleep briefly
                    continue
                yield line


def get_log_path():
    candidates = [
        "C:/Program Files (x86)/Hearthstone/Logs/",
        "C:/Program Files/Hearthstone/Logs/",
        "/mnt/c/Program Files (x86)/Hearthstone/Logs/",
    ]

    for path in candidates:
        if os.path.exists(path):
            return path + "Power.log"

    raise OSError("Hearthstone not detected")
