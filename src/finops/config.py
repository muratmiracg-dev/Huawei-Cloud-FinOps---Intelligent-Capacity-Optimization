"""Runtime configuration with safe environment-variable defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    data_dir: Path
    app_env: str = "development"
    log_level: str = "INFO"
    default_currency: str = "USD"
    forecast_months: int = 3
    minimum_savings_usd: float = 5.0
    headroom_pct: float = 25.0

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            data_dir=Path(os.getenv("FINOPS_DATA_DIR", "data/demo")),
            app_env=os.getenv("APP_ENV", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            default_currency=os.getenv("DEFAULT_CURRENCY", "USD"),
            forecast_months=int(os.getenv("FORECAST_MONTHS", "3")),
            minimum_savings_usd=float(os.getenv("MINIMUM_SAVINGS_USD", "5")),
            headroom_pct=float(os.getenv("CAPACITY_HEADROOM_PCT", "25")),
        )
