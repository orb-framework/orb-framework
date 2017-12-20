"""Define Schema class."""
import inflection

from typing import Any, Dict, List, Union


class Schema:
    """Metadata about a Model class."""

    def __init__(
        self,
        *,
        inherits: list=None,
        label: str='',
        name: str='',
        namespace: str='',
        resource_name: str='',
        i18n_name: str=''
    ):
        self.inherits = inherits
        self.local_collectors = {}
        self.local_fields = {}
        self.local_indexes = {}
        self.local_references = {}
        self.name = name
        self.namespace = namespace

        self._i18n_name = i18n_name
        self._key_fields = None
        self._label = label
        self._resource_name = resource_name

    def __getitem__(
        self,
        key: str
    ) -> Union['Collector', 'Field', 'Reference']:
        """Shortcut to getting collectors, fields and references by name."""
        try:
            return self.fields[key]
        except KeyError:
            try:
                return self.collectors[key]
            except KeyError:
                try:
                    return self.references[key]
                except KeyError:
                    pass
        raise KeyError(key)

    @property
    def collectors(self) -> dict:
        """Return all collectors with this schema."""
        output = {}
        if self.inherits:
            for schema in self.inherits:
                output.update(schema.local_collectors)
        output.update(self.local_collectors)
        return output

    @property
    def default_order(self) -> Dict[str, 'Ordering']:
        """Return default order for this schema."""
        return [
            (field.name, field.default_ordering)
            for field in self.key_fields
        ]

    @property
    def default_values(self) -> dict:
        """Return defualt values for this model's fields."""
        return {
            field.name: field.default
            for field in self.fields.values()
            if not field.test_flag(field.Flags.Virtual)
        }

    def get(
        self,
        key: str,
        default: Any=None
    ) -> Union['Collector', 'Field', 'Reference']:
        """Get a schema object by name."""
        try:
            return self[key]
        except KeyError:
            return default

    @property
    def has_translations(self) -> bool:
        """Return whether or not this schema has any translated fields."""
        for field in self.fields.values():
            if field.test_flag(field.Flags.Translatable):
                return True
        return False

    @property
    def key_fields(self) -> List['Field']:
        """Return a list of the key fields for this schema."""
        if self._key_fields is None:
            fields = self.fields
            key_fields = []
            for f in fields.values():
                if f.test_flag(f.Flags.Key):
                    key_fields.append(f)
                    break

            if not key_fields:
                for i in self.indexes.values():
                    if i.test_flag(i.Flags.Key):
                        key_fields = [
                            fields[field_name]
                            for field_name in i.field_names
                        ]

            self._key_fields = key_fields
        return self._key_fields

    @property
    def fields(self) -> dict:
        """Return all fields associated with this schema."""
        output = {}
        if self.inherits:
            for schema in self.inherits:
                output.update(schema.local_fields)
        output.update(self.local_fields)
        return output

    @property
    def indexes(self) -> dict:
        """Return all the indexes associated with this schema."""
        output = {}
        if self.inherits:
            for schema in self.inherits:
                output.update(schema.local_indexes)
        output.update(self.local_indexes)
        return output

    @property
    def label(self) -> str:
        """Reurn the label for this schema."""
        return self._label or inflection.titelize(self.name)

    @property
    def references(self) -> dict:
        """Return all references associated with this schema."""
        output = {}
        if self.inherits:
            for schema in self.inherits:
                output.update(schema.local_references)
        output.update(self.local_references)
        return output

    @property
    def resource_name(self) -> str:
        """Return the resource name for this schema."""
        if self._resource_name:
            return self._resource_name
        underscore = inflection.underscore(self.name)
        return inflection.pluralize(underscore)

    @property
    def i18n_name(self) -> str:
        """Return the name used for internationalization for this model."""
        return self._i18n_name or '{}_i18n'.format(self.resource_name)

    @property
    def translatable_fields(self) -> List['Field']:
        """Return translatable fields for this schema."""
        return [
            f for f in self.fields.values()
            if f.test_flag(f.Flags.Translatable)
        ]
