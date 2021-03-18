from ..actions import *


class FiendishServant:
    def deathrattle(self):
        choice(self.friendly_minions).attack += self.attack


class RedWhelp:
    def start_of_combat(self):
        amount = len(
            minion for minion in self.friendly_minions if minion.minion_type == 24
        )
        deal_damage(amount, choice(self.enemy_minions))
