#!/usr/bin/env python3
import random
from itertools import cycle
from collections import defaultdict

from hearthstone.entities import Entity, Game, Card as BaseCard
from hearthstone.enums import CardType, GameTag, Zone

from . import entities


def check_death(game: Game):
    for entity in game.entities:
        if GameTag.HEALTH in entity.tags and entity.tags[
            GameTag.HEALTH
        ] <= entity.tags.get(GameTag.DAMAGE, 0):
            import pdb

            pdb.set_trace()


def extend_entities(game: Game):
    game.dispatcher = defaultdict(list)
    for entity in game.entities:
        class_name = "".join(map(str.capitalize, entity.type.name.split("_")))
        entity.__class__ = getattr(entities, class_name)


def battle(game: Game):
    extend_entities(game)

    friendly_minion_num = len(game.players[0].minions)
    enemy_minion_num = len(game.players[1].minions)
    current_player_iter = cycle(game.players)
    if enemy_minion_num > friendly_minion_num + random.uniform(-0.1, 0.1):
        next(current_player_iter)

    for entity in game.entities:
        if GameTag.START_OF_COMBAT in entity.tags:
            pass

    game.dispatcher["after_attack"].append((game, lambda *_: check_death(game)))

    check_death(game)

    attackable = lambda minion: minion.num_attacks_this_turn < 1 and minion.atk > 0

    while any(filter(attackable, game.filter(cardtype=CardType.MINION))) and all(
        player.minions for player in game.players
    ):
        import pdb

        pdb.set_trace()
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
                minion = entities.Minion.fromid(minion_stat)
            else:
                attack, health, *args = minion_stat
                if args and isinstance(args[0], str):
                    card_id = args.pop(0)
                    minion = entities.Minion.fromid(card_id, atk=attack, health=health)
                else:
                    minion = entities.Minion(atk=attack, health=health)
                for arg in args:
                    if isinstance(arg, str):
                        enchantment = entities.Enchantment.fromid(arg)
                        minion.enchantments.append(enchantment)
                        enchantment.attached = minion
                    elif issubclass(arg, GameTag):
                        minion.tag_change(arg, True)
            minion.game = game
            for entity in (minion, *minion.enchantments):
                if hasattr(entity, "effect"):
                    game.dispatcher[minion.effect.condition].append(
                        (minion, entity.effect)
                    )

    return game
