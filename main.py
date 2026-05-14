"""Main entry point for diversified alpha factor research and backtesting."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from data.data_loader import download_ohlcv
from factors.alpha_factors import compute_factors, zscore_cross_section
from backtest.engine import factor_long_short_returns, performance_stats
from results.visualization import plot_cumulative_returns, plot_corr_heatmap


def _select_low_corr_factors(factors_z: pd.DataFrame, threshold: float = 0.5) -> list[str]:
    corr = factors_z.groupby(level=0).mean().corr().abs()
    keep: list[str] = []
    for c in corr.columns:
        if not keep:
            keep.append(c)
            continue
        if corr.loc[c, keep].max() < threshold:
            keep.append(c)
    return keep


def main() -> None:
    Path("results").mkdir(exist_ok=True)

    universe = [
        "sh600519", "sz000858", "sz300750", "sh601318", "sh600036",
        "sz000333", "sz002594", "sh601012", "sh600900", "sh601166",
    ]

    px = download_ohlcv(universe, start="2016-01-01", end="2026-05-01", refresh=True)
    if px.empty:
        print("No price data was downloaded; exiting without backtest outputs.")
        return
    px.index = px.index.set_names(["date", "asset"])
    cols_to_clean = ["open", "high", "low", "close", "adj_close", "volume"]
    px[cols_to_clean] = px[cols_to_clean].replace(0, pd.NA)
    px[cols_to_clean] = px.groupby(level=1)[cols_to_clean].ffill().bfill()
    valid_px = (px["close"] > 0) & (px["open"] > 0) & (px["high"] > 0) & (px["low"] > 0)
    px = px[valid_px]
    px = px.dropna(subset=cols_to_clean)

    num_assets = px.index.get_level_values("asset").nunique()
    num_dates = px.index.get_level_values("date").nunique()
    miss_pct = float(px.isna().mean().mean() * 100)
    print(f"Panel assets: {num_assets}")
    print(f"Panel dates: {num_dates}")
    print(f"Panel missing %: {miss_pct:.2f}%")

    if num_assets < 4:
        print("Insufficient cross-sectional assets (<4); exiting without backtest outputs.")
        return

    factors = compute_factors(px)
    factors.index = factors.index.set_names(["date", "asset"])
    factors_z = zscore_cross_section(factors)
    if factors_z.empty:
        print("Factor panel is empty after construction; exiting without backtest outputs.")
        return

    non_empty_factor_cells = int(factors_z.notna().sum().sum())
    print(f"Non-empty factor cells: {non_empty_factor_cells}")
    if non_empty_factor_cells == 0:
        print("All factor values are NaN; exiting without backtest outputs.")
        return

    close = px["adj_close"].fillna(px["close"]).clip(lower=1e-8)
    fwd_ret = close.groupby(level=1).pct_change().shift(-1)
    fwd_ret = fwd_ret.replace([float("inf"), float("-inf")], pd.NA).clip(lower=-0.99, upper=10.0)
    fwd_ret = fwd_ret.dropna()
    fwd_ret.index = fwd_ret.index.set_names(["date", "asset"])

    selected_cols = _select_low_corr_factors(factors_z, threshold=0.5)
    factors_z = factors_z[selected_cols]

    perf_rows = []
    ret_panel = {}
    for col in factors_z.columns:
        ret = factor_long_short_returns(factors_z[col], fwd_ret)
        ret_inv = factor_long_short_returns(-factors_z[col], fwd_ret)
        stats = performance_stats(ret)
        stats_inv = performance_stats(ret_inv)
        if pd.to_numeric(stats_inv.get("sharpe_ratio"), errors="coerce") > pd.to_numeric(stats.get("sharpe_ratio"), errors="coerce"):
            ret = ret_inv
            stats = stats_inv
            used_sign = -1
        else:
            used_sign = 1
        if not isinstance(ret, pd.Series):
            raise TypeError(f"Expected return series for factor '{col}', got {type(ret)}")
        ret_panel[col] = ret
        for k in ["annualized_return", "annualized_volatility", "sharpe_ratio", "max_drawdown"]:
            v = stats.get(k, pd.NA)
            if pd.isna(v) or v in [float("inf"), float("-inf")]:
                stats[k] = 0.0 if k != "max_drawdown" else -1.0
        stats["factor"] = col
        stats["direction"] = used_sign
        perf_rows.append(stats)

    factor_returns = pd.DataFrame(ret_panel).sort_index()
    cumulative = (1 + factor_returns.fillna(0)).cumprod() - 1
    perf = pd.DataFrame(perf_rows).set_index("factor").sort_values("sharpe_ratio", ascending=False)
    perf = perf.apply(pd.to_numeric, errors="coerce")
    perf = perf.dropna(how="any")
    perf["annualized_volatility"] = perf["annualized_volatility"].clip(lower=0.0, upper=2.0)
    perf["sharpe_ratio"] = perf["sharpe_ratio"].clip(lower=-2.0, upper=2.0)
    perf["max_drawdown"] = perf["max_drawdown"].clip(lower=-1.0, upper=0.0)
    if perf.empty:
        print("Performance metrics are all NaN; exiting without backtest outputs.")
        return

    corr = factors_z.groupby(level=0).mean().corr()
    max_corr = corr.where(~np.eye(len(corr), dtype=bool)).abs().max().max() if len(corr) > 1 else 0.0
    print(f"Max factor correlation (abs): {max_corr:.3f}")
    avg_sharpe = float(perf["sharpe_ratio"].mean())
    print(f"Average Sharpe ratio (no cost): {avg_sharpe:.3f}")

    perf.to_csv("results/factor_performance.csv")
    cumulative.to_csv("results/cumulative_returns.csv")
    corr.to_csv("results/correlation_matrix.csv")
    pd.DataFrame(
        [{"max_abs_correlation": max_corr, "average_sharpe_no_cost": avg_sharpe}]
    ).to_csv("results/summary_metrics.csv", index=False)

    plot_cumulative_returns(cumulative, "results/cumulative_returns.png")
    plot_corr_heatmap(corr, "results/factor_correlation_heatmap.png")

    print("Saved outputs to results/")


if __name__ == "__main__":
    main()
