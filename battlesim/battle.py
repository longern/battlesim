#!/usr/bin/env python3
import random
from itertools import cycle
from typing import List

from .keywords import *


class Card:
    def __init__(self):
        self.name = "Unknown"
        self.divine_shield = False
        self.poisoned = False
        self.revive = False
        self.taunt = False

    def __repr__(self):
        return f"<Card({self.name}, {self.attack}, {self.health})>"


class Player:
    def __init__(self):
        self.hero = None
        self.minions: List[Card] = []
        self.active_minion = None

    @property
    def first_minion(self):
        return next(iter(self.minions), None)


def has_attackable_minions(player: Player):
    return any(minion.attack > 0 for minion in player.minions)


def deal_damage(amount: int, card):
    if amount <= 0:
        return

    if card.divine_shield:
        card.divine_shield = False
        return

    card.health -= amount


def attack(attacker, defender):
    deal_damage(attacker.attack, defender)
    deal_damage(defender.attack, attacker)


def pick_attacked_target(minions):
    if any(minion.taunt for minion in minions):
        minions = [minion for minion in minions if minion.taunt]
    return random.choice(minions)


def check_death(players: List[Player]):
    for player in players:
        for minion in player.minions[:]:
            if minion.health <= 0 or minion.poisoned:
                minion_index = player.minions.index(minion)
                player.minions.remove(minion)
                if player.active_minion == minion:
                    if minion_index >= len(player.minions):
                        player.active_minion = player.first_minion
                    else:
                        player.active_minion = player.minions[minion_index]


def battle(players: List[Player]):
    for player in players:
        for minion in player.minions:
            # minion.start_of_combat()
            pass

    for player in players:
        player.active_minion = next(iter(player.minions), None)

    current_player_iter = cycle(players)
    if len(players[1].minions) > len(players[0].minions) + random.uniform(-0.1, 0.1):
        next(current_player_iter)

    while any(has_attackable_minions(player) for player in players):
        current_player = next(current_player_iter)
        opponent = next(filter(lambda player: player != current_player, players))
        attack(current_player.active_minion, pick_attacked_target(opponent.minions))
        check_death(players)

        if any(not player.minions for player in players):
            break

        next_active_minion_index = (
            current_player.minions.index(current_player.active_minion) + 1
        )
        if next_active_minion_index >= len(current_player.minions):
            next_active_minion_index = 0
        current_player.active_minion = current_player.minions[next_active_minion_index]

    return bool(players[0].minions) - bool(players[1].minions)


def parse_battlefield(*player_minions_stats):
    players = []
    for minions_stats in player_minions_stats:
        player = Player()
        for attack, health, *args in minions_stats:
            minion = Card()
            minion.attack = attack
            minion.health = health
            for arg in filter(lambda arg: issubclass(arg, Keyword), args):
                    setattr(minion, arg.as_attribute(), True)
            player.minions.append(minion)
        players.append(player)

    return players


battlefield_data = [(1, 1, DivineShield)], [(1, 1)]
battlefield = parse_battlefield(*battlefield_data)
from collections import Counter

c = Counter(battle(parse_battlefield(*battlefield_data)) for _ in range(10000))
print(c)
