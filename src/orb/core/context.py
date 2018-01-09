"""Define the Context class."""
from enum import Enum
from typing import Union

from dotted.utils import dot

from .store import current_store

DEFAULT_LOCALE = 'en_US'


class Ordering(Enum):
    """Define ordering options."""

    Asc = 'asc'
    Desc = 'desc'


class ReturnType(Enum):
    """Define return options."""

    Data = 'data'
    Records = 'records'
    Count = 'count'


class Context:
    """Metadata class for tracking lookup options."""

    def __init__(
        self,
        *,
        include: 'DottedDict'=None,
        distinct: list=None,
        fields: list=None,
        force_namespace: bool=False,
        locale: str=DEFAULT_LOCALE,
        limit: int=None,
        namespace: str=None,
        order: list=None,
        page: int=None,
        page_size: int=None,
        returning: ReturnType=ReturnType.Records,
        scope: dict=None,
        start: int=None,
        store: Union['Store', str]=None,
        timezone: str=None,
        where: 'Query'=None
    ):
        self.include = include or dot({})
        self.distinct = distinct
        self.force_namespace = force_namespace
        self.fields = fields
        self.locale = locale
        self._limit = limit
        self.namespace = namespace
        self.order = order
        self.page = page
        self.page_size = page_size
        self.returning = returning
        self.scope = scope or {}
        self._start = start
        self._store = store
        self.timezone = timezone
        self.where = where

    def get_limit(self) -> int:
        """Return limit for this context."""
        return self.page_size or self._limit

    def get_start(self) -> int:
        """Return start index for this context."""
        if self.page:
            return (self.page - 1) * (self.limit or 0)
        return self._start

    def get_store(self) -> 'Store':
        """Return the store associated with this context."""
        if self._store is None or type(self._store) is str:
            return current_store(self._store)
        return self._store

    def set_limit(self, limit: int=None):
        """Set limit for this context."""
        self._limit = limit

    def set_start(self, start: int=None):
        """Set start index for this context."""
        self._start = start

    def set_store(self, store: 'Store'):
        """Set local store property for this context."""
        self._store = store

    limit = property(get_limit, set_limit)
    start = property(get_start, set_start)
    store = property(get_store, set_store)


def _merge_include(options: dict, base_context: Context) -> 'DottedDict':
    """Return trie containing the hierarchy of includes."""
    out = dot({})
    out.update(base_context.include if base_context else {})
    option_include = options.get('include', {})
    option_fields = options.get('fields', [])
    if type(option_fields) is str:
        option_fields = option_fields.split(',')
    if type(option_include) is str:
        for incl in option_include.split(','):
            out.setdefault(incl, {})
    elif type(option_include) in (list, tuple):
        for incl in option_include:
            out.setdefault(incl, {})
    for field in option_fields:
        if '.' in field:
            out.setdefault(field.rpartition('.')[0], {})
    return out


def _merge_distinct(options: dict, base_context: Context) -> list:
    """Return distinct joined from option and base context."""
    try:
        distinct = options['distinct']
    except KeyError:
        distinct = base_context.distinct if base_context else None
    else:
        if type(distinct) is str:
            distinct = distinct.split(',')
    return distinct


def _merge_fields(options: dict, base_context: Context) -> list:
    """Return new fields based on input and context."""
    option_fields = options.get('fields')
    base_fields = base_context.fields if base_context else None
    if type(option_fields) is str:
        option_fields = option_fields.split(',')

    if option_fields and base_fields:
        return option_fields + [
            f for f in base_fields if f not in option_fields
        ]
    elif option_fields:
        return option_fields
    else:
        return base_fields


def _merge_limit(options: dict, base_context: Context) -> int:
    """Return new limit based on input and context."""
    try:
        return options['limit']
    except KeyError:
        return base_context._limit if base_context else None


def _merge_locale(options: dict, base_context: Context) -> str:
    """Return new locale based on input and context."""
    try:
        return options['locale']
    except KeyError:
        return base_context.locale if base_context else DEFAULT_LOCALE


def _merge_namespace(options: dict, base_context: Context) -> str:
    """Return new namespace based on input and context."""
    try:
        return options['namespace']
    except KeyError:
        return base_context.namespace if base_context else None


def _merge_order(options: dict, base_context: Context) -> list:
    """Return new order based on input and context."""
    try:
        order = options['order']
    except KeyError:
        order = base_context.order if base_context else None
    else:
        if type(order) is str:
            order = [
                (
                    part.strip('+-'),
                    Ordering.Desc if part.startswith('-') else Ordering.Asc
                ) for part in order.split(',')
            ]
    return order


def _merge_page(options: dict, base_context: Context) -> int:
    """Return new page based on input and context."""
    try:
        return options['page']
    except KeyError:
        return base_context.page if base_context else None


def _merge_page_size(options: dict, base_context: Context) -> int:
    """Return new page size based on input and context."""
    try:
        return options['page_size']
    except KeyError:
        return base_context.page_size if base_context else None


def _merge_query(options: dict, base_context: Context) -> 'Query':
    """Return new query based on input and context."""
    try:
        query = options['where']
    except KeyError:
        query = base_context.where if base_context else None
    else:
        if query is not None and base_context:
            query &= base_context.where
    return query


def _merge_returning(options: dict, base_context: Context) -> ReturnType:
    """Return new returning based on input and context."""
    try:
        return options['returning']
    except KeyError:
        return base_context.returning if base_context else ReturnType.Records


def _merge_scope(options: dict, base_context: Context) -> dict:
    """Return new scope based on input and context."""
    try:
        scope = options['scope']
    except KeyError:
        scope = base_context.scope if base_context else None
    else:
        if scope and base_context:
            new_scope = {}
            new_scope.update(base_context.scope)
            new_scope.update(scope)
            return new_scope
    return scope


def _merge_start(options: dict, base_context: Context) -> int:
    """Return new start index based on input and context."""
    try:
        return options['start']
    except KeyError:
        return base_context._start if base_context else None


def _merge_store(options: dict, base_context: Context) -> 'Store':
    """Return new store based on input and context."""
    try:
        return options['store']
    except KeyError:
        return base_context._store if base_context else None


def _merge_timezone(options: dict, base_context: Context) -> str:
    """Return new timezone based on input and context."""
    try:
        return options['timezone']
    except KeyError:
        return base_context.timezone if base_context else None


def make_context(**options) -> Context:
    """Merge context options together."""
    base_context = options.pop('context', None)
    if base_context and not options:
        return base_context
    return Context(
        distinct=_merge_distinct(options, base_context),
        fields=_merge_fields(options, base_context),
        include=_merge_include(options, base_context),
        limit=_merge_limit(options, base_context),
        locale=_merge_locale(options, base_context),
        namespace=_merge_namespace(options, base_context),
        order=_merge_order(options, base_context),
        page_size=_merge_page_size(options, base_context),
        page=_merge_page(options, base_context),
        returning=_merge_returning(options, base_context),
        scope=_merge_scope(options, base_context),
        start=_merge_start(options, base_context),
        store=_merge_store(options, base_context),
        timezone=_merge_timezone(options, base_context),
        where=_merge_query(options, base_context)
    )


def make_record_context(**options) -> Context:
    """Generate a context for a record."""
    base_context = options.pop('context', None)
    return Context(
        distinct=_merge_distinct(options, base_context),
        fields=_merge_fields(options, base_context),
        locale=_merge_locale(options, base_context),
        namespace=_merge_namespace(options, base_context),
        returning=_merge_returning(options, base_context),
        scope=_merge_scope(options, base_context),
        store=_merge_store(options, base_context)
    )


def resolve_namespace(
    schema: 'Schema',
    context: 'Context',
    default: str=''
) -> str:
    """Determine the best possible namespace for a set of params."""
    if schema.namespace and not context.force_namespace:
        return schema.namespace
    elif context.namespace:
        return context.namespace
    elif context.store and context.store.namespace:
        return context.store.namespace
    return default


def reverse_order(order: list) -> list:
    """Reverse ordering by switching ascending and descending."""
    return [
        (x[0], Ordering.Asc if x[1] is Ordering.Desc else Ordering.Desc)
        for x in order
    ]
