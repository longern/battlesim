from ..card import Card, choice, after, whenever


class ImpGangBoss(Card):
    @whenever(Card.deal_damage)
    def effect(self, this, amount, target):
        if self is target:
            self.summon(Card.fromid(2779))


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
        self.summon(Card.fromid(41839))


class SoulJuggler(Card):
    @after(Card.die)
    def effect(self, this):
        if this.minion_type == 15:
            self.deal_damage(3, choice(self.enemy_minions))
