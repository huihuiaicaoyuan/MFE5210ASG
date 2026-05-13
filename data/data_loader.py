"""Data loading utilities for market data retrieval and preprocessing."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import yfinance as yf


def download_ohlcv(
    tickers: Iterable[str],
    start: str,
    end: str,
    cache_path: str | Path = "data/ohlcv.parquet",
    refresh: bool = False,
) -> pd.DataFrame:
    """Download daily OHLCV data from Yahoo Finance and return a stacked dataframe.

    Returns dataframe indexed by [date, ticker] with columns:
    open, high, low, close, adj_close, volume.
    """
    cache_path = Path(cache_path)
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)

    raw = yf.download(
        tickers=list(tickers),
        start=start,
        end=end,
        interval="1d",
        auto_adjust=False,
        progress=False,
        group_by="ticker",
        threads=True,
    )

    frames = []
    for t in tickers:
        if (t,) in raw.columns:
            df_t = raw[t].copy()
        else:
            # yfinance single-level columns when one ticker
            df_t = raw.copy()
        df_t = df_t.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
        )
        df_t["ticker"] = t
        frames.append(df_t)

    df = pd.concat(frames).reset_index().rename(columns={"Date": "date"})
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["close"]).set_index(["date", "ticker"]).sort_index()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path)
    return df
