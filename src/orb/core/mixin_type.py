"""Define ModelType metaclass."""


class MixinType(type):
    """Metaclass to define Mixin types."""

    def __new__(cls, clsname: str, superclasses: list, attributes: dict):
        """Generate new Mixin class."""
        return type.__new__(cls, clsname, superclasses, attributes)
