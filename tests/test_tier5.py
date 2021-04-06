from battlesim.battle import battle, parse_battlefield
from battlesim.keywords import *


def test_herald_of_flame():
    assert battle(parse_battlefield((["BGS_030", "EX1_509"], [(7, 7)]))) == 0
