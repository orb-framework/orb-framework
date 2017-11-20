"""Define ReverseLookup Collector class."""
from .collector import Collector
from .collection import Collection
from .context import Context
from .model import Model
from .query import Query as Q


class ReverseLookup(Collector):
    """Define a one-to-many lookup class."""

    def __init__(
        self,
        path='',
        field='',
        **kw,
    ):
        if path:
            model, _, field = path.partition('.')
            kw.setdefault('model', model)
        super().__init__(**kw)

        self.field = field

    async def collect_by_record(self, record: Model) -> Collection:
        """Create collection for a given record."""
        query = Q(model=self._model, name=self.field) == record

        return Collection(
            collector=self,
            context=Context(query=query),
            model=self._model,
            source=record,
        )
