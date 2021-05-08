#!/usr/bin/env python3
import random
from collections import defaultdict
from itertools import cycle

from hearthstone.cardxml import load
from hearthstone.enums import CardType, GameTag, Zone

from . import entities
from .entities import Card, Game, Player


def check_death(game: Game):
    while game.to_check_death:
        to_check_death = game.to_check_death.copy()
        game.to_check_death.clear()
        for card in to_check_death:
            if card.health <= card.damage:
                try:
                    card.index = card.controller_entity.minions.index(card)
                    card.zone = Zone.GRAVEYARD
                    del card.controller_entity.minions
                    card.die()
                except ValueError:
                    pass


def battle(game: Game):
    friendly_minion_num = len(game.players[0].minions)
    enemy_minion_num = len(game.players[1].minions)
    current_player_iter = cycle(game.players)
    if enemy_minion_num > friendly_minion_num + random.uniform(-0.1, 0.1):
        next(current_player_iter)

    game.dispatcher["after_attack"].append((game, lambda *_: check_death(game)))

    for entity in game.entities:
        if callable(getattr(entity, "start_of_combat", None)):
            entity.start_of_combat()

    check_death(game)

    attackable = lambda minion: minion.num_attacks_this_turn < 1 and minion.atk > 0
    while all(player.minions for player in game.players):
        current_player = next(current_player_iter)
        try:
            active_minion: entities.Minion = next(
                filter(attackable, current_player.minions)
            )
        except StopIteration:
            for minion in current_player.minions:
                minion.num_attacks_this_turn = 0
            active_minion = next(filter(attackable, current_player.minions), None)
            if active_minion is None:
                continue
        active_minion.attack()

        if (
            getattr(active_minion, "windfury", False)
            and active_minion in current_player.minions
        ):
            active_minion.attack()

        active_minion.num_attacks_this_turn += 1

    return bool(game.players[0].minions) - bool(game.players[1].minions)


def parse_battlefield(player_minions_stats) -> Game:
    game = Game(entity_id=1)
    game.entities[1] = game
    game.register_entity(Player(player_id=1, cardtype=CardType.PLAYER))
    game.register_entity(Player(player_id=9, cardtype=CardType.PLAYER))

    for player, minions_stats in zip(game.players, player_minions_stats):
        for i, minion_stat in enumerate(minions_stats):
            if isinstance(minion_stat, str):
                minion = entities.Minion.fromid(game, minion_stat)
            else:
                attack, health, *args = minion_stat
                if args and isinstance(args[0], str):
                    card_id = args.pop(0)
                    minion = entities.Minion.fromid(
                        game, card_id, atk=attack, health=health
                    )
                else:
                    minion = entities.Minion(
                        atk=attack, health=health, cardtype=CardType.MINION
                    )
                for arg in args:
                    if isinstance(arg, str):
                        enchantment = entities.Enchantment.fromid(game, arg)
                        enchantment.attached = minion.entity_id
                        if callable(getattr(enchantment, "on_attached", None)):
                            enchantment.on_attached()
                    elif isinstance(arg, GameTag):
                        setattr(minion, arg.name.lower(), True)
            game.register_entity(minion)
            minion.controller = player.player_id
            minion.zone = Zone.PLAY
            minion.zone_position = i + 1
            for entity in (minion, *minion.enchantments):
                if hasattr(entity, "effect"):
                    game.dispatcher[minion.effect.condition].append(
                        (minion, entity.effect)
                    )

    return game
