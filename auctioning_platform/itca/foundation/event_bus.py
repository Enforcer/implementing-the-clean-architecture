from typing import Type, TypeVar

from injector import Injector, Provider

from itca.foundation.event import Event

T = TypeVar("T")


class EventBus:
    def publish(self, event: Event) -> None:
        pass


class Listener(list[T]):
    """Simple generic used to associate listeners with events using DI.

    e.g Listener[BidderHasBeenOverbid].
    """

    pass


class AsyncListener(list[T]):
    """An async counterpart of Listener[Event]."""

    pass


class EventListenerProvider(Provider):
    """Useful for configuring bind for event listners.

    Using DI for dispatching events to listeners requires ability to bind
    multiple listeners to a single key (Listener[Event]).
    """

    def __init__(self, cls: Type[T]) -> None:
        self._cls = cls

    def get(self, injector: Injector) -> list[T]:
        return [injector.create_object(self._cls)]


class AsyncEventListenerProvider(Provider):
    """An async counterpart of EventListenerProvider.

    In async, one does not need to actually construct the instance.
    It is enough to obtain class itself.
    """

    def __init__(self, cls: Type[T]) -> None:
        self._cls = cls

    def get(self, _injector: Injector) -> list[Type[T]]:
        return [self._cls]
