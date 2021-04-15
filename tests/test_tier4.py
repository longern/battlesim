from battlesim.simulator.battle import battle, parse_battlefield
from hearthstone.enums import GameTag


def test_herald_of_flame():
    assert battle(parse_battlefield((["BGS_032"], [(1, 1), (5, 3), (5, 3)]))) == 0


def test_security_rover():
    assert (
        battle(parse_battlefield(([(2, 6, "BOT_218", GameTag.TAUNT)], [(6, 4)]))) == 0
    )
    assert (
        battle(
            parse_battlefield(
                ([(6, 6, "CFM_316"), (2, 6, "BOT_218", GameTag.TAUNT)], [(14, 14)])
            )
        )
        == 0
    )
