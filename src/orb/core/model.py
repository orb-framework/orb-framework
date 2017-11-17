"""Define Model class."""

import asyncio
from typing import Any, Dict, Tuple

from .collection import Collection
from .model_type import ModelType
from ..exceptions import ReadOnly
from ..utils import ensure_instance_of


class Model(metaclass=ModelType):
    """Define Model class."""

    __abstract__ = True
    __schema__ = None
    __store__ = None
    __view__ = False

    def __init__(self, key: Any=None, state: dict=None):
        defaults = self.__schema__.default_state
        defaults.update(state or {})
        self.__fields = {
            f: defaults[f] for f in self.__schema__.fields if f in defaults
        }
        self.__changes = {}
        self.__collections = {
            c: ensure_instance_of(defaults[c], Collection)
            for c in self.__schema__.collectors if c in defaults
        }

    async def delete(self):
        """Delete this record from it's store."""
        if type(self).__view__:
            raise ReadOnly(type(self).__name__)
        else:
            self.__store__.delete_record(self)

    async def gather(self, *keys, state: dict=None) -> tuple:
        """Return a list of values for the given keys."""
        state = state or {}
        return await asyncio.gather(*(
            self.get(key, default=state.get(key))
            for key in keys
        ))

    async def get(self, key: str, default: Any=None) -> Any:
        """Return a single value from this record."""
        curr_key, _, next_key = key.partition('.')
        try:
            result = await self.get_value(curr_key, default)
        except KeyError:
            result = await self.get_collection(curr_key, default)

        if next_key and result:
            return await result.get(next_key)
        return result

    async def get_collection(self, key: str, default: Any=None) -> Any:
        """Return a collection from this record."""
        if key not in self.__schema__.collectors:
            raise KeyError(key)
        try:
            return self.__collections[key]
        except KeyError:
            collector = self.__schema__.collectors[key]
            collection = await collector.get_by_record(self)
            self.__collections[key] = collection
            return collection

    async def get_value(self, key: str, default: Any=None) -> Any:
        """Return the record's value for a given field."""
        field = self.__schema__.fields[key]
        if field.gettermethod is not None:
            return await field.gettermethod(self)
        else:
            try:
                return self.__changes[key]
            except KeyError:
                return self.__fields.get(key, default)

    def local_changes(self) -> Dict[str, Tuple[Any, Any]]:
        """Return a set of changes for this model.

        This method will gather all the local changes for the record,
        modifications that have been made to the original state,
        and return them as a key / value pair for the name of
        the field, and the (old, new) value.
        """
        return {
            key: (self.__fields[key], self.__changes[key])
            for key in self.__changes
        }

    async def save(self):
        """Save this model to the store."""
        self.__store__.save_record(self)

    async def set(self, key: str, value: Any):
        """Set the value for the given key."""
        target_key, _, field_key = key.rpartition('.')
        if not target_key:
            field = self.__schema__.fields[field_key]

            if field.settermethod:
                return field.settermethod(self, field_key, value)
            elif self.__fields[field_key] is not value:
                self.__changes[field_key] = value
            else:
                self.__changes.pop(field_key)
        else:
            target = await self.get(target_key)
            await target.set(field_key, value)

    async def update(self, values: dict):
        """Update a number of values by the given dictionary."""
        await asyncio.gather(*(self.set(*item) for item in values.items()))

    @classmethod
    async def create(cls, state: dict) -> object:
        """Create a new record in the store with the given state."""
        if cls.__view__:
            raise ReadOnly(cls.__name__)
        else:
            record = cls(state=state)
            await record.save()
            return record

    @classmethod
    async def fetch(cls, key: Any):
        """Fetch a single record from the store for the given key."""
        pass

    @classmethod
    async def select(cls) -> Collection:
        """Lookup a collection of records from the store."""
        pass
