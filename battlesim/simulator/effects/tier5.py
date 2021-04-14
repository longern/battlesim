from ..minion_types import Race
from ..entities import Card, choice, after, whenever


class IronhideDirehorn(Card):
    def overkill(self):
        self.summon(self.child_card())


class KingBagurgle(Card):
    def battlecry(self):
        """Battlecry and Deathrattle: Give your other Murlocs +2/+2."""
        for minion in self.friendly_minions | self.other | Race.Murloc:
            minion.atk += 2
            minion.health += 2

    deathrattle = battlecry


class Malganis(Card):
    def aura(self):
        """Your other Demons have +2/+2. Your hero is Immune."""


class MamaBear(Card):
    @whenever(Card.summon)
    def effect(self, this, card, before=None):
        if self.controller == card.controller and card in Race.Beast:
            card.gain(4 * self.tip, 4 * self.tip)


class SeabreakerGoliath(Card):
    def overkill(self):
        """Overkill: Give your other Pirates +2/+2."""
        for minion in self.friendly_minions | self.other | Race.Pirate:
            minion.gain(2 * self.tip, 2 * self.tip)


class SneedsOldShredder(Card):
    def deathrattle(self):
        # Summon a random Legendary minion.
        self.summon(Card.random(type="MINION", rarity="LEGENDARY"))


class Voidlord(Card):
    normal_child = "CS2_065"

    def deathrattle(self):
        # Summon three 1/3 Demons with Taunt.
        for _ in range(3):
            self.summon(self.child_card())
