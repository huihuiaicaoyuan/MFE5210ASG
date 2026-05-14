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

## Notes
- BaoStock历史接口在部分网络环境下更稳定；下载器会记录失败股票并继续处理其余股票。
- Transaction costs, slippage, and shorting constraints are not modeled.

## How to Run
```bash
pip install -r requirements.txt
python main.py
```

The script downloads/caches data, computes factors, runs backtests, and writes outputs to `results/`.
