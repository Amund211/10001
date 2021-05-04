from math import comb

from dice_10001.generate import generate_rolls


def test_weightsum():
    for amt_dice in range(1, 7):
        weightsum = sum(weight for roll, weight in generate_rolls(amt_dice))
        assert weightsum == 6 ** amt_dice


def test_unique_rolls():
    for amt_dice in range(1, 7):
        amt_unique = sum(1 for roll, weight in generate_rolls(amt_dice))
        assert amt_unique == comb(6 + amt_dice - 1, amt_dice)
