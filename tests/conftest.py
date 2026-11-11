import pytest


@pytest.fixture(autouse=True)
def no_real_keys(monkeypatch):
    """Tests never call Google Places for real, even if a key is in the environment."""
    monkeypatch.delenv("GOOGLE_PLACES_API_KEY", raising=False)
