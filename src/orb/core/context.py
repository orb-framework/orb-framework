"""Define the Context class."""
from enum import Enum
from typing import Union

from .query import Query


class Ordering(Enum):
    """Define ordering options."""

    Asc = 'asc'
    Desc = 'desc'


class ReturnType(Enum):
    """Define return options."""

    Data = 'data'
    Records = 'records'


class Context:
    """Metadata class for tracking lookup options."""

    def __init__(
        self,
        *,
        distinct: list=None,
        fields: list=None,
        locale: str=None,
        limit: int=None,
        namespace: str=None,
        ordering: list=None,
        page: int=None,
        page_size: int=None,
        query: Query=None,
        returning: ReturnType=ReturnType.Records,
        scope: dict=None,
        start: int=None,
        timezone: str=None,
    ):
        self.distinct = distinct
        self.fields = fields
        self.locale = locale
        self._limit = limit
        self.namespace = namespace
        self.ordering = ordering
        self.page = page
        self.page_size = page_size
        self.query = query
        self.returning = returning
        self.scope = scope or {}
        self._start = start
        self.timezone = timezone

    def get_limit(self) -> int:
        """Return limit for this context."""
        return self.page_size or self._limit

    def get_start(self) -> int:
        """Return start index for this context."""
        if self.page:
            return (self.page - 1) * (self.limit or 0)
        return self._start

    def set_limit(self, limit: int=None):
        """Set limit for this context."""
        self._limit = limit

    def set_start(self, start: int=None):
        """Set start index for this context."""
        self._start = start

    limit = property(get_limit, set_limit)
    start = property(get_start, set_start)


def _merge_distinct(distinct: list, context: Context) -> list:
    """Return distinct joined from option and base context."""
    if distinct:
        return distinct
    elif context:
        return context.distinct
    return None


def _merge_fields(fields: Union[str, list], context: Context) -> list:
    """Return new fields based on input and context."""
    if type(fields) is str:
        fields = fields.split(',')
    if fields and context and context.fields:
        context_fields = [f for f in context.fields if f not in fields]
        return fields + context_fields
    elif fields:
        return fields
    return context.fields if context else None


def _merge_limit(limit: int, context: Context) -> int:
    """Return new limit based on input and context."""
    if limit is not None:
        return limit
    return context._limit if context else None


def _merge_locale(locale: str, context: Context) -> str:
    """Return new locale based on input and context."""
    if locale is not None:
        return locale
    return context.locale if context else None


def _merge_namespace(namespace: str, context: Context) -> str:
    """Return new namespace based on input and context."""
    if namespace is not None:
        return namespace
    return context.namespace if context else None


def _merge_ordering(ordering: Union[str, list], context: Context) -> list:
    """Return new ordering based on input and context."""
    if type(ordering) is str:
        ordering = [
            (
                part.strip('+-'),
                Ordering.Desc if part.startswith('-') else Ordering.Asc
            ) for part in ordering.split(',')
        ]

    if ordering is not None:
        return ordering
    return context.ordering if context else None


def _merge_page(page: int, context: Context) -> int:
    """Return new page based on input and context."""
    if page is not None:
        return page
    return context.page if context else None


def _merge_page_size(page_size: int, context: Context) -> int:
    """Return new page size based on input and context."""
    if page_size is not None:
        return page_size
    return context.page_size if context else None


def _merge_query(query: Query, context: Context) -> Query:
    """Return new query based on input and context."""
    if query is not None and context and context.query is not None:
        return query & context.query
    elif query is not None:
        return query
    return context.query if context else None


def _merge_returning(returning: ReturnType, context: Context) -> ReturnType:
    """Return new returning based on input and context."""
    if returning is not None:
        return returning
    return context.returning if context else ReturnType.Records


def _merge_scope(scope: dict, context: Context) -> dict:
    """Return new scope based on input and context."""
    if scope and context and context.scope:
        new_scope = {}
        new_scope.update(context.scope)
        new_scope.update(scope)
        return new_scope
    elif scope:
        return scope
    return context.scope if context else None


def _merge_start(start: int, context: Context) -> int:
    """Return new start index based on input and context."""
    if start is not None:
        return start
    return context._start if context else None


def _merge_timezone(timezone: str, context: Context) -> str:
    """Return new timezone based on input and context."""
    if timezone is not None:
        return timezone
    return context.timezone if context else None


def make_context(
    *,
    context: Context=None,
    distinct: list=None,
    fields: Union[str, list]=None,
    locale: str=None,
    limit: int=None,
    namespace: str=None,
    ordering: Union[str, list]=None,
    page: int=None,
    page_size: int=None,
    query: Query=None,
    returning: ReturnType=None,
    scope: dict=None,
    start: int=None,
    timezone: str=None,
) -> Context:
    """Merge context options together."""
    return Context(
        distinct=_merge_distinct(distinct, context),
        fields=_merge_fields(fields, context),
        locale=_merge_locale(locale, context),
        limit=_merge_limit(limit, context),
        namespace=_merge_namespace(namespace, context),
        ordering=_merge_ordering(ordering, context),
        page=_merge_page(page, context),
        page_size=_merge_page_size(page, context),
        query=_merge_query(query, context),
        returning=_merge_returning(returning, context),
        scope=_merge_scope(scope, context),
        start=_merge_start(start, context),
        timezone=_merge_timezone(timezone, context)
    )
