#!/usr/bin/env python3
import random
from itertools import cycle
from typing import List
from functools import cached_property

from .card import Card
from .keywords import *
from .actions import *


class Player:
    def __init__(self, game):
        self.game = game
        self.hero = None
        self.minions: List[Card] = []
        self.active_minion = None

    @property
    def first_minion(self):
        return next(iter(self.minions), None)

    @property
    def has_attackable_minions(self):
        return any(minion.attack > 0 for minion in self.minions)

    @cached_property
    def opponent(self):
        return next(filter(lambda player: player is not self, self.game.players), None)


class Game:
    def __init__(self):
        self.players = [Player(self), Player(self)]

    @property
    def minions(self):
        for player in self.players:
            yield from player.minions


def check_death(game: Game):
    for player in game.players:
        for minion in player.minions[:]:
            if minion.health <= 0 or minion.poisoned:
                minion_index = player.minions.index(minion)
                player.minions.remove(minion)
                die(minion)
                if player.active_minion == minion:
                    if minion_index >= len(player.minions):
                        player.active_minion = player.first_minion
                    else:
                        player.active_minion = player.minions[minion_index]


def battle(game: Game):
    for player in game.players:
        for minion in player.minions:
            if hasattr(minion, "start_of_combat"):
                minion.start_of_combat()

    for player in game.players:
        player.active_minion = next(iter(player.minions), None)

    current_player_iter = cycle(game.players)
    if len(game.players[1].minions) > len(game.players[0].minions) + random.uniform(
        -0.1, 0.1
    ):
        next(current_player_iter)

    while any(player.has_attackable_minions for player in game.players):
        current_player = next(current_player_iter)
        opponent = next(filter(lambda player: player != current_player, game.players))
        attack(current_player.active_minion)
        check_death(game)

        if any(not player.minions for player in game.players):
            break

        next_active_minion_index = (
            current_player.minions.index(current_player.active_minion) + 1
        )
        if next_active_minion_index >= len(current_player.minions):
            next_active_minion_index = 0
        current_player.active_minion = current_player.minions[next_active_minion_index]

    return bool(game.players[0].minions) - bool(game.players[1].minions)


def parse_battlefield(player_minions_stats) -> Game:
    game = Game()
    for player, minions_stats in zip(game.players, player_minions_stats):
        for attack, health, *args in minions_stats:
            if args and isinstance(args[0], int):
                card_id = args.pop(0)
                minion = Card.fromid(
                    card_id, attack=attack, health=health, controller=player
                )
            else:
                minion = Card(attack=attack, health=health, controller=player)
            for arg in filter(lambda arg: issubclass(arg, Keyword), args):
                setattr(minion, arg.as_attribute(), True)
            player.minions.append(minion)

    return game
