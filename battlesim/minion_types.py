from enum import Enum


class MinionType(Enum):
    NoMinionType = 0
    Murloc = 14
    Demon = 15
    Mech = 17
    Elemental = 18
    Beast = 20
    Pirate = 23
    Dragon = 24
    All = 26

    def __ror__(self, minions):
        return filter(
            lambda minion: minion.minion_type in (self, MinionType.All), minions
        )

    def __contains__(self, minion):
        return minion.minion_type in (self, MinionType.All)
