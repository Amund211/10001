"""
Tests for roll generation
"""
from math import comb

from dice_10001.generate import generate_rolls


def test_weightsum():
    """Assert that the sum of the weights are correct"""
    for amt_dice in range(1, 7):
        weightsum = sum(weight for roll, weight in generate_rolls(amt_dice))
        assert weightsum == 6 ** amt_dice


def test_amount_unique_rolls():
    """Assert that the amount of unique rolls is correct"""
    for amt_dice in range(1, 7):
        amt_unique = sum(1 for roll, weight in generate_rolls(amt_dice))
        assert amt_unique == comb(6 + amt_dice - 1, amt_dice)


def test_rolls_are_sorted():
    """Assert that the rolls are sorted"""
    for amt_dice in range(1, 7):
        assert all(
            tuple(sorted(roll)) == roll for roll, weight in generate_rolls(amt_dice)
        )


def test_rolls_are_unique():
    """Assert that the rolls are unique"""
    for amt_dice in range(1, 7):
        amt_unique = len(set(roll for roll, weight in generate_rolls(amt_dice)))
        amt = sum(1 for roll, weight in generate_rolls(amt_dice))
        assert amt_unique == amt
