from ..minion_types import MinionType
from ..card import Card, after, choice, whenever


class FiendishServant(Card):
    def deathrattle(self):
        if self.friendly_minions:
            choice(self.friendly_minions).atk += self.atk


class RedWhelp(Card):
    def start_of_combat(self):
        amount = len(list(self.friendly_minions | MinionType.Dragon))
        self.deal_damage(amount, choice(self.enemy_minions))


class Scallywag(Card):
    def deathrattle(self):
        pirate = Card.fromid("TB_BaconUps_141t" if self.premium else "BGS_061t")
        self.summon(pirate)


class SkyPirate(Card):
    """Child card of scallywag"""

    @after(Card.summon)
    def effect(self, this, card, before=None):
        if self is card:
            self.attack()


class ScavengingHyena(Card):
    @whenever(Card.die)
    def effect(self, this):
        if self.controller is this.controller and this in MinionType.Beast:
            self.gain(2, 1)


class SelflessHero(Card):
    def deathrattle(self):
        candidates = [
            minion for minion in self.friendly_minions if not minion.divine_shield
        ]
        if candidates:
            choice(candidates).divine_shield = True
