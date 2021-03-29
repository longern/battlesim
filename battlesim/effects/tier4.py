from battlesim.minion_types import MinionType
from ..card import Card, choice, after, whenever
from ..view import view


@view
def alive(minions):
    return filter(lambda minion: minion.health > 0 and not minion.poisoned, minions)


class HeraldOfFlame(Card):
    def overkill(self):
        self.deal_damage(3, next(self.enemy_minions | alive, None))


class Junkbot(Card):
    @whenever(Card.die)
    def effect(self, this):
        if self.controller is this.controller and this.minion_type is MinionType.Mech:
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


class RingMatron(Card):
    def deathrattle(self):
        for _ in range(2):
            self.summon(Card.fromid(63273))


class SavannahHighmane(Card):
    def deathrattle(self):
        for _ in range(2):
            self.summon(Card.fromid(1624))


class SecurityRover(Card):
    @whenever(Card.deal_damage)
    def effect(self, this, amount, card: Card):
        if self is this:
            self.summon(Card.fromid(49278))
