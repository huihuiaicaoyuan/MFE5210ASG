# Factor References and Submission Checklist

This file is provided to satisfy the required **Reference** deliverable.

## 4. Submit to GitHub account (public or private)
Please ensure the repository submission includes:

a. **Code for generating alpha factors**  
- `factors/alpha_factors.py`

b. **Reference**  
- This file: `references/factor_references.md`

c. **Readme**  
- `README.md`, including:
  1. **Correlation matrix** (maximal correlation is `0.5`)  
  2. **Average Sharpe ratio** for all alpha factors (without cost)  
  3. **Others** (methodology, assumptions, limitations)

---

## Factor Source References

> Note: Current pipeline is **OHLCV-only**. Fundamental or short-interest factors are listed as future extensions.

### Implemented OHLCV-based factors
1. **Momentum / Reversal family**
   - `mom_20`, `mom_60`, `reversal_5`
   - Jegadeesh, N., & Titman, S. (1993). *Returns to Buying Winners and Selling Losers*.

2. **Volatility-related**
   - `volatility_20`
   - Ang, A., Hodrick, R., Xing, Y., & Zhang, X. (2006). *The Cross-Section of Volatility and Expected Returns*.

3. **Liquidity / Activity proxies**
   - `dollar_volume_20`, `turnover_20`, `volume_anom`, `size_proxy`
   - Amihud, Y. (2002). *Illiquidity and stock returns*.

4. **Technical / price-shape factors**
   - `ma_dist_20`, `rsi_14`, `overnight`, `hl_spread_5`, `intraday_momentum`, `max_ret_5d`
   - Jegadeesh, N. (1990). *Evidence of predictable behavior of security returns*.
   - Bali, T. G., Cakici, N., & Whitelaw, R. F. (2011). *Maxing out: Stocks as lotteries and the cross-section of expected returns*.

### Not implemented in current OHLCV-only pipeline
- `book_to_market`, `earnings_surprise`, `short_interest` (require fundamental / alternative datasets).

---

## Reporting Fields Required in README
For reproducible submission, README should report:
- Maximum absolute off-diagonal correlation across selected factors (`<= 0.5`).
- Average Sharpe ratio across all selected alpha factors (no transaction cost).
- Universe, period, rebalancing, ranking method, and constraints.
