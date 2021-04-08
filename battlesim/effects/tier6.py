from battlesim.minion_types import MinionType
from ..minion_types import MinionType
from ..card import Card, choice, after, whenever


class DreadAdmiralEliza(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        if self.controller is this.controller and this in MinionType.Pirate:
            for minion in self.friendly_minions:
                minion.gain(2 * self.tip, self.tip)


class FoeReaper4000(Card):
    @after(Card.attack)
    def effect(self, this, defender):
        """Also damages the minions next to whomever this attacks."""
        if self is this:
            for minion in defender.adjacent_minions:
                self.deal_damage(self.atk, minion)


class GentleDjinni(Card):
    def deathrattle(self):
        """Summon another random Elemental and add a copy of it to your hand."""


class GoldrinnTheGreatWolf(Card):
    def deathrattle(self):
        for minion in self.friendly_minions | MinionType.Beast:
            minion.gain(5 * self.tip, 5 * self.tip)


class NadinaTheRed(Card):
    def deathrattle(self):
        for minion in self.friendly_minions | MinionType.Dragon:
            minion.divine_shield = True
