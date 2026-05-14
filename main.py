"""Main entry point for diversified alpha factor research and backtesting."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from data.data_loader import download_ohlcv
from factors.alpha_factors import compute_factors, zscore_cross_section
from backtest.engine import factor_long_short_returns, performance_stats
from results.visualization import plot_cumulative_returns, plot_corr_heatmap


def main() -> None:
    Path("results").mkdir(exist_ok=True)

    universe = [
        "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "JPM", "V", "UNH",
        "HD", "PG", "MA", "XOM", "LLY", "JNJ", "BAC", "AVGO", "KO", "PEP",
        "COST", "ABBV", "MRK", "WMT", "CVX", "ADBE", "CRM", "NFLX", "AMD", "INTC",
    ]

    px = download_ohlcv(universe, start="2016-01-01", end="2026-05-01")
    px.index = px.index.set_names(["date", "asset"])
    factors = compute_factors(px)
    factors.index = factors.index.set_names(["date", "asset"])
    factors_z = zscore_cross_section(factors)

    close = px["adj_close"].fillna(px["close"])
    fwd_ret = close.groupby(level=1).pct_change().shift(-1)
    fwd_ret.index = fwd_ret.index.set_names(["date", "asset"])

    perf_rows = []
    ret_panel = {}
    for col in factors_z.columns:
        ret = factor_long_short_returns(factors_z[col], fwd_ret)
        ret_panel[col] = ret
        stats = performance_stats(ret)
        stats["factor"] = col
        perf_rows.append(stats)

    factor_returns = pd.DataFrame(ret_panel).sort_index()
    cumulative = (1 + factor_returns.fillna(0)).cumprod() - 1
    perf = pd.DataFrame(perf_rows).set_index("factor").sort_values("sharpe_ratio", ascending=False)

    corr = factors_z.groupby(level=0).mean().corr()

    perf.to_csv("results/factor_performance.csv")
    cumulative.to_csv("results/cumulative_returns.csv")
    corr.to_csv("results/correlation_matrix.csv")

    plot_cumulative_returns(cumulative, "results/cumulative_returns.png")
    plot_corr_heatmap(corr, "results/factor_correlation_heatmap.png")

    print("Saved outputs to results/")


if __name__ == "__main__":
    main()
