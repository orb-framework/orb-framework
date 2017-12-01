"""Define Postgres backend store."""

from orb import value_literal

from .base import (
    DEFAULT_OP_MAP,
    DEFAULT_ORDER_MAP,
    SqlBackend,
    changes_to_sql,
    resolve_namespace
)


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

    async def create_standard_record(
        self,
        record: 'Model',
        context: 'Context',
        changes: dict
    ) -> dict:
        """Create a standard record in the database."""
        schema = record.__schema__
        sql = (
            'INSERT INTO {q}{namespace}{q}.{q}{table}{q} (\n'
            '   {columns}\n'
            ')\n'
            'VALUES({values})\n'
            'RETURNING *;'
        )

        column_str, value_str, values = changes_to_sql(
            changes,
            quote=self.quote
        )

        statement = sql.format(
            columns=column_str,
            namespace=resolve_namespace(
                schema,
                context,
                default=self.default_namespace
            ),
            q=self.quote,
            values=value_str,
            table=schema.resource_name,
        )
        return await self.execute(statement, *values)

    async def create_i18n_record(
        self,
        record: 'Model',
        context: 'Context',
        standard_changes: dict,
        i18n_changes: dict
    ) -> dict:
        """Create a translatable record in the database."""
        schema = record.__schema__
        sql = (
            'WITH inserted AS (\n'
            '   INSERT INTO {q}{namespace}{q}.{q}{table}{q} (\n'
            '       {columns}\n'
            '   )\n'
            '   VALUES({values})\n'
            '   RETURNING *;\n'
            ')\n'
            'INSERT INTO {q}{namespace}{q}.{q}{i18n_table}{q} (\n'
            '   {i18n_columns}\n'
            ')\n'
            'SELECT {i18n_values} FROM inserted\n'
            'RETURNING *;'
        )

        column_str, value_str, values = changes_to_sql(
            standard_changes,
            quote=self.quote
        )

        i18n_changes.setdefault('locale', context.locale)
        for field in schema.key_fields:
            i18n_changes[field.code] = value_literal(
                'inserted."{}"'.format(field.code)
            )

        i18n_column_str, i18n_value_str, i18n_values = changes_to_sql(
            i18n_changes,
            quote=self.quote,
            offset=len(values)
        )

        statement = sql.format(
            columns=column_str,
            i18n_columns=i18n_column_str,
            i18n_values=i18n_value_str,
            i18n_table=schema.i18n_name,
            namespace=resolve_namespace(
                schema,
                context,
                default=self.default_namespace
            ),
            q=self.quote,
            values=value_str,
            table=schema.resource_name,
        )
        return await self.execute(statement, *values, *i18n_values)

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
