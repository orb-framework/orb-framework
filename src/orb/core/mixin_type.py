"""Define ModelType metaclass."""


class MixinType(type):
    """Metaclass to define Mixin types."""

    def __new__(cls, clsname: str, superclasses: list, attributes: dict):
        """Generate new Mixin class."""
        if not attributes.get('__abstract__'):
            from .collector import Collector
            from .field import Field
            from .index import Index

            inherits, mixins = parse_schema_info(superclasses)

            schema = (
                attributes.get('__schema__') or
                Schema(name=clsname, inherits=inherits)
            )

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
