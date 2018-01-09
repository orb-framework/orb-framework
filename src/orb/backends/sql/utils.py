"""Define useful utility methods for manipulating sql calls."""
from collections import OrderedDict
from typing import Any, Dict, List, Tuple, Type, Union

from orb.core.model import Model
from orb.core.context import Ordering
from orb.core.query import Query
from orb.core.query_group import QueryGroup


DEFAULT_ORDER_MAP = {
    Ordering.Asc: 'ASC',
    Ordering.Desc: 'DESC'
}
DEFAULT_QUOTE = '`'
DEFAULT_OP_MAP = {
    Query.Op.After: '>',
    Query.Op.Before: '<',
    Query.Op.Contains: 'LIKE',
    Query.Op.ContainsInsensitive: 'ILIKE',
    Query.Op.Is: '=',
    Query.Op.IsIn: 'IN',
    Query.Op.IsNot: '!=',
    Query.Op.IsNotIn: 'NOT IN',
    Query.Op.GreaterThan: '>',
    Query.Op.GreaterThanOrEqual: '>=',
    Query.Op.LessThan: '<',
    Query.Op.LessThanOrEqual: '<=',
    Query.Op.Matches: '~',

    QueryGroup.Op.And: 'AND',
    QueryGroup.Op.Or: 'OR'
}


def args_to_sql(
    kwargs: dict,
    *,
    joiner: str=', ',
    quote: str=DEFAULT_QUOTE
) -> Tuple[str, list]:
    """Generate argument tuple from a dictionary."""
    pattern = '{q}{key}{q}={value}'
    return (
        joiner.join(
            pattern.format(
                q=quote,
                key=key,
                value=getattr(
                    kwargs[key],
                    'literal_value',
                    '${}'.format(i + 1)
                )
            ) for i, key in enumerate(kwargs.keys())
        ),
        kwargs.values()
    )


def changes_to_sql(
    changes: Dict[Union['Field', str], Any],
    quote: str=DEFAULT_QUOTE,
    offset: int=0
) -> Tuple[str, str, list]:
    """Create change statements in sql."""
    column_str = ', '.join(
        '{0}{1}{0}'.format(quote, getattr(field, 'code', field))
        for field in changes.keys()
    )
    values = changes.values()
    value_str = ', '.join(
        getattr(value, 'literal_value', '${}'.format(i + 1 + offset))
        for i, value in enumerate(values)
    )
    return column_str, value_str, values


def group_changes(record: 'Model') -> Tuple[dict, dict]:
    """Group changes into standard and translatable fields."""
    standard = OrderedDict()
    i18n = OrderedDict()

    fields = record.__schema__.fields
    for field_name, (_, new_value) in sorted(record.local_changes.items()):
        field = fields[field_name]
        if field.test_flag(field.Flags.Translatable):
            i18n[field] = new_value
        else:
            standard[field] = new_value

    return standard, i18n


def fields_to_sql(
    model: Type['Model'],
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
            key = '{prefix}{q}{code}{q} AS {q}{name}{q}'
        else:
            key = '{prefix}{q}{code}{q}'

        columns.append(key.format(
            code=field.code,
            name=field.name,
            prefix=(
                'i18n.' if field.test_flag(field.Flags.Translatable)
                else ''
            ),
            q=quote,
        ))

    return fields, columns


async def query_to_sql(
    backend: 'StoreBackend',
    model: Type['Model'],
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
        sub_queries = []
        for sub_query in query.queries:
            sub_queries.append(
                await query_to_sql(
                    backend,
                    model,
                    sub_query,
                    context,
                    op_map=op_map,
                    quote=quote,
                    values=values
                )
            )
        return ' {} '.format(joiner).join(sub_queries)
    else:
        op = op_map[query.op]
        field = model.__schema__.fields[query.name]
        value = await prepare_value(backend, field, query.value)
        values.append(value)
        if callable(op):
            return await op(field.code, len(values), quote)

        pattern = '{q}{code}{q}{op}{value}'
        return pattern.format(
            q=quote,
            code=field.code,
            op=op,
            value=getattr(
                value,
                'literal_value',
                '${}'.format(len(values))
            )
        )


def order_to_sql(
    model: Type['Model'],
    order: Dict[str, Ordering],
    *,
    order_map: Dict[Ordering, str]=DEFAULT_ORDER_MAP,
    quote: str=DEFAULT_QUOTE
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


async def prepare_value(
    backend: 'StoreBackend',
    field: 'Field',
    value: Any,
) -> Any:
    """Prepare the value to be stored to the backend."""
    if isinstance(value, Model):
        return await value.get_key()
    return value
