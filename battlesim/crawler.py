#!/usr/bin/env python3
import requests
import json
import pathlib
import os


def crawl_cards_data() -> dict:
    file_directory = pathlib.Path(__file__).parent
    if not os.path.exists(file_directory / "downloads"):
        os.mkdir(file_directory / "downloads")

    response = requests.get(
        "https://api.blizzard.com/hearthstone/cards?gameMode=battlegrounds&locale=en_US&pageSize=2000",
        headers={"Authorization": "Bearer KR0TZFpUeCM5q4QdrFqKfgdRUk5Wgayl4M"},
    )

    cards_data: list = response.json()["cards"]

    child_card_ids = []
    for card_data in cards_data:
        child_card_ids.extend(card_data.get("childIds", []))
    ids_param = "%2C".join(str(card_id) for card_id in child_card_ids)
    child_card_response = requests.get(
        f"https://api.blizzard.com/hearthstone/cards?ids={ids_param}&locale=en_US",
        headers={"Authorization": "Bearer KR0TZFpUeCM5q4QdrFqKfgdRUk5Wgayl4M"},
    )
    cards_data.extend(child_card_response.json()["cards"])

    with open(file_directory / "downloads/cards.json", "w") as cards_data_file:
        json.dump(cards_data, cards_data_file, indent=2)


if __name__ == "__main__":
    crawl_cards_data()
