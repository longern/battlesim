import logging
import operator
import re
from collections import defaultdict
from functools import lru_cache, wraps
from typing import Any, Dict, List

from hearthstone.cardxml import load
from hearthstone.entities import Card as BaseCard
from hearthstone.entities import Game as BaseGame
from hearthstone.entities import Player as BasePlayer
from hearthstone.enums import CardType, GameTag, Zone

from .event import after, register_action, whenever
from .view import view


def choice(seq):
    import random

    try:
        return random.choice(seq)
    except IndexError:
        return None


def pick_attacked_target(minions):
    minions = [minion for minion in minions if minion.alive]
    if any(minion.taunt for minion in minions):
        minions = [minion for minion in minions if minion.taunt]
    return choice(minions)


def tag_getter(tag: GameTag, default=None):
    @property
    def get_tag(self):
        return self.tags.get(tag, default)

    @get_tag.setter
    def get_tag(self, value):
        self.tag_change(tag, value)

    return get_tag


class Game(BaseGame):
    def __init__(self, id=1):
        super(Game, self).__init__(id)
        self.dispatcher = defaultdict(list)
        self.to_check_death = []

    def filter(self, **kwargs):
        queries = {getattr(GameTag, k.upper()): v for k, v in kwargs.items()}
        for entity in self.entities:
            if all(entity.tags.get(k) == v for k, v in queries.items()):
                yield entity

    def __repr__(self):
        return repr(self.players[0].minions) + "\n" + repr(self.players[1].minions)


class Player(BasePlayer):
    @property
    def minions(self):
        return sorted(
            self.game.filter(
                controller=self.player_id, zone=Zone.PLAY, cardtype=CardType.MINION
            ),
            key=lambda minion: minion.tags.get(GameTag.ZONE_POSITION, 10),
        )

    @property
    def opponent(self) -> "Player":
        for player in self.game.players:
            if player is not self:
                return player
        return None


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
    def __init__(self, id, card_id, **kwargs):
        try:
            super(Card, self).__init__(id, card_id)

            self.tags = self.base_tags.copy()
        except KeyError:
            self.tags[GameTag.CARDTYPE] = CardType.MINION

        for key, value in kwargs.items():
            self.tags[getattr(GameTag, key.upper())] = value

        if kwargs.get("start_with_1_health", False):
            self.tags[GameTag.DAMAGE] = self.tags[GameTag.HEALTH] - 1

    def __repr__(self):
        return f"{self.name}"

    atk = tag_getter(GameTag.ATK, 0)
    attacking = tag_getter(GameTag.ATTACKING, False)
    defending = tag_getter(GameTag.DEFENDING, False)
    divine_shield = tag_getter(GameTag.DIVINE_SHIELD, False)
    num_attacks_this_turn = tag_getter(GameTag.NUM_ATTACKS_THIS_TURN, 0)
    poisonous = tag_getter(GameTag.POISONOUS, False)
    premium = tag_getter(GameTag.PREMIUM, False)
    reborn = tag_getter(GameTag.REBORN, False)
    taunt = tag_getter(GameTag.TAUNT, False)
    to_be_destroyed = tag_getter(GameTag.TO_BE_DESTROYED, False)
    windfury = tag_getter(GameTag.WINDFURY, False)

    @property
    def name(self):
        db, _ = load(locale="zhCN")
        try:
            return db[self.card_id].name
        except KeyError:
            return self.card_id

    def create(self, card_id, **kwargs):
        return Minion.fromid(self.game, card_id, **kwargs)

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
        card.tags.setdefault(GameTag.DAMAGE, 0)
        card.tags[GameTag.DAMAGE] += amount

        if (
            card.health < 0
            and hasattr(self, "overkill")
            and self.controller is self.game.current_player
        ):
            self.overkill()

        if isinstance(self, Card) and self.poisonous:
            card.to_be_destroyed = True

        if card.health <= 0 or card.to_be_destroyed:
            self.game.to_check_death.append(card)

    def gain(self, atk, health, permanently=False):
        self.tags[GameTag.ATK] += atk
        self.tags[GameTag.HEALTH] += health

    @register_action
    def die(self):
        self.trigger("Deathrattle")
        if self.reborn:
            self.summon(self.create(self.card_id, start_with_1_health=1, reborn=False))

    @register_action
    def lose_divine_shield(self):
        self.tags[GameTag.DIVINE_SHIELD] = False

    @register_action
    def summon(self, card: "Card"):
        if not card or len(self.friendly_minions) >= 7:
            return

        card.tags[GameTag.CONTROLLER] = self.tags[GameTag.CONTROLLER]
        card.tags[GameTag.ZONE] = Zone.PLAY
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
    def load_effect(cls, card_name: str):
        # Load effect
        from . import effects

        words = re.sub(r"[^ 0-9A-Za-z]", "", card_name).split(" ")
        class_name = "".join(map(str.capitalize, words))
        if hasattr(effects, class_name):
            cls = getattr(effects, class_name)

        return cls

    @classmethod
    def fromid(cls, game: Game, card_id: str, **kwargs):
        try:
            db, _ = load()
            card_data = db[card_id]
        except KeyError:
            logging.error("Card %d not found.", card_id)
            return None

        cls = cls.load_effect(card_data.name)

        card: Card = cls(max(game._entities.keys(), default=0) + 1, card_id, **kwargs)
        game.register_entity(card)
        return card

    def random(**kwargs):
        db, _ = load()
        conditions = [
            (
                re.sub("__.*", "", key),
                getattr(
                    operator, re.search("(__[a-z]*)?$", key).group()[2:], operator.eq
                ),
                value,
            )
            for key, value in kwargs.items()
        ]

        candidates = [
            card.id
            for card in db.values()
            if GameTag.TECH_LEVEL in card.tags
            and all(op(getattr(card, key), value) for key, op, value in conditions)
        ]

        if not candidates:
            return None

        return choice(candidates)

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
        return Card.fromid(self.game, child_card_id)

    @property
    def enchantments(self):
        return [
            entity
            for entity in self.game.entities
            if entity.tags.get(GameTag.ATTACHED) == self.id
        ]

    @property
    def enemy_minions(self) -> List["Card"]:
        return self.controller.opponent.minions

    @property
    def friendly_minions(self) -> List["Card"]:
        return self.controller.minions

    @property
    def health(self):
        return self.tags[GameTag.HEALTH] - self.tags.get(GameTag.DAMAGE, 0)

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


class Enchantment(Card):
    def __repr__(self):
        return f"{self.name}"

    @property
    def attached(self):
        return self.game._entities[self.tags[GameTag.ATTACHED]]
