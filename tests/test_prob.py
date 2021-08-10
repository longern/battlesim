from collections import Counter

from battlesim.simulator.battle import calculate_winrate


def test_prob_1():
    winrate = calculate_winrate(
        ["BGS_039", "BGS_039", (2, 2), (2, 2, "BGS_019"), "BGS_019", (2, 1), (1, 1)],
        ["OG_256", "BGS_045", "BGS_119", (4, 4), "BOT_606", (1, 1)],
    )
    assert 0.7 < winrate[-1] < 0.9


def test_prob_2():
    winrate = calculate_winrate(
        ["BGS_061", "BGS_055", "BGS_060"],
        ["BGS_106", "BGS_201", "BGS_106"],
    )
    assert abs(winrate[-1] - 0.8) < 0.1
