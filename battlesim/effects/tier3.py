from ..minion_types import MinionType
from ..keywords import Frenzy
from ..card import Card, choice, after, whenever


class ArmOfTheEmpire(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        """Whenever a friendly Taunt minion is attacked, give it +2 Attack permanently."""
        if self.controller is defender.controller and defender.taunt:
            defender.gain(2, 0, permanently=True)


class BarrensBlacksmith(Card, Frenzy):
    def frenzy(self):
        """Frenzy: Give your other minions +2/+2."""
        for minion in self.friendly_minions | self.other:
            minion.gain(2, 2)


class DeflectOBot(Card):
    @whenever(Card.summon)
    def effect(self, this, card):
        if self.controller is card.controller and card in MinionType.Mechanical:
            self.atk += 1
            self.divine_shield = True


class ImpGangBoss(Card):
    @whenever(Card.deal_damage)
    def effect(self, this, amount, target):
        if self is target:
            self.summon(self.child_card())


class InfestedWolf(Card):
    def deathrattle(self):
        for _ in range(2):
            self.summon(self.child_card())


class MonstrousMacaw(Card):
    @after(Card.attack)
    def effect(self, this, defender):
        if self is not this:
            return

        friendly_deathrattle = [
            minion for minion in self.friendly_minions if hasattr(minion, "deathrattle")
        ]
        if friendly_deathrattle:
            choice(friendly_deathrattle).trigger("deathrattle")


class RatPack(Card):
    def deathrattle(self):
        for _ in range(self.atk):
            self.summon(self.child_card())


class ReplicatingMenace(Card):
    def deathrattle(self):
        for _ in range(3):
            self.summon(self.child_card())


class SoulJuggler(Card):
    @after(Card.die)
    def effect(self, this):
        if this in MinionType.Demon:
            self.deal_damage(3, choice(self.enemy_minions))
