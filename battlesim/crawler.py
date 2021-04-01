#!/usr/bin/env python3
import requests
import json
import pathlib
import os


def crawl_cards_data() -> dict:
    file_directory = pathlib.Path(__file__).parent
    if not os.path.exists(file_directory / "downloads"):
        os.mkdir(file_directory / "downloads")

    response = requests.get("https://api.hearthstonejson.com/v1/latest/enUS/cards.json")

    cards_data: list = response.json()

    with open(file_directory / "downloads/cards.json", "w") as cards_data_file:
        json.dump(cards_data, cards_data_file, indent=2)


if __name__ == "__main__":
    crawl_cards_data()
