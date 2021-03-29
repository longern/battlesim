from battlesim.battle import battle, parse_battlefield
from battlesim.keywords import *


def test_crackling_cyclone():
    assert battle(parse_battlefield(([(4, 1, 64054), (1, 1, Taunt)], [(1, 8)]))) == 1
