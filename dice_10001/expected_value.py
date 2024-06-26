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

Pointloss limit at 1000:
Expected value at 0 points for given dice count:
6: 766.16
5: 514.56
4: 385.39
3: 298.82
2: 256.01
1: 278.20
Minimum score for negative EV at given dice count:
6: 18100
5:  3100
4:  1050
3:  1000
2:  1000
1:  1000
"""

from functools import cache

from dice_10001.scoring import best_outcomes_per_dice_count
from dice_10001.types import DiceCount, Score

# The minimum score you should stop at for a given dice count
MIN_SCORE_FOR_NEGATIVE_EV = {i: 10_000_000 for i in range(1, 7)}


@cache
def estimate_ev(
    dice_count: int, score: Score, depth: int = 400, limit: int = 0
) -> float:
    """
    Estimate the expected value of rolling `dice_count` dice with the given score

    limit: The minimum score that is treated as a loss if you bust.
           This is used to get a proxy for the expected value and minimum scores when
           forced to reach the given score (1000 in the first round of the game)

    depth: Search depth for recursion. With limit 0, the maximum score cutoff is 18100.
           Since the minimum score per roll is 50, all rounds must reach cutoff within
           18100 / 50 = 362 depth. With a high limit, depth may need to be increased.
    """
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
            if score >= limit:
                total_score -= score * weight
            continue

        max_ev = -1.0
        for outcome in outcomes:
            branch_ev: float = outcome.points
            if score + outcome.points < MIN_SCORE_FOR_NEGATIVE_EV[outcome.dice]:
                subtree_ev = estimate_ev(
                    outcome.dice, score + outcome.points, depth - 1, limit
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


def estimate_evs(
    score: Score = 0, limit: int = 0, net_ev: bool = True
) -> dict[int, float]:
    """
    Return a mapping from dice count to estimated ev

    net_ev: If True, the ev is the expected net gain. If False, the ev is the expected
            gain including the current score (expected score for the whole turn).
    """
    evs = {}
    for dice_count in range(1, 7):
        evs[dice_count] = estimate_ev(dice_count, score, limit=limit) + (
            0 if net_ev else score
        )
    return evs


def estimate_min_score_for_negative_ev() -> dict[int, int]:
    """
    Return the minimum score you should stop at for a given dice count

    This can be used to play an ev-optimal game
    """
    estimate_evs()  # Ensure the min score lookup is populated
    return MIN_SCORE_FOR_NEGATIVE_EV


def reset_min_score_for_negative_ev() -> None:
    """Reset the minimum score lookup"""
    global MIN_SCORE_FOR_NEGATIVE_EV  # pylint: disable=global-statement
    MIN_SCORE_FOR_NEGATIVE_EV = {i: 10_000_000 for i in range(1, 7)}
