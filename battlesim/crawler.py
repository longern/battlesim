#!/usr/bin/env python3
import requests
import json
import pathlib
import os


def crawl_cards_data() -> dict:
    response = requests.get(
        "https://api.blizzard.com/hearthstone/cards?gameMode=battlegrounds&locale=en_US&pageSize=2000",
        headers={"Authorization": "Bearer KR0TZFpUeCM5q4QdrFqKfgdRUk5Wgayl4M"},
    )

    file_directory = pathlib.Path(__file__).parent
    if not os.path.exists(file_directory / "downloads"):
        os.mkdir(file_directory / "downloads")

    with open(file_directory / "downloads/cards.json", "w") as cards_data_file:
        json.dump(response.json()["cards"], cards_data_file, indent=2)


if __name__ == "__main__":
    crawl_cards_data()
