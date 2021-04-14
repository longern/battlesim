import json
import logging
import pathlib
import re
from functools import lru_cache, wraps
from typing import Any, Dict, List

from hearthstone.cardxml import load
from hearthstone.entities import (
    Card as BaseCard,
    Game as BaseGame,
    Player as BasePlayer,
)
from hearthstone.enums import GameTag, Zone, CardType

from .event import after, register_action, whenever


def tag_getter(tag: GameTag, default=None):
    @property
    def get_tag(self):
        return self.tags.get(tag, default)

    @get_tag.setter
    def set_tag(self, value):
        self.update_tag(tag, value)

    return get_tag


class Game(BaseGame):
    def filter(self, **kwargs):
        for entity in self.entities:
            if all(
                entity.tags[getattr(GameTag, k.upper())] == v for k, v in kwargs.items()
            ):
                yield entity


class Player(BasePlayer):
    @property
    def minions(self):
        return list(
            self.game.filter(
                zone=Zone.PLAY,
                cardtype=CardType.MINION,
                controller=self.player_id,
            )
        )


@lru_cache(maxsize=None)
def infer_child_card_id(parent_id: str) -> str:
    db, _ = load()
    candidates = [
        key for key in db.keys() if key.startswith(parent_id) and key != parent_id
    ]
    if len(candidates) != 1:
        raise AttributeError(
            f"Child ID not defined and cannot be inferred. Candidates: {candidates}"
        )
    return candidates[0]


class Card(BaseCard):
    def __init__(self, **kwargs):
        super(Card, self).__init__()

    def __repr__(self):
        return f"{self.name}"

    atk = tag_getter(GameTag.ATK)
    divine_shield = tag_getter(GameTag.DIVINE_SHIELD, False)
    num_attacks_this_turn = tag_getter(GameTag.NUM_ATTACKS_THIS_TURN, 0)
    poisonous = tag_getter(GameTag.POISONOUS, False)
    premium = tag_getter(GameTag.PREMIUM, False)
    to_be_destroyed = tag_getter(GameTag.TO_BE_DESTROYED, False)

    @property
    def name(self):
        db, _ = load(locale="zhCN")
        return db[self.card_id].name

    @classmethod
    def fromid(cls, card_id):
        return cls()

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
        card.damage += amount

        if (
            card.damage > card.health
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
            self.summon(Card.fromid(self.card_id, start_with_1_health=1, reborn=False))

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
    def fromid(cls, game: Game, card_id: str, **kwargs):
        try:
            db, _ = load()
        except KeyError:
            logging.error("Card %d not found.", card_id)
            return None

        # Load effect
        from .. import effects

        words = re.sub(r"[^ 0-9A-Za-z]", "", db["name"]).split(" ")
        class_name = "".join(map(str.capitalize, words))
        if hasattr(effects, class_name):
            cls = getattr(effects, class_name)

        return cls(card_id, **kwargs)

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
        return self.damage < self.health and not self.to_be_destroyed

    def child_card(self) -> str:
        if not self.premium and hasattr(self.__class__, "normal_child"):
            child_card_id = self.__class__.normal_child
        elif self.premium and hasattr(self.__class__, "premium_child"):
            child_card_id = self.__class__.premium_child
        else:
            child_card_id = infer_child_card_id(self.card_id)
        return Card.fromid(child_card_id)

    @property
    def controller(self):
        return self.game._entities[self.tags[GameTag.CONTROLLER]]

    @property
    def enemy_minions(self) -> List["Card"]:
        return self.controller.opponent.minions

    @property
    def friendly_minions(self) -> List["Card"]:
        return list(
            self.game.filter(
                controller=self.tags[GameTag.CONTROLLER],
                zone=Zone.PLAY,
                cardtype=CardType.MINION,
            )
        )

    @property
    def other(self):
        return view(lambda iterable: filter(lambda x: x is not self, iterable))

    @property
    def tip(self):
        return 2 if self.premium else 1


class Hero(Card):
    pass


class HeroPower(Card):
    pass


class Minion(Card):
    def __repr__(self):
        return f"{self.name}{self.atk}/{self.health}"

    @property
    def health(self):
        return self.tags[GameTag.HEALTH] - self.tags.get(GameTag.DAMAGE, 0)


class Enchantment(Card):
    def __repr__(self):
        return f"{self.name}"

    attached = tag_getter(GameTag.ATTACHED)
