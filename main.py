from collections import defaultdict
from collections.abc import Callable
from itertools import chain

from dice_10001.chance_to_reach import estimate_chances_to_reach
from dice_10001.expected_value import (
    estimate_evs,
    estimate_min_score_for_negative_ev,
    reset_min_score_for_negative_ev,
)
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


def print_table(rows: list[list[str]]) -> None:
    max_lengths = [max(len(cell) for cell in column) for column in zip(*rows)]

    for row in rows:
        print(
            "  ".join(
                f"{cell:>{max_length}}" for max_length, cell in zip(max_lengths, row)
            )
        )


def print_dict_table(
    data: dict[str, dict[int, float]], format_number: Callable[[float], str] = str
) -> None:
    dice_count_order = tuple(range(6, 0, -1))
    columns = [[""] + [str(dice_count) for dice_count in dice_count_order]]
    for key, values in data.items():
        columns.append(
            [key]
            + [format_number(values[dice_count]) for dice_count in dice_count_order]
        )
    print_table(list(zip(*columns)))


if __name__ == "__main__":
    best_outcomes_per_dice_count  # Prevent unused import error
    """
    # Interesting performance optimization, but not relevant to actual play
    print('Unique rolls vs "best outcomes per dice count" for given dice count:')
    outcomes_per_dice_count = best_outcomes_per_dice_count()
    for dice_count, outcomes in reversed(outcomes_per_dice_count.items()):
        print(f"{dice_count}:")
        print(f"\tUnordered rolls: {sum(outcomes.values()):>5}")
        print(f"\tOrdered rolls:   {len(tuple(generate_rolls(dice_count))):>5}")
        print(f"\tOutcomes:        {len(outcomes):>5}")
    """

    """
    # Included in the table below
    print("Expected value at 0 points for given dice count:")
    for dice_count, ev in reversed(estimate_evs(score=0).items()):
        print(f"{dice_count}: {ev:>5.2f}")
    """

    print("Minimum score for negative EV at given dice count:")
    for dice_count, min_score in reversed(estimate_min_score_for_negative_ev().items()):
        print(f"{dice_count}: {min_score:>5}")

    print("\nExpected value for the whole turn for given dice count/score:")
    print_dict_table(
        {
            str(score): estimate_evs(score=score, net_ev=False)
            for score in range(0, 1050, 50)
        },
        lambda x: f"{x:.1f}",
    )

    reset_min_score_for_negative_ev  # Prevent unused import error
    """
    # Setting pointloss limit to 1000 is an okay proxy, but estimate_chance to reach
    # is exact.
    print("\nPointloss limit at 1000:")
    reset_min_score_for_negative_ev()
    print("Expected value at 0 points for given dice count:")
    for dice_count, ev in reversed(estimate_evs(score=0, limit=1000).items()):
        print(f"{dice_count}: {ev:>5.2f}")

    print("Minimum score for negative EV at given dice count:")
    for dice_count, min_score in reversed(estimate_min_score_for_negative_ev().items()):
        print(f"{dice_count}: {min_score:>5}")

    print("\nExpected value for given dice count/score with pointloss limit at 1000:")
    print_dict_table(
        {
            str(score): estimate_evs(score=score, limit=1000)
            for score in range(0, 1050, 50)
        },
        lambda x: f"{x:.2f}",
    )
    """

    """
    # Included in the table below
    print("\nChance to reach 1000 points for given dice count at 0 points:")
    for dice_count, chance in reversed(
        estimate_chances_to_reach(score=0, target=1000).items()
    ):
        print(f"{dice_count}: {chance * 100:>5.2f}%")
    """

    print("\nChance to reach 1000 points for given dice count/score:")
    print_dict_table(
        {
            str(score): estimate_chances_to_reach(score=score, target=1000)
            for score in range(0, 1050, 50)
        },
        lambda x: f"{x * 100:.2f}%",
    )
