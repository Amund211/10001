"""
Tests for roll scoring
"""

from dice_10001.scoring import (
    DiceCount,
    Outcome,
    _get_frequencies,
    _get_keep_counts,
    get_all_outcomes,
    get_best_outcomes,
    is_bust,
)


def make_tuple(*outcomes: tuple[int, int]) -> tuple[Outcome, ...]:
    """
    Make a tuple of outcome instances from a list of tuples

    Argument order follows that of Outcome: points, dice
    """
    return tuple(Outcome(*outcome) for outcome in outcomes)


def make_set(*outcomes: tuple[int, int]) -> set[Outcome]:
    """
    Make a set of outcome instances from a list of tuples

    Argument order follows that of Outcome: points, dice
    """
    return set(Outcome(*outcome) for outcome in outcomes)


def test_frequencies() -> None:
    """Assert that the frequency table is generated correctly"""
    cases = (
        ((1, 2, 3, 4, 5, 6), {k: 1 for k in range(1, 7)}),
        ((2, 2, 3, 3, 5, 5), {2: 2, 3: 2, 5: 2}),
        ((2, 3, 5, 5, 5), {2: 1, 3: 1, 5: 3}),
        ((6,), {6: 1}),
        ((6, 6, 6, 6, 6), {6: 5}),
        # Rolls should be sorted, but this helper does not require it
        ((6, 3, 1, 5, 1), {1: 2, 3: 1, 5: 1, 6: 1}),
    )

    for roll, freq in cases:
        assert _get_frequencies(roll) == freq


def test_keep_counts() -> None:
    """Assert that the keep counts are generated correctly"""
    cases = (
        # (eye_count, count), keep_counts
        ((5, 6), range(7)),
        ((5, 2), range(3)),
        ((1, 4), range(5)),
        ((2, 4), (0, 3, 4)),
        ((4, 2), (0,)),
        ((6, 1), (0,)),
    )

    for (eye_count, count), keep_counts in cases:
        assert tuple(_get_keep_counts(eye_count, count)) == tuple(keep_counts)


def test_get_all_outcomes() -> None:
    """Assert that all generated outcomes are correct"""
    cases = (
        ((1, 2, 3, 4, 5, 6), make_set((2000, 6), (150, 4), (100, 5), (50, 5))),
        ((2, 2, 3, 3, 5, 5), make_set((1500, 6), (100, 4), (50, 5))),
        ((2, 3, 5, 5, 5), make_set((500, 2), (100, 3), (50, 4))),
        ((6,), make_set((0, DiceCount.BUST))),
        ((6, 6), make_set((0, DiceCount.BUST))),
        ((1, 5), make_set((50, 1), (100, 1), (150, 6))),
        ((1, 3, 5), make_set((50, 2), (100, 2), (150, 1))),
        ((2, 2, 5, 6), make_set((50, 3))),
        ((2, 2, 3, 3, 4, 6), make_set((0, DiceCount.BUST))),
        ((6, 6, 6, 6, 6), make_set((2400, 6), (1200, 1), (600, 2))),
        ((1, 1, 2, 2, 3), make_set((100, 4), (200, 3))),
        ((1, 1, 2, 2, 3, 5), make_set((50, 5), (100, 5), (200, 4), (150, 4), (250, 3))),
        ((1, 1, 2, 2, 3, 3), make_set((100, 5), (200, 4), (1500, 6))),
        (
            (1, 1, 2, 3, 3, 3),
            make_set((100, 5), (200, 4), (300, 3), (400, 2), (500, 1)),
        ),
        (
            (1, 1, 1, 5, 5, 5),
            make_set(
                (50, 5),
                (2 * 50, 4),
                (500, 3),
                (100, 5),
                (100 + 50, 4),
                (100 + 2 * 50, 3),
                (100 + 500, 2),
                (2 * 100, 4),
                (2 * 100 + 50, 3),
                (2 * 100 + 2 * 50, 2),
                (2 * 100 + 500, 1),
                (1000, 3),
                (1000 + 50, 2),
                (1000 + 2 * 50, 1),
                (1000 + 500, 6),
            ),
        ),
    )

    for roll, outcomes in cases:
        assert get_all_outcomes(roll) == outcomes, f"Failed on roll {roll}"


def test_get_best_outcomes() -> None:
    """Assert that generated best outcomes are correct"""
    cases = (
        ((1, 2, 3, 4, 5, 6), make_tuple((2000, 6), (150, 4), (100, 5))),
        ((2, 2, 3, 3, 5, 5), make_tuple((1500, 6), (100, 4), (50, 5))),
        ((2, 3, 5, 5, 5), make_tuple((500, 2), (100, 3), (50, 4))),
        ((6,), make_tuple((0, DiceCount.BUST))),
        ((6, 6), make_tuple((0, DiceCount.BUST))),
        ((1, 5), make_tuple((100, 1), (150, 6))),
        ((1, 3, 5), make_tuple((100, 2), (150, 1))),
        ((2, 2, 5, 6), make_tuple((50, 3))),
        ((2, 2, 3, 3, 4, 6), make_tuple((0, DiceCount.BUST))),
        ((6, 6, 6, 6, 6), make_tuple((2400, 6), (1200, 1), (600, 2))),
        ((1, 1, 2, 2, 3), make_tuple((100, 4), (200, 3))),
        ((1, 1, 2, 2, 3, 5), make_tuple((100, 5), (200, 4), (250, 3))),
        ((1, 1, 2, 2, 3, 3), make_tuple((100, 5), (200, 4), (1500, 6))),
        (
            (1, 1, 2, 3, 3, 3),
            make_tuple((100, 5), (200, 4), (300, 3), (400, 2), (500, 1)),
        ),
        (
            (1, 1, 1, 5, 5, 5),
            make_tuple(
                (1000 + 500, 6),
                (100, 5),
                (2 * 100, 4),
                (1000, 3),
                (1000 + 50, 2),
                (1000 + 2 * 50, 1),
            ),
        ),
    )

    for roll, outcomes in cases:
        assert get_best_outcomes(roll) == outcomes, f"Failed on roll {roll}"


def test_is_bust() -> None:
    """Test that the `is_bust` helper works"""
    cases = (
        ((6,), True),
        ((6, 6), True),
        ((2, 4, 6), True),
        ((2, 4, 4, 6), True),
        ((2, 4, 4, 6, 6), True),
        ((2, 2, 3, 3, 4, 6), True),
        ((1, 2, 3, 4, 5, 6), False),
        ((2, 2, 2, 3, 4, 6), False),
        ((1, 2, 3, 4, 5, 6), False),
        ((2, 2, 3, 3, 5, 5), False),
        ((2, 2, 3, 3, 6, 6), False),
        ((2, 3, 5, 5, 5), False),
        ((1, 5), False),
        ((1, 3, 5), False),
        ((2, 2, 5, 6), False),
        ((6, 6, 6, 6, 6), False),
        ((1, 1, 2, 2, 3), False),
        ((1, 1, 2, 2, 3, 5), False),
        ((1, 1, 2, 2, 3, 3), False),
        ((1, 1, 2, 3, 3, 3), False),
        ((1, 1, 1, 5, 5, 5), False),
    )

    for roll, bust in cases:
        assert is_bust(roll) == bust, f"Failed on roll {roll}"
