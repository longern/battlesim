from battlesim.minion_types import MinionType
from ..card import Card, choice, after, whenever


class GlyphGuardian(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        if self is this:
            self.atk *= 1 + self.tip


class HarvestGolem(Card):
    normal_child = "skele21"

    def deathrattle(self):
        self.summon(self.child_card())


class Imprisoner(Card):
    normal_child = "BRM_006t"
    premium_child = "TB_BaconUps_030t"

    def deathrattle(self):
        self.summon(self.child_card())


class KaboomBot(Card):
    def deathrattle(self):
        for _ in range(self.tip):
            self.deal_damage(4, choice(self.enemy_minions))


class KindlyGrandmother(Card):
    def deathrattle(self):
        self.summon(self.child_card())


class MurlocWarleader(Card):
    def aura(self):
        pass


class OldMurkEye(Card):
    def aura(self):
        """Has +1 Attack for each other Murloc on the battlefield."""


class PackLeader(Card):
    @whenever(Card.summon)
    def effect(self, this, card):
        if this.controller == self.controller and card in MinionType.Beast:
            card.atk += 2


class SouthseaCaptain(Card):
    def aura(self):
        pass


class SpawnOfNzoth(Card):
    def deathrattle(self):
        for minion in self.friendly_minions:
            minion.gain(self.tip, self.tip)


class TormentedRitualist(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        if self is defender:
            for minion in self.adjacent_minions:
                minion.gain(self.tip, self.tip)


class UnstableGhoul(Card):
    def deathrattle(self):
        for minion in [*self.friendly_minions, *self.enemy_minions]:
            self.deal_damage(1, minion)


class WaxriderTogwaggle(Card):
    @whenever(Card.attack)
    def effect(self, this):
        """Whenever a friendly Dragon kills an enemy, gain +2/+2."""


class YoHoOgre(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        if self is defender and self.alive:
            self.attack()
