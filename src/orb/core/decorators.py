"""Define common decorator method."""


class value_literal:
    """Define literal valute to be used in the backend."""

    def __init__(self, value):
        self.literal_value = value

    def __eq__(self, other):
        """Check if this literal value equals the provided other value."""
        return self.literal_value == other


def virtual(cls, *args, **kw):
    """Generate a virtual member of the given class bound to a function."""
    def wrapper(func: callable):
        kw.setdefault('name', func.__name__)
        kw.setdefault('gettermethod', func)

        flags = kw.get('flags', 0)
        flags |= cls.Flags.Virtual
        kw['flags'] = flags

        obj = cls(*args, **kw)
        func.__virtual__ = obj
        func.getter = obj.getter
        func.setter = obj.setter
        func.query = obj.query
        return func
    return wrapper
