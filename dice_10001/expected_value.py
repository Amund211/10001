"""
Module provinding functions for estimating the expected value of rolls

Results with depth=10_000:

Expected value at 0 points for given dice count:
6: 590.66
5: 336.84
4: 240.80
3: 197.23
2: 185.01
1: 217.15

Minimum score for negative EV at given dice count:
6: 18100
5:  3100
4:  1050
3:   450
2:   250
1:   350
"""

from functools import cache

from dice_10001.scoring import best_outcomes_per_dice_count
from dice_10001.types import DiceCount, Score

# The minimum score you should stop at for a given dice count
MIN_SCORE_FOR_NEGATIVE_EV = {i: 10_000_000 for i in range(1, 7)}


@cache
def estimate_ev(dice_count: int, score: Score, depth: int) -> float:
    """Estimate the expected value of rolling `dice_count` dice with the given score"""
    if depth == 0:
        # This is wrong, but made insignificant by high depths
        return 0

    outcomes_per_dice_count = best_outcomes_per_dice_count()[dice_count]
    total_weight = 0
    total_score = 0.0
    for outcomes, weight in outcomes_per_dice_count.items():
        total_weight += weight

        if outcomes[0].dice == DiceCount.BUST:
            assert len(outcomes) == 1
            total_score -= score * weight
            continue

        max_ev = -1.0
        for outcome in outcomes:
            branch_ev: float = outcome.points
            if score + outcome.points < MIN_SCORE_FOR_NEGATIVE_EV[outcome.dice]:
                subtree_ev = estimate_ev(
                    outcome.dice, score + outcome.points, depth - 1
                )
                if subtree_ev > 0:  # It is worth it to roll again
                    branch_ev += subtree_ev

            max_ev = max(max_ev, branch_ev)

        assert max_ev >= 0

        total_score += max_ev * weight

    ev = total_score / total_weight

    if ev < 0:
        MIN_SCORE_FOR_NEGATIVE_EV[dice_count] = min(
            MIN_SCORE_FOR_NEGATIVE_EV[dice_count], score
        )

    return ev


def estimate_evs() -> dict[int, float]:
    """Return a mapping from dice count to estimated ev"""
    evs = {}
    for dice_count in range(1, 7):
        evs[dice_count] = estimate_ev(dice_count, 0, depth=10_000)
    return evs


def estimate_min_score_for_negative_ev() -> dict[int, int]:
    """
    Return the minimum score you should stop at for a given dice count

    This can be used to play an ev-optimal game
    """
    estimate_evs()  # Ensure the min score lookup is populated
    return MIN_SCORE_FOR_NEGATIVE_EV
