# Factor References

本文档聚焦说明本项目各 Alpha 因子的**来源与文献依据**（按当前实现的 14 个因子）。

## Data Scope Statement
- 数据范围：仅使用日频 OHLCV（open/high/low/close/volume）
- 因此本项目因子均为价格/成交量可直接构造的技术与交易型因子
- 不含需财务报表、分析师预期、融券余额等替代数据的基本面因子

---

## Implemented Factors and Sources

### 1) Momentum / Reversal
- **`mom_20`, `mom_60`（20/60日动量）**
  - 核心思想：过去表现较强（较弱）资产在后续短中期延续（反转）
  - 经典来源：Jegadeesh, N., & Titman, S. (1993). *Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency*.

- **`reversal_5`（5日短期反转）**
  - 核心思想：短期过度反应后的均值回归
  - 经典来源：Jegadeesh, N. (1990). *Evidence of Predictable Behavior of Security Returns*.

### 2) Volatility / Lottery-like Effect
- **`volatility_20`（20日波动率，策略中取负向暴露）**
  - 核心思想：高特质波动资产常对应较低风险调整后回报
  - 经典来源：Ang, A., Hodrick, R. J., Xing, Y., & Zhang, X. (2006). *The Cross-Section of Volatility and Expected Returns*.

- **`max_ret_5d`（过去5日最大单日收益，策略中取反）**
  - 核心思想：极端高单日收益所代表的“彩票型”偏好通常对应较差未来收益
  - 经典来源：Bali, T. G., Cakici, N., & Whitelaw, R. F. (2011). *Maxing Out: Stocks as Lotteries and the Cross-Section of Expected Returns*.

### 3) Liquidity / Trading Activity
- **`dollar_volume_20`（20日平均成交额对数）**
- **`turnover_20`（20日平均成交量代理换手活跃度）**
- **`volume_anom`（20日/120日成交量比）**
- **`size_proxy`（以价格×成交量构造的规模代理并取反）**
  - 核心思想：流动性与交易拥挤度会影响横截面预期收益
  - 经典来源：Amihud, Y. (2002). *Illiquidity and Stock Returns: Cross-Section and Time-Series Effects*.

### 4) Technical Price-shape / Micro-structure Proxies
- **`ma_dist_20`（价格相对20日均线偏离）**
- **`rsi_14`（14日RSI变换）**
- **`overnight`（隔夜跳空收益）**
- **`hl_spread_5`（5日高低振幅均值）**
- **`intraday_momentum`（日内开收到收盘收益）**
  - 核心思想：趋势偏离、超买超卖、隔夜信息与日内行为可提供短期定价偏差信号
  - 参考来源：Jegadeesh, N. (1990). *Evidence of Predictable Behavior of Security Returns*.

---

## Not Included in Current Pipeline
以下常见因子需要额外数据源，当前 OHLCV-only 管线暂未纳入：
- `book_to_market`（需财务报表）
- `earnings_surprise`（需盈利预期与公告数据）
- `short_interest`（需融券或卖空数据）

后续如接入基本面和替代数据，可在现有框架中扩展。
