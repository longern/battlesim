#!/usr/bin/env python3
import random
from itertools import cycle
from collections import defaultdict

from .entities import Game, Player, Card
from hearthstone.enums import CardType, GameTag, Zone

from . import entities


def check_death(game: Game):
    for entity in list(game.entities):
        if GameTag.HEALTH in entity.tags and entity.tags[
            GameTag.HEALTH
        ] <= entity.tags.get(GameTag.DAMAGE, 0):
            try:
                entity.index = entity.controller.minions.index(entity)
                entity.tags[GameTag.ZONE] = Zone.GRAVEYARD
                entity.die()
            except ValueError:
                pass


def extend_entities(game: Game):
    game.dispatcher = defaultdict(list)
    for entity in game.entities:
        class_name = "".join(map(str.capitalize, entity.type.name.split("_")))
        entity.__class__ = getattr(entities, class_name)


def battle(game: Game):
    if not isinstance(game, Game):
        extend_entities(game)

    friendly_minion_num = len(game.players[0].minions)
    enemy_minion_num = len(game.players[1].minions)
    current_player_iter = cycle(game.players)
    if enemy_minion_num > friendly_minion_num + random.uniform(-0.1, 0.1):
        next(current_player_iter)

    for entity in game.entities:
        if GameTag.START_OF_COMBAT in entity.tags:
            entity.start_of_combat()

    game.dispatcher["after_attack"].append((game, lambda *_: check_death(game)))

    check_death(game)

    attackable = lambda minion: minion.num_attacks_this_turn < 1 and minion.atk > 0
    while any(filter(attackable, game.filter(cardtype=CardType.MINION))) and all(
        player.minions for player in game.players
    ):
        current_player = next(current_player_iter)
        try:
            active_minion: entities.Minion = next(
                filter(attackable, current_player.minions)
            )
        except StopIteration:
            for minion in current_player.minions:
                minion.tags[GameTag.NUM_ATTACKS_THIS_TURN] = 0
            active_minion = next(filter(attackable, current_player.minions), None)
            if active_minion is None:
                continue
        active_minion.attack()

        if active_minion.windfury and active_minion in current_player.minions:
            active_minion.attack()

        active_minion.tags.setdefault(GameTag.NUM_ATTACKS_THIS_TURN, 0)
        active_minion.tags[GameTag.NUM_ATTACKS_THIS_TURN] += 1

    return bool(game.players[0].minions) - bool(game.players[1].minions)


def parse_battlefield(player_minions_stats) -> Game:
    game = Game(1)
    game.register_entity(Player(2, 1, 1, 1))
    game.register_entity(Player(3, 9, 0, 0))

    for player in game.players:
        player.game = game

    for player, minions_stats in zip(game.players, player_minions_stats):
        for minion_stat in minions_stats:
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
                        id(minion_stat),
                        str(hash(minion_stat)),
                        atk=attack,
                        health=health,
                    )
                for arg in args:
                    if isinstance(arg, str):
                        enchantment = entities.Enchantment.fromid(game, arg)
                        enchantment.tags[GameTag.ATTACHED] = minion.id
                    elif isinstance(arg, GameTag):
                        minion.tag_change(arg, True)
            game.register_entity(minion)
            minion.tags[GameTag.CONTROLLER] = player.player_id
            minion.tags[GameTag.ZONE] = Zone.PLAY
            for entity in (minion, *minion.enchantments):
                if hasattr(entity, "effect"):
                    game.dispatcher[minion.effect.condition].append(
                        (minion, entity.effect)
                    )

    return game
