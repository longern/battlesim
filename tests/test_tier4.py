from battlesim.battle import battle, parse_battlefield
from battlesim.keywords import *


def test_herald_of_flame():
    assert battle(parse_battlefield(([(5, 6, 60498)], [(1, 1), (5, 3), (5, 3)]))) == 0
