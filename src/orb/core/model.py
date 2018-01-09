"""Define Model class."""

import asyncio
from collections import OrderedDict
from typing import Any, Dict, Tuple

from .collector import Collector
from .collection import Collection
from .context import ReturnType, make_context
from .field import Field
from .model_type import ModelType
from .reference import Reference
from ..exceptions import ReadOnly


class Model(metaclass=ModelType):
    """Define Model class."""

    __abstract__ = True
    __schema__ = None
    __store__ = None
    __view__ = False

    def __init__(
        self,
        values: dict=None,
        state: dict=None,
        **context
    ):
        context.setdefault('store', type(self).__store__)
        self.context = make_context(**context)
        self.__state = {}
        self.__changes = {}
        self.__collections = {}
        self.__references = {}

        # apply base state
        cls = type(self)
        fields, references, collections = self._parse_items(
            state,
            constructor=lambda x: cls(state=x)
        )
        self.__state.update(self.__schema__.default_values)
        self.__state.update(fields)
        self.__references.update(references)
        self.__collections.update(collections)

        # apply overrides
        fields, references, collections = self._parse_items(
            values,
            constructor=lambda x: cls(values=x)
        )
        self.__changes.update(fields)
        self.__references.update(references)
        self.__collections.update(collections)

    def _parse_items(self, values: dict, constructor: callable=None):
        fields = {}
        references = {}
        collections = {}
        if not values:
            return fields, references, collections

        schema = self.__schema__
        for key, value in values.items():
            schema_object = schema[key]
            if isinstance(schema_object, Field):
                if not schema_object.test_flag(Field.Flags.Virtual):
                    fields[key] = value
            elif isinstance(schema_object, Collector):
                collections[key] = schema_object.make_collection(
                    constructor=constructor,
                    records=value,
                    source=self
                )
            elif isinstance(schema_object, Reference):
                model = schema_object.model
                if not isinstance(value, model):
                    references[key] = model(values=value)
                else:
                    references[key] = value

        return fields, references, collections

    async def delete(self, **context):
        """Delete this record from it's store."""
        if type(self).__view__:
            raise ReadOnly(type(self).__name__)
        else:
            context.setdefault('context', self.context)
            delete_context = make_context(**context)
            return await self.context.store.delete_record(self, delete_context)

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
            try:
                result = await self.get_reference(curr_key, default)
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
            collection = await collector.collect(self)
            self.__collections[key] = collection
            return collection

    async def get_key(self):
        """Return the unique key for this model."""
        out = await self.gather(*(f.name for f in self.__schema__.key_fields))
        if len(out) == 1:
            return out[0]
        return out

    async def get_key_dict(self, key_property: str='name') -> dict:
        """Return the key values for this record."""
        out = OrderedDict()
        for field in sorted(self.__schema__.key_fields):
            out[getattr(field, key_property)] = await self.get(field.name)
        return out

    async def get_reference(self, key: str, default: 'Model'=None) -> 'Model':
        """Return the reference for the given key."""
        try:
            return self.__references[key]
        except KeyError:
            ref = self.__schema__.references[key]
            if ref.source:
                field = self.__schema__[ref.source]
                ref_model = field.refers_to_model
                ref_field = field.refers_to_field
                value = await self.get(ref.source)
                if value is not None:
                    reference = await ref_model.fetch({ref_field: value})
                else:
                    reference = None
                self.__references[key] = reference
                return reference
            return None

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

    @property
    def is_new_record(self) -> bool:
        """Return whether or not this record is new or not."""
        for field in self.__schema__.key_fields:
            if self.__state.get(field.name) is not None:
                return False
        return True

    def mark_loaded(self):
        """Stash changes to the local state."""
        self.__state.update(self.__changes)
        self.__changes.clear()

    async def reset(self):
        """Reset the local changes on this model."""
        self.__changes.clear()

    async def save(self, **context):
        """Save this model to the store."""
        if type(self).__view__:
            raise ReadOnly(type(self).__name__)
        elif self.__changes:
            context.setdefault('context', self.context)
            save_context = make_context(**context)
            values = await self.context.store.save_record(self, save_context)
            self.__changes.update(values)
            self.mark_loaded()
            return True
        return False

    async def set(self, key: str, value: Any, ignore_method: bool=False):
        """Set the value for the given key."""
        target_key, _, field_key = key.rpartition('.')
        if target_key:
            target = await self.get(target_key)
            await target.set(field_key, value)
        else:
            schema = self.__schema__
            schema_object = schema[field_key]
            settermethod = schema_object.settermethod
            if settermethod and not ignore_method:
                await settermethod(self, value)
            elif isinstance(schema_object, Reference):
                self.__references[field_key] = value
            elif isinstance(schema_object, Collection):
                self.__collections[field_key] = value
            elif self.__state.get(field_key) is not value:
                self.__changes[field_key] = value
            else:
                self.__changes.pop(field_key)

    async def update(self, values: dict):
        """Update a number of values by the given dictionary."""
        await asyncio.gather(*(self.set(*item) for item in values.items()))

    @classmethod
    async def create(cls, values: dict, **context) -> object:
        """Create a new record in the store with the given state."""
        if cls.__view__:
            raise ReadOnly(cls.__name__)
        else:
            record = cls(values=values, **context)
            await record.save()
            return record

    @classmethod
    async def fetch(cls, key: Any, **context):
        """Fetch a single record from the store for the given key."""
        from .query import Query as Q

        q = Q()
        key_fields = cls.__schema__.key_fields
        if type(key) in (list, tuple):
            if len(key) != len(key_fields):
                raise RuntimeError('Invalid key provided.')
            for i, field in key_fields:
                q &= Q(field.name) == key[i]

        elif type(key) is dict:
            for field, value in key.items():
                q &= Q(field.name) == value

        else:
            if len(key_fields) == 1:
                q |= Q(key_fields[0].name) == key

            for field in cls.__schema__.fields.values():
                if field.test_flag(field.Flags.Keyable):
                    q |= Q(field.name) == key

        context['where'] = q & context.get('where')
        context['limit'] = 1
        context.setdefault('store', cls.__store__)
        fetch_context = make_context(**context)
        records = await fetch_context.store.get_records(cls, fetch_context)
        try:
            record_data = dict(records[0])
        except IndexError:
            return None
        else:
            if fetch_context.returning == ReturnType.Records:
                return cls(state=record_data)
            return record_data

    @classmethod
    def select(cls, **context) -> Collection:
        """Lookup a collection of records from the store."""
        context.setdefault('store', cls.__store__)
        return Collection(
            context=make_context(**context),
            model=cls,
        )

    @classmethod
    def find_model(cls, name):
        """Find subclass model by name."""
        sub_model = cls.registry.get(name)
        if sub_model and issubclass(sub_model, cls):
            return sub_model
        return None
