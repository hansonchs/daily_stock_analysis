"""The real API response model must retain research limitations for clients."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.deps import get_database_manager
from api.v1.endpoints import backtest


def test_results_endpoint_exposes_gross_research_basis(monkeypatch):
    class FakeService:
        def __init__(self, _db):
            pass

        def get_recent_evaluations(self, **_kwargs):
            return {
                "total": 1,
                "page": 1,
                "limit": 50,
                "items": [
                    {
                        "analysis_history_id": 1,
                        "code": "AAA",
                        "eval_window_days": 10,
                        "engine_version": "v1",
                        "eval_status": "completed",
                        "simulated_return_pct": 7.0,
                    }
                ],
            }

    monkeypatch.setattr(backtest, "BacktestService", FakeService)
    app = FastAPI()
    app.include_router(backtest.router)
    app.dependency_overrides[get_database_manager] = lambda: object()
    response = TestClient(app).get("/results")
    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_kind"] == "advice_score_gross"
    assert data["costs_included"] is False and data["publication_time_verified"] is False
    assert data["items"][0]["entry_price_basis"] == "analysis_date_close"
    assert data["items"][0]["simulated_return_pct"] == 7.0
