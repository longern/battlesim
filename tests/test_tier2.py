from battlesim.battle import battle, parse_battlefield
from battlesim.keywords import *


def test_kaboom_bot():
    assert battle(parse_battlefield(([(2, 2, 49279)], [(2, 6)]))) == 0
