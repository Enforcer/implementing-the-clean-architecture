from extra.event_bus_draft import EventBus


def assemble() -> None:  # 1
    event_bus = EventBus()
    setup_dependency_injection(event_bus)
    setup_event_subscriptions()


def setup_dependency_injection(
    event_bus: EventBus,
) -> None:
    def di_config(binder: inject.Binder) -> None:
        binder.bind(EventBus, event_bus)  # 2
        ...

    inject.configure(di_config)


def setup_event_subscriptions(
    event_bus: EventBus,
) -> None:
    event_bus.subscribe(  # 3
        BidderHasBeenOverbid,
        lambda event: send_email.delay(
            event.auction_id,
            event.bidder_id,
            event.old_price,
            event.new_price,
        ),
    )
