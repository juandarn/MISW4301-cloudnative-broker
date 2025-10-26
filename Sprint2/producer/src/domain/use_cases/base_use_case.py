from abc import ABC, abstractmethod
from typing import Any


class BaseUseCase(ABC):
    """Base use case class."""

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the use case."""
        pass
