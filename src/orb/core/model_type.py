"""Define ModelType metaclass."""
import inspect
from typing import Tuple

from .schema import Schema


def parse_schema_info(classes: list) -> Tuple[dict, dict, dict, list]:
    """Iterate over class list to find schemas."""
    from .collector import Collector
    from .field import Field
    from .index import Index

    collectors = {}
    fields = {}
    indexes = {}
    inherits = []

    for cls in classes:
        (
            sub_inherits,
            sub_collectors,
            sub_fields,
            sub_indexes
        ) = parse_schema_info(cls.__bases__)

        inherits.extend(sub_inherits)
        collectors.update(sub_collectors)
        fields.update(sub_fields)
        indexes.update(sub_indexes)

        if type(cls) is ModelType and not cls.__abstract__:
            if cls.__schema__:
                inherits.append(cls.__schema__)
        else:
            for key, value in inspect.getmembers(cls):
                value = getattr(value, '__virtual__', value)
                if isinstance(value, Collector):
                    collectors[key] = value
                elif isinstance(value, Index):
                    indexes[key] = value
                elif isinstance(value, Field):
                    fields[key] = value

    return collectors, fields, indexes, inherits


class ModelType(type):
    """Metaclass to define Model types."""

    def __new__(cls, clsname: str, superclasses: list, attributes: dict):
        """Generate new Model class."""
        if not attributes.get('__abstract__'):
            from .collector import Collector
            from .field import Field
            from .index import Index

            (
                collectors,
                fields,
                indexes,
                inherits,
            ) = parse_schema_info(superclasses)

            schema = (
                attributes.get('__schema__') or
                Schema(name=clsname, inherits=inherits)
            )
            if not schema.name:
                schema.name = clsname

            cls_attributes = {}
            for key, value in attributes.items():
                value = getattr(value, '__virtual__', value)
                if isinstance(value, Field):
                    value.name = key
                    fields[key] = value
                elif isinstance(value, Index):
                    value.name = key
                    indexes[key] = value
                elif isinstance(value, Collector):
                    value.name = key
                    collectors[key] = value
                else:
                    cls_attributes[key] = value

            schema.local_collectors.update(collectors)
            schema.local_fields.update(fields)
            schema.local_indexes.update(indexes)

            cls_attributes['__schema__'] = schema
            cls_attributes['__abstract__'] = False
        else:
            cls_attributes = attributes

        return type.__new__(cls, clsname, superclasses, cls_attributes)
