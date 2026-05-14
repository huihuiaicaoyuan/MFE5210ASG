"""Data loading utilities for market data retrieval and preprocessing."""
from __future__ import annotations

from pathlib import Path
import time
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

    Returns dataframe indexed by [date, asset] with columns:
    open, high, low, close, adj_close, volume.
    """
    cache_path = Path(cache_path)
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)

    clean_tickers = [str(t).strip().upper() for t in tickers if str(t).strip()]
    if not clean_tickers:
        raise ValueError("No valid tickers provided after cleaning.")

    # Small sequential batches reduce Yahoo rate-limit pressure.
    batch_size = 5
    max_retries = 3
    sleep_base_s = 2.0
    frames = []

    for i in range(0, len(clean_tickers), batch_size):
        batch = clean_tickers[i:i + batch_size]
        for t in batch:
            df_t = None
            for attempt in range(max_retries):
                try:
                    raw = yf.download(
                        tickers=t,
                        start=start,
                        end=end,
                        interval="1d",
                        auto_adjust=False,
                        progress=False,
                        group_by="ticker",
                        threads=False,
                    )
                    if raw is None or raw.empty:
                        break
                    if isinstance(raw.columns, pd.MultiIndex):
                        raw = raw.sort_index(axis=1)
                        if t in raw.columns.get_level_values(0):
                            df_t = raw[t].copy()
                        else:
                            df_t = raw.copy()
                    else:
                        df_t = raw.copy()
                    break
                except Exception:
                    if attempt == max_retries - 1:
                        df_t = None
                    else:
                        time.sleep(sleep_base_s * (attempt + 1))

            if df_t is None or df_t.empty:
                continue

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
            required_cols = {"open", "high", "low", "close", "adj_close", "volume"}
            if not required_cols.issubset(df_t.columns):
                continue
            df_t["ticker"] = t
            frames.append(df_t)

        # Throttle between batches.
        time.sleep(1.0)

    if not frames:
        raise RuntimeError("Failed to download any ticker data from Yahoo Finance.")

    df = pd.concat(frames).reset_index().rename(columns={"Date": "date"})
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["close"]).set_index(["date", "ticker"]).sort_index()
    df.index = df.index.set_names(["date", "asset"])
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path)
    return df
