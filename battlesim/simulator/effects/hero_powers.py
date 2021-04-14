from ..entities import Card, after, choice, whenever


class FishOfNZoth(Card):
    def deathrattle(self):
        pass


class SproutItOut(Card):
    @after(Card.summon)
    def effect(self, this, card: Card):
        card.gain(1, 2)
        card.taunt = True


class SwattingInsects(Card):
    def start_of_combat(self):
        """Give your left-most minion Windfury, Divine Shield, and Taunt"""
        if self.controller.minions:
            self.controller.minions[0].windfury = True
            self.controller.minions[0].divine_shield = True
            self.controller.minions[0].taunt = True


class Wingmen(Card):
    def start_of_combat(self):
        for minion in self.controller.minions[1 :: max(len(self.minions) - 1, 1)]:
            minion.attack()
