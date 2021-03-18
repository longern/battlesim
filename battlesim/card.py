import json
import logging
import pathlib
import re

cards_data_file_path = pathlib.Path(__file__).parent / "downloads/cards.json"
with open(cards_data_file_path, "r") as cards_data_file:
    cards_data = {card["id"]: card for card in json.load(cards_data_file)["cards"]}


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
            card_data = cards_data[card_id]
        except KeyError:
            logging.error("Card %d not found.", card_id)
            return None

        # Load effect
        from . import effects

        words = re.sub("^\d+-", "", card_data["slug"]).split("-")
        class_name = "".join(map(str.capitalize, words))
        if hasattr(effects, class_name):
            effect_class = getattr(effects, class_name)
            cls = type(effect_class.__name__, (cls, effect_class), {})

        kwargs.setdefault("attack", card_data["attack"])
        kwargs.setdefault("health", card_data["health"])
        kwargs["name"] = card_data["name"]
        kwargs["tier"] = card_data["battlegrounds"]["tier"]

        # Load keywords from card text.
        text_match = re.match("^<b>[A-Za-z ]*</b>(?: |$)", card_data["text"])
        group = text_match.group() if text_match else ""
        keywords = re.findall("<b>([A-Za-z ]*)</b>", group)
        for keyword in keywords:
            kwargs.setdefault(keyword.replace(" ", "_").lower(), True)

        return cls(**kwargs)

    @property
    def enemy_minions(self):
        return self.controller.opponent.minions
