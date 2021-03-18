from .card import Card
from .event import register_action
from random import choice, randrange


@register_action
def attack(attacker, defender):
    deal_damage(attacker.attack, defender, source=attacker)
    deal_damage(defender.attack, attacker, source=defender)


@register_action
def deal_damage(amount: int, card: Card, source=None):
    if amount <= 0:
        return

    if card.divine_shield:
        card.divine_shield = False
        return

    card.health -= amount

    if card.health < 0 and hasattr(source, "overkill"):
        source.overkill()

    if isinstance(source, Card) and source.poisonous:
        card.poisoned = True


@register_action
def die(card: Card):
    trigger_deathrattle(card)


@register_action
def summon(card: Card, before=None):
    if not card:
        return

    if before in card.controller.minions:
        card.controller.minions.insert(card, card.controller.minions.index(before))
    else:
        card.controller.minions.append(card)


@register_action
def trigger_deathrattle(card: Card):
    if hasattr(card, "deathrattle") and callable(card.deathrattle):
        card.deathrattle()
