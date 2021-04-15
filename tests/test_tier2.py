from hearthstone.enums import GameTag

from battlesim.simulator.battle import battle, parse_battlefield


def test_glyph_guardian():
    assert battle(parse_battlefield((["BGS_045", (1, 1)], [(4, 5)]))) == 0


def test_harvest_golem():
    assert battle(parse_battlefield((["LOOT_013"], [(3, 3)]))) == 0
    assert (
        battle(
            parse_battlefield((["LOOT_013", (6, 1), (1, 1, GameTag.TAUNT)], [(6, 6)]))
        )
        == 0
    )


def test_kaboom_bot():
    assert battle(parse_battlefield((["BOT_606"], [(2, 6)]))) == 0
