from hearthstone.enums import Race

from ..entities import Minion, after, choice, whenever


class IronhideDirehorn(Minion):
    def overkill(self):
        self.summon(self.child_card())


class KingBagurgle(Minion):
    def battlecry(self):
        """Battlecry and Deathrattle: Give your other Murlocs +2/+2."""
        for minion in self.friendly_minions | self.other | Race.MURLOC:
            minion.gain(2, 2)

    deathrattle = battlecry


class Malganis(Minion):
    def aura(self):
        """Your other Demons have +2/+2. Your hero is Immune."""


class MamaBear(Minion):
    @whenever(Minion.summon)
    def effect(self, this, card, before=None):
        if self.controller == card.controller and card in Race.BEAST:
            card.gain(4 * self.tip, 4 * self.tip)


class SeabreakerGoliath(Minion):
    def overkill(self):
        """Overkill: Give your other Pirates +2/+2."""
        for minion in self.friendly_minions | self.other | Race.PIRATE:
            minion.gain(2 * self.tip, 2 * self.tip)


class SneedsOldShredder(Minion):
    def deathrattle(self):
        # Summon a random Legendary minion.
        self.summon(Minion.random(type="MINION", rarity="LEGENDARY"))


class Voidlord(Minion):
    normal_child = "CS2_065"

    def deathrattle(self):
        # Summon three 1/3 Demons with Taunt.
        for _ in range(3):
            self.summon(self.child_card())
