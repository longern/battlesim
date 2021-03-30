import json
import logging
import pathlib
import re
from random import choice

from .event import after, register_action, whenever
from .minion_types import MinionType
from .view import view

cards_data_file_path = pathlib.Path(__file__).parent / "downloads/cards.json"
with open(cards_data_file_path, "r") as cards_data_file:
    cards_data = {card["id"]: card for card in json.load(cards_data_file)}


def pick_attacked_target(minions):
    if any(minion.taunt for minion in minions):
        minions = [minion for minion in minions if minion.taunt]
    return choice(minions)


class Card:
    def __init__(self, **kwargs):
        self.name = "Unknown"
        self.minion_type = None
        self.divine_shield = False
        self.poisoned = False
        self.poisonous = False
        self.reborn = False
        self.taunt = False
        self.windfury = False

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Card({self.name}, {self.attack_power}, {self.health})>"

    @register_action
    def attack(self, defender=None):
        if defender is None:
            defender = pick_attacked_target(self.enemy_minions)

        self.deal_damage(self.attack_power, defender)
        defender.deal_damage(defender.attack_power, self)

    @register_action
    def deal_damage(self, amount: int, card: "Card"):
        if amount <= 0 or not card:
            return

        if card.divine_shield:
            card.lose_divine_shield()
            return

        card.health -= amount

        if (
            card.health < 0
            and hasattr(self, "overkill")
            and self.controller is self.game.current_player
        ):
            self.overkill()

        if isinstance(self, Card) and self.poisonous:
            card.poisoned = True

    def gain(self, attack_power, health):
        self.attack_power += attack_power
        self.health += health

    @register_action
    def die(self):
        self.trigger("Deathrattle")
        if self.reborn:
            self.summon(Card.fromid(self.card_id, health=1, reborn=False))

    @register_action
    def lose_divine_shield(self):
        self.divine_shield = False

    @register_action
    def summon(self, card: "Card"):
        if not card or len(self.friendly_minions) >= 7:
            return

        card.controller = self.controller
        self.friendly_minions.insert(
            getattr(self, "index", len(self.friendly_minions)), card
        )

        if hasattr(card, "effect"):
            self.game.dispatcher[card.effect.condition].append((card, card.effect))

    @register_action
    def trigger(self, ability: str):
        ability = ability.lower()
        if callable(getattr(self, ability, None)):
            getattr(self, ability)()

    @classmethod
    def fromid(cls, card_id: int, **kwargs):
        try:
            card_data: dict = cards_data[card_id]
        except KeyError:
            logging.error("Card %d not found.", card_id)
            return None

        # Load effect
        from . import effects

        words = re.sub(r"^\d+-", "", card_data["slug"]).split("-")
        class_name = "".join(map(str.capitalize, words))
        if hasattr(effects, class_name):
            cls = getattr(effects, class_name)

        kwargs["card_id"] = card_id
        kwargs.setdefault("attack_power", card_data["attack"])
        kwargs.setdefault("health", card_data["health"])
        kwargs.setdefault("minion_type", MinionType(card_data.get("minionTypeId", 0)))
        kwargs["name"] = card_data["name"]
        kwargs["tier"] = card_data.get("battlegrounds", {}).get("tier", 1)

        # Load keywords from card text.
        text_match = re.match("^(<b>[A-Za-z ]*</b>(?: |$))*", card_data["text"])
        group = text_match.group() if text_match else ""
        keywords = re.findall("<b>([A-Za-z ]*)</b>", group)
        for keyword in keywords:
            kwargs.setdefault(keyword.replace(" ", "_").lower(), True)

        return cls(**kwargs)

    @property
    def enemy_minions(self):
        return self.controller.opponent.minions

    @property
    def friendly_minions(self):
        return self.controller.minions

    @property
    def game(self):
        return self.controller.game

    @property
    def other(self):
        return view(lambda iterable: filter(lambda x: x is not self, iterable))
