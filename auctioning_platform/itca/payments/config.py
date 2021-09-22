from attr import define


@define(repr=False)
class PaymentsConfig:
    username: str
    password: str
