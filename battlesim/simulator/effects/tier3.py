from ..minion_types import Race
from ..keywords import Frenzy
from ..entities import Card, choice, after, whenever


class ArmOfTheEmpire(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        """Whenever a friendly Taunt minion is attacked, give it +2 Attack permanently."""
        if self.controller is defender.controller and defender.taunt:
            defender.gain(2 * self.tip, 0, permanently=True)


class BarrensBlacksmith(Card, Frenzy):
    def frenzy(self):
        """Frenzy: Give your other minions +2/+2."""
        for minion in self.friendly_minions | self.other:
            minion.gain(2 * self.tip, 2 * self.tip)


class Deflectobot(Card):
    @whenever(Card.summon)
    def effect(self, this, card):
        if self.controller is this.controller and card in Race.Mechanical:
            self.atk += self.tip
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


class Khadgar(Card):
    @after(Card.summon)
    def effect(self, this, card: Card):
        if self.controller is this.controller and not getattr(card, "khadgar", False):
            card.copied_by_khadgar = True
            for _ in range(self.tip):
                copy = Card.fromid(card.card_id)
                copy.atk = card.atk
                copy.health = card.health
                copy.damage = card.damage
                copy.reborn = card.reborn
                copy.khadgar = True
                card.index = card.friendly_minions.index(card) + 1
                card.summon(copy)


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
            self.summon(Card.fromid("TB_BaconUps_032t" if self.premium else "BOT_312t"))


class SoulJuggler(Card):
    @after(Card.die)
    def effect(self, this):
        if this in Race.Demon:
            self.deal_damage(3, choice(self.enemy_minions))
