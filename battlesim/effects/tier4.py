from battlesim.minion_types import MinionType
from ..card import Card, choice, after, whenever
from ..view import view


@view
def alive(minions):
    return filter(lambda minion: minion.alive, minions)


class Bigfernal(Card):
    @after(Card.summon)
    def effect(self, this, card):
        if self.controller is card.controller and card in MinionType.Demon:
            self.gain(self.tip, self.tip, permanently=True)


class BolvarFireblood(Card):
    @after(Card.lose_divine_shield)
    def effect(self, this):
        """After a friendly minion loses Divine Shield, gain +2 Attack."""
        if self.controller is this.controller:
            self.gain(2 * self.tip, 0)


class CaveHydra(Card):
    """Also damages the minions next to whomever this attacks."""


class ChampionOfYshaarj(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        """Whenever a friendly Taunt minion is attacked, gain +1/+1 permanently."""
        if self.controller is defender.controller and defender.taunt:
            self.gain(self.tip, self.tip, permanently=True)


class DrakonidEnforcer(Card):
    @after(Card.lose_divine_shield)
    def effect(self, this):
        """After a friendly minion loses Divine Shield, gain +2/+2."""
        if self.controller is this.controller:
            self.gain(2 * self.tip, 2 * self.tip)


class HeraldOfFlame(Card):
    def overkill(self):
        self.deal_damage(3 * self.tip, next(self.enemy_minions | alive, None))


class Junkbot(Card):
    @whenever(Card.die)
    def effect(self, this):
        if self.controller is this.controller and this in MinionType.Mechanical:
            self.gain(2 * self.tip, 2 * self.tip)


class MechanoEgg(Card):
    def deathrattle(self):
        self.summon(self.child_card())


class QirajiHarbinger(Card):
    @after(Card.die)
    def effect(self, this):
        if self.controller == this.controller and this.taunt:
            for minion in this.adjacent_minions:
                minion.gain(2 * self.tip, 2 * self.tip)


class RingMatron(Card):
    def deathrattle(self):
        for _ in range(2):
            self.summon(self.child_card())


class RipsnarlCaptain(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        if (
            self is not this
            and self.controller is this.controller
            and this in MinionType.Pirate
        ):
            this.gain(2 * self.tip, 2 * self.tip)


class SavannahHighmane(Card):
    def deathrattle(self):
        for _ in range(2):
            self.summon(self.child_card())


class SecurityRover(Card):
    @whenever(Card.deal_damage)
    def effect(self, this, amount, card: Card):
        if self is this:
            self.summon(self.child_card())


class WildfileElemental(Card):
    """After this attacks and kills a minion, deal excess damage to a random adjacent minion."""
