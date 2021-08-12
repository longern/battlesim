from contextvars import ContextVar
from functools import cached_property
from typing import Dict, List

from hearthstone.enums import CardType

from .entity import Entity, Game, Player, Minion


class GameState:
    def __init__(self):
        self.entities: Dict[int, "Entity"] = {}

    def __repr__(self):
        from hearthstone.cardxml import load

        db, _ = load(locale=locale.get())

        def minion_repr(card: Minion):
            return "%s%d/%d" % (
                db[card.card_id].name,
                card.atk,
                card.health - card.damage,
            )

        state_repr = "Turn %d\n" % self.game.turn
        friendly_minions = self.players[0].minions
        state_repr += " ".join(map(minion_repr, friendly_minions))
        state_repr += "\n"

        enemy_minions = self.players[1].minions
        state_repr += " ".join(map(minion_repr, enemy_minions))
        
        return state_repr

    @classmethod
    def from_pandas(cls, dfs: Dict):
        pass

    @cached_property
    def game(self) -> Game:
        return next(
            entity
            for entity in self.entities.values()
            if entity.cardtype == CardType.GAME
        )

    @cached_property
    def players(self) -> List[Player]:
        return [
            entity
            for entity in self.entities.values()
            if entity.cardtype == CardType.PLAYER
        ]

    def to_pandas(self):
        import pandas as pd

        return {
            "game": pd.DataFrame.from_dict(vars(self.game)),
            "players": pd.DataFrame([vars(player) for player in self.players.values()]),
            "cards": pd.DataFrame([vars(entity) for entity in self.entities.values()]),
        }


g: ContextVar[GameState] = ContextVar("g")
locale: ContextVar[str] = ContextVar("locale", default="zhCN")
