from battlesim.battle import battle, parse_battlefield
from battlesim.keywords import *


def test_herald_of_flame():
    assert battle(parse_battlefield(([60247, 475], [(7, 7)]))) == 0
