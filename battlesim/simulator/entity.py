from functools import lru_cache
from typing import List, Type

from hearthstone.enums import CardType, Zone


class Entity:
    pass


class Game(Entity):
    turn: int


class Player(Entity):
    player_id: int

    @property
    def minions(self) -> List["Minion"]:
        from .state import g

        return sorted(
            filter(
                lambda entity: entity.cardtype == CardType.MINION
                and entity.zone == Zone.PLAY
                and entity.controller == self.player_id,
                g.get().entities.values(),
            ),
            key=lambda minion: minion.zone_position,
        )


class Hero(Entity):
    health: int


class Minion(Entity):
    atk = 0
    damage = 0
    health: int


@lru_cache(maxsize=16)
def get(cardtype: CardType) -> Type[Entity]:
    if not isinstance(cardtype, CardType):
        return Entity

    cls_name = "".join(map(str.capitalize, cardtype.name.split("-")))
    return globals().get(cls_name, Entity)
