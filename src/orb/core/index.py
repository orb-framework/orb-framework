"""Define Index class."""


class Index:
    """Class to identify lookups."""

    def __init__(
        self,
        code: str=None,
        name: str=None,
    ):
        self.code = code
        self.name = name
