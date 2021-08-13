from functools import lru_cache
from typing import List, Type

from hearthstone.enums import CardType, Race, SpellSchool, Zone

from .state import g


class Entity:
    cardtype: CardType
    controller: int
    entity_id: int
    zone: Zone

    @property
    def controller_e(self):
        players = g.get().players
        return players[0] if players[0].player_id == self.controller else players[1]


class Game(Entity):
    turn: int


class Player(Entity):
    current_player: int
    maxresources = 10
    num_options_played_this_turn: int
    player_id: int
    player_tech_level: int
    playstate: int
    resources: int
    resources_used = 0
    temp_resources = 0

    @property
    def minions(self) -> List["Minion"]:
        return sorted(
            filter(
                lambda entity: entity.cardtype == CardType.MINION
                and entity.zone == Zone.PLAY
                and entity.controller == self.player_id,
                g.get().entities.values(),
            ),
            key=lambda minion: minion.zone_position,
        )

    @property
    def opponent(self) -> "Player":
        for player in g.get().players:
            if player is not self:
                return player
        return None


class Card(Entity):
    atk = 0
    attacking = 0
    battlecry = 0
    cant_attack = 0
    damage = 0
    deathrattle = 0
    defending = 0
    dormant = 0
    exhausted = 0
    freeze = 0
    health: int
    num_attacks_this_turn = 0
    poisonous = 0
    premium = 0
    spawn_time_count = 0
    taunt = 0
    windfury = 0
    zone: Zone
    zone_position = 0


class Hero(Card):
    hero_power: int
    leaderboard: int
    next_opponent_player_id: int
    player_id: int
    player_tech_level: int


class Minion(Card):
    cardrace = Race.INVALID
    tech_level = 1


class Spell(Card):
    spell_school = SpellSchool.NONE


class Enchantment(Entity):
    attached: int

    @property
    def attached_e(self):
        return g.get().entities[self.attached]


@lru_cache(maxsize=16)
def get(cardtype: CardType) -> Type[Entity]:
    if not isinstance(cardtype, CardType):
        return Entity

    cls_name = "".join(map(str.capitalize, cardtype.name.split("-")))
    return globals().get(cls_name, Entity)
