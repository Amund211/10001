from collections import defaultdict
from itertools import chain

from dice_10001.generate import generate_rolls
from dice_10001.scoring import get_best_outcomes, is_bust
from dice_10001.types import DiceCount


def find_unique_outcomes():
    outcomes = {}

    for dice_count in range(1, 7):
        outcomes[dice_count] = defaultdict(int)
        for roll, weight in generate_rolls(dice_count):
            for outcome in get_best_outcomes(roll):
                outcomes[dice_count][outcome] += 1

    return outcomes


def _display_strategy(outcomes):
    for from_count in outcomes:
        total_weight = sum(outcomes[from_count].values())
        assert total_weight == 6**from_count
        print(f"From {from_count}:")
        for to_count in chain((DiceCount.BUST,), range(1, 7)):
            to_weight = sum(
                outcomes[from_count][key]
                for key in filter(
                    lambda x: x.dice == to_count, outcomes[from_count].keys()
                )
            )
            print(f"\tTo {to_count}: {100 * to_weight / total_weight:.2f}%")


def _naive_points_strategy():
    outcomes = {}

    for dice_count in range(1, 7):
        outcomes[dice_count] = defaultdict(int)
        for roll, weight in generate_rolls(dice_count):
            # Choose the option that gives the most points
            outcome = max(get_best_outcomes(roll), key=lambda x: x.points)
            outcomes[dice_count][outcome] += weight

    return outcomes


def display_naive_points_strategy():
    _display_strategy(_naive_points_strategy())


def find_bust_chances():
    bust_chance = {}

    for dice_count in range(1, 7):
        total_weight = bust_weight = 0
        for roll, weight in generate_rolls(dice_count):
            if is_bust(roll):
                bust_weight += weight
            total_weight += weight
        bust_chance[dice_count] = bust_weight / total_weight

    return bust_chance


if __name__ == "__main__":
    from pprint import pprint  # noqa
