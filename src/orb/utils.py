"""Defines a variety of helper functions."""

from enum import Flag


def ensure_instance_of(obj: object, typ: type) -> object:
    """Ensure obj is of type typ.

    This method will check if the given object is of the given type.  If
    it is, then it will return the object directly, if it is not, then
    it will cast the object as the other type.

    Example:

        from orb.utils import ensure_instance_of

        assert type(ensure_instance_of((1, 2), tuple)) is tuple
        assert type(ensure_instance_of([1, 2], tuple)) is tuple
    """
    if not isinstance(obj, typ):
        return typ(obj)
    return obj


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
