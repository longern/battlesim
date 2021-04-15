from hearthstone.enums import GameTag

from battlesim.simulator.battle import battle, parse_battlefield


def test_imp_mama():
    assert battle(parse_battlefield((["BGS_044"], [(10, 6)]))) == 1
