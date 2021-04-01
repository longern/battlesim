from battlesim.minion_types import MinionType
from ..card import Card, choice, after, whenever
from ..view import view


@view
def alive(minions):
    return filter(lambda minion: minion.health > 0 and not minion.poisoned, minions)


class Bigfernal(Card):
    @after(Card.summon)
    def effect(self, this, card):
        if self.controller is card.controller and card in MinionType.Demon:
            self.gain(1, 1, permanently=True)


class BolvarFireblood(Card):
    @after(Card.lose_divine_shield)
    def effect(self, this):
        """After a friendly minion loses Divine Shield, gain +2 Attack."""
        if self.controller is this.controller:
            self.gain(2, 0)


class CaveHydra(Card):
    """Also damages the minions next to whomever this attacks."""


class ChampionOfYshaarj(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        """Whenever a friendly Taunt minion is attacked, gain +1/+1 permanently."""
        if self.controller is defender.controller and defender.taunt:
            self.gain(1, 1, permanently=True)


class DrakonidEnforcer(Card):
    @after(Card.lose_divine_shield)
    def effect(self, this):
        """After a friendly minion loses Divine Shield, gain +2/+2."""
        if self.controller is this.controller:
            self.gain(2, 2)


class HeraldOfFlame(Card):
    def overkill(self):
        self.deal_damage(3, next(self.enemy_minions | alive, None))


class Junkbot(Card):
    @whenever(Card.die)
    def effect(self, this):
        if self.controller is this.controller and this in MinionType.Mechanical:
            self.gain(2, 2)


class MechanoEgg(Card):
    def deathrattle(self):
        self.summon(Card.fromid(49168))


class QirajiHarbinger(Card):
    @after(Card.die)
    def effect(self, this):
        if self.controller == this.controller and this.taunt:
            for minion in this.adjacent_minions:
                minion.gain(2, 2)


class RingMatron(Card):
    def deathrattle(self):
        for _ in range(2):
            self.summon(Card.fromid(63273))


class RipsnarlCaptain(Card):
    @whenever(Card.attack)
    def effect(self, this, defender):
        if (
            self is not this
            and self.controller is this.controller
            and this in MinionType.Pirate
        ):
            this.gain(2, 2)


class SavannahHighmane(Card):
    def deathrattle(self):
        for _ in range(2):
            self.summon(Card.fromid(1624))


class SecurityRover(Card):
    @whenever(Card.deal_damage)
    def effect(self, this, amount, card: Card):
        if self is this:
            self.summon(Card.fromid(49278))


class WildfileElemental(Card):
    """After this attacks and kills a minion, deal excess damage to a random adjacent minion."""
