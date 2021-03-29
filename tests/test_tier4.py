from battlesim.battle import battle, parse_battlefield
from battlesim.keywords import *


def test_herald_of_flame():
    assert battle(parse_battlefield(([60498], [(1, 1), (5, 3), (5, 3)]))) == 0


def test_security_rover():
    assert battle(parse_battlefield(([(2, 6, 48100, Taunt)], [(6, 4)]))) == 0
    assert (
        battle(parse_battlefield(([(6, 6, 40428), (2, 6, 48100, Taunt)], [(14, 14)])))
        == 0
    )
