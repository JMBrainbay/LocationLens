from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

API_DIR = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = API_DIR.parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(WORKSPACE_ROOT / ".env"),
        extra="ignore",
    )

    NODE_ENV: Literal["development", "test", "production"] = "development"
    API_PORT: int = 4000

    LOCATION_PROVIDER: Literal["fixture", "pdok", "live"] = "fixture"
    BUILDING_PROVIDER: Literal["fixture", "bag", "none", "live"] = "fixture"
    METRICS_PROVIDER: Literal["fixture", "cbs", "none", "live"] = "fixture"

    PDOK_LOCATIESERVER_BASE_URL: str = Field(
        default="https://api.pdok.nl/bzk/locatieserver/search/v3_1"
    )
    PDOK_BAG_OGC_BASE_URL: str = Field(default="https://api.pdok.nl/kadaster/bag/ogc/v2")
    CBS_ODATA_BASE_URL: str = Field(default="https://datasets.cbs.nl/odata/v1/CBS")
    CBS_TABLE_ID: str = "86165NED"
    CBS_QUERY_STRATEGY: Literal["batch", "targeted"] = "batch"

    ENABLE_EP_ONLINE: bool = False
    EP_ONLINE_BASE_URL: str = Field(default="https://public.ep-online.nl")
    EP_ONLINE_API_KEY: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
