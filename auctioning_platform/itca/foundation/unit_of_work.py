import abc
from typing import Callable


class UnitOfWork(abc.ABC):
    @abc.abstractmethod
    def begin(self) -> None:
        pass

    @abc.abstractmethod
    def rollback(self) -> None:
        pass

    @abc.abstractmethod
    def commit(self) -> None:
        pass

    @abc.abstractmethod
    def register_callback_after_commit(
        self, callback: Callable[[], None]
    ) -> None:
        pass
