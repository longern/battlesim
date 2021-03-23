from battlesim.battle import battle, parse_battlefield
from battlesim.keywords import *


def test_red_whelp():
    assert battle(parse_battlefield(([(1, 2, 59968)], [(1, 2)]))) == 1
    assert battle(parse_battlefield(([(1, 2, 59968)], [(1, 3)]))) == 0
    assert battle(parse_battlefield(([(1, 2, 59968)], [(1, 4)]))) == -1


def test_acolyte_of_cthun():
    assert battle(parse_battlefield(([(2, 2, 63614)], [(2, 2)]))) == 1
    assert battle(parse_battlefield(([(2, 2, 63614)], [(2, 3)]))) == 0
    assert battle(parse_battlefield(([(2, 2, 63614)], [(2, 5)]))) == -1
