"""FastAPI delivery layer for FinOps analytics."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse

from finops.adapters import CsvRepository
from finops.config import Settings
from finops.engine import FinOpsEngine
from finops.models import model_to_dict
from finops.repository import FinOpsRepository
from finops.telemetry import render_metrics


def _serialize(value: object) -> object:
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return model_to_dict(value)
    return value


def build_app(repository: FinOpsRepository | None = None) -> FastAPI:
    settings = Settings.from_env()
    repo = repository or CsvRepository(settings.data_dir)
    engine = FinOpsEngine(
        repo,
        minimum_savings=settings.minimum_savings_usd,
        headroom_pct=settings.headroom_pct,
    )
    app = FastAPI(
        title="Huawei Cloud FinOps & Intelligent Capacity Optimization API",
        version="1.0.0",
        description=(
            "Explainable cost allocation, anomaly detection, forecasting, "
            "rightsizing, and capacity-risk recommendations."
        ),
    )

    @app.get("/health/live", tags=["health"])
    def liveness() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/health/ready", tags=["health"])
    def readiness() -> dict[str, object]:
        try:
            resource_count = len(repo.resources())
            return {"status": "ready", "resources": resource_count}
        except (FileNotFoundError, ValueError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.get("/api/v1/summary", tags=["finops"])
    def summary() -> object:
        return _serialize(engine.summary())

    @app.get("/api/v1/recommendations", tags=["finops"])
    def recommendations(
        min_savings: float = Query(default=0.0, ge=0.0),
    ) -> list[object]:
        return [
            _serialize(item)
            for item in engine.recommendations()
            if item.estimated_monthly_savings >= min_savings
        ]

    @app.get("/api/v1/anomalies", tags=["finops"])
    def anomalies() -> object:
        return _serialize(engine.anomalies())

    @app.get("/api/v1/forecast", tags=["finops"])
    def forecast(months: int = Query(default=3, ge=1, le=18)) -> object:
        return _serialize(engine.forecast(months))

    @app.get("/api/v1/allocation", tags=["finops"])
    def allocation(dimension: str = "product") -> dict[str, float]:
        try:
            return engine.allocation(dimension)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/v1/budgets", tags=["finops"])
    def budgets() -> object:
        return _serialize(engine.budget_statuses())

    @app.post("/api/v1/analysis/run", tags=["operations"])
    def run_analysis(months: int = Query(default=3, ge=1, le=18)) -> object:
        return _serialize(engine.full_analysis(months))

    @app.get("/metrics", response_class=PlainTextResponse, tags=["operations"])
    def metrics() -> str:
        return render_metrics(engine.summary())

    return app


app = build_app()
