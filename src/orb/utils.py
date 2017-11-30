"""Defines a variety of helper functions."""

try:  # python 3.6
    from enum import Flag
except ImportError:  # python 3.5
    from aenum import Flag


def enum_from_set(flags: Flag, options: set) -> Flag:
    """Convert a set of strings to a bitwise flag instance.

    Example:

        from enum import Flag, auto
        from orb.utils import enum_from_set

        class MyFlag(Flag):
            A = auto()
            B = auto()

        assert enum_from_set(MyFlag, {'A', 'B'}) == MyFlag.A | MyFlag.B
        assert enum_from_set(MyFlag, {}) == MyFlag(0)
        assert enum_from_set(MyFlag, {'A'}) == MyFlag.A
    """
    out = flags(0)
    for option in options:
        out |= getattr(flags, option)
    return out
