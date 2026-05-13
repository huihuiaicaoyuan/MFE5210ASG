# MFE5210ASG: Diversified Cross-Sectional Alpha Research Framework

## Project Overview
This repository implements a professional end-to-end quantitative research workflow for cross-sectional long-short equity investing. The framework downloads real US stock market data, builds diversified alpha factors across multiple signal families, runs robust daily-rebalanced backtests, and exports diagnostics and visualizations for factor evaluation.

## Data Source
- **Provider:** Yahoo Finance via `yfinance`
- **Frequency:** Daily OHLCV
- **Universe:** 30 large-cap US equities
- **Period:** 2016-01-01 to 2026-05-01 (configurable in `main.py`)

## Project Structure
```
MFE5210ASG/
├── docs/
├── data/
│   └── data_loader.py
├── factors/
│   └── alpha_factors.py
├── backtest/
│   └── engine.py
├── results/
│   └── visualization.py
├── notebooks/
├── README.md
├── requirements.txt
└── main.py
```

## Factor Methodology
Implemented 11 diversified factors with distinct economic intuition:
1. `mom_20`: 1-month momentum (trend persistence)
2. `mom_60`: 3-month momentum (medium-term trend)
3. `reversal_5`: short-term mean reversion
4. `volatility_20`: low-volatility preference
5. `dollar_volume_20`: liquidity proxy
6. `volume_anom`: abnormal volume regime detector
7. `ma_dist_20`: moving-average displacement
8. `rsi_14`: overbought/oversold oscillator
9. `overnight`: close-to-open information gap
10. `turnover_20`: trading activity intensity
11. `hl_spread_5`: intraday range/turbulence proxy

All factors are transformed cross-sectionally (daily z-score) and used for ranking in long-short construction.

## Portfolio Construction
- Daily cross-sectional ranking per factor
- **Long:** top 10%
- **Short:** bottom 10%
- Equal-weight on each side
- Daily rebalancing
- Forward return alignment (`t+1`) to avoid look-ahead bias

## Performance Evaluation
The framework computes for every factor:
- Sharpe ratio
- Annualized return
- Annualized volatility
- Max drawdown
- Cumulative return path

Generated output files in `results/`:
- `factor_performance.csv`
- `cumulative_returns.csv`
- `correlation_matrix.csv`
- `cumulative_returns.png`
- `factor_correlation_heatmap.png`

## Correlation Control and Diversification
Factor diversification matters because highly correlated signals often represent the same risk premium and reduce incremental alpha. This project intentionally mixes trend, reversal, volatility, liquidity, and activity-based factors to lower redundancy. Correlation is monitored through `correlation_matrix.csv` and heatmap inspection. The practical target is keeping pairwise relationships moderate (often below 0.5), while recognizing market regimes can temporarily increase co-movement.

## Visualization Examples
- Multi-factor cumulative return chart
- Factor correlation heatmap

Both are saved under `results/` and can be reused in reports.

## Limitations
- Yahoo Finance data quality may vary by ticker/date.
- Corporate action handling relies on provider-adjusted fields.
- Transaction costs, slippage, borrow fees, and short constraints are not modeled.
- Universe is static in this baseline and may introduce survivorship bias.

## How to Run
```bash
pip install -r requirements.txt
python main.py
```

The script will download/cached data, compute factors, run backtests, and write outputs to `results/`.
