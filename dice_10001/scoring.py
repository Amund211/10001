"""
Module providing functions for scoring rolls
"""
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, unique
from itertools import chain, product

# Points granted for an amount of each eye count
POINTS_TABLE = {
    1: [0, 100, 200, 1000, 2000, 4000, 8000],
    2: [0, 0, 0, 200, 400, 800, 1600],
    3: [0, 0, 0, 300, 600, 1200, 2400],
    4: [0, 0, 0, 400, 800, 1600, 3200],
    5: [0, 50, 100, 500, 1000, 2000, 4000],
    6: [0, 0, 0, 600, 1200, 2400, 4800],
}


@unique
class DiceCount(int, Enum):
    """
    Enum for dicecount

    Can be either a number [1, 6] or the special value DiceCount.BUST
    """

    BUST = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6


@dataclass(frozen=True)
class Outcome:
    """
    A possible outcome of a roll

    Stores the points gained from the roll, and the amount of remaining dice
    """

    points: int
    dice: DiceCount


def _get_frequencies(roll):
    """
    Return the frequency table for `roll`

    The returned type is a defaultdict
    """
    freq = defaultdict(int)
    for dice in roll:
        freq[dice] += 1

    return freq


def _get_keep_counts(eye_count, count):
    """
    Return an iterator of the amount of this eye_count you are allowed to keep
    """
    # We are allowed to keep any amount of 1s and 5s since they all give points
    if eye_count in (1, 5):
        return range(0, count + 1)

    # For 2, 3, 4, and 6 we are allowed to keep 0, or collections of 3 or higher
    # since they only give points when there are 3 or more.
    return chain((0,), range(3, count + 1))


def get_outcomes(roll):
    """
    Return a set of possible outcomes for the given roll

    Roll must be sorted.
    """
    outcomes = set()
    freq = _get_frequencies(roll)
    starting_dice = len(roll)

    # The two special cases: full straight and three pairs
    if roll == (1, 2, 3, 4, 5, 6):
        outcomes.add(Outcome(2000, 6))
    elif len(freq.keys()) == 3 and all(count == 2 for count in freq.values()):
        outcomes.add(Outcome(1500, 6))

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

        outcomes.add(Outcome(points, dice))

    return outcomes or set([Outcome(0, DiceCount.BUST)])


def filter_outcomes(outcomes):
    """
    Remove outcomes with the same remaining dice count but lower score
    """
    # The placeholder outcome has points=-1, and so will always be less than
    # the outcome it is compared to in `max`
    best_outcomes = defaultdict(lambda: Outcome(-1, DiceCount.BUST))
    for outcome in outcomes:
        best_outcomes[outcome.dice] = max(
            outcome, best_outcomes[outcome.dice], key=lambda x: x.points
        )

    return set(best_outcomes.values())


def is_bust(roll):
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
