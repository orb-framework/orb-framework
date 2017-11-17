"""Define Collection class."""

import asyncio
from typing import Any

from ..exceptions import ReadOnly


class Collection:
    """Collection of model instances."""

    RESERVED_WORDS = {
        'count',
        'first',
        'last',
    }

    def __init__(self, state=None):
        self.__state = state

    def __len__(self):
        """Return length of this collection."""
        if self.__state is not None:
            return len(self.__state)
        return 0

    async def get_count(self) -> int:
        """Return the size of the collection."""
        if self.__state is not None:
            return len(self.__state)
        return 0

    async def get(self, key: str, default: Any=None) -> Any:
        """Get a value from the collection."""
        curr_key, _, next_key = key.partition('.')

        if curr_key not in Collection.RESERVED_WORDS:
            return await self.get_values(key, default)

        if curr_key == 'count':
            out = await self.get_count()
        elif curr_key == 'first':
            out = await self.get_first()
        elif curr_key == 'last':
            out = await self.get_last()
        else:
            out = default

        if next_key and out:
            return await out.get(next_key, default)
        return out

    async def get_first(self) -> Any:
        """Return the first record in the collection."""
        if self.__state is not None:
            try:
                return self.__state[0]
            except IndexError:
                return None
        return None

    async def get_last(self) -> Any:
        """Return the last record in the collection."""
        if self.__state is not None:
            try:
                return self.__state[-1]
            except IndexError:
                return None
        return None

    async def get_values(self, key: str, default: Any=None) -> tuple:
        """Return a list of values from each record in the collection."""
        if self.__state is not None:
            return await asyncio.gather(*(
                record.get(key, default) for record in self.__state
            ))
        return tuple()

    async def set(self, key: str, value: Any):
        """Set the value for a given key on each record in the collection."""
        target_key, _, value_key = key.rpartition('.')
        if target_key:
            target = await self.get(target_key)
            return target.set(value_key, value)
        elif value_key in Collection.RESERVED_WORDS:
            raise ReadOnly(value_key)
        elif self.__state:
            await asyncio.gather(*(
                record.set(key, value)
                for record in self.__state
            ))
