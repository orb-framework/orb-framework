"""Define Schema class."""
import inflection


class Schema:
    """Metadata about a Model class."""

    def __init__(
        self,
        *,
        inherits: list=None,
        label: str=None,
        name: str=None,
        resource_name: str=None,
    ):
        self.inherits = inherits
        self._label = label
        self.local_collectors = {}
        self.local_fields = {}
        self.local_indexes = {}
        self.name = name
        self._resource_name = resource_name

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
    def default_values(self) -> dict:
        """Return defualt values for this model's fields."""
        return {
            field.name: field.default
            for field in self.fields.values()
            if not field.test_flag(field.Flags.Virtual)
        }

    @property
    def has_translations(self) -> bool:
        """Return whether or not this schema has any translated fields."""
        for field in self.fields.values():
            if field.test_flag(field.Flags.Translatable):
                return True
        return False

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
    def primary_fields(self) -> list:
        """Return a list of the primary fields for this schema."""
        return [f for f in self.fields if f.test_flag(f.Flags.Primary)]

    @property
    def resource_name(self) -> str:
        """Return the resource name for this schema."""
        if self._resource_name:
            return self._resource_name
        underscore = inflection.underscore(self.name)
        return inflection.pluralize(underscore)
