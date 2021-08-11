import logging
from collections import Counter
from copy import deepcopy

from hearthstone import enums
from hearthstone.cardxml import load

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
    game = parser.export_game()
    turn = game.turn // 2
    print(f"Combat of turn {turn} starts.")

    friendly_minions = game.players[0].minions
    print(" ".join(map(card_repr, friendly_minions)))

    enemy_minions = game.players[1].minions
    print(" ".join(map(card_repr, enemy_minions)))

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
