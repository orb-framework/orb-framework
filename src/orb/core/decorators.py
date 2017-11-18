"""Define common decorator method."""


def virtual(cls, *args, **kw):
    """Generate a virtual member of the given class bound to a function."""
    def wrapper(func):
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
