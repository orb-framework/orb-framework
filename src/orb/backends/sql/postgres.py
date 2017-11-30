"""Define Postgres backend store."""
from .base import DEFAULT_OP_MAP, DEFAULT_ORDER_MAP, SqlBackend


class Postgres(SqlBackend):
    """Implement abstract store backend for PostgreSQL database."""

    def __init__(
        self,
        **base_options
    ):
        base_options.setdefault('default_namespace', 'public')
        base_options.setdefault('op_map', DEFAULT_OP_MAP)
        base_options.setdefault('order_map', DEFAULT_ORDER_MAP)
        base_options.setdefault('quote', '"')
        base_options.setdefault('port', 5432)

        super().__init__(**base_options)

        self._pool = None

    async def execute(self, sql, *args):
        """Execute the given sql statement in this backend pool."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                return await conn.execute(sql, *args)

    async def fetch(self, sql, *args):
        """Fetch values from the database for the given sql."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetch(sql, *args)

    async def get_pool(self):
        """Return the connection pool for this backend."""
        if self._pool is None:
            import asyncpg
            self._pool = await asyncpg.create_pool(
                database=self.database,
                host=self.host,
                password=self.password,
                port=self.port,
                user=self.username
            )
        return self._pool
