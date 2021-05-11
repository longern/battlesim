from collections import Counter

from battlesim.simulator.battle import battle, parse_battlefield


def calculate_winrate(friendly_minions, enemy_minions):
    result_counter = Counter({-1: 0, 0: 0, 1: 0})
    SIMULATION_REPEATS = 1000
    for _ in range(SIMULATION_REPEATS):
        result = battle(parse_battlefield((friendly_minions, enemy_minions)))
        result_counter[result] += 1

    return {key: value / SIMULATION_REPEATS for key, value in result_counter.items()}


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
