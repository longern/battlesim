from battlesim.battle import battle, parse_battlefield
from battlesim.keywords import *


def test_crackling_cyclone():
    assert battle(parse_battlefield((["BGS_119", (1, 1, Taunt)], [(1, 8)]))) == 1


def test_rat_pack():
    assert battle(parse_battlefield(([(8, 8, "CFM_316")], [(15, 15)]))) == 0


def test_soul_juggler():
    assert battle(parse_battlefield((["LOOT_013", "BGS_002"], [(4, 8)]))) == 0
