import json
import logging
import pathlib
import re
from functools import lru_cache, wraps
from typing import Any, Dict, List

from .event import after, register_action, whenever
from .minion_types import MinionType
from .view import view


@lru_cache(maxsize=1)
def get_cards_data() -> Dict[str, Dict[str, Any]]:
    cards_data_file_path = pathlib.Path(__file__).parent / "downloads/cards.json"
    with open(cards_data_file_path, "r") as cards_data_file:
        cards_data = {card["id"]: card for card in json.load(cards_data_file)}
    return cards_data


@lru_cache(maxsize=None)
def infer_child_card_id(parent_id: str) -> str:
    candidates = [
        key
        for key in get_cards_data().keys()
        if key.startswith(parent_id) and key != parent_id
    ]
    if len(candidates) != 1:
        raise AttributeError(
            f"Child ID not defined and cannot be inferred. Candidates: {candidates}"
        )
    return candidates[0]


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
    tech_level = 1
    atk = 0
    health = 0

    divine_shield = False
    poisonous = False
    premium = False
    reborn = False
    taunt = False
    to_be_destroyed = False
    windfury = False

    def __init__(self, **kwargs):
        self.name = "?"
        self.minion_type = None
        self.enchantments = []

        self.attacking = False
        self.burst = False
        self.num_of_attacks = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Card({self.name}, {self.atk}, {self.health})>"

    def propose_defender(func):
        @wraps(func)
        def wrapper(self, defender=...):
            if defender is ...:
                defender = pick_attacked_target(self.enemy_minions)

            if defender is not None:
                return func(self, defender)

        return wrapper

    @propose_defender
    @register_action
    def attack(self, defender):
        self.attacking = True
        self.deal_damage(self.atk, defender)
        defender.deal_damage(defender.atk, self)
        self.attacking = False

    def predamage(func):
        @wraps(func)
        def wrapper(self, amount: int, card: "Card"):
            if amount <= 0 or not card:
                return

            if card.divine_shield:
                card.lose_divine_shield()
                return

            return func(self, amount, card)

        return wrapper

    @predamage
    @register_action
    def deal_damage(self, amount: int, card: "Card"):
        card.health -= amount

        if (
            card.health < 0
            and hasattr(self, "overkill")
            and self.controller is self.game.current_player
        ):
            self.overkill()

        if isinstance(self, Card) and self.poisonous:
            card.to_be_destroyed = True

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
            card_data = get_cards_data()[card_id]
        except KeyError:
            logging.error("Card %d not found.", card_id)
            return None

        # Load effect
        from . import effects

        words = re.sub(r"[^ 0-9A-Za-z]", "", card_data["name"]).split(" ")
        class_name = "".join(map(str.capitalize, words))
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
            r"^(<b>[A-Za-z ]*</b>(?:\W|$))*", card_data.get("text", "")
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
            for card in get_cards_data().values()
            if "techLevel" in card
            and all(card.get(key) == value for key, value in kwargs.items())
        ]

        if not candidates:
            return None

        return cls.fromid(choice(candidates))

    @property
    def adjacent_minions(self) -> List["Card"]:
        index = self.controller.minions.index(self)
        return self.controller.minions[abs(index - 1) : index + 2 : 2]

    @property
    def alive(self) -> bool:
        return self.health > 0 and not self.to_be_destroyed

    def child_card(self) -> str:
        if not self.premium and hasattr(self.__class__, "normal_child"):
            child_card_id = self.__class__.normal_child
        elif self.premium and hasattr(self.__class__, "premium_child"):
            child_card_id = self.__class__.premium_child
        else:
            child_card_id = infer_child_card_id(self.card_id)
        return Card.fromid(child_card_id)

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

    @property
    def tip(self):
        return 2 if self.premium else 1
