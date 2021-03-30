from battlesim.battle import battle, parse_battlefield
from battlesim.keywords import *


def test_glyph_guardian():
    assert battle(parse_battlefield(([61029, (1, 1)], [(4, 5)]))) == 0


def test_harvest_golem():
    assert battle(parse_battlefield(([778], [(3, 3)]))) == 0
    assert battle(parse_battlefield(([778, (6, 1), (1, 1, Taunt)], [(6, 6)]))) == 0


def test_kaboom_bot():
    assert battle(parse_battlefield(([49279], [(2, 6)]))) == 0
