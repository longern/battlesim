from battlesim.minion_types import MinionType
from ..minion_types import MinionType
from ..card import Card, choice, after, whenever


class DreadAdmiralEliza(Card):
    @whenever(Card.attack)
    def effect(self, this, defender=None):
        if self.controller is this.controller and this in MinionType.Pirate:
            for minion in self.friendly_minions:
                minion.attack_power += 2
                minion.health += 1


class GoldrinnTheGreatWolf(Card):
    def deathrattle(self):
        for minion in self.friendly_minions | MinionType.Beast:
            minion.attack_power += 5
            minion.health += 5


class NadinaTheRed(Card):
    def deathrattle(self):
        for minion in self.friendly_minions | MinionType.Dragon:
            minion.divine_shield = True
