from battlesim.minion_types import MinionType
from ..minion_types import MinionType
from ..card import Card, choice, after, whenever


class DreadAdmiralEliza(Card):
    @whenever(Card.attack)
    def effect(self, this, defender=None):
        if self.controller is this.controller and this in MinionType.Pirate:
            for minion in self.friendly_minions:
                minion.gain(2, 1)


class GentleDjinni(Card):
    def deathrattle(self):
        """Summon another random Elemental and add a copy of it to your hand."""


class GoldrinnTheGreatWolf(Card):
    def deathrattle(self):
        for minion in self.friendly_minions | MinionType.Beast:
            minion.atk += 5
            minion.health += 5


class NadinaTheRed(Card):
    def deathrattle(self):
        for minion in self.friendly_minions | MinionType.Dragon:
            minion.divine_shield = True
