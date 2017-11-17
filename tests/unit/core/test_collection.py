"""Tests for the Collection class."""
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize('records,expected_count', (
    (None, 0),
    ([], 0),
    ([1, 2], 2),
))
async def test_collection_counter(records, expected_count):
    """Test counter function."""
    from orb import Collection

    coll = Collection(records)
    count = await coll.get_count()
    length = len(coll)

    assert count == length == expected_count
