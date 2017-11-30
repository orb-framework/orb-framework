"""Define abstract SQL backend class."""

from abc import ABCMeta, abstractmethod
from typing import Dict, List, Tuple, Type, Union

from orb.core.context import Ordering, ReturnType, make_context
from orb.core.query import Query
from orb.core.query_group import QueryGroup

DEFAULT_ORDER_MAP = {
    Ordering.Asc: 'ASC',
    Ordering.Desc: 'DESC'
}
DEFAULT_QUOTE = '`'
DEFAULT_OP_MAP = {
    Query.Op.Is: '=',
    Query.Op.IsNot: '!=',
    QueryGroup.Op.And: 'AND',
    QueryGroup.Op.Or: 'OR'
}


class SqlBackend(metaclass=ABCMeta):
    """Define abstract SQL based backend."""

    def __init__(
        self,
        *,
        database: str='',
        default_namespace: str='',
        host: str='',
        op_map: Dict[Union[Query.Op, QueryGroup.Op], str]=None,
        order_map: Dict[Ordering, str]=None,
        quote: str='',
        password: str='',
        port: int=0,
        username: str=''
    ):
        self.database = database
        self.default_namespace = default_namespace
        self.host = host
        self.op_map = op_map or {}
        self.order_map = order_map or {}
        self.quote = quote
        self.password = password
        self.port = port
        self.username = username

    async def delete_collection(
        self,
        collection: 'Collection',
        context: 'Context'
    ) -> int:
        """Delete collection of records from the database."""
        pass

    async def delete_record(self, record: 'Model', context: 'Context') -> int:
        """Delete record from database."""
        schema = record.__schema__
        key_dict = await record.get_key_dict(key_property='code')
        args, values = args_to_sql(
            key_dict,
            joiner=' {} '.format(self.op_map[QueryGroup.Op.And]),
            quote=self.quote)

        if schema.has_translations:
            sql = (
                'DELETE FROM {q}{namespace}{q}.{q}{table}{q} '
                'WHERE ({args});\n'
                'DELETE FROM {q}{namespace}{q}.{q}{table_i18n}{q} '
                'WHERE ({args});'
            )
        else:
            sql = (
                'DELETE FROM {q}{namespace}{q}.{q}{table}{q} '
                'WHERE ({args});'
            )

        statement = sql.format(
            args=args,
            namespace=context.namespace or self.default_namespace,
            q=self.quote,
            table=schema.resource_name,
            table_i18n=schema.i18n_name
        )
        return await self.execute(statement, *values)

    @abstractmethod
    async def execute(self, sql: str, *args) -> bool:
        """Execute the given sql statement in this backend pool."""
        pass

    @abstractmethod
    async def fetch(self, sql: str, *args) -> dict:
        """Fetch values from the database for the given sql."""
        pass

    async def get_records(
        self,
        model: Type['Model'],
        context: 'Context'
    ) -> List[dict]:
        """Get records from the store based on the given context."""
        sql = (
            'SELECT {columns}\n'
            'FROM {q}{namespace}{q}.{q}{table}{q}\n'
            '{where}'
            '{order}'
            '{start}'
            '{limit}'
        )

        if context.returning == ReturnType.Count:
            fields = []
            columns = ['COUNT(*) AS count']
        else:
            fields, columns = fields_to_sql(
                model,
                context,
                quote=self.quote
            )

        values = []
        where = query_to_sql(
            model,
            context.where,
            context,
            quote=self.quote,
            op_map=self.op_map,
            values=values
        )
        order = order_to_sql(
            model,
            context.order,
            order_map=self.order_map,
            quote=self.quote
        )

        statement = sql.format(
            columns=', '.join(columns),
            limit='LIMIT {}\n'.format(context.limit) if context.limit else '',
            namespace=context.namespace or self.default_namespace,
            order='ORDER BY {}\n'.format(order) if order else '',
            q=self.quote,
            start='START {}\n'.format(context.start) if context.start else '',
            where='WHERE ({})\n'.format(where) if where else '',
            table=model.__schema__.resource_name
        ).strip() + ';'

        result = await self.fetch(statement, *values)
        if context.returning == ReturnType.Count:
            return result[0]['count']
        return result

    async def get_record_count(
        self,
        model: Type['Model'],
        context: 'Context'
    ) -> int:
        """Return number of records available for the given context."""
        count_context = make_context(
            returning=ReturnType.Count,
            context=context
        )
        results = await self.get_records(model, count_context)
        return results[0]['count']

    async def insert_record(self, record: 'Model', context: 'Context') -> dict:
        """Insert new record into the database."""
        schema = record.__schema__

        standard_columns = []
        standard_values = []
        i18n_columns = []
        i18n_values = []

        values = []

        for field_name, (_, new_value) in record.local_changes.items():
            field = schema.fields[field_name]

            if not field.test_flag(field.Flags.Translatable):
                values.append(new_value)
                standard_columns.append('{0}{1}{0}'.format(
                    self.quote,
                    field.code
                ))
                standard_values.append('${}'.format(len(values)))
            else:
                if not i18n_columns:
                    values.append(context.locale)
                    i18n_columns.append('{0}locale{0}'.format(self.quote))
                    i18n_values.append('${}'.format(len(values)))
                values.append(new_value)
                i18n_columns.append('{0}{1}{0}'.format(self.quote, field.code))
                i18n_values.append('${}'.format(len(values)))

        sql = (
            'INSERT INTO {q}{namespace}{q}.{q}{table}{q}\n'
            'SET ({standard_columns})\n'
            'VALUES {standard_values};'
        )
        if i18n_columns:
            sql += (
                '\n'
                'INSERT INTO {q}{namespace}{q}.{q}{table_i18n}{q}\n'
                'SET ({i18n_columns})\n'
                'VALUES {i18n_values};'
            )

        statement = sql.format(
            namespace=context.namespace or self.default_namespace,
            i18n_columns=', '.join(i18n_columns),
            i18n_values=', '.join(i18n_values),
            q=self.quote,
            standard_columns=', '.join(standard_columns),
            standard_values=', '.join(standard_values),
            table=schema.resource_name,
            table_i18n=schema.i18n_name
        )
        return await self.execute(statement, *values)

    async def save_collection(
        self,
        collection: 'Collection',
        context: 'Context'
    ) -> int:
        """Save a collection of records to the database."""
        pass

    async def save_record(self, record: 'Model', context: 'Context') -> dict:
        """Save record to backend database."""
        if record.is_new_record:
            return await self.insert_record(record, context)
        else:
            return await self.update_record(record, context)


def args_to_sql(
    kwargs: dict,
    *,
    joiner: str=', ',
    quote: str=DEFAULT_QUOTE,
) -> Tuple[str, list]:
    """Generate argument tuple from a dictionary."""
    pattern = '{q}{key}{q}=${index}'
    return (
        joiner.join(
            pattern.format(q=quote, key=key, index=i + 1)
            for i, key in enumerate(kwargs.keys())
        ),
        kwargs.values()
    )


def fields_to_sql(
    model: 'Model',
    context: 'Context',
    *,
    quote: str=DEFAULT_QUOTE
) -> Tuple[List['Field'], List[str]]:
    """Extract fields and columns from the model and context."""
    schema = model.__schema__
    all_fields = schema.fields
    field_names = (
        context.fields if context.fields is not None
        else sorted(all_fields.keys())
    )
    fields = []
    columns = []
    for field_name in field_names:
        field = all_fields[field_name]
        fields.append(field)
        if field.code != field.name:
            key = '{q}{code}{q} AS {q}{name}{q}'
        else:
            key = '{q}{code}{q}'
        columns.append(key.format(
            code=field.code,
            name=field.name,
            q=quote,
        ))

    return fields, columns


def query_to_sql(
    model: 'Model',
    query: Union['Query', 'QueryGroup'],
    context: 'Context',
    *,
    quote: str=DEFAULT_QUOTE,
    op_map: Dict[Union[Query.Op, QueryGroup.Op], str]=DEFAULT_OP_MAP,
    values: list=None
) -> str:
    """Convert the Query object to a SQL statement."""
    if getattr(query, 'is_null', True):
        return ''
    elif isinstance(query, QueryGroup):
        joiner = op_map[query.op]
        return joiner.join(
            query_to_sql(
                model,
                sub_query,
                context,
                op_map=op_map,
                quote=quote,
                values=values
            )
            for sub_query in query.queries
        )
    else:
        field = model.__schema__.fields[query.name]
        values.append(query.value)
        pattern = '{q}{code}{q}{op}${index}'
        return pattern.format(
            q=quote,
            code=field.code,
            op=op_map[query.op],
            index=len(values)
        )


def order_to_sql(
    model: 'Model',
    order: Dict[str, Ordering],
    *,
    order_map: Dict[Ordering, str]=DEFAULT_ORDER_MAP,
    quote: str=DEFAULT_QUOTE,
) -> str:
    """Convert ordering information to SQL."""
    if not order:
        return ''

    fields = model.__schema__.fields
    return ', '.join(
        '{q}{field}{q} {order}'.format(
            field=fields[field_name].code,
            q=quote,
            order=order_map[ordering]
        ) for field_name, ordering in order
    )
