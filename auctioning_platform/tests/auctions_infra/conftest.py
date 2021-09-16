import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from itca.db import metadata


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite://", future=True, echo=True)
    metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, future=True)()
