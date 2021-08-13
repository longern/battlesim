import logging
from collections import Counter
from copy import deepcopy

from hearthstone import enums
from hearthstone.cardxml import load

from battlesim.simulator.state import GameState, g
from battlesim.tracker.exporter import GameStateExporter

from ..simulator.battle import battle
from .logfile import LogStream, get_log_path
from .parser import BattlegroundParser

db, _ = load(locale="zhCN")
logging.getLogger().setLevel(logging.ERROR)


def card_repr(card) -> str:
    return "%s%d/%d" % (
        db[card.card_id].name,
        getattr(card, "atk", 0),
        card.health - getattr(card, "damage", 0),
    )


def combat_callback(parser: BattlegroundParser):
    exporter = GameStateExporter(parser.games[-1])
    gs: GameState = getattr(exporter.export(), "game_state", None)

    gs.entities = {
        entity_id: entity
        for entity_id, entity in gs.entities.items()
        if entity.zone.name != "REMOVEDFROMGAME"
    }

    g.set(gs)
    print(gs)


def main():
    parser = BattlegroundParser({"combat": combat_callback})
    parser.read(LogStream(get_log_path()))


if __name__ == "__main__":
    main()
