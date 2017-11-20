"""Define Collection class."""

import asyncio
from typing import Any

from .context import make_context
from ..exceptions import ReadOnly


class Collection:
    """Collection of model instances."""

    RESERVED_WORDS = {
        'count',
        'first',
        'last',
    }

    def __init__(
        self,
        *,
        collector=None,
        context=None,
        model=None,
        records=None,
        source=None,
        store=None,
        target=None
    ):
        self.context = context
        self.collector = collector
        self._model = model
        self._records = records
        self.source = source
        self.store = store
        self.target = target

    def __len__(self):
        """Return length of this collection."""
        if self._records is not None:
            return len(self._records)
        return 0

    async def add(self, record: object) -> object:
        """Add given record to the collection."""
        if self._records and record:
            self._records.append(record)

        if self.collector and record:
            return await self.collector.add_record(self, record)

        return None

    async def create(self, values: dict) -> object:
        """Create a new record for this collection."""
        if self.collector:
            return await self.collector.create_record(values)

        elif self._records is not None:
            record = self.model(values=values)
            self._records.append(record)
            return record

        return None

    async def delete(self) -> int:
        """Delete the records in this collection from the store."""
        store = self.store or self.model.__store__
        return await store.delete_collection(self)

    async def get_count(self) -> int:
        """Return the size of the collection."""
        if self._records is not None:
            return len(self._records)
        return 0

    async def get(self, key: str, default: Any=None) -> Any:
        """Get a value from the collection."""
        curr_key, _, next_key = key.partition('.')

        if curr_key == 'count':
            out = await self.get_count()
        elif curr_key == 'first':
            out = await self.get_first()
        elif curr_key == 'last':
            out = await self.get_last()
        else:
            return await self.get_values(key, default)

        if next_key and out:
            return await out.get(next_key, default)
        return out

    async def get_first(self) -> Any:
        """Return the first record in the collection."""
        if self._records is not None:
            try:
                return self._records[0]
            except IndexError:
                return None
        return None

    async def get_last(self) -> Any:
        """Return the last record in the collection."""
        if self._records is not None:
            try:
                return self._records[-1]
            except IndexError:
                return None
        return None

    async def get_values(self, key: str, default: Any=None) -> tuple:
        """Return a list of values from each record in the collection."""
        if self._records is not None:
            return await asyncio.gather(*(
                record.get(key, default) for record in self._records
            ))
        return []

    def refine(self, **context):
        """Refine this collection down with a new context."""
        context.setdefault('context', self.context)
        new_context = make_context(**context)
        return Collection(
            context=new_context,
            collector=self.collector,
            model=self._model,
            source=self.source,
            store=self.store,
            target=self.target
        )

    @property
    def model(self):
        """Return the model the records in this collection represent."""
        from .model import Model
        if type(self._model) is str:
            return Model.find_model(self._model)
        return self._model

    async def save(self) -> int:
        """Delete the records in this collection from the store."""
        store = self.store or self.model.__store__
        return await store.save_collection(self)

    async def set(self, key: str, value: Any):
        """Set the value for a given key on each record in the collection."""
        if key in Collection.RESERVED_WORDS:
            raise ReadOnly(key)
        elif self._records:
            is_iterable = type(value) in (list, tuple)
            await asyncio.gather(*(
                record.set(key, value[i] if is_iterable else value)
                for i, record in enumerate(self._records)
            ))
