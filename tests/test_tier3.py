from battlesim.simulator.battle import battle, parse_battlefield
from hearthstone.enums import GameTag


def test_crackling_cyclone():
    assert (
        battle(parse_battlefield((["BGS_119", (1, 1, GameTag.TAUNT)], [(1, 8)]))) == 1
    )


def test_khadgar():
    assert battle(parse_battlefield((["BGS_106", "DAL_575"], [(8, 8)]))) == 0


def test_rat_pack():
    assert battle(parse_battlefield(([(8, 8, "CFM_316")], [(15, 15)]))) == 0


def test_soul_juggler():
    assert battle(parse_battlefield((["LOOT_013", "BGS_002"], [(4, 8)]))) == 0
