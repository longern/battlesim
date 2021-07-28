import logging
import time

from battlesim.bot.actions import tier_up
from hearthstone.cardxml import load
from hearthstone.enums import CardType, Zone

from ..tracker.logfile import follow, get_log_path
from ..tracker.parser import BattlegroundParser
from .actions import *

db, _ = load(locale="zhCN")
logging.getLogger().setLevel(logging.ERROR)


def choose_hero_callback(parser: BattlegroundParser):
    time.sleep(10)
    choose_hero(1)


def idle_callback(parser: BattlegroundParser):
    game = parser.export_game()
    turn = (game.turn + 1) // 2
    coins_remained = game.players[0].resources - getattr(
        game.players[0], "resources_used", 0
    )
    minions_in_battlefield = sorted(
        filter(
            lambda entity: entity.zone == Zone.PLAY
            and getattr(entity, "cardtype", None) == CardType.MINION
            and getattr(entity, "controller", None) == game.players[0].player_id,
            game.entities.values(),
        ),
        key=lambda entity: entity.zone_position,
    )
    minions_in_tavern = sorted(
        filter(
            lambda entity: entity.zone == Zone.PLAY
            and getattr(entity, "cardtype", None) == CardType.MINION
            and getattr(entity, "controller", None) == game.players[1].player_id,
            game.entities.values(),
        ),
        key=lambda entity: entity.zone_position,
    )
    print(
        turn,
        coins_remained,
        minions_in_battlefield,
        minions_in_tavern,
    )

    if turn in [2, 5] and coins_remained == turn + 2:
        tier_up()

    if coins_remained >= 3:
        buy_minion(0, len(minions_in_battlefield))


def main():
    parser = BattlegroundParser(
        {"idle": idle_callback, "choose_hero": choose_hero_callback}
    )
    parser.read(follow(get_log_path()))


if __name__ == "__main__":
    main()
