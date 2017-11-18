"""Define Schema class."""


class Schema:
    """Metadata about a Model class."""

    def __init__(self, name: str=None, inherits: list=None):
        self.inherits = inherits
        self.local_collectors = {}
        self.local_fields = {}
        self.local_indexes = {}
        self.name = name

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
