"""Backtesting engine for cross-sectional long-short factor portfolios."""
from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def factor_long_short_returns(factor: pd.Series, fwd_ret: pd.Series, quantile: float = 0.1) -> pd.Series:
    """Compute daily L/S returns from a factor and next-day returns."""
    panel = pd.concat([factor.rename("factor"), fwd_ret.rename("fwd_ret")], axis=1).dropna()

    def _per_day(df: pd.DataFrame) -> float:
        n = len(df)
        if n < 20:
            return np.nan
        k = max(1, int(np.floor(n * quantile)))
        s = df.sort_values("factor")
        short_r = s.iloc[:k]["fwd_ret"].mean()
        long_r = s.iloc[-k:]["fwd_ret"].mean()
        return long_r - short_r

    return panel.groupby(level="date").apply(_per_day)


def performance_stats(ret: pd.Series) -> dict:
    ret = ret.dropna()
    ann_ret = (1 + ret).prod() ** (TRADING_DAYS / max(len(ret), 1)) - 1
    ann_vol = ret.std(ddof=0) * np.sqrt(TRADING_DAYS)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan
    curve = (1 + ret).cumprod()
    dd = curve / curve.cummax() - 1
    return {
        "annualized_return": ann_ret,
        "annualized_volatility": ann_vol,
        "sharpe_ratio": sharpe,
        "max_drawdown": dd.min(),
    }
