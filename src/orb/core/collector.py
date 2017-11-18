"""Define Collector class."""

from enum import IntFlag, auto
from typing import Iterable

from .collection import Collection
from .model import Model


class CollectorFlags(IntFlag):
    """Flags for the Collector class."""

    Virtual = auto()


class Collector:
    """Class to generate a collection from a record."""

    Flags = CollectorFlags

    def __init__(
        self,
        *,
        code: str=None,
        flags: CollectorFlags=CollectorFlags(0),
        gettermethod: callable=None,
        model: str=None,
        name: str=None,
        querymethod: callable=None,
        settermethod: callable=None,
    ):
        self.code = code
        self.gettermethod = gettermethod
        self._model = model
        self.name = name
        self.querymethod = querymethod
        self.settermethod = settermethod

    def getter(self, func: callable) -> callable:
        """Assign gettermethod via decorator."""
        self.gettermethod = func
        return func

    async def get_by_record(self, record: Model) -> Collection:
        """Create collection for specific record."""
        if self.gettermethod:
            return await self.gettermethod(record)
        return Collection()

    def make_collection(
        self,
        value: Iterable,
        as_state: bool=False
    ) -> Collection:
        """Create new collection instance from value."""
        if isinstance(value, Collection):
            return value

        model = self.model
        if model is not None:
            key = 'state' if as_state else 'values'
            return Collection([
                data if type(data) is model else model(**{key: data})
                for data in value
            ])
        return Collection(value)

    @property
    def model(self):
        """Return Model class instance associated with this collector."""
        if self._model:
            return Model.find_model(self._model)
        return None

    def query(self, func: callable) -> callable:
        """Assign querymethod via decorator."""
        self.querymethod = func
        return func

    def setter(self, func: callable) -> callable:
        """Assign settermethod via decorator."""
        self.settermethod = func
        return func
