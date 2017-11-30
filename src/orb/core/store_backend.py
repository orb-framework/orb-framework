"""Define an abstract backend interface for a store."""
from abc import ABCMeta, abstractmethod
from typing import List, Type


class StoreBackend(metaclass=ABCMeta):
    """Define abstract StoreBackend class to handle specific backend types."""

    @abstractmethod
    async def delete_record(self, record: 'Model', context: 'Context') -> int:
        """Delete the record from the store."""
        pass

    @abstractmethod
    async def delete_collection(
        self,
        collection: 'Collection',
        context: 'Context'
    ) -> int:
        """Delete the collection from the backend."""
        pass

    @abstractmethod
    async def get_records(
        self,
        model: Type['Model'],
        context: 'Context'
    ) -> List[dict]:
        """Get records from the store based on the given context."""
        pass

    @abstractmethod
    async def get_record_count(
        self,
        model: Type['Model'],
        context: 'Context'
    ) -> int:
        """Return the number of records available for the given context."""
        pass

    @abstractmethod
    async def save_record(self, record: 'Model', context: 'Context') -> dict:
        """Save the record to the store backend."""
        pass

    @abstractmethod
    async def save_collection(
        self,
        collection: 'Collection',
        context: 'Context'
    ) -> list:
        """Save the collection to the store backend."""
        pass
