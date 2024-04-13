from collections import defaultdict
from itertools import chain

from dice_10001.expected_value import estimate_evs, estimate_min_score_for_negative_ev
from dice_10001.generate import generate_rolls
from dice_10001.scoring import best_outcomes_per_dice_count, get_best_outcomes
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


if __name__ == "__main__":
    import sys

    # estimate_ev uses deep recursion
    sys.setrecursionlimit(25_000)

    print('Unique rolls vs "best outcomes per dice count" for given dice count:')
    outcomes_per_dice_count = best_outcomes_per_dice_count()
    for dice_count, outcomes in reversed(outcomes_per_dice_count.items()):
        print(f"{dice_count}:")
        print(f"\tUnordered rolls: {sum(outcomes.values()):>5}")
        print(f"\tOrdered rolls:   {len(tuple(generate_rolls(dice_count))):>5}")
        print(f"\tOutcomes:        {len(outcomes):>5}")

    print("Expected value at 0 points for given dice count:")
    for dice_count, ev in reversed(estimate_evs().items()):
        print(f"{dice_count}: {ev:>5.2f}")

    print("Minimum score for negative EV at given dice count:")
    for dice_count, min_score in reversed(estimate_min_score_for_negative_ev().items()):
        print(f"{dice_count}: {min_score:>5}")
