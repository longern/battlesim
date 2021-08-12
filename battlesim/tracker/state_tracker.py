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
    game = gs.game
    turn = game.turn // 2
    print(gs)

    result_counter = Counter({1: 0, 0: 0, -1: 0})
    for _ in range(1000):
        result_counter[battle(deepcopy(game))] += 1

    print(result_counter)

    print(f"Combat of turn {turn} ends.")


def main():
    parser = BattlegroundParser({"combat": combat_callback})
    parser.read(LogStream(get_log_path()))


if __name__ == "__main__":
    main()
