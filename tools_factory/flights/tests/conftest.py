import json
import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def real_flight_data():
    with open(FIXTURES_DIR / "real_flight_results.json", encoding="utf-8") as f:
        return json.load(f)
