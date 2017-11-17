"""Define Collector class."""

from .collection import Collection
from .model import Model


class Collector:
    """Class to generate a collection from a record."""

    def __init__(
        self,
        *,
        code: str=None,
        name: str=None,
    ):
        self.code = code
        self.name = name

    async def get_by_record(self, record: Model) -> Collection:
        """Create collection for specific record."""
        return Collection()
