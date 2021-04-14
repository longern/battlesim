from hearthstone.enums import Race
from ..minion_types import Race
from ..entities import Card, choice, after, whenever


class DreadAdmiralEliza(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        if self.controller is this.controller and this in Race.Pirate:
            for minion in self.friendly_minions:
                minion.gain(2 * self.tip, self.tip)


class FoeReaper4000(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        """Also damages the minions next to whomever this attacks."""
        if self is this:
            for minion in defender.adjacent_minions:
                self.deal_damage(self.atk, minion)


class GentleDjinni(Card):
    def deathrattle(self):
        """Summon another random Elemental and add a copy of it to your hand."""


class Ghastcoiler(Card):
    def deathrattle(self):
        for _ in range(2 * self.tip):
            self.summon(
                Card.random(mechanics__contains="DEATHRATTLE", cardtype="MINION")
            )


class GoldrinnTheGreatWolf(Card):
    def deathrattle(self):
        for minion in self.friendly_minions | Race.Beast:
            minion.gain(5 * self.tip, 5 * self.tip)


class ImpMama(Card):
    @whenever(Card.deal_damage)
    def effect(self, this, amount, card):
        if self is card:
            random_demon = Card.random(race="DEMON")
            self.summon(random_demon)
            random_demon.taunt = True


class NadinaTheRed(Card):
    def deathrattle(self):
        for minion in self.friendly_minions | Race.Dragon:
            minion.divine_shield = True


class TheTideRazor(Card):
    def deathrattle(self):
        for _ in range(3 * self.tip):
            self.summon(Card.random(race="PIRATE"))
