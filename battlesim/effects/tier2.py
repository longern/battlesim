from ..actions import *


class HarvestGolem:
    def deathrattle(self):
        summon(Card.fromid(471, controller=self.controller))


class KaboomBot:
    def deathrattle(self):
        deal_damage(4, choice(self.enemy_minions))
