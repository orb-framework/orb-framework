"""Define Postgres backend store."""
from typing import Tuple

from orb.core.store_backend import StoreBackend


class Postgres(StoreBackend):
    """Implement abstract store backend for PostgreSQL database."""

    def __init__(
        self,
        *,
        database='',
        host='localhost',
        password='',
        port=5432,
        username='',
    ):
        self.database = database
        self.host = host
        self.password = password
        self.port = port
        self.username = username
        self._pool = None

    async def delete_collection(
        self,
        collection: 'Collection',
        context: 'Context'
    ) -> int:
        pass

    async def delete_record(self, record: 'Model', context: 'Context') -> int:
        """Delete record from database."""
        primary_values = await record.get_primary_values(key='code')
        args, values = self.parse_args(primary_values)
        resource = record.__schema__.resource_name
        namespace = context.namespace or 'public'

        sql = [
            'DELETE FROM "{}"."{}" WHERE {};'.format(
                namespace,
                resource,
                args
            )
        ]
        if record.__schema__.has_translations:
            sql.append(
                'DELETE FROM "{}"."{}_i18n" WHERE {};'.format(
                    namespace,
                    resource,
                    args
                )
            )
        return await self.execute('\n'.join(sql), *values)

    async def execute(self, sql, *args):
        """Execute the given sql statement in this backend pool."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                return await conn.execute(sql, *args)

    def parse_args(self, kwargs: dict) -> Tuple[str, list]:
        """Generate argument tuple from a dictionary."""
        arg_str = ''
        args = []
        for key, value in kwargs.items():
            if arg_str:
                arg_str += ','
            args.append(value)
            arg_str += '"{}"=${}'.format(key, len(args))
        return arg_str, args

    @property
    def pool(self):
        """Return the connection pool for this backend."""
        if self._pool is None:
            import asyncpg
            self._pool = asyncpg.create_pool(
                database=self.database,
                host=self.host,
                password=self.password,
                port=self.port,
                username=self.username
            )
        return self._pool

    async def save_collection(
        self,
        collection: 'Collection',
        context: 'Context'
    ) -> int:
        pass

    async def save_record(self, record: 'Model', context: 'Context') -> int:
        """Save record to backend database."""
