import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class SimpleTTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[float, object]] = {}

    async def get_or_set(self, key: str, loader: Callable[[], Awaitable[T]]) -> T:
        now = time.time()
        cached = self._store.get(key)
        if cached and now - cached[0] < self.ttl_seconds:
            return cached[1]  # type: ignore[return-value]

        value = await loader()
        self._store[key] = (now, value)
        return value
