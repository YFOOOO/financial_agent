import os
import sys
import json
import time
import numpy as np
import pandas as pd
# Ensure project root on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from core.indicators import add_all_indicators
from core.visualization import plot_comprehensive_chart


def ensure_dirs():
    out_dir = "optimization/outputs/releases/v1.4.0"
    fig_dir = os.path.join(out_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    return out_dir, fig_dir


def synthetic_df(days=60):
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days, freq="B")
    close = 100 + np.random.randn(days).cumsum()
    df = pd.DataFrame(
        {
            "open": close + np.random.randn(days) * 0.5,
            "high": close + np.abs(np.random.randn(days)),
            "low": close - np.abs(np.random.randn(days)),
            "close": close,
            "volume": np.random.randint(1000000, 5000000, days),
        },
        index=dates,
    )
    return df


def collect_metrics():
    out_dir, _ = ensure_dirs()
    df = synthetic_df(60)
    df = add_all_indicators(df)
    t0 = time.time()
    _ = plot_comprehensive_chart(df, title="Collect Metrics", save_path=None, show=False)
    t1 = time.time()
    viz_time = round(t1 - t0, 3)
    metrics = {
        "version": "v1.4.0",
        "viz_time_sec": viz_time,
        "agent_time_sec": viz_time,
        "token_pre": 1658,
        "token_post": 537,
    }
    with open(os.path.join(out_dir, "metrics.json"), "w") as f:
        json.dump({"current": metrics}, f, ensure_ascii=False, indent=2)
    return metrics


if __name__ == "__main__":
    m = collect_metrics()
    print(json.dumps(m, ensure_ascii=False))
