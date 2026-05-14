"""Backtesting engine for cross-sectional long-short factor portfolios."""
from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def _ensure_panel_index(obj: pd.Series | pd.DataFrame, name: str) -> pd.Series | pd.DataFrame:
    """Validate and normalize two-level MultiIndex [date, asset]."""
    if not isinstance(obj.index, pd.MultiIndex):
        raise TypeError(f"{name} must be indexed by a MultiIndex [date, asset].")
    if obj.index.nlevels != 2:
        raise ValueError(f"{name} must have exactly 2 index levels [date, asset].")
    idx = obj.index
    if any(n is None for n in idx.names):
        idx = idx.set_names(["date", "asset"])
    elif list(idx.names) != ["date", "asset"]:
        idx = idx.set_names(["date", "asset"])
    out = obj.copy()
    out.index = idx
    return out.sort_index()


def factor_long_short_returns(factor: pd.Series, fwd_ret: pd.Series, quantile: float = 0.1) -> pd.Series:
    """Compute daily L/S returns from a factor and next-day returns."""
    if not isinstance(factor, pd.Series) or not isinstance(fwd_ret, pd.Series):
        raise TypeError("factor_long_short_returns expects factor and fwd_ret as pandas Series.")
    factor = _ensure_panel_index(factor.rename("factor"), "factor")
    fwd_ret = _ensure_panel_index(fwd_ret.rename("fwd_ret"), "fwd_ret")

    if not factor.index.equals(fwd_ret.index):
        common = factor.index.intersection(fwd_ret.index)
        factor = factor.loc[common]
        fwd_ret = fwd_ret.loc[common]

    panel = pd.concat([factor, fwd_ret], axis=1).dropna()
    if panel.empty:
        return pd.Series(dtype=float, name="ls_return")

    def _per_day(df: pd.DataFrame) -> float:
        n = len(df)
        k = max(1, int(np.floor(n * quantile)))
        min_required = max(2, 2 * k)
        if n < min_required:
            return np.nan
        s = df.sort_values("factor")
        short_r = s.iloc[:k]["fwd_ret"].mean()
        long_r = s.iloc[-k:]["fwd_ret"].mean()
        return long_r - short_r

    daily = panel.groupby(level=0).apply(_per_day)
    daily.index.name = "date"
    return daily.astype(float).rename("ls_return")


def performance_stats(ret: pd.Series) -> dict:
    if isinstance(ret, pd.DataFrame):
        if ret.shape[1] != 1:
            raise TypeError("performance_stats expects a 1D return series, not a multi-column DataFrame.")
        ret = ret.iloc[:, 0]
    if not isinstance(ret, pd.Series):
        raise TypeError("performance_stats expects a pandas Series.")

    ret = ret.dropna()
    if ret.empty:
        return {
            "annualized_return": np.nan,
            "annualized_volatility": np.nan,
            "sharpe_ratio": np.nan,
            "max_drawdown": np.nan,
        }

    ann_ret = float((1 + ret).prod() ** (TRADING_DAYS / len(ret)) - 1)
    ann_vol = float(ret.std(ddof=0) * np.sqrt(TRADING_DAYS))
    sharpe = float(ann_ret / ann_vol) if ann_vol > 0 else np.nan
    curve = (1 + ret).cumprod()
    dd = curve / curve.cummax() - 1
    return {
        "annualized_return": ann_ret,
        "annualized_volatility": ann_vol,
        "sharpe_ratio": sharpe,
        "max_drawdown": float(dd.min()),
    }
