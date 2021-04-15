from battlesim.simulator.battle import battle, parse_battlefield
from hearthstone.enums import GameTag


def test_acolyte_of_cthun():
    assert battle(parse_battlefield((["BGS_106"], [(2, 2)]))) == 1
    assert battle(parse_battlefield((["BGS_106"], [(2, 3)]))) == 0
    assert battle(parse_battlefield((["BGS_106"], [(2, 5)]))) == -1


def test_red_whelp():
    assert battle(parse_battlefield((["BGS_019"], [(1, 2)]))) == 1
    assert battle(parse_battlefield((["BGS_019"], [(1, 3)]))) == 0
    assert battle(parse_battlefield((["BGS_019"], [(1, 4)]))) == -1


def test_scally_wag():
    assert (
        battle(parse_battlefield((["BGS_061", (4, 1, GameTag.TAUNT)], [(1, 4)]))) == 0
    )


def test_scavenging_hyena():
    assert battle(parse_battlefield((["CFM_315", "EX1_531"], [(2, 4)]))) == 1


def test_selfless_hero():
    assert battle(parse_battlefield((["OG_221", (1, 1)], [(2, 4)]))) == 0
