from typing import Callable, Type


class Event:
    pass


class EventBus:
    def emit(self, event: Event) -> None:
        ...

    def subscribe(
        self, event_cls: Type[Event], listener: Callable[[Event], None]
    ) -> None:
        ...
