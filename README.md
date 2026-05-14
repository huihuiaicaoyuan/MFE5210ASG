# MFE5210ASG: Diversified Cross-Sectional Alpha Research Framework

## Project Overview
本项目实现了一个完整的横截面多空因子研究流程：下载 A 股日频数据、构建多类 Alpha 因子、执行按日再平衡回测，并输出因子表现、相关性与可视化结果。

## Data Source
- **Provider:** BaoStock（`query_history_k_data_plus`）
- **Frequency:** Daily OHLCV
- **Universe:** 10 只流动性较好的 A 股（在 `main.py` 中配置）
- **Period:** 2016-01-01 至 2026-05-01（可在 `main.py` 调整）

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
│   ├── visualization.py
│   ├── factor_performance.csv
│   ├── cumulative_returns.csv
│   ├── correlation_matrix.csv
│   ├── cumulative_returns.png
│   └── factor_correlation_heatmap.png
├── references/
│   └── factor_references.md
├── README.md
├── requirements.txt
└── main.py
```

## Factor Methodology
当前实现 **14 个** OHLCV 可计算因子（动量、反转、波动率、流动性、技术形态等）：

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
12. `size_proxy`
13. `intraday_momentum`
14. `max_ret_5d`

所有因子均进行日度横截面 z-score 标准化，用于排名构建多空组合。

## Portfolio Construction
- 每日按因子横截面排序
- **Long:** 前 10%
- **Short:** 后 10%
- 多空两侧等权
- 日频再平衡
- 使用 `t+1` 前瞻收益对齐，避免未来函数

---

## Results (Assignment Required)

### i. 相关性矩阵（最大相关系数 ≤ 0.5）
所有因子之间的两两相关系数均小于 0.5。最大绝对相关系数为 **0.1129**（出现在 `mom_20` 与 `reversal_5` 之间），显著低于作业要求上限 0.5，说明因子之间分散化效果良好。

- 完整相关性矩阵：`results/correlation_matrix.csv`
- 热力图：`results/factor_correlation_heatmap.png`

### ii. 所有 Alpha 因子的平均夏普比率（无交易成本）
基于 14 个因子的日度多空收益（每日等权做多前 10% / 做空后 10%），得到无交易成本年化夏普比率如下：

| 因子 | 夏普比率 |
|---|---:|
| intraday_momentum | 2.000 |
| reversal_5 | 1.760 |
| overnight | 1.460 |
| max_ret_5d | 1.378 |
| ma_dist_20 | 1.135 |
| mom_20 | 0.602 |
| rsi_14 | 0.411 |
| dollar_volume_20 | 0.292 |
| size_proxy | 0.262 |
| turnover_20 | 0.202 |
| volatility_20 | -0.011 |
| mom_60 | -0.112 |
| hl_spread_5 | -0.163 |
| volume_anom | -0.184 |

- **平均夏普比率（算术平均）= 0.645**
- 正夏普因子数量：10 个
- 负夏普因子数量：4 个

虽然部分因子夏普为负，但在样本期内，整体因子池仍体现出正向平均预测能力。

### iii. 其他补充信息
- 回测期间：2016-01-01 至 2026-05-01（约 2507 个交易日）
- 股票池：10 只流动性较好的 A 股（见 `main.py`）
- 因子总数：14 个
- 组合构建：每日横截面排名，做多最高 10%，做空最低 10%，等权重再平衡
- 最佳表现因子：`intraday_momentum`（年化收益 155%，夏普 2.0，最大回撤 -37.9%）
- 最差表现因子：`volume_anom`（年化收益 -7.2%，夏普 -0.184，最大回撤 -88.5%）
- 所有因子最大回撤范围：-0.886 至 -0.341，无低于 -100% 的异常值，说明数据清洗有效
- 代码结构：模块化（`data/`、`factors/`、`backtest/`），运行 `main.py` 可一键生成结果
- 依赖库：见 `requirements.txt`（pandas, numpy, baostock, matplotlib, seaborn 等）

---

## Outputs
运行后主要输出到 `results/`：
- `factor_performance.csv`
- `cumulative_returns.csv`
- `correlation_matrix.csv`
- `cumulative_returns.png`
- `factor_correlation_heatmap.png`
- `summary_metrics.csv`（最大相关性与平均夏普汇总）

## Notes
- BaoStock 历史接口在部分网络环境下更稳定；下载器会记录失败股票并继续处理其余股票。
- 当前回测未显式建模交易成本、冲击成本、融券约束与可借券限制。

## How to Run
```bash
pip install -r requirements.txt
python main.py
```

脚本会自动下载/缓存数据、计算因子、运行回测并导出全部结果。

## References
因子来源与文献说明见：`references/factor_references.md`
