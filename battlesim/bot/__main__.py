from battlesim.tracker.exporter import SimulatorExporter
import logging
import os
import time

import pyautogui
from PIL.Image import Image
from battlesim.bot.actions import tier_up
from hearthstone.cardxml import load
from hearthstone.enums import CardType, Zone

from ..tracker.logfile import LogStream, get_log_path
from ..tracker.parser import BattlegroundParser
from .actions import *

db, _ = load(locale="zhCN")
logging.getLogger().setLevel(logging.ERROR)
FREEZE_ENABLED_PATH = os.path.join(os.path.dirname(__file__), "freeze_enabled.png")

log_stream = LogStream(get_log_path())


def is_controllable(im: Image) -> bool:
    green = 0
    for pixel in im.getdata():
        if pixel[1] >= 250 and pixel[0] < 127 and pixel[2] < 127:
            green += 1
    return green >= 20


def choose_hero_callback(parser: BattlegroundParser):
    if not log_stream.last_line:
        return

    time.sleep(10)
    choose_hero(1)


def idle_callback(parser: BattlegroundParser):
    if not log_stream.last_line:
        return

    game = parser.export_game()
    turn = (game.turn + 1) // 2
    coins_remained = (
        game.players[0].resources
        - getattr(game.players[0], "resources_used", 0)
        + getattr(game.players[0], "temp_resources", 0)
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
    cards_in_hand = sorted(
        filter(
            lambda entity: entity.zone == Zone.HAND
            and getattr(entity, "controller", None) == game.players[0].player_id,
            game.entities.values(),
        ),
        key=lambda entity: entity.zone_position,
    )
    print(
        turn,
        coins_remained,
        minions_in_battlefield,
        minions_in_tavern,
        cards_in_hand,
    )

    if coins_remained == min(10, turn + 2):
        # Wait for recruit phrase
        while True:
            im = pyautogui.screenshot(region=(1195, 120, 90, 120))
            if is_controllable(im):
                break
            time.sleep(0.5)

        if turn == 1:
            time.sleep(5)

    if len(cards_in_hand) and len(minions_in_battlefield) < 7:
        play_card(0, len(cards_in_hand))
        return

    if turn in [2, 5, 7, 8] and coins_remained == turn + 2:
        tier_up()
        return

    if turn == 3 and coins_remained == turn + 2:
        sell_minion(0, len(minions_in_battlefield))

    if coins_remained >= 3:
        minion_to_buy = max(
            range(len((minions_in_tavern))),
            key=lambda index: getattr(minions_in_tavern[index], "tech_level", 1),
        )
        if turn == 1:
            priority = ["EX1_506", "BGS_115", "CFM_315"]
            minion_to_buy = max(
                range(len((minions_in_tavern))),
                key=lambda index: priority.index(minions_in_tavern[index].card_id)
                if minions_in_tavern[index].card_id in priority
                else -1,
            )
        buy_minion(minion_to_buy, len(minions_in_tavern))
        return


def main():
    parser = BattlegroundParser(
        {"idle": idle_callback, "choose_hero": choose_hero_callback}
    )
    parser.read(log_stream)


if __name__ == "__main__":
    main()
