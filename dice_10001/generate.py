"""
Module providing functions for generating rolls
"""
import operator
from functools import reduce
from itertools import groupby
from math import factorial


def _calculate_weight(roll):
    """Return the amount of permutations of the sorted `roll`"""
    return factorial(len(roll)) // reduce(
        operator.mul, (factorial(len(tuple(g))) for k, g in groupby(roll))
    )


def generate_rolls(amt_dice):
    """Generate rolls and corresponding weights in lexicographic order"""
    assert 0 < amt_dice <= 6

    roll = [1] * amt_dice
    while True:
        yield tuple(roll), _calculate_weight(roll)
        roll[-1] += 1
        # Loop through all indicies in reverse order
        for i in range(amt_dice - 1, -1, -1):
            if roll[i] == 7 and i != 0:
                # For all but the first index: carry the one once we reach 7
                roll[i - 1] += 1
            elif roll[i] != 7:
                # Nothing more to carry => set the value at all later indicies
                # to the value at this index. This gives all ordered selections.
                for j in range(i + 1, amt_dice):
                    roll[j] = roll[i]
                break
            # else: roll[i] = 7 and i = 0 => finished
            # Since i = 0 this is caught by the else clause of the for loop
        else:
            return
