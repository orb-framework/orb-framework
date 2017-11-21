"""Define the Id field type."""
from orb.core.field import Field


class Id(Field):
    """Define Id plugin class."""

    def __init__(self, **kw):
        super().__init__(**kw)

        self.flags |= Field.Flags.Primary
