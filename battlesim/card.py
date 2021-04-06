import json
import logging
import pathlib
import re
from typing import List

from .event import after, register_action, whenever
from .minion_types import MinionType
from .view import view

cards_data_file_path = pathlib.Path(__file__).parent / "downloads/cards.json"
with open(cards_data_file_path, "r") as cards_data_file:
    cards_data = {card["id"]: card for card in json.load(cards_data_file)}


def choice(seq):
    import random

    try:
        return random.choice(seq)
    except IndexError:
        return None


def pick_attacked_target(minions):
    if any(minion.taunt for minion in minions):
        minions = [minion for minion in minions if minion.taunt]
    return choice(minions)


class Card:
    def __init__(self, **kwargs):
        self.name = "Unknown"
        self.minion_type = None
        self.attacking = False
        self.burst = False
        self.divine_shield = False
        self.num_of_attacks = 0
        self.poisoned = False
        self.poisonous = False
        self.reborn = False
        self.taunt = False
        self.windfury = False

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Card({self.name}, {self.atk}, {self.health})>"

    @register_action
    def attack(self, defender=None):
        if defender is None:
            defender = pick_attacked_target(self.enemy_minions)

        if defender is not None:
            self.attacking = True
            self.deal_damage(self.atk, defender)
            defender.deal_damage(defender.atk, self)
            self.attacking = False

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

    def gain(self, atk, health, permanently=False):
        self.atk += atk
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
    def fromid(cls, card_id: str, **kwargs):
        try:
            card_data: dict = cards_data[card_id]
        except KeyError:
            logging.error("Card %d not found.", card_id)
            return None

        # Load effect
        from . import effects

        class_name = "".join(
            map(
                str.capitalize,
                re.sub(r"[^ 0-9A-Za-z]", "", card_data["name"]).split(" "),
            )
        )
        if hasattr(effects, class_name):
            cls = getattr(effects, class_name)

        kwargs["card_id"] = card_id
        kwargs.setdefault("atk", card_data.get("attack"))
        kwargs.setdefault("health", card_data.get("health"))
        kwargs.setdefault("cardtype", card_data.get("type"))
        kwargs.setdefault(
            "minion_type",
            getattr(
                MinionType,
                card_data.get("race", "").lower().capitalize(),
                MinionType.NoMinionType,
            ),
        )
        kwargs["name"] = card_data["name"]
        kwargs["tier"] = card_data.get("techLevel", 1)

        # Load keywords from card text.
        text_match = re.match(
            r"^(<b>[A-Za-z ]*</b>(?:\s|$))*", card_data.get("text", "")
        )
        group = text_match.group() if text_match else ""
        keywords = re.findall("<b>([A-Za-z ]*)</b>", group)
        for keyword in keywords:
            kwargs.setdefault(keyword.replace(" ", "_").lower(), True)

        return cls(**kwargs)

    @classmethod
    def random(cls, **kwargs):
        candidates = [
            card["id"]
            for card in cards_data
            if all(card.get(key) == value for key, value in kwargs.items())
        ]

        if not candidates:
            return None

        return cls.fromid(choice(candidates))

    @property
    def adjacent_minions(self) -> List["Card"]:
        index = self.controller.minions.index(self)
        return self.controller.minions[max(index - 1, 0), index + 1 : 2]

    @property
    def enemy_minions(self) -> List["Card"]:
        return self.controller.opponent.minions

    @property
    def friendly_minions(self) -> List["Card"]:
        return self.controller.minions

    @property
    def game(self):
        return self.controller.game

    @property
    def other(self):
        return view(lambda iterable: filter(lambda x: x is not self, iterable))
