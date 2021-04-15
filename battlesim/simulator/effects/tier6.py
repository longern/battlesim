from hearthstone.enums import GameTag, Race
from ..entities import Minion, choice, after, whenever


class DreadAdmiralEliza(Minion):
    @whenever(Minion.attack)
    def effect(self, this, defender):
        if self.controller is this.controller and this in Race.Pirate:
            for minion in self.friendly_minions:
                minion.gain(2 * self.tip, self.tip)


class FoeReaper4000(Minion):
    @whenever(Minion.attack)
    def effect(self, this, defender):
        """Also damages the minions next to whomever this attacks."""
        if self is this:
            for minion in defender.adjacent_minions:
                self.deal_damage(self.atk, minion)


class GentleDjinni(Minion):
    def deathrattle(self):
        """Summon another random Elemental and add a copy of it to your hand."""


class Ghastcoiler(Minion):
    def deathrattle(self):
        for _ in range(2 * self.tip):
            self.summon(
                Minion.random(mechanics__contains="DEATHRATTLE", cardtype="MINION")
            )


class GoldrinnTheGreatWolf(Minion):
    def deathrattle(self):
        for minion in self.friendly_minions | Race.Beast:
            minion.gain(5 * self.tip, 5 * self.tip)


class ImpMama(Minion):
    @whenever(Minion.deal_damage)
    def effect(self, this, amount, card):
        if self is card:
            random_demon = self.create(Minion.random(race=Race.DEMON))
            self.summon(random_demon)
            random_demon.tags[GameTag.TAUNT] = True


class NadinaTheRed(Minion):
    def deathrattle(self):
        for minion in self.friendly_minions | Race.Dragon:
            minion.divine_shield = True


class TheTideRazor(Minion):
    def deathrattle(self):
        for _ in range(3 * self.tip):
            self.summon(Minion.random(race="PIRATE"))
