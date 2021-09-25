import pytest
from injector import Injector
from sqlalchemy.engine import Engine

from itca.db import metadata
from itca.main import assemble


@pytest.fixture(scope="session")
def container() -> Injector:
    ioc_container = assemble("test_config.ini")
    metadata.create_all(bind=ioc_container.get(Engine))
    return ioc_container
