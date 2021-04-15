import hearthstone.enums

hearthstone.enums.Race.__ror__ = lambda self, left: filter(
    lambda entity: entity.tags.get(hearthstone.enums.GameTag.CARDRACE) == self, left
)

hearthstone.enums.Race.__contains__ = lambda self, left: (
    left.tags.get(hearthstone.enums.GameTag.CARDRACE)
    in (self, hearthstone.enums.Race.ALL)
)
