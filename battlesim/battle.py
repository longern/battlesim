#!/usr/bin/env python3
from battlesim.effects import enchantments
import random
from collections import defaultdict
from functools import cached_property
from itertools import cycle
from typing import List

from .card import Card
from .keywords import *


class Player:
    def __init__(self, game):
        self.game = game
        self.hero = None
        self.hero_power = None
        self.minions: List[Card] = []
        self.active_minion = None

    @property
    def first_minion(self):
        return next(iter(self.minions), None)

    @property
    def has_attackable_minions(self):
        return any(minion.atk > 0 for minion in self.minions)

    @cached_property
    def opponent(self):
        return next(filter(lambda player: player is not self, self.game.players), None)

    def __repr__(self):
        return repr(self.minions)


class Game:
    def __init__(self):
        self.players = [Player(self), Player(self)]
        self.dispatcher = defaultdict(list)

    @property
    def minions(self):
        for player in self.players:
            yield from player.minions

    def __repr__(self):
        return "\n".join(map(repr, self.players))


def check_death(game: Game):
    for player in game.players:
        for minion in player.minions[:]:
            if not minion.alive:
                try:
                    minion.index = player.minions.index(minion)
                    player.minions.remove(minion)
                    minion.die()
                except ValueError:
                    pass


def battle(game: Game):
    game.dispatcher["after_attack"].append((game, lambda *_: check_death(game)))

    for player in game.players:
        if hasattr(player.hero_power, "start_of_combat"):
            player.hero_power.start_of_combat()
        for minion in player.minions:
            for entity in [minion, *minion.enchantments]:
                if hasattr(entity, "start_of_combat"):
                    entity.start_of_combat()
    check_death(game)

    current_player_iter = cycle(game.players)
    if len(game.players[1].minions) > len(game.players[0].minions) + random.uniform(
        -0.1, 0.1
    ):
        next(current_player_iter)

    attackable = lambda minion: minion.num_of_attacks < 1 and minion.atk > 0

    while any(player.has_attackable_minions for player in game.players) and all(
        player.minions for player in game.players
    ):
        game.current_player = next(current_player_iter)
        try:
            active_minion = next(filter(attackable, game.current_player.minions))
        except StopIteration:
            for minion in game.current_player.minions:
                minion.num_of_attacks = 0
            active_minion = next(filter(attackable, game.current_player.minions), None)
            if active_minion is None:
                continue
        active_minion.attack()

        if (
            getattr(active_minion, "windfury", False)
            and active_minion in game.current_player.minions
        ):
            active_minion.attack()

        active_minion.num_of_attacks += 1

    return bool(game.players[0].minions) - bool(game.players[1].minions)


def parse_battlefield(player_minions_stats) -> Game:
    game = Game()
    for player, minions_stats in zip(game.players, player_minions_stats):
        for minion_stat in minions_stats:
            if isinstance(minion_stat, str):
                minion = Card.fromid(minion_stat)
            else:
                attack, health, *args = minion_stat
                if args and isinstance(args[0], str):
                    card_id = args.pop(0)
                    minion = Card.fromid(card_id, atk=attack, health=health)
                else:
                    minion = Card(atk=attack, health=health)
                for arg in args:
                    if isinstance(arg, str):
                        enchantment = Card.fromid(arg)
                        minion.enchantments.append(enchantment)
                        enchantment.attached = minion
                    elif issubclass(arg, Keyword):
                        setattr(minion, arg.as_attribute(), True)
            minion.controller = player
            player.minions.append(minion)
            for entity in (minion, *minion.enchantments):
                if hasattr(entity, "effect"):
                    game.dispatcher[minion.effect.condition].append(
                        (minion, entity.effect)
                    )

    return game
