"""
Module provinding functions for estimating the chance to reach a given score
"""

from functools import cache

from dice_10001.scoring import best_outcomes_per_dice_count
from dice_10001.types import DiceCount, Score


@cache
def estimate_chance_to_reach(
    dice_count: int, score: Score, target: int, depth: int
) -> float:
    """
    Estimate the chance to reach the target value from (dice_count, score)
    """
    if score >= target:
        return 1
    if depth == 0:
        return 0

    outcomes_per_dice_count = best_outcomes_per_dice_count()[dice_count]
    total_weight = 0
    total_score = 0.0
    for outcomes, weight in outcomes_per_dice_count.items():
        total_weight += weight

        if outcomes[0].dice == DiceCount.BUST:
            assert len(outcomes) == 1
            continue

        max_ev = max(
            estimate_chance_to_reach(
                outcome.dice, score + outcome.points, target, depth - 1
            )
            for outcome in outcomes
        )

        total_score += max_ev * weight

    return total_score / total_weight


def estimate_chances_to_reach(score: Score = 0, target: int = 1000) -> dict[int, float]:
    """Return a mapping from dice count to estimated ev"""
    evs = {}
    for dice_count in range(1, 7):
        evs[dice_count] = estimate_chance_to_reach(
            dice_count, score, target=target, depth=target // 50 + 1
        )
    return evs
