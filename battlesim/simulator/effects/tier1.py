from hearthstone.enums import GameTag, Race

from ..battle import check_death
from ..entities import Minion, after, choice, whenever


class FiendishServant(Minion):
    def deathrattle(self):
        if self.friendly_minions:
            for _ in range(self.tip):
                choice(self.friendly_minions).tags[GameTag.ATK] += self.atk


class RedWhelp(Minion):
    def start_of_combat(self):
        amount = len(list(self.friendly_minions | Race.DRAGON))
        for _ in range(self.tip):
            self.deal_damage(amount, choice(self.enemy_minions))
            check_death(self.game)


class Scallywag(Minion):
    def deathrattle(self):
        self.summon(self.child_card())


class SkyPirate(Minion):
    """Child card of scallywag"""

    @after(Minion.summon)
    def effect(self, this, card, before=None):
        if self is card:
            self.attack()


class ScavengingHyena(Minion):
    @whenever(Minion.die)
    def effect(self, this):
        if self.controller is this.controller and this in Race.BEAST:
            self.gain(2 * self.tip, self.tip)


class SelflessHero(Minion):
    def deathrattle(self):
        candidates = [
            minion for minion in self.friendly_minions if not minion.divine_shield
        ]
        if candidates:
            choice(candidates).divine_shield = True
