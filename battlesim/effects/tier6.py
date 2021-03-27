from ..card import Card, choice, after, whenever


class DreadAdmiralEliza(Card):
    @whenever(Card.attack)
    def effect(self, this, defender=None):
        if self.controller is this.controller and this.minion_type == 23:
            for minion in self.friendly_minions:
                minion.attack_power += 2
                minion.health += 1


class GoldrinnTheGreatWolf(Card):
    def deathrattle(self):
        for minion in self.friendly_minions:
            if minion.minion_type == 20:
                minion.attack_power += 5
                minion.health += 5


class NadinaTheRed(Card):
    def deathrattle(self):
        for minion in self.friendly_minions:
            if minion.minion_type == 24:
                minion.divine_shield = True
