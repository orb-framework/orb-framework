"""Model class tests."""
import pytest


# define local tests
def test_model_schema_exists(user_model):
    """Test the User model has a schema object."""
    assert user_model.__schema__ is not None


@pytest.mark.asyncio
async def test_model_get_value(make_users):
    """Test getting simple values work."""
    bob = make_users('bob')

    assert await bob.get('id') == 1
    assert await bob.get_value('id') == 1

    with pytest.raises(KeyError):
        assert await bob.get('id2') is None
    with pytest.raises(KeyError):
        assert await bob.get_value('id2') is None


@pytest.mark.asyncio
async def test_model_gather_values(make_users):
    """Test gathering multiple values at one time."""
    bob = make_users('bob')
    assert await bob.gather('id', 'username') == [1, 'bob']


@pytest.mark.asyncio
async def test_model_get_nested_value(make_users):
    """Test getting nested properties."""
    john, jane = make_users('john', 'jane')
    await john.set('manager', jane)
    assert await john.get('manager.username') == 'jane'


@pytest.mark.asyncio
async def test_model_gather_nested_values(make_users):
    """Test gathering multiple values which can be nested."""
    john, jane = make_users('john', 'jane')
    await john.set('manager', jane)
    assert await john.gather('username', 'manager.username') == ['john', 'jane']
