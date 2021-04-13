import os
import time


def follow(filepath):
    while not os.path.exists(filepath):
        time.sleep(0.1)

    with open(filepath) as file:
        while True:
            line = file.readline()
            if not line:
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
