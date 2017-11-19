"""Define Model class."""

import asyncio
from typing import Any, Dict, Tuple

from .collection import Collection
from .model_type import ModelType
from ..exceptions import ReadOnly


class Model(metaclass=ModelType):
    """Define Model class."""

    __abstract__ = True
    __schema__ = None
    __store__ = None
    __view__ = False

    def __init__(self, key: Any=None, values: dict=None, state: dict=None):
        self.__state = {}
        self.__changes = {}
        self.__collections = {}

        # apply base state
        cls = type(self)
        fields, collections = self._parse_items(
            state,
            constructor=lambda x: cls(state=x)
        )
        self.__state.update(self.__schema__.default_values)
        self.__state.update(fields)
        self.__collections.update(collections)

        # apply overrides
        fields, collections = self._parse_items(
            values,
            constructor=lambda x: cls(values=x)
        )
        self.__changes.update(fields)
        self.__collections.update(collections)

    def _parse_items(self, values: dict, constructor: callable=None):
        if not values:
            return {}, {}

        schema = self.__schema__
        fields = {}
        collections = {}
        for key, value in values.items():
            field = schema.fields.get(key)
            if field:
                if not field.test_flag(field.Flags.Virtual):
                    fields[key] = value
            else:
                collector = self.__schema__.collectors[key]
                collections[key] = collector.get_collection(
                    records=value,
                    constructor=constructor
                )

        return fields, collections

    async def delete(self):
        """Delete this record from it's store."""
        if type(self).__view__:
            raise ReadOnly(type(self).__name__)
        else:
            return await self.__store__.delete_record(self)

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

        if next_key and result is not None:
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
                return self.__state.get(key, default)

    @property
    def local_changes(self) -> Dict[str, Tuple[Any, Any]]:
        """Return a set of changes for this model.

        This method will gather all the local changes for the record,
        modifications that have been made to the original state,
        and return them as a key / value pair for the name of
        the field, and the (old, new) value.
        """
        return {
            key: (self.__state.get(key), self.__changes[key])
            for key in self.__changes
        }

    def mark_loaded(self):
        """Stash changes to the local state."""
        self.__state.update(self.__changes)
        self.__changes.clear()

    async def reset(self):
        """Reset the local changes on this model."""
        self.__changes.clear()

    async def save(self):
        """Save this model to the store."""
        if type(self).__view__:
            raise ReadOnly(type(self).__name__)
        elif self.__changes:
            values = await self.__store__.save_record(self)
            self.__changes.update(values)
            self.mark_loaded()
            return True
        return False

    async def set(self, key: str, value: Any):
        """Set the value for the given key."""
        target_key, _, field_key = key.rpartition('.')
        if not target_key:
            try:
                field = self.__schema__.fields[field_key]
            except KeyError:
                coll = self.__schema__.collectors[field_key]
                if coll and coll.settermethod:
                    await coll.settermethod(self, value)
                self.__collections[key] = value
            else:
                if field.settermethod:
                    return await field.settermethod(self, value)
                elif self.__state.get(field_key) is not value:
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
    async def create(cls, values: dict) -> object:
        """Create a new record in the store with the given state."""
        if cls.__view__:
            raise ReadOnly(cls.__name__)
        else:
            record = cls(values=values)
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

    @classmethod
    def find_model(cls, name):
        """Find subclass model by name."""
        for sub_cls in cls.__subclasses__():
            if sub_cls.__name__ == name:
                return sub_cls
            found = sub_cls.find_model(name)
            if found:
                return found
        return None
