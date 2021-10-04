import abc
from abc import ABC

from itca.event_sourcing.event import EsEvent


class Projection(abc.ABC):
    @abc.abstractmethod
    def __call__(self, events: list[EsEvent]) -> None:
        pass


class SynchronousProjection(Projection, ABC):
    pass
