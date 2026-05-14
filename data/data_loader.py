"""Data loading utilities for market data retrieval and preprocessing."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import baostock as bs
import pandas as pd


def _to_bs_symbol(code: str) -> str:
    code = code.strip().lower()
    if code.startswith(("sh.", "sz.")):
        return code
    if code.startswith(("sh", "sz")) and len(code) >= 8:
        return f"{code[:2]}.{code[2:]}"
    if code.startswith("6"):
        return f"sh.{code}"
    if code.startswith(("0", "3")):
        return f"sz.{code}"
    return code


def download_ohlcv(
    tickers: Iterable[str],
    start: str,
    end: str,
    cache_path: str | Path = "data/ohlcv.parquet",
    refresh: bool = False,
) -> pd.DataFrame:
    """Download daily OHLCV data from BaoStock and return a stacked dataframe.

    Returns dataframe indexed by [date, asset] with columns:
    open, high, low, close, adj_close, volume.
    """
    cache_path = Path(cache_path)
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)

    clean_tickers = [_to_bs_symbol(str(t)) for t in tickers if str(t).strip()]
    if not clean_tickers:
        raise ValueError("No valid tickers provided after cleaning.")

    login_res = bs.login()
    if login_res.error_code != "0":
        raise RuntimeError(f"BaoStock login failed: {login_res.error_msg}")

    frames = []
    failed_tickers: list[str] = []
    failed_reasons: dict[str, str] = {}

    fields = "date,open,high,low,close,volume"
    for t in clean_tickers:
        try:
            rs = bs.query_history_k_data_plus(
                code=t,
                fields=fields,
                start_date=start,
                end_date=end,
                frequency="d",
                adjustflag="2",  # forward adjusted
            )
            if rs.error_code != "0":
                failed_tickers.append(t)
                failed_reasons[t] = f"query error: {rs.error_msg}"
                continue

            rows = []
            while rs.next():
                rows.append(rs.get_row_data())
            if not rows:
                failed_tickers.append(t)
                failed_reasons[t] = "empty result"
                continue

            df_t = pd.DataFrame(rows, columns=rs.fields)
            required = ["date", "open", "high", "low", "close", "volume"]
            if not set(required).issubset(df_t.columns):
                failed_tickers.append(t)
                failed_reasons[t] = f"missing columns: {list(df_t.columns)}"
                continue

            df_t = df_t[required].copy()
            df_t["date"] = pd.to_datetime(df_t["date"])
            for col in ["open", "high", "low", "close", "volume"]:
                df_t[col] = pd.to_numeric(df_t[col], errors="coerce")
            df_t["asset"] = t
            df_t["adj_close"] = df_t["close"]
            frames.append(df_t)
        except Exception as e:
            failed_tickers.append(t)
            failed_reasons[t] = f"exception: {type(e).__name__}: {e}"

    bs.logout()

    if not frames:
        raise RuntimeError(f"Failed to download any ticker data from BaoStock. failures={failed_reasons}")

    print(f"BaoStock download success: {len(frames)} tickers")
    print(f"BaoStock download failed: {len(failed_tickers)} tickers")
    if failed_tickers:
        print(f"Failed tickers: {failed_tickers}")
        for sym in failed_tickers:
            print(f"Failure detail [{sym}]: {failed_reasons.get(sym, 'unknown reason')}")

    df = pd.concat(frames, ignore_index=True)
    df = df.dropna(subset=["date", "open", "high", "low", "close", "volume"])
    df = df.set_index(["date", "asset"]).sort_index()
    df.index = df.index.set_names(["date", "asset"])
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path)
    return df
