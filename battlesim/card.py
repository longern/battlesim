import pathlib
import json
import re

with open(
    pathlib.Path(__file__).parent / "downloads/cards.json", "r"
) as cards_data_file:
    cards_data = json.load(cards_data_file)["cards"]


class Card:
    def __init__(self, **kwargs):
        self.name = "Unknown"
        self.divine_shield = False
        self.poisoned = False
        self.poisonous = False
        self.revive = False
        self.taunt = False

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Card({self.name}, {self.attack}, {self.health})>"

    @classmethod
    def fromid(cls, card_id: int, **kwargs):
        try:
            card_data = next(filter(lambda card: card["id"] == card_id, cards_data))
        except StopIteration:
            return None

        card = cls(**kwargs)
        card.name = card_data["name"]
        card.tier = card_data["battlegrounds"]["tier"]

        # Load keywords from card text.
        text_match = re.match("^<b>[A-Za-z ]*</b>(?: |$)", card_data["text"])
        group = text_match.group() if text_match else ""
        keywords = re.findall("<b>([A-Za-z ]*)</b>", group)
        for keyword in keywords:
            setattr(card, keyword.replace(" ", "_").lower(), True)

        return card
