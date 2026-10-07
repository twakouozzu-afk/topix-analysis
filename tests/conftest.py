from pathlib import Path

import pandas as pd
import pytest

SAMPLE_CSV = Path(__file__).resolve().parents[1] / "samples" / "topix_sample.csv"


@pytest.fixture
def sample_csv() -> Path:
    return SAMPLE_CSV


@pytest.fixture
def prices() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-04", "2024-01-05", "2024-01-09", "2024-01-10"]),
            "open": [100.0, 110.0, 99.0, 104.0],
            "high": [111.0, 111.0, 105.0, 121.0],
            "low": [99.0, 98.0, 98.0, 103.0],
            "close": [110.0, 99.0, 104.5, 121.0],
        }
    )
