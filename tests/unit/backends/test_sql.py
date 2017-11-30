"""Define tests for the SQL based backend stores."""
import pytest

from .sql import SQL_ENGINES


@pytest.fixture
def mock_sql_backend(mocker):
    """Define mock sql backend instance."""
    def _wrapper(engine, side_effect=None):
        from orb import Store
        backend = engine.make_backend()
        patch = mocker.patch.object(
            backend,
            side_effect.__name__,
            side_effect=side_effect
        )
        return Store(backend=backend), patch
    return _wrapper


@pytest.mark.asyncio
@pytest.mark.parametrize('name,engine', SQL_ENGINES.items())
async def test_sql_delete_record_by_key_field(
    mock_sql_backend,
    name,
    engine
):
    """Test the SQL engine deletes a record by unique field."""
    from orb import Model, Field

    class User(Model):
        id = Field(flags=Field.Flags.Key)

    async def execute(sql, *values):
        return 0

    store, mock = mock_sql_backend(engine, side_effect=execute)
    with store:
        u = User(values={'id': 1})
        result = await u.delete()
        mock.assert_called_with(
            engine.DELETE_RECORD_BY_KEY_FIELD.format(
                namespace=store.backend.default_namespace,
                table='users',
                column='id'
            ),
            1,
        )
        assert result == 0


@pytest.mark.asyncio
@pytest.mark.parametrize('name,engine', SQL_ENGINES.items())
async def test_sql_delete_record_by_key_index(
    mock_sql_backend,
    name,
    engine
):
    """Test the SQL engine deletes a record by unique index."""
    from orb import Model, Field, Index

    class GroupUser(Model):
        group_id = Field()
        user_id = Field()

        by_group_and_user = Index(('group_id', 'user_id'), flags={'Key'})

    async def execute(sql, *values):
        return 0

    store, mock = mock_sql_backend(engine, side_effect=execute)
    with store:
        u = GroupUser(values={'group_id': 1, 'user_id': 2})
        result = await u.delete()
        mock.assert_called_with(
            engine.DELETE_RECORD_BY_KEY_INDEX.format(
                namespace=store.backend.default_namespace,
                table='group_users',
                column_a='group_id',
                column_b='user_id'
            ),
            1,
            2
        )
        assert result == 0


@pytest.mark.asyncio
@pytest.mark.parametrize('name,engine', SQL_ENGINES.items())
async def test_sql_delete_record_from_namespace(
    mock_sql_backend,
    name,
    engine
):
    """Test the SQL engine deletes a record from a given namespace."""
    from orb import Model, Field

    class User(Model):
        id = Field(flags=Field.Flags.Key)

    async def execute(sql, *values):
        return 0

    store, mock = mock_sql_backend(engine, side_effect=execute)
    with store:
        u = User(values={'id': 1})
        result = await u.delete(namespace='auth')
        mock.assert_called_with(
            engine.DELETE_RECORD_BY_KEY_FIELD.format(
                namespace='auth',
                table='users',
                column='id'
            ),
            1
        )
        assert result == 0


@pytest.mark.asyncio
@pytest.mark.parametrize('name,engine', SQL_ENGINES.items())
async def test_sql_delete_record_with_translation(
    mock_sql_backend,
    name,
    engine
):
    """Test the SQL engine delete method with translations."""
    from orb import Model, Field

    class Page(Model):
        id = Field(flags=Field.Flags.Key)
        content = Field(flags=Field.Flags.Translatable)

    async def execute(sql, *values):
        return 0

    store, mock = mock_sql_backend(engine, side_effect=execute)
    with store:
        p = Page(values={'id': 1})
        result = await p.delete()
        mock.assert_called_with(
            engine.DELETE_I18N_RECORD_BY_KEY_FIELD.format(
                namespace=store.backend.default_namespace,
                table='pages',
                column='id'
            ),
            1
        )
        assert result == 0


@pytest.mark.asyncio
@pytest.mark.parametrize('name,engine', SQL_ENGINES.items())
async def test_sql_insert_record(
    mock_sql_backend,
    name,
    engine
):
    """Test SQL engine is able to insert record."""
    from orb import Model, Field

    class User(Model):
        id = Field(flags=Field.Flags.Key)
        first_name = Field()
        last_name = Field()
        username = Field()

    async def execute(sql, *values):
        return {'id': 1}

    store, mock = mock_sql_backend(engine, side_effect=execute)
    with store:
        u = User(values={
            'first_name': 'Bob',
            'last_name': 'Dole',
            'username': 'bob'
        })
        assert await u.get('id') is None
        result = await u.save()
        mock.assert_called_with(
            engine.INSERT_RECORD.format(
                namespace=store.backend.default_namespace,
                table='users',
                column_a='first_name',
                column_b='last_name',
                column_c='username'
            ),
            'Bob',
            'Dole',
            'bob'
        )
        assert await u.get('id') == 1
        assert result is True


@pytest.mark.asyncio
@pytest.mark.parametrize('name,engine', SQL_ENGINES.items())
async def test_sql_insert_i18n_record(
    mock_sql_backend,
    name,
    engine
):
    """Test SQL engine is able to insert translatable record."""
    from orb import Model, Field

    class Page(Model):
        id = Field(flags={'Key'})
        code = Field()
        title = Field(flags={'Translatable'})
        content = Field(flags={'Translatable'})

    async def execute(sql, *values):
        return {'id': 1}

    store, mock = mock_sql_backend(engine, side_effect=execute)
    with store:
        p = Page(values={
            'code': 'some-page',
            'title': 'Some Page',
            'content': 'Some Content'
        })
        assert await p.get('id') is None
        result = await p.save()
        mock.assert_called_with(
            engine.INSERT_I18N_RECORD.format(
                namespace=store.backend.default_namespace,
                table='pages',
                column_a='code',
                column_b='title',
                column_c='content'
            ),
            'some-page',
            'en_US',
            'Some Page',
            'Some Content'
        )
        assert await p.get('id') == 1
        assert result is True


@pytest.mark.asyncio
@pytest.mark.parametrize('name,engine', SQL_ENGINES.items())
async def test_sql_fetch_record_by_key_field(mock_sql_backend, name, engine):
    """Test SQL engine getting a single record by field."""
    from orb import Model, Field

    class User(Model):
        id = Field(flags={'Key'})
        username = Field()

    async def fetch(sql, *values):
        return [{'id': 1, 'username': 'bob'}]

    store, mock = mock_sql_backend(engine, side_effect=fetch)
    with store:
        u = await User.fetch(1)
        assert await u.get('id') == 1
        assert await u.get('username') == 'bob'
        mock.assert_called_with(
            engine.GET_RECORD_BY_KEY_FIELD.format(
                namespace=store.backend.default_namespace,
                table='users',
                column_a='id',
                column_b='username',
            ),
            1
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('name,engine', SQL_ENGINES.items())
async def test_sql_fetch_record_by_key_index(mock_sql_backend, name, engine):
    """Test SQL engine getting a single record by index."""
    from orb import Model, Field, Index
    from orb.core.collection import UNDEFINED

    class User(Model):
        first_name = Field()
        last_name = Field()
        username = Field()

        by_first_and_last_name = Index(
            ('first_name', 'last_name'),
            flags={'Key'}
        )

    async def fetch(sql, *values):
        return [{'first_name': 'Bob', 'last_name': 'Smith', 'username': 'bob'}]

    store, mock = mock_sql_backend(engine, side_effect=fetch)
    with store:
        all_users = User.select()
        u = await all_users.get_first()
        mock.assert_called_with(
            engine.GET_RECORD_BY_KEY_INDEX.format(
                namespace=store.backend.default_namespace,
                table='users',
                column_a='first_name',
                column_b='last_name',
                column_c='username'
            )
        )
        assert await u.get('first_name') == 'Bob'
        assert await u.get('last_name') == 'Smith'
        assert await u.get('username') == 'bob'
        assert all_users._first is u
        assert all_users._last is UNDEFINED
        assert all_users._records is None


@pytest.mark.asyncio
@pytest.mark.parametrize('name,engine', SQL_ENGINES.items())
async def test_sql_get_record_with_column_as(
    mock_sql_backend,
    name,
    engine
):
    """Test SQL engine getting the first record of a collection."""
    from orb import Model, Field

    class User(Model):
        id = Field(flags={'Key'})
        username = Field(code='name')

    async def fetch(sql, *values):
        return [{'id': 1, 'username': 'bob'}]

    store, mock = mock_sql_backend(engine, side_effect=fetch)
    with store:
        u = await User.fetch(1)
        assert await u.get('id') == 1
        assert await u.get('username') == 'bob'
        mock.assert_called_with(
            engine.GET_RECORD_WITH_COLUMN_AS.format(
                namespace=store.backend.default_namespace,
                table='users',
                column_a='id',
                column_b='name',
                column_b_as='username'
            ),
            1
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('name,engine', SQL_ENGINES.items())
async def test_sql_get_first_record(mock_sql_backend, name, engine):
    """Test SQL engine getting the first record of a collection."""
    from orb import Model, Field
    from orb.core.collection import UNDEFINED

    class User(Model):
        id = Field(flags={'Key'})
        username = Field()

    async def fetch(sql, *values):
        return [{'id': 1, 'username': 'bob'}]

    store, mock_fetch = mock_sql_backend(engine, side_effect=fetch)
    with store:
        all_users = User.select()
        u = await all_users.get_first()
        mock_fetch.assert_called_with(
            engine.GET_FIRST_RECORD.format(
                namespace=store.backend.default_namespace,
                table='users',
                column_a='id',
                column_b='username'
            )
        )
        assert await u.get('id') == 1
        assert await u.get('username') == 'bob'
        assert all_users._first is u
        assert all_users._last is UNDEFINED
        assert all_users._records is None


@pytest.mark.asyncio
@pytest.mark.parametrize('name,engine', SQL_ENGINES.items())
async def test_sql_get_last_record(mock_sql_backend, name, engine):
    """Test SQL engine getting last record from a collection."""
    from orb import Model, Field
    from orb.core.collection import UNDEFINED

    class User(Model):
        id = Field(flags={'Key'})
        username = Field()

    async def fetch(sql, *values):
        return [{'id': 10, 'username': 'jdoe'}]

    store, mock = mock_sql_backend(engine, side_effect=fetch)
    with store:
        all_users = User.select()
        u = await all_users.get_last()
        mock.assert_called_with(
            engine.GET_LAST_RECORD.format(
                namespace=store.backend.default_namespace,
                table='users',
                column_a='id',
                column_b='username'
            )
        )
        assert await u.get('id') == 10
        assert await u.get('username') == 'jdoe'
        assert all_users._last is u
        assert all_users._first is UNDEFINED
        assert all_users._records is None
