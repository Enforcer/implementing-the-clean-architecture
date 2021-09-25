import logging
from configparser import ConfigParser
from pathlib import Path

from injector import Injector

from itca.auctions import Auctions
from itca.auctions_infra import AuctionsInfra
from itca.customer_relationship import CustomerRelationship
from itca.db import Db
from itca.main.event_bus import EventBusModule
from itca.payments import Payments
from itca.processes import Processes


def assemble(config_path: str = "config.ini") -> Injector:
    config = read_config(config_path)
    configure_loggers()

    return Injector(
        [
            Db(url=config["database"]["url"]),
            EventBusModule(),
            Auctions(),
            AuctionsInfra(),
            Payments(
                username=config["bripe"]["username"],
                password=config["bripe"]["password"],
            ),
            CustomerRelationship(),
            Processes(redis_url=config["redis"]["url"]),
        ],
        auto_bind=False,
    )


def read_config(config_path: str) -> ConfigParser:
    assert Path(config_path).is_file(), f"Config {config_path} doesn't exist!"
    config = ConfigParser()
    config.read(config_path)
    return config


def configure_loggers() -> None:
    logging.getLogger("itca.processes.locking").setLevel(logging.DEBUG)
