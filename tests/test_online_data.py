import os
import pytest
import pandas as pd
from core.data_fetcher import fetch_stock_daily, fetch_etf_daily


pytestmark = pytest.mark.online


def online_enabled() -> bool:
    return os.environ.get("ENABLE_ONLINE_TESTS") == "1"


@pytest.mark.skipif(not online_enabled(), reason="Online tests disabled")
def test_fetch_stock_daily_online():
    df = fetch_stock_daily("600519", "20240101", "20240201")
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@pytest.mark.skipif(not online_enabled(), reason="Online tests disabled")
def test_fetch_etf_daily_online():
    df = fetch_etf_daily("510300", "20240101", "20240201")
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
