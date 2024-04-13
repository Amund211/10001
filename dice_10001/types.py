"""
Module providing type aliases
"""

from collections.abc import Collection
from dataclasses import dataclass
from enum import Enum, unique

Roll = Collection[int]

Score = int


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


@dataclass(frozen=True, slots=True, order=True)
class Outcome:
    """
    A possible outcome of a roll

    Stores the points gained from the roll, and the amount of remaining dice
    """

    points: Score
    dice: int
