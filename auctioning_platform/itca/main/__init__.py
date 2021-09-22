from configparser import ConfigParser
from pathlib import Path

from injector import Injector

from itca.auctions import Auctions
from itca.auctions_infra import AuctionsInfra
from itca.db import Db
from itca.payments import Payments


def assemble(config_path: str = "config.ini") -> Injector:
    config = read_config(config_path)

    return Injector(
        [
            Db(url=config["database"]["url"]),
            Auctions(),
            AuctionsInfra(),
            Payments(
                username=config["bripe"]["username"],
                password=config["bripe"]["password"],
            ),
        ],
        auto_bind=False,
    )


def read_config(config_path: str) -> ConfigParser:
    assert Path(config_path).is_file(), f"Config {config_path} doesn't exist!"
    config = ConfigParser()
    config.read(config_path)
    return config
