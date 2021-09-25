import injector
from attr import define
from redis import Redis

from itca.processes.locking import Lock, RedisLock
from itca.processes.paying_for_won_auction import PayingForWonAuctionModule


@define
class Processes(injector.Module):
    _redis_url: str

    def configure(self, binder: injector.Binder) -> None:
        binder.install(PayingForWonAuctionModule())

    @injector.provider
    def lock(self) -> Lock:
        return RedisLock(redis=Redis.from_url(self._redis_url))
