from itca.auctions.app.ports.payments import Payments


class Config(dict):
    pass


class BripePayments(Payments):
    def __init__(self, config: Config) -> None:
        self._basic_auth = (
            config["bripe"]["username"],
            config["bripe"]["password"],
        )
