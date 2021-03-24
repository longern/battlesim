from ..card import Card, choice, after, whenever


class HeraldOfFlame(Card):
    def overkill(self):
        self.deal_damage(3, next(iter(self.enemy_minions), None))


class Junkbot(Card):
    @whenever(Card.die)
    def effect(self, this):
        if self.controller is this.controller and this.minion_type == 17:
            self.gain(2, 2)


class MechanoEgg(Card):
    def deathrattle(self):
        self.summon(Card.fromid(49168))


class QirajiHarbinger(Card):
    @after(Card.die)
    def effect(self, this):
        if self.controller == this.controller and this.taunt:
            for minion in this.adjacent_minions:
                self.give(minion, 2, 2)
