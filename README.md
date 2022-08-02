# Implementing the Clean Architecture
An example project for my book under the same title. [English version in digital format available on Leanpub](https://leanpub.com/implementing-the-clean-architecture), [polish version in print will be available soon](https://helion.magazyn.pl/Implementowanie-Czystej-Architektury-w-Pythonie/imczar/ksiazka.html)!

This repository is meant to be a reference of many useful patterns when one implements projects using the Clean Architecture or Domain-Driven Design.

[![Join our Discord server!](https://invidget.switchblade.xyz/cDyDKv2VsY)](http://discord.gg/cDyDKv2VsY)

# Table of contents
- [Diagrams](#diagrams) (coming soon)
  - Big Picture Event Storming
  - Context Map
  - C4
- [Tactical Patterns](#tactical-patterns) (coming soon)
- [Components Integration Patterns](#components-integration-patterns) (coming soon)
- [Using with popular tools](#using-with-popular-tools) (more coming soon)

# Diagrams
Coming soon

# Tactical Patterns
Coming soon

# Components Integration Patterns
## Dependency Injection
- [Assemble components to configure IoC Container (main)](https://github.com/Enforcer/implementing-the-clean-architecture/blob/trunk/auctioning_platform/itca/main/__init__.py#L18)
- Nesting Injector's modules - [nested](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/processes/paying_for_won_auction/__init__.py#L21) and [component-level one](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/processes/__init__.py#L10) that's included in top-level's assemble

## Integration via Direct component's API call
[e.g. Process Manager directly calls Customer Relationship Facade](https://github.com/Enforcer/implementing-the-clean-architecture/blob/trunk/auctioning_platform/itca/processes/paying_for_won_auction/process_manager.py#L48) 

## Integration via Port / Adapter
- [Port in one component](https://github.com/Enforcer/implementing-the-clean-architecture/blob/trunk/auctioning_platform/itca/auctions/app/ports/payments.py)
- [Adapter in the other](https://github.com/Enforcer/implementing-the-clean-architecture/blob/trunk/auctioning_platform/itca/auctions_infra/adapters/payments.py)

## Integration via Events
### Groundwork
- [Event Bus (mediator) interface](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/foundation/event_bus.py#L11)
- [Injector-based Event Bus](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/foundation/event_bus.py#L65)
- [Handling of synchronous listeners](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/foundation/event_bus.py#L79)
- [Handling of asynchronous listeners](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/foundation/event_bus.py#L93)
  - [Interface for a function used to run listener asynchronously](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/foundation/event_bus.py#L61)
  - [Implementation of function used to run listeners asynchronously](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/main/event_bus.py#L19)

### Example
- One component [defines an Event](https://github.com/Enforcer/implementing-the-clean-architecture/blob/trunk/auctioning_platform/itca/auctions/domain/events/bidder_has_been_overbid.py) and [publishes it](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/auctions/app/use_cases/placing_bid.py#L59)
- [Another component subscribes to it using DI](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/customer_relationship/__init__.py#L34)
- [Another component handles the Event](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/customer_relationship/__init__.py#L18)

## Integration via Process Manager
- [Process Manager itself (multilistener with keeping state)](https://github.com/Enforcer/implementing-the-clean-architecture/blob/trunk/auctioning_platform/itca/processes/paying_for_won_auction/process_manager.py)
- [Subscriptions to Events using DI](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/processes/paying_for_won_auction/__init__.py#L22)
- [Handling Events using singledispatchmethod](https://github.com/Enforcer/implementing-the-clean-architecture/blob/6e1c28b51ddde9d55944c8d52397806299e38099/auctioning_platform/itca/processes/paying_for_won_auction/process_manager.py#L28)

# Using with popular tools
## Celery
- [Creating instance as usual after building IoC Container, then setting it on an attribute](https://github.com/Enforcer/implementing-the-clean-architecture/blob/trunk/auctioning_platform/itca/tasks/cli.py)
- Custom integration of Celery and Injector (coming soon)

## More coming soon
