from battlesim.battle import battle, parse_battlefield
from battlesim.keywords import *


def test_imp_mama():
    assert battle(parse_battlefield((["BGS_044"], [(10, 6)]))) == 1
