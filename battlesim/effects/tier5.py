from ..minion_types import MinionType
from ..card import Card, choice, after, whenever


class IronhideDirehorn(Card):
    def overkill(self):
        self.summon(Card.fromid(50359))


class KingBagurgle(Card):
    def battlecry(self):
        """Battlecry and Deathrattle: Give your other Murlocs +2/+2."""
        for minion in self.friendly_minions | self.other | MinionType.Murloc:
            minion.attack_power += 2
            minion.health += 2

    deathrattle = battlecry


class MamaBear(Card):
    @whenever(Card.summon)
    def effect(self, this, card, before=None):
        if self.controller == card.controller and card.minion_type is MinionType.Beast:
            card.attack_power += 4
            card.health += 4


class SeabreakerGoliath(Card):
    def overkill(self):
        """Overkill: Give your other Pirates +2/+2."""
        for minion in self.friendly_minions | self.other | MinionType.Pirate:
            minion.attack_power += 2
            minion.health += 2


class SneedsOldShredder(Card):
    def deathrattle(self):
        # Summon a random Legendary minion.
        pass


class Voidlord(Card):
    def deathrattle(self):
        # Summon three 1/3 Demons with Taunt.
        for _ in range(3):
            self.summon(Card.fromid(46056))
