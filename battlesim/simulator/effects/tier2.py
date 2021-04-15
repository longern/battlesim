from hearthstone.enums import GameTag, Race

from ..entities import Minion, after, choice, whenever


class GlyphGuardian(Minion):
    @whenever(Minion.attack)
    def effect(self, this, defender):
        if self is this:
            self.tags[GameTag.ATK] *= 1 + self.tip


class HarvestGolem(Minion):
    normal_child = "skele21"

    def deathrattle(self):
        self.summon(self.child_card())


class Imprisoner(Minion):
    normal_child = "BRM_006t"
    premium_child = "TB_BaconUps_030t"

    def deathrattle(self):
        self.summon(self.child_card())


class KaboomBot(Minion):
    def deathrattle(self):
        for _ in range(self.tip):
            self.deal_damage(4, choice(self.enemy_minions))


class KindlyGrandmother(Minion):
    def deathrattle(self):
        self.summon(self.child_card())


class MurlocWarleader(Minion):
    def aura(self):
        pass


class OldMurkEye(Minion):
    def aura(self):
        """Has +1 Attack for each other Murloc on the battlefield."""


class PackLeader(Minion):
    @whenever(Minion.summon)
    def effect(self, this, card):
        if this.controller == self.controller and card in Race.BEAST:
            card.gain(2, 0)


class SouthseaCaptain(Minion):
    def aura(self):
        pass


class SpawnOfNzoth(Minion):
    def deathrattle(self):
        for minion in self.friendly_minions:
            minion.gain(self.tip, self.tip)


class TormentedRitualist(Minion):
    @whenever(Minion.attack)
    def effect(self, this, defender):
        if self is defender:
            for minion in self.adjacent_minions:
                minion.gain(self.tip, self.tip)


class UnstableGhoul(Minion):
    def deathrattle(self):
        for minion in [*self.friendly_minions, *self.enemy_minions]:
            self.deal_damage(1, minion)


class WaxriderTogwaggle(Minion):
    @whenever(Minion.attack)
    def effect(self, this):
        """Whenever a friendly Dragon kills an enemy, gain +2/+2."""


class YoHoOgre(Minion):
    @whenever(Minion.attack)
    def effect(self, this, defender):
        if self is defender and self.alive:
            self.attack()
