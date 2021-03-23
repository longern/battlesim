from ..card import Card, after, choice, whenever


class FiendishServant(Card):
    def deathrattle(self):
        choice(self.friendly_minions).attack_power += self.attack_power


class RedWhelp(Card):
    def start_of_combat(self):
        amount = len(
            [minion for minion in self.friendly_minions if minion.minion_type == 24]
        )
        self.deal_damage(amount, choice(self.enemy_minions))


class Scallywag(Card):
    def deathrattle(self):
        pirate = Card.fromid(62213)
        self.summon(pirate)
        pirate.attack()


class ScavengingHyena(Card):
    @whenever(Card.die)
    def effect(self, this):
        if this.minion_type == 20:
            self.gain(2, 1)


class SelflessHero(Card):
    def deathrattle(self):
        choice(
            minion for minion in self.friendly_minions if not minion.divine_shield
        ).divine_shield = True
