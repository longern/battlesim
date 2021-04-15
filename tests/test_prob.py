from collections import Counter

from battlesim.simulator.battle import battle, parse_battlefield


def calculate_winrate(friendly_minions, enemy_minions):
    result_counter = Counter()
    for _ in range(100):
        result = battle(parse_battlefield((friendly_minions, enemy_minions)))
        result_counter[result] += 1

    return {key: value / 100 for key, value in result_counter.items()}


def test_prob_1():
    winrate = calculate_winrate(
        ["BGS_039", "BGS_039", (2, 2), (2, 2, "BGS_019"), "BGS_019", (2, 1), (1, 1)],
        ["OG_256", "BGS_045", "BGS_119", (4, 4), "BOT_606", (1, 1)],
    )
    assert winrate[-1] > 0.7
