"""Data loading utilities for market data retrieval and preprocessing."""
from __future__ import annotations

from pathlib import Path
import time
from typing import Iterable

import akshare as ak
import pandas as pd


def _to_ak_date(date_str: str) -> str:
    return pd.to_datetime(date_str).strftime("%Y%m%d")


def download_ohlcv(
    tickers: Iterable[str],
    start: str,
    end: str,
    cache_path: str | Path = "data/ohlcv.parquet",
    refresh: bool = False,
) -> pd.DataFrame:
    """Download daily OHLCV data from AkShare and return a stacked dataframe.

    Returns dataframe indexed by [date, asset] with columns:
    open, high, low, close, adj_close, volume.
    """
    cache_path = Path(cache_path)
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)

    clean_tickers = [str(t).strip() for t in tickers if str(t).strip()]
    if not clean_tickers:
        raise ValueError("No valid tickers provided after cleaning.")

    start_ak = _to_ak_date(start)
    end_ak = _to_ak_date(end)

    frames = []
    max_retries = 3
    for t in clean_tickers:
        df_t = None
        for attempt in range(max_retries):
            try:
                raw = ak.stock_zh_a_hist(
                    symbol=t,
                    period="daily",
                    start_date=start_ak,
                    end_date=end_ak,
                    adjust="qfq",
                )
                if raw is None or raw.empty:
                    break

                rename_map = {
                    "日期": "date",
                    "开盘": "open",
                    "最高": "high",
                    "最低": "low",
                    "收盘": "close",
                    "成交量": "volume",
                }
                if not set(rename_map.keys()).issubset(raw.columns):
                    break

                df_t = raw.rename(columns=rename_map)[list(rename_map.values())].copy()
                df_t["date"] = pd.to_datetime(df_t["date"])
                df_t["asset"] = t
                # Use front-adjusted close as both close and adjusted close.
                df_t["adj_close"] = df_t["close"]
                break
            except Exception:
                if attempt < max_retries - 1:
                    time.sleep(1.5 * (attempt + 1))
                else:
                    df_t = None

        if df_t is None or df_t.empty:
            continue
        frames.append(df_t)
        time.sleep(0.2)

    if not frames:
        raise RuntimeError("Failed to download any ticker data from AkShare.")

    df = pd.concat(frames, ignore_index=True)
    for col in ["open", "high", "low", "close", "adj_close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["date", "close"]).set_index(["date", "asset"]).sort_index()
    df.index = df.index.set_names(["date", "asset"])
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path)
    return df
