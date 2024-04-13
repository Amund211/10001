"""
Module providing functions for scoring rolls
"""

from collections import defaultdict
from collections.abc import Mapping
from itertools import chain, product
from typing import Iterable

from dice_10001.types import DiceCount, Outcome, Roll, Score

# Points granted for an amount of each eye count
POINTS_TABLE: Mapping[int, list[Score]] = {
    1: [0, 100, 200, 1000, 2000, 4000, 8000],
    2: [0, 0, 0, 200, 400, 800, 1600],
    3: [0, 0, 0, 300, 600, 1200, 2400],
    4: [0, 0, 0, 400, 800, 1600, 3200],
    5: [0, 50, 100, 500, 1000, 2000, 4000],
    6: [0, 0, 0, 600, 1200, 2400, 4800],
}


def _get_frequencies(roll: Roll) -> dict[int, int]:
    """Return the frequency table for `roll`"""
    freq: dict[int, int] = defaultdict(int)
    for dice in roll:
        freq[dice] += 1

    return freq


def _get_keep_counts(eye_count: int, count: int) -> Iterable[int]:
    """
    Return an iterable of the amount of this eye_count you are allowed to keep
    """
    # We are allowed to keep any amount of 1s and 5s since they all give points
    if eye_count in (1, 5):
        return range(0, count + 1)

    # For 2, 3, 4, and 6 we are allowed to keep 0, or collections of 3 or higher
    # since they only give points when there are 3 or more.
    return chain((0,), range(3, count + 1))


def generate_outcomes(roll: Roll) -> Iterable[Outcome]:
    """Yield a all possible outcomes for the given (sorted) roll"""
    assert roll == tuple(sorted(roll))

    if is_bust(roll):
        yield Outcome(0, DiceCount.BUST)
        return

    freq = _get_frequencies(roll)
    starting_dice = len(roll)

    # The two special cases: full straight and three pairs
    if starting_dice == 6:
        if roll == (1, 2, 3, 4, 5, 6):
            yield Outcome(2000, 6)
        elif len(freq.keys()) == 3 and all(count == 2 for count in freq.values()):
            yield Outcome(1500, 6)

    # Iterate over all unique selections of dice to keep
    for selection in product(
        *(_get_keep_counts(eye_count, count) for eye_count, count in freq.items())
    ):
        # Must keep at least one dice
        if all(count == 0 for count in selection):
            continue

        points = sum(
            POINTS_TABLE[eye_count][count]
            for eye_count, count in zip(freq.keys(), selection)
            if count != 0
        )
        dice = starting_dice - sum(selection)

        # You get to continue with all 6 dice if you use them all
        if dice == 0:
            dice = 6

        yield Outcome(points, dice)


def get_best_outcomes(roll: Roll) -> tuple[Outcome, ...]:
    """Return a tuple of the best outcomes for each remaining dice count"""
    best_outcomes: dict[int, Outcome] = defaultdict(lambda: Outcome(-1, DiceCount.BUST))

    for outcome in generate_outcomes(roll):
        best_outcomes[outcome.dice] = max(
            outcome, best_outcomes[outcome.dice], key=lambda x: x.points
        )

    return tuple(best_outcomes.values())


def get_all_outcomes(roll: Roll) -> set[Outcome]:
    """Return a set of possible outcomes for the given roll"""
    all_outcomes = set[Outcome]()

    all_outcomes.update(generate_outcomes(roll))

    return all_outcomes


def is_bust(roll: Roll) -> bool:
    """Determine if the given roll is bust"""
    if 1 in roll or 5 in roll:
        # 1s and 5s always give points
        return False

    freq = _get_frequencies(roll)

    if any(count >= 3 for count in freq.values()):
        # Three or more of a kind always gives points
        return False

    # Three pairs (full straight is handled by the 1s or 5s rule)
    if len(freq.keys()) == 3 and all(count == 2 for count in freq.values()):
        return False

    return True
