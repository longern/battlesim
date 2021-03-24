from ..card import Card, choice, after, whenever


class IronhideDirehorn(Card):
    def overkill(self):
        self.summon(Card.fromid(50359))


class MamaBear(Card):
    @whenever(Card.summon)
    def effect(self, this, card, before=None):
        if self.controller == card.controller and card.minion_type == 20:
            card.attack_power += 4
            card.health += 4


class SeabreakerGoliath(Card):
    def overkill(self):
        for minion in self.friendly_minions:
            if minion is not self and minion.minion_type == 23:
                minion.attack_power += 2
                minion.health += 2


class SneedsOldShredder(Card):
    def deathrattle(self):
        # Summon a random Legendary minion.
        pass


class Voidlord(Card):
    def deathrattle(self):
        # Summon three 1/3 Demons with Taunt.
        self.summon(Card.fromid(46056))
