"""Define tests for the Postgres backend store."""
import pytest


@pytest.fixture
def mock_pg(mocker):
    """Define mock Postgres backend instance."""
    from orb.backends.postgres import Postgres

    async def execute(backend, sql, *args):
        return sql, args

    mocker.patch('orb.backends.postgres.Postgres.execute', execute)
    return Postgres()


@pytest.mark.asyncio
async def test_postgres_delete_record(mock_pg):
    """Test the postgres delete record method."""
    from orb import Store, Model, Field

    class User(Model):
        id = Field(flags=Field.Flags.Primary)

    with Store(backend=mock_pg):
        u = User(values={'id': 1})
        sql, args = await u.delete()
        assert sql == 'DELETE FROM "public"."users" WHERE "id"=$1;'
        assert args == (1,)


@pytest.mark.asyncio
async def test_postgres_delete_record_with_multiple_id_columns(mock_pg):
    """Test the postgres delete record with multiple ids."""
    from orb import Store, Model, Field

    class GroupUser(Model):
        group_id = Field(flags=Field.Flags.Primary)
        user_id = Field(flags=Field.Flags.Primary)

    with Store(backend=mock_pg):
        u = GroupUser(values={'group_id': 1, 'user_id': 2})
        sql, args = await u.delete()
        assert sql == 'DELETE FROM "public"."group_users" WHERE ' \
                      '"group_id"=$1,"user_id"=$2;'
        assert args == (1, 2)


@pytest.mark.asyncio
async def test_postgres_delete_record_with_namespace(mock_pg):
    """Test the postgres delete record with proper namespace."""
    from orb import Store, Model, Field

    class User(Model):
        id = Field(flags=Field.Flags.Primary)

    with Store(backend=mock_pg):
        u = User(values={'id': 1})
        sql, args = await u.delete(namespace='auth')
        assert sql == 'DELETE FROM "auth"."users" WHERE "id"=$1;'
        assert args == (1,)


@pytest.mark.asyncio
async def test_postgres_delete_record_with_translation(mock_pg):
    """Test the postgres delete method with translations."""
    from orb import Store, Model, Field

    class Page(Model):
        id = Field(flags=Field.Flags.Primary)
        content = Field(flags=Field.Flags.Translatable)

    with Store(backend=mock_pg):
        p = Page(values={'id': 1})
        sql, args = await p.delete()
        assert sql == '\n'.join((
            'DELETE FROM "public"."pages" WHERE "id"=$1;',
            'DELETE FROM "public"."pages_i18n" WHERE "id"=$1;'
        ))
        assert args == (1,)
