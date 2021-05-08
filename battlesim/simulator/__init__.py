import hearthstone.enums

hearthstone.enums.Race.__ror__ = lambda self, left: filter(
    lambda entity: getattr(entity, "cardrace", None)
    in (self, hearthstone.enums.Race.ALL),
    left,
)

hearthstone.enums.Race.__contains__ = lambda self, left: (
    getattr(left, "cardrace", None) in (self, hearthstone.enums.Race.ALL)
)
