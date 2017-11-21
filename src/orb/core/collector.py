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

    async def collect_by_record(self, record: Model) -> Collection:
        """Create collection for specific record."""
        if self.gettermethod:
            return await self.gettermethod(record)
        return Collection(
            collector=self,
            model=self._model,
            source=record,
        )

    def getter(self, func: callable) -> callable:
        """Assign gettermethod via decorator."""
        self.gettermethod = func
        return func

    def get_collection(
        self,
        records: Iterable=None,
        constructor: callable=None
    ) -> Collection:
        """Create new collection instance from value."""
        if isinstance(records, Collection):
            return records

        model = self.model
        constructor = constructor or (lambda x: model(values=x))
        if model is not None and records:
            records = [
                constructor(record) if type(record) is dict else record
                for record in records
            ]
            return Collection(
                collector=self,
                model=self._model,
                records=records,
            )
        return Collection(
            collector=self,
            model=self._model,
            records=records,
        )

    @property
    def model(self):
        """Return Model class instance associated with this collector."""
        if type(self._model) is str:
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
