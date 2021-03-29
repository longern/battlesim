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

    @property
    def minion_type_id(self):
        return self.value


locals().update(MinionType.__members__)
