import os
import time
import re

from .card import Card
from .battle import Game, battle
from copy import deepcopy
from collections import Counter


def follow(filepath: str):
    while not os.path.exists(filepath):
        time.sleep(0.1)
    with open(filepath) as file:
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)  # Sleep briefly
                continue
            yield line


def simulate_combat(friendly_minions, enemy_minions):
    result_counter = Counter({1: 0, 0: 0, -1: 0})
    for _ in range(1000):
        game = Game()
        game.players[0].minions = deepcopy(friendly_minions)
        for minion in game.players[0].minions:
            minion.controller = game.players[0]
        game.players[1].minions = deepcopy(enemy_minions)
        for minion in game.players[1].minions:
            minion.controller = game.players[1]
        result_counter[battle(game)] += 1
    print({k: f"{round(v / 1000 * 100, 2)}%" for k, v in result_counter.items()})


def combat_round(line_iter):
    player_id = 0
    while True:
        line = next(line_iter)
        player_id_match = re.search(
            "Player EntityID=\d+ PlayerID=(\d+) GameAccountId=\[hi=\d\d+ lo=\d\d+\]",
            line,
        )
        turn_match = re.search("tag=TURN value=(\d*[02468])\s", line)
        if player_id_match:
            player_id = int(player_id_match.group(1))
        elif turn_match:
            turn = int(turn_match.group(1))
            print(f"Combat of turn {turn // 2} starts.")
            while not re.search(
                "TAG_CHANGE.*TB_BaconShop_8p_Reroll_Button.*value=REMOVEDFROMGAME",
                next(line_iter),
            ):
                pass
            entities = {}
            while True:
                line = next(line_iter)
                full_entity_match = re.search(
                    "FULL_ENTITY - Creating ID=(\d+) CardID=([\S]+)", line
                )
                tag_change_match = re.search(
                    "TAG_CHANGE Entity=(\d+) tag=(\S+) value=(\S+)",
                    line,
                )
                main_ready_match = re.search(
                    "TAG_CHANGE Entity=GameEntity tag=(NEXT_)?STEP value=MAIN_START_TRIGGER",
                    line,
                )
                if full_entity_match:
                    entity_id, card_id = full_entity_match.groups()
                    card = Card.fromid(card_id)
                    while True:
                        line = next(line_iter)
                        controller_match = re.search("tag=CONTROLLER value=(\d+)", line)
                        if controller_match:
                            card.controller = int(controller_match.group(1))
                            break
                    if card.cardtype == "MINION":
                        entities[int(entity_id)] = card
                elif tag_change_match:
                    entity_id, tag, value = tag_change_match.groups()
                    if int(entity_id) in entities and not tag.isdigit():
                        setattr(
                            entities[int(entity_id)],
                            tag.lower(),
                            int(value) if value.isdigit() else value,
                        )
                elif main_ready_match:
                    print(
                        [
                            entity
                            for entity in entities.values()
                            if entity.controller == player_id
                        ]
                    )
                    print(
                        [
                            entity
                            for entity in entities.values()
                            if entity.controller == player_id + 8
                        ],
                    )
                    simulate_combat(
                        [
                            entity
                            for entity in entities.values()
                            if entity.controller == player_id
                        ],
                        [
                            entity
                            for entity in entities.values()
                            if entity.controller == player_id + 8
                        ],
                    )
                    print(f"Combat of turn {turn // 2} ends.")
                    break


def read_log():
    log_path = "/mnt/c/Program Files (x86)/Hearthstone/Logs/Power.log"
    line_iter = filter(lambda line: "GameState." in line, follow(log_path))
    combat_round(line_iter)


read_log()
