"""Cross-sectional alpha factor construction."""
from __future__ import annotations

import numpy as np
import pandas as pd


def _grp(df: pd.DataFrame):
    return df.groupby(level=1, group_keys=False)


def compute_factors(px: pd.DataFrame) -> pd.DataFrame:
    """Build a diversified panel of alpha factors.

    Input indexed by [date, asset] with OHLCV columns.
    Output indexed identically with factor columns.
    """
    g = _grp(px)
    close = px["adj_close"].copy().fillna(px["close"])
    open_ = px["open"]
    volume = px["volume"].replace(0, np.nan)
    ret1 = g["adj_close"].pct_change().fillna(g["close"].pct_change())

    fac = pd.DataFrame(index=px.index)
    fac["mom_20"] = close.groupby(level=1).pct_change(20)
    fac["mom_60"] = close.groupby(level=1).pct_change(60)
    fac["reversal_5"] = -close.groupby(level=1).pct_change(5)
    fac["volatility_20"] = -ret1.groupby(level=1).rolling(20).std().droplevel(0)
    fac["dollar_volume_20"] = (
        (close * volume).groupby(level=1).rolling(20).mean().droplevel(0).pipe(np.log)
    )
    fac["volume_anom"] = (
        volume.groupby(level=1).rolling(20).mean().droplevel(0)
        / volume.groupby(level=1).rolling(120).mean().droplevel(0)
    )
    ma_20 = close.groupby(level=1).rolling(20).mean().droplevel(0)
    fac["ma_dist_20"] = (close - ma_20) / ma_20

    delta = g["adj_close"].diff().fillna(g["close"].diff())
    up = delta.clip(lower=0)
    down = (-delta).clip(lower=0)
    rs = (up.groupby(level=1).rolling(14).mean().droplevel(0) /
          down.groupby(level=1).rolling(14).mean().droplevel(0))
    rsi = 100 - (100 / (1 + rs))
    fac["rsi_14"] = -(rsi - 50) / 50

    fac["overnight"] = (open_ / close.groupby(level=1).shift(1)) - 1
    fac["turnover_20"] = volume.groupby(level=1).rolling(20).mean().droplevel(0)
    fac["hl_spread_5"] = -((px["high"] - px["low"]) / close).groupby(level=1).rolling(5).mean().droplevel(0)

    fac.index = fac.index.set_names(["date", "asset"])

    return fac.replace([np.inf, -np.inf], np.nan)


def zscore_cross_section(factors: pd.DataFrame) -> pd.DataFrame:
    """Cross-sectional standardization for daily ranking."""
    if factors.empty:
        out = factors.copy()
        if isinstance(out.index, pd.MultiIndex) and out.index.nlevels == 2:
            out.index = out.index.set_names(["date", "asset"])
        return out

    def _z(x: pd.Series) -> pd.Series:
        std = x.std(ddof=0)
        if std == 0 or np.isnan(std):
            return x * np.nan
        return (x - x.mean()) / std

    out = factors.groupby(level=0, group_keys=False).transform(_z)
    out.index = factors.index
    out.index = out.index.set_names(["date", "asset"])
    return out
