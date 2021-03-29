from battlesim.battle import battle, parse_battlefield
from battlesim.keywords import *


def test_crackling_cyclone():
    assert battle(parse_battlefield(([64054, (1, 1, Taunt)], [(1, 8)]))) == 1


def test_rat_pack():
    assert battle(parse_battlefield(([(8, 8, 40428)], [(15, 15)]))) == 0


def test_soul_juggler():
    assert battle(parse_battlefield(([43121, 59660], [(4, 8)]))) == 0
