from ..card import Card, choice, after, whenever


class GlyphGuardian(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        if self is this:
            self.attack_power *= 2


class HarvestGolem(Card):
    def deathrattle(self):
        self.summon(Card.fromid(471))


class Imprisoner(Card):
    def deathrattle(self):
        self.summon(Card.fromid(2779))


class KaboomBot(Card):
    def deathrattle(self):
        self.deal_damage(4, choice(self.enemy_minions))


class MurlocWarleader(Card):
    def aura(self):
        pass


class PackLeader(Card):
    @whenever(Card.summon)
    def effect(self, this, card):
        if this.controller == self.controller and card.minion_type == 20:
            card.attack_power += 2


class SpawnOfNZoth(Card):
    def deathrattle(self):
        self.give(self.friendly_minions, attack_power=1, health=1)


class TormentedRitualist(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        if self is defender:
            self.give(self.adjacent_minions, attack_power=1, health=1)


class YoHoOgre(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        if self is defender and self.health > 0 and not self.poisoned:
            self.attack()