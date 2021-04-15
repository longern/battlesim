import logging
from collections import Counter

from hearthstone import enums
from hearthstone.cardxml import load

from ..simulator.battle import battle
from .logfile import follow, get_log_path
from .parser import BattlegroundParser

db, _ = load(locale="zhCN")
logging.getLogger().setLevel(logging.ERROR)


def card_repr(card) -> str:
    return "%s%d/%d" % (
        db[card.card_id].name,
        card.tags.get(enums.GameTag.ATK),
        card.tags.get(enums.GameTag.HEALTH) - card.tags.get(enums.GameTag.DAMAGE, 0),
    )


def combat_callback(parser: BattlegroundParser):
    game = parser.export_game()
    turn = game.tags[enums.GameTag.TURN] // 2
    print(f"Combat of turn {turn} starts.")

    in_play_minions_filter = (
        lambda entity: entity.zone is enums.Zone.PLAY
        and entity.type is enums.CardType.MINION
    )

    friendly_minions = sorted(
        filter(in_play_minions_filter, game.players[0].entities),
        key=lambda card: card.tags.get(enums.GameTag.ZONE_POSITION),
    )
    print(" ".join(map(card_repr, friendly_minions)))

    enemy_minions = sorted(
        filter(in_play_minions_filter, game.players[1].entities),
        key=lambda card: card.tags.get(enums.GameTag.ZONE_POSITION),
    )
    print(" ".join(map(card_repr, enemy_minions)))

    result_counter = Counter({1: 0, 0: 0, -1: 0})
    for _ in range(1000):
        game = parser.export_game()
        result_counter[battle(game)] += 1

    print(result_counter)

    print(f"Combat of turn {turn} ends.")


def main():
    parser = BattlegroundParser(combat_callback)
    parser.read(follow(get_log_path()))


if __name__ == "__main__":
    main()
