from battlesim.simulator.battle import battle, parse_battlefield


def test_reborn_rite():
    battlefield = parse_battlefield(
        ([(2, 1, "OG_221", "TB_BaconShop_HP_024e2")], [(2, 3)])
    )
    assert battle(battlefield) == 0
