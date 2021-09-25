import abc
import logging
from contextlib import contextmanager
from typing import Iterator

from attr import define
from pottery import Redlock
from redis import Redis

logger = logging.getLogger(__name__)


class Lock(abc.ABC):
    class FailedToAcquire(Exception):
        pass

    @contextmanager
    @abc.abstractmethod
    def acquire(self, name: str, expires_after: int, wait_for: int) -> Iterator:
        pass


@define
class RedisLock(Lock):
    _redis: Redis

    @contextmanager
    def acquire(self, name: str, expires_after: int, wait_for: int) -> Iterator:
        logger.debug(
            "Trying to acquire lock %s, to expire after %s, wait for %s",
            name,
            expires_after,
            wait_for,
        )
        redlock = Redlock(
            key=name,
            masters={self._redis},
            auto_release_time=expires_after * 1000,
        )
        acquired = False
        try:
            acquired = redlock.acquire(blocking=True, timeout=wait_for)
            if acquired:
                logger.debug(
                    "Lock acquired %s, will hold for %s",
                    name,
                    expires_after,
                )
            else:
                raise Lock.FailedToAcquire
            yield
        finally:
            if acquired:
                redlock.release()
                logger.debug("Lock released %s", name)
