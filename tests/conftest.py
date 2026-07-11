import pytest


@pytest.fixture(autouse=True)
def setup_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HARVEST_ACCESS_TOKEN", "test-harvest-token")
    monkeypatch.setenv("HARVEST_ACCOUNT_ID", "123")
    monkeypatch.setenv("FORECAST_ACCESS_TOKEN", "test-forecast-token")
    monkeypatch.setenv("FORECAST_ACCOUNT_ID", "456")
    monkeypatch.setenv("HARVEST_USER_AGENT", "test (test@example.com)")


HARVEST_BASE = "https://api.harvestapp.com/v2"
FORECAST_BASE = "https://api.forecastapp.com"
