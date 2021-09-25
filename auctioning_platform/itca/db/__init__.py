from typing import Callable

import injector
from attr import attrib, define
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session, sessionmaker

from itca.db.base import Base, mapper_registry, metadata
from itca.db.guid import GUID
from itca.db.jsonb import JSONB

__all__ = [
    # Module
    "Db",
    # SQLAlchemy registry objects & Base class for models
    "Base",
    "metadata",
    "mapper_registry",
    # Fields
    "JSONB",
    "GUID",
]


@define(repr=False)
class Db(injector.Module):
    _url: str
    _engine: Engine = attrib(init=False)
    _session_factory: Callable[[], Session] = attrib(init=False)

    def configure(self, _binder: injector.Binder) -> None:
        self._engine = create_engine(self._url, future=True)
        self._session_factory = sessionmaker(bind=self._engine, future=True)

    @injector.singleton
    @injector.provider
    def engine(self) -> Engine:
        return self._engine

    @injector.threadlocal
    @injector.provider
    def session(self) -> Session:
        return self._session_factory()

    @injector.threadlocal
    @injector.provider
    def connection(self, current_session: Session) -> Connection:
        return current_session.connection()
