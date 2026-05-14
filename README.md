# MFE5210ASG: Diversified Cross-Sectional Alpha Research Framework

## Project Overview
This repository implements an end-to-end quantitative research workflow for cross-sectional long-short equity investing. The framework downloads real A-share stock data, builds diversified alpha factors, runs daily-rebalanced backtests, and exports diagnostics and visualizations for factor evaluation.

## Data Source
- **Provider:** BaoStock (`query_history_k_data_plus`)
- **Frequency:** Daily OHLCV
- **Universe:** 10 large and liquid A-share stocks (configured in `main.py`)
- **Period:** 2016-01-01 to 2026-05-01 (configurable in `main.py`)

## Project Structure
```
MFE5210ASG/
├── data/
│   └── data_loader.py
├── factors/
│   └── alpha_factors.py
├── backtest/
│   └── engine.py
├── results/
│   └── visualization.py
├── README.md
├── requirements.txt
└── main.py
```

## Factor Methodology
Implemented 11 diversified factors with distinct economic intuition:
1. `mom_20`
2. `mom_60`
3. `reversal_5`
4. `volatility_20`
5. `dollar_volume_20`
6. `volume_anom`
7. `ma_dist_20`
8. `rsi_14`
9. `overnight`
10. `turnover_20`
11. `hl_spread_5`

All factors are transformed cross-sectionally (daily z-score) and used for ranking in long-short construction.

## Portfolio Construction
- Daily cross-sectional ranking per factor
- **Long:** top 10%
- **Short:** bottom 10%
- Equal-weight on each side
- Daily rebalancing
- Forward return alignment (`t+1`) to avoid look-ahead bias

## Outputs
Generated files in `results/`:
- `factor_performance.csv`
- `cumulative_returns.csv`
- `correlation_matrix.csv`
- `cumulative_returns.png`
- `factor_correlation_heatmap.png`
- `summary_metrics.csv` (max correlation and average Sharpe, no cost)

## Notes
- BaoStock历史接口在部分网络环境下更稳定；下载器会记录失败股票并继续处理其余股票。
- Transaction costs, slippage, and shorting constraints are not modeled.

## How to Run
```bash
pip install -r requirements.txt
python main.py
```

The script downloads/caches data, computes factors, runs backtests, and writes outputs to `results/`.

## Factor Source Table
| Factor | Type | Data Source Fields | Notes |
|---|---|---|---|
| mom_20 / mom_60 | Momentum | close | 20/60日价格动量 |
| reversal_5 | Reversal | close | 5日反转 |
| volatility_20 | Volatility | close | 20日波动率（取负） |
| dollar_volume_20 | Liquidity | close, volume | 20日成交额对数 |
| volume_anom | Volume regime | volume | 20日/120日成交量比 |
| ma_dist_20 | Trend distance | close | 相对20日均线偏离 |
| rsi_14 | Oscillator | close | RSI标准化后取反 |
| overnight | Gap | open, close | 隔夜跳空收益 |
| turnover_20 | Activity | volume | 20日均成交量代理 |
| hl_spread_5 | Intraday range | high, low, close | 5日高低价振幅均值 |
| size_proxy | Size proxy | close, volume | 市值代理（成交额对数取反） |
| intraday_momentum | Intraday momentum | open, close | 当日开收到收盘动量 |
| max_ret_5d | Lottery effect | close | 过去5日最大单日收益取反 |

> 说明：book_to_market、earnings_surprise、short_interest 需要基本面/卖空数据源，当前OHLCV-only数据管线未包含。


## References File
- See `references/factor_references.md` for factor literature references and submission checklist items.
