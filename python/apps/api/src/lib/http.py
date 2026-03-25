from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx


async def get_json(
    client: httpx.AsyncClient, url: str, params: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    response = await client.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        return {"value": data}
    return data
