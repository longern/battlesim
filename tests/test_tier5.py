from battlesim.simulator.battle import battle, parse_battlefield


def test_herald_of_flame():
    assert battle(parse_battlefield((["BGS_030", "EX1_509"], [(7, 7)]))) == 0
