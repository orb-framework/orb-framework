"""Define Reference class."""
from typing import Type, Union


class Reference:
    """Define Reference class."""

    def __init__(
        self,
        *,
        model: Union[Type['Model'], str]=None,
        name: str=None,
        source: Union[Type['Model'], str]=None
    ):
        self.source = source
        self._model = model
        self.name = name

    def get_model(self) -> Type['Model']:
        """Return model instance associated with this reference."""
        if type(self._model) is str:
            from .model import Model
            return Model.find_model(self._model)
        return self._model

    def set_model(self, model: Union[Type['Model'], str]):
        """Set model instance or name associated with this reference."""
        self._model = model

    model = property(get_model, set_model)
