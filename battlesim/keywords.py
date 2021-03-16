import re

class Keyword:
    @classmethod
    def as_attribute(cls):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


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


class Magnetic(Keyword):
    keyword_id = 66


class Reborn(Keyword):
    keyword_id = 78
