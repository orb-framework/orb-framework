"""Define ModelType metaclass."""
from typing import Tuple

from .mixin_type import MixinType
from .schema import Schema


def parse_schema_info(classes: list) -> Tuple[list, dict, dict, dict]:
    """Iterate over class list to find schemas."""
    inherits = []
    collectors = {}
    fields = {}
    indexes = {}

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

        if type(cls) is ModelType and cls.__schema__:
            inherits.append(cls.__schema__)
        elif type(cls) is MixinType:
            sub_collectors.update(cls.__collectors__)
            sub_fields.update(cls.__fields__)
            sub_indexes.update(cls.__indexes__)

    return inherits, fields, indexes, indexes


class ModelType(type):
    """Metaclass to define Model types."""

    def __new__(cls, clsname: str, superclasses: list, attributes: dict):
        """Generate new Model class."""
        if not attributes.get('__abstract__'):
            from .collector import Collector
            from .field import Field
            from .index import Index

            (
                inherits,
                mixin_collectors,
                mixin_fields,
                mixin_indexes,
            ) = parse_schema_info(superclasses)

            schema = (
                attributes.get('__schema__') or
                Schema(name=clsname, inherits=inherits)
            )

            schema.local_collectors.update(mixin_collectors)
            schema.local_fields.update(mixin_fields)
            schema.local_indexes.update(mixin_indexes)

            cls_attributes = {}
            for key, value in attributes.items():
                if isinstance(value, Field):
                    value.name = key
                    schema.local_fields[key] = value
                elif isinstance(value, Index):
                    value.name = key
                    schema.local_indexes[key] = value
                elif isinstance(value, Collector):
                    value.name = key
                    schema.local_collectors[key] = value
                else:
                    cls_attributes[key] = value

            cls_attributes['__schema__'] = schema
            cls_attributes['__abstract__'] = False
        else:
            cls_attributes = attributes

        return type.__new__(cls, clsname, superclasses, cls_attributes)
