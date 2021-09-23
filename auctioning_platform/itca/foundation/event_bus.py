from typing import Callable, List, Type, TypeVar, cast

from attr import define
from injector import Injector, Provider, UnknownProvider, UnsatisfiedRequirement

from itca.foundation.event import Event

TEvent = TypeVar("TEvent")


class EventBus:
    def publish(self, event: Event) -> None:
        pass


class Listener(List[TEvent]):
    """Simple generic used to associate listeners with events using DI.

    e.g Listener[BidderHasBeenOverbid].
    """

    def __call__(self, event: TEvent) -> None:
        raise NotImplementedError


class AsyncListener(List[TEvent]):
    """An async counterpart of Listener[Event]."""

    def __call__(self, event: TEvent) -> None:
        raise NotImplementedError


class EventListenerProvider(Provider):
    """Useful for configuring bind for event listeners.

    Using DI for dispatching events to listeners requires ability to bind
    multiple listeners to a single key (Listener[Event]).
    """

    def __init__(self, cls: Type[TEvent]) -> None:
        self._cls = cls

    def get(self, injector: Injector) -> list[TEvent]:
        return [injector.create_object(self._cls)]


class AsyncEventListenerProvider(Provider):
    """An async counterpart of EventListenerProvider.

    In async, one does not need to actually construct the instance.
    It is enough to obtain class itself.
    """

    def __init__(self, cls: Type[TEvent]) -> None:
        self._cls = cls

    def get(self, _injector: Injector) -> list[Type[TEvent]]:
        return [self._cls]


RunAsyncHandler = Callable[[Type[AsyncListener[TEvent]], TEvent], None]


@define
class InjectorEventBus(EventBus):
    _container: Injector
    _run_async_handler: RunAsyncHandler

    def publish(self, event: Event) -> None:
        event_cls = type(event)
        try:
            sync_listeners = self._container.get(
                Listener[event_cls]  # type: ignore
            )
        except (UnsatisfiedRequirement, UnknownProvider):
            pass
        else:
            assert isinstance(sync_listeners, list)
            for listener in cast(List[Listener], sync_listeners):
                listener(event)

        try:
            async_handlers = self._container.get(
                AsyncListener[event_cls]  # type: ignore
            )
        except (UnsatisfiedRequirement, UnknownProvider):
            pass
        else:
            assert isinstance(async_handlers, list)
            for async_handler in cast(
                List[Type[AsyncListener]], async_handlers
            ):
                self._run_async_handler(async_handler, event)
