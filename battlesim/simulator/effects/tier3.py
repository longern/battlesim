from hearthstone.enums import GameTag, Race

from ..entities import Minion, after, choice, whenever


class ArmOfTheEmpire(Minion):
    @whenever(Minion.attack)
    def effect(self, this, defender):
        """Whenever a friendly Taunt minion is attacked, give it +2 Attack permanently."""
        if self.controller is defender.controller and defender.taunt:
            defender.gain(2 * self.tip, 0, permanently=True)


class BarrensBlacksmith(Minion):
    def frenzy(self):
        """Frenzy: Give your other minions +2/+2."""
        for minion in self.friendly_minions | self.other:
            minion.gain(2 * self.tip, 2 * self.tip)


class Deflectobot(Minion):
    @whenever(Minion.summon)
    def effect(self, this, card):
        if self.controller is this.controller and card in Race.MECHANICAL:
            self.atk += self.tip
            self.divine_shield = True


class ImpGangBoss(Minion):
    @whenever(Minion.deal_damage)
    def effect(self, this, amount, target):
        if self is target:
            self.summon(self.child_card())


class InfestedWolf(Minion):
    def deathrattle(self):
        for _ in range(2):
            self.summon(self.child_card())


class Khadgar(Minion):
    @after(Minion.summon)
    def effect(self, this, card: Minion):
        if self.controller is this.controller and not getattr(card, "khadgar", False):
            card.copied_by_khadgar = True
            for _ in range(self.tip):
                copy = self.create(card.card_id)
                copy.tags = card.tags.copy()
                copy.khadgar = True
                card.index = card.friendly_minions.index(card) + 1
                card.summon(copy)


class MonstrousMacaw(Minion):
    @after(Minion.attack)
    def effect(self, this, defender):
        if self is not this:
            return

        friendly_deathrattle = [
            minion for minion in self.friendly_minions if hasattr(minion, "deathrattle")
        ]
        if friendly_deathrattle:
            choice(friendly_deathrattle).trigger("deathrattle")


class RatPack(Minion):
    def deathrattle(self):
        for _ in range(self.atk):
            self.summon(self.child_card())


class ReplicatingMenace(Minion):
    def deathrattle(self):
        for _ in range(3):
            self.summon(self.create("TB_BaconUps_032t" if self.premium else "BOT_312t"))


class SoulJuggler(Minion):
    @after(Minion.die)
    def effect(self, this):
        if this in Race.DEMON:
            self.deal_damage(3, choice(self.enemy_minions))
