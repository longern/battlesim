import logging
import operator
import re
from collections import defaultdict
from functools import lru_cache, wraps, cached_property
from typing import Any, Dict, List

from hearthstone.cardxml import load
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


class Entity:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not callable(getattr(self, key, None)) or not value:
                setattr(self, key, value)


class Game(Entity):
    turn: int

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entities: Dict[int, Entity] = {}
        self.dispatcher = defaultdict(list)
        self.to_check_death: List[Card] = []
        self.max_entity_id = 1

    def __repr__(self):
        return repr(self.players[0].minions) + "\n" + repr(self.players[1].minions)

    @cached_property
    def players(self) -> List["Player"]:
        return [
            entity
            for entity in self.entities.values()
            if getattr(entity, "cardtype", None) == CardType.PLAYER
        ]

    def register_entity(self, entity: Entity):
        entity.game = self

        if not hasattr(entity, "entity_id"):
            entity.entity_id = self.max_entity_id + 1
        self.entities[entity.entity_id] = entity
        self.max_entity_id = max(self.max_entity_id, entity.entity_id)


class Player(Entity):
    @cached_property
    def minions(self):
        return sorted(
            filter(
                lambda entity: getattr(entity, "cardtype", None) == CardType.MINION
                and entity.zone == Zone.PLAY
                and entity.controller == self.player_id,
                self.game.entities.values(),
            ),
            key=lambda minion: minion.zone_position,
        )

    @cached_property
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


class Card(Entity):
    controller: int
    cardtype: CardType
    zone: Zone

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if getattr(self, "cardtype", None) == CardType.MINION:
            self.damage = 0
            self.divine_shield = getattr(self, "divine_shield", False)
            self.num_attacks_this_turn = 0
            self.taunt = getattr(self, "taunt", False)
            self.to_be_destroyed = False

            if kwargs.get("start_with_1_health", False):
                self.damage = self.health - 1

    def __repr__(self):
        return f"{self.name}"

    @property
    def name(self):
        db, _ = load(locale="zhCN")
        try:
            return db[self.card_id].name
        except (KeyError, AttributeError):
            return getattr(self, "card_id", "?")

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
            card.health < card.damage
            and hasattr(self, "overkill")
            and getattr(self, "attacking", False)
        ):
            self.overkill()

        if isinstance(self, Card) and getattr(self, "poisonous", False):
            card.to_be_destroyed = True

        if card.health <= card.damage or card.to_be_destroyed:
            self.game.to_check_death.append(card)

    def gain(self, atk, health, permanently=False):
        self.atk += atk
        self.health += health

    @register_action
    def die(self):
        self.trigger("Deathrattle")
        if getattr(self, "reborn", False):
            new_card = Card.fromid(
                self.game, self.card_id, start_with_1_health=1, reborn=False
            )
            self.summon(new_card)

    @register_action
    def lose_divine_shield(self):
        self.divine_shield = False

    @register_action
    def summon(self, card: "Card"):
        if not card or len(self.friendly_minions) >= 7:
            return

        card.controller = self.controller
        card.zone = Zone.PLAY
        card.zone_position = getattr(self, "index", len(self.friendly_minions)) + 1
        self.friendly_minions.insert(card.zone_position - 1, card)

        for pos, minion in enumerate(self.friendly_minions, 1):
            minion.zone_position = pos

        if hasattr(card, "effect"):
            self.game.dispatcher[card.effect.condition].append((card, card.effect))

    def check_mechanics(func):
        @wraps(func)
        def wrapper(self, ability: str):
            ability = ability.lower()
            if not callable(getattr(self, ability, None)):
                return

            return func(self, ability)

        return wrapper

    @check_mechanics
    @register_action
    def trigger(self, ability: str):
        getattr(self, ability)()

    @staticmethod
    def load_effect(card_name: str, cardtype: CardType):
        # Load effect
        from . import effects

        default_cls = Minion if cardtype == CardType.MINION else Card

        words = re.sub(r"[^ 0-9A-Za-z]", "", card_name).split(" ")
        class_name = "".join(map(str.capitalize, words))
        cls = getattr(effects, class_name, default_cls)

        return cls

    @staticmethod
    def fromid(game: Game, card_id: str, **kwargs):
        try:
            db, _ = load()
            card_data = db[card_id]
        except KeyError:
            logging.error("Card %d not found.", card_id)
            return None

        for tag, value in card_data.tags.items():
            if isinstance(tag, GameTag):
                kwargs.setdefault(tag.name.lower(), value)
        kwargs.setdefault("zone", Zone.SETASIDE)

        cls = Card.load_effect(card_data.name, card_data.tags[GameTag.CARDTYPE])

        card: Card = cls(card_id=card_id, **kwargs)
        game.register_entity(card)
        return card

    def create(self, card_id: str, **kwargs):
        return Card.fromid(self.game, card_id, **kwargs)

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
        index = self.zone_position - 1
        return self.controller_entity.minions[abs(index - 1) : index + 2 : 2]

    @property
    def alive(self) -> bool:
        return self.health > self.damage and not self.to_be_destroyed

    @cached_property
    def controller_entity(self) -> Player:
        for player in self.game.players:
            if player.player_id == self.controller:
                return player
        return None

    def child_card(self) -> str:
        premium = getattr(self, "premium", False)
        if not premium and hasattr(self.__class__, "normal_child"):
            child_card_id = self.__class__.normal_child
        elif premium and hasattr(self.__class__, "premium_child"):
            child_card_id = self.__class__.premium_child
        else:
            child_card_id = infer_child_card_id(self.card_id)
        return Card.fromid(self.game, child_card_id)

    @property
    def enchantments(self):
        return [
            entity
            for entity in self.game.entities
            if getattr(entity, "attached", None) == self.entity_id
        ]

    @property
    def enemy_minions(self) -> List["Card"]:
        return self.controller_entity.opponent.minions

    @property
    def friendly_minions(self) -> List["Card"]:
        return self.controller_entity.minions

    @property
    def other(self):
        return view(lambda iterable: filter(lambda x: x is not self, iterable))

    @property
    def tip(self):
        return 2 if getattr(self, "premium", False) else 1


class Hero(Card):
    pass


class HeroPower(Card):
    pass


class Minion(Card):
    def __repr__(self):
        return f"{self.name}{self.atk}/{self.health - self.damage}"


class Enchantment(Card):
    def __repr__(self):
        return f"{self.name}"

    @property
    def attached_entity(self):
        return self.game.entities[self.attached]
