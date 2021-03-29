from battlesim.battle import battle, parse_battlefield
from battlesim.keywords import *


def test_acolyte_of_cthun():
    assert battle(parse_battlefield(([63614], [(2, 2)]))) == 1
    assert battle(parse_battlefield(([63614], [(2, 3)]))) == 0
    assert battle(parse_battlefield(([63614], [(2, 5)]))) == -1


def test_red_whelp():
    assert battle(parse_battlefield(([59968], [(1, 2)]))) == 1
    assert battle(parse_battlefield(([59968], [(1, 3)]))) == 0
    assert battle(parse_battlefield(([59968], [(1, 4)]))) == -1


def test_scavenging_hyena():
    assert battle(parse_battlefield(([40426, 1281], [(2, 4)]))) == 1


def test_selfless_hero():
    assert battle(parse_battlefield(([38740, (1, 1)], [(2, 4)]))) == 0
