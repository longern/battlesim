from hearthstone.enums import Race

from ..entities import Minion, after, choice, whenever
from ..view import view


@view
def alive(minions):
    return filter(lambda minion: minion.alive, minions)


class Bigfernal(Minion):
    @after(Minion.summon)
    def effect(self, this, card):
        if self.controller is card.controller and card in Race.Demon:
            self.gain(self.tip, self.tip, permanently=True)


class BolvarFireblood(Minion):
    @after(Minion.lose_divine_shield)
    def effect(self, this):
        """After a friendly minion loses Divine Shield, gain +2 Attack."""
        if self.controller is this.controller:
            self.gain(2 * self.tip, 0)


class CaveHydra(Minion):
    @whenever(Minion.attack)
    def effect(self, this, defender):
        """Also damages the minions next to whomever this attacks."""
        if self is this:
            for minion in defender.adjacent_minions:
                self.deal_damage(self.atk, minion)


class ChampionOfYshaarj(Minion):
    @whenever(Minion.attack)
    def effect(self, this, defender):
        """Whenever a friendly Taunt minion is attacked, gain +1/+1 permanently."""
        if self.controller is defender.controller and defender.taunt:
            self.gain(self.tip, self.tip, permanently=True)


class DrakonidEnforcer(Minion):
    @after(Minion.lose_divine_shield)
    def effect(self, this):
        """After a friendly minion loses Divine Shield, gain +2/+2."""
        if self.controller is this.controller:
            self.gain(2 * self.tip, 2 * self.tip)


class HeraldOfFlame(Minion):
    def overkill(self):
        self.deal_damage(3 * self.tip, next(self.enemy_minions | alive, None))


class Junkbot(Minion):
    @whenever(Minion.die)
    def effect(self, this):
        if self.controller is this.controller and this in Race.Mechanical:
            self.gain(2 * self.tip, 2 * self.tip)


class MechanoEgg(Minion):
    def deathrattle(self):
        self.summon(self.child_card())


class QirajiHarbinger(Minion):
    @after(Minion.die)
    def effect(self, this):
        if self.controller == this.controller and this.taunt:
            for minion in this.adjacent_minions:
                minion.gain(2 * self.tip, 2 * self.tip)


class RingMatron(Minion):
    def deathrattle(self):
        for _ in range(2):
            self.summon(self.child_card())


class RipsnarlCaptain(Minion):
    @whenever(Minion.attack)
    def effect(self, this, defender):
        if (
            self is not this
            and self.controller is this.controller
            and this in Race.Pirate
        ):
            this.gain(2 * self.tip, 2 * self.tip)


class SavannahHighmane(Minion):
    def deathrattle(self):
        for _ in range(2):
            self.summon(self.child_card())


class SecurityRover(Minion):
    @whenever(Minion.deal_damage)
    def effect(self, this, amount, card: Minion):
        if self is this:
            self.summon(self.child_card())


class WildfileElemental(Minion):
    """After this attacks and kills a minion, deal excess damage to a random adjacent minion."""
