import re
from .event import after
from .card import Card


class Keyword:
    @classmethod
    def as_attribute(cls):
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class Taunt(Keyword):
    keyword_id = 1


class DivineShield(Keyword):
    keyword_id = 3


class Battlecry(Keyword):
    keyword_id = 8


class Windfury(Keyword):
    keyword_id = 11


class Deathrattle(Keyword):
    keyword_id = 12


class Poisonous(Keyword):
    keyword_id = 32


class Magnetic(Keyword):
    keyword_id = 66


class Reborn(Keyword):
    keyword_id = 78


class Frenzy(Keyword):
    keyword_id = 99

    def frenzy(self):
        raise NotImplementedError()

    @after(Card.deal_damage)
    def effect(self, this, amount, card: "Card"):
        if self is card and self.health > 0 and not self.poisoned and not self.burst:
            self.burst = True
            self.frenzy()
