# 量化交易课程大纲 V2（内容依赖驱动）
# Quantitative Trading Curriculum V2 (dependency-driven)

> **学习用途 · 非投资建议 / Learning only — not investment advice**
> 不构成买卖推荐或收益承诺。示例仅供教学。实盘须自行合规并承担风险。

**相对 V1 的主要变化：** V1 被硬塞进 Hardware-learning 的「5 个月 / 20 课」日历格；V2 按**知识依赖簇**划分阶段，课次与时长由内容深度决定；补上可测验跳过的零基础；加重回测陷阱 / 因子 / ML 防泄漏 / 仓位风险；并系统纳入先前 X/Canvas 的非主流做法与已核验的 2024–2026 前沿方法。

**先验材料：** Canvas `e986247c-…`（14 模块）、`1c5e6f58-…`（32 条 X 策展 + 10 周课）、`docs/CURRICULUM_RESEARCH.md`，以及本轮对 RD-Agent / TSFM / 链上等的检索。

## 0. 工时估算口径

| 档位 | 典型课时 | 依据 |
|------|---------|------|
| 轻 | 3–5h | 概念少 + 1–2 短练习 + 测验 |
| 中 | 6–10h | 多概念 + 一个完整 notebook |
| 重 | 12–18h | 多组对照实验 / 多 notebook / 长写作 |
| 项目 | 20–28h | 端到端交付物 |

每课 `hours` = 概念阅读与例题 + 练习/实验 + 测验/复盘缓冲。难度 1–5。

## 1. 知识地图（主题节点）

| 节点 slug | 阶段 | 课时 | 难度 | 可跳过 | 直接前置 |
|-----------|------|-----:|-----:|:------:|----------|
| `python-pandas-timeseries` | P0 | 7 | 1 | 是 | — |
| `stats-probability-basics` | P0 | 8 | 2 | 是 | python-pandas-timeseries |
| `basic-finance-markets` | P0 | 5 | 1 | 是 | — |
| `markets-language` | P1 | 5.5 | 2 | 否 | basic-finance-markets |
| `microstructure-orders` | P1 | 14.75 | 2 | 否 | markets-language |
| `returns-vol-corr` | P1 | 9.25 | 2 | 否 | python-pandas-timeseries, stats-probability-basics, markets-language |
| `eval-lab` | P1 | 7 | 2 | 否 | returns-vol-corr, microstructure-orders |
| `data-cleaning` | P2 | 32.75 | 3 | 否 | eval-lab |
| `backtest-traps` | P2 | 32.25 | 4 | 否 | data-cleaning, stats-probability-basics |
| `costs-in-backtest` | P2 | 7.5 | 3 | 否 | backtest-traps |
| `engines-vectorized-event` | P2 | 8 | 3 | 否 | costs-in-backtest |
| `momentum-trend` | P3 | 8 | 3 | 否 | engines-vectorized-event |
| `mean-reversion` | P3 | 7 | 3 | 否 | momentum-trend |
| `pairs-stat-arb` | P3 | 15.25 | 3 | 否 | mean-reversion |
| `strategy-compare-lab` | P3 | 5 | 3 | 否 | momentum-trend, mean-reversion, pairs-stat-arb |
| `factor-workflow` | P4 | 25 | 4 | 否 | strategy-compare-lab, backtest-traps |
| `factor-portfolio-lab` | P4 | 8 | 4 | 否 | factor-workflow |
| `ml-leakage-control` | P5 | 21 | 5 | 否 | factor-workflow, backtest-traps |
| `modern-ml-pipelines` | P5 | 11 | 4 | 否 | ml-leakage-control, data-cleaning |
| `portfolio-risk-sizing` | P6 | 24 | 4 | 否 | returns-vol-corr, strategy-compare-lab |
| `execution-slippage` | P6 | 15.75 | 3 | 否 | costs-in-backtest, portfolio-risk-sizing |
| `risk-systems-lab` | P6 | 8 | 3 | 否 | portfolio-risk-sizing, execution-slippage |
| `market-regimes-crisis` | P6 | 17.75 | 4 | 否 | risk-systems-lab |
| `paper-trading-infra` | P7 | 17.5 | 3 | 否 | market-regimes-crisis |
| `compliance-ethics` | P7 | 24 | 2 | 否 | paper-trading-infra |
| `frontier-llm-agents` | P8 | 29 | 5 | 否 | factor-workflow, ml-leakage-control, modern-ml-pipelines, compliance-ethics |
| `frontier-tsfm-altdata-crypto` | P8 | 19 | 4 | 否 | modern-ml-pipelines, data-cleaning, execution-slippage |
| `capstone` | P9 | 26 | 5 | 否 | paper-trading-infra, compliance-ethics, factor-workflow, portfolio-risk-sizing |

**程序员建议：** 对 P0 三课做测验；通过则跳过，把时间补给 P2/P4/P5/P6 的重课。

## 2. 阶段总览（由依赖簇导出，非日历格）

| 阶段 | 名称 | 课数 | 总课时 | 6h/周 | 12h/周 | 依赖簇 |
|------|------|-----:|-------:|------:|-------:|--------|
| P0 | 零基础准备（可测验跳过） / Zero-basis foundations (test-out OK) | 3 | 20h | ~3.3 周 | ~1.7 周 | Foundational skills before market microstructure |
| P1 | 市场语言与度量 / Market language & measurement | 4 | 36.50h | ~6.1 周 | ~3.0 周 | Market concepts + evaluation language |
| P2 | 数据与诚实回测 / Data & honest backtests | 4 | 80.50h | ~13.4 周 | ~6.7 周 | Research infrastructure / scientific method for backtests |
| P3 | 经典策略族 / Classic strategy families | 4 | 35.25h | ~5.9 周 | ~2.9 周 | Classic alpha templates before factors/ML |
| P4 | 因子研究 / Factor research | 2 | 33h | ~5.5 周 | ~2.8 周 | Cross-sectional research methods |
| P5 | 机器学习与现代流水线 / ML & modern pipelines | 2 | 32h | ~5.3 周 | ~2.7 周 | Supervised ML methodology for finance |
| P6 | 风险、仓位与执行 / Risk, sizing & execution | 4 | 65.50h | ~10.9 周 | ~5.5 周 | Portfolio construction / execution / controls / regimes |
| P7 | 纸面与伦理 / Paper trading & ethics | 2 | 41.50h | ~6.9 周 | ~3.5 周 | Operationalization and professional norms |
| P8 | 前沿与非主流方法 / Frontier & unconventional methods | 2 | 48h | ~8.0 周 | ~4.0 周 | Post-prerequisite frontier / niche methods |
| P9 | 结业项目 / Capstone | 1 | 26h | ~4.3 周 | ~2.2 周 | Synthesis |

**全量（含 P0）：精确 418.25 学时（跳过 P0 为 398.25）。** 6h/周 ≈ 69.7 周；12h/周 ≈ 34.9 周。
**跳过 P0 后：精确 398.25 学时。** 6h/周 ≈ 66.4 周；12h/周 ≈ 33.2 周。

精确合计：**418.25h 全量 / 398.25h 跳过 P0**。对外可表述为约 **350–418.25h 全量 / 330–398.25h 跳过基础**（含个人复盘缓冲）。

## 3. 阶段 ← 来源映射

| 阶段 | 主要来源（经典/平台） | Canvas / X 策展 | 前沿来源（已核验） |
|------|----------------------|-----------------|-------------------|
| P0 | 本地 Python（自包含）；QuantStart Python 清单；中文补充：聚宽零基础教程 | — | — |
| P1 | QuantStart；NYU MATH-GA 2708；Stern metrics | Canvas m1–m3；手册教程 | — |
| P2 | 回测审讯纪律；美国数据源（SEC EDGAR / ALFRED / Ken French / CRSP 文档）；AFML；VectorBT/Zipline；QuantStart；中文补充：聚宽审讯帖 | Canvas m4–m5；@AfuOnTheWay；@RoundtableSpace；@pyquantnews | Nautilus 同构；Quant-Arena 密封 hold-out 精神 |
| P3 | Stern；Canvas m6–m8；JT；Moskowitz et al. 2012 | quants.md 对照样本；QuantJourney | further reading: Chan Algorithmic Trading (Wiley 2013) |
| P4 | AFML；Factor Mirage；Qlib Alpha；@alin_alphapilot | Canvas m9；quant-wiki | LLM alpha mining（练习在 P8） |
| P5 | AFML CV/labeling；ML4T；Qlib Quick Start | Canvas m10；@quantscience_；ML4T 帖 | Qlib 深度模型可选对照 |
| P6 | QuantStart VaR/Kelly/execution；NYU TCA；UChicago FINM | Canvas m11–m12；@sera00111 | — |
| P7 | 本地离线纸面；Alpaca / IBKR paper 文档（仅文档级）；QuantStart paper-before-live；中文补充：聚宽模拟交易 | Canvas m13–m14；Qbot/Atlas | — |
| P8 | — | XQuant / Crypto 工具链等非主流 | RD-Agent(Q)；Chain-of-Alpha；Quant-Arena；TSFM 评测；GMX CCXT; perp funding arXiv:2212.06888; liquidation subcritical arXiv:2608.03616 |
| P9 | Canvas 结业量规；美国研究合同（离线）；中文补充：聚宽综合 | 开源策略库仅灵感 | 可选前沿负结果附录 |

## 4. 非主流 / 前沿条目清单 → 归属课

| 条目 | 来源 | 类型 | 归属课 |
|------|------|------|--------|
| 假设→数据→回测→风险→执行主链 | QuantStart SAT；Canvas 教程 | classic | `贯穿 P1–P7` |
| JoinQuant 审讯室 | 聚宽教程（第三方 lookmori 8 周镜像已移除：持续 500） | classic | `backtest-traps` |
| AFML 标签/purge/回测当CV/虚假发现 | LdP AFML；@lopezdeprado | classic | `backtest-traps / ml-leakage-control / factor-workflow` |
| Factor Mirage | @lopezdeprado | classic | `factor-workflow` |
| IC 优先于规则堆砌 | @alin_alphapilot | classic | `factor-workflow` |
| 回测好实盘亏三坑 | @AfuOnTheWay | classic | `backtest-traps` |
| 动量/均值回归/配对 | Canvas m6–m8；Stern；JT 1993；Moskowitz et al. 2012 | classic | `P3` |
| VectorBT | vectorbt.dev | classic | `engines-vectorized-event` |
| Zipline Reloaded | zipline.ml4trading.io；@_zheergen | classic | `engines-vectorized-event` |
| Backtrader | @pyquantnews | classic | `engines-vectorized-event` |
| Qlib 人工流水线 | qlib docs；@bkdgiffug | classic | `modern-ml-pipelines` |
| ML4T 仓库 | stefan-jansen；多条 X 帖 | classic | `ml-leakage-control / modern-ml-pipelines` |
| 仓位/VaR/Kelly | QuantStart；Canvas m11 | classic | `portfolio-risk-sizing` |
| 纸面先于实盘 | 本地离线纸面；Canvas m13；中文补充：聚宽模拟交易 | classic | `paper-trading-infra` |
| XQuant Learning Spec+AI 先跑再补 | @_zheergen/2114885286039789576 | niche | `python-pandas-timeseries + frontier-llm-agents` |
| Awesome Systematic Trading / 开源合集 | paperswithbacktest/awesome-systematic-trading | niche | `markets-language` |
| Crypto 工具链 Binance Vision/CCXT/资金费率 | @sera00111 | niche | `data-cleaning + frontier-tsfm-altdata-crypto` |
| quants.md + QuantJourney | @_zheergen | niche | `strategy-compare-lab` |
| Algo Trading Cookbook 配套仓 | @_zheergen；Packt | niche | `engines-vectorized-event / paper-trading-infra` |
| Qbot 本地一体 | @BTCqzy1 | niche | `engines-vectorized-event / paper-trading-infra` |
| 四引擎帖 Nautilus/Hummingbot | @RoundtableSpace | niche | `engines-vectorized-event` |
| quant-wiki | @bkdgiffug；LLMQuant | niche | `factor-workflow / markets-language` |
| OpenBB+AlphaLens+PyFolio 栈 | @quantscience_ | niche | `data-cleaning / modern-ml-pipelines` |
| 金融 API 清单 | @pyquantnews | niche | `data-cleaning` |
| NautilusTrader research-to-live | nautilustrader.io 2026；GitHub | frontier | `engines-vectorized-event + paper-trading-infra` |
| R&D-Agent(Q) | microsoft/RD-Agent；arXiv:2505.15155；MSR | frontier | `frontier-llm-agents` |
| AlphaAgent originality/complexity/alignment | arXiv:2502.16789；GitHub RndmVariableQ/AlphaAgent | frontier | `frontier-llm-agents` |
| Parametric look-ahead / FinCAD (problem; recipe NAME-ONLY) | arXiv:2605.24564 | frontier | `frontier-llm-agents` |
| CogAlpha (NAME-ONLY) | arXiv:2511.18850 | frontier | `frontier-llm-agents` |
| Chain-of-Alpha (**withdrawn by Lang Cao**; admin license comment) | arXiv:2508.06312 | frontier | `frontier-llm-agents` |
| LLM+MCTS 公式因子 | arXiv:2505.11122 | frontier | `frontier-llm-agents` |
| Quant-Arena 密封年基准 | arXiv:2610.30113 | frontier | `frontier-llm-agents / backtest-traps` |
| Chronos/TimesFM 金融评测 | arXiv:2511.18578 等 | frontier | `frontier-tsfm-altdata-crypto` |
| Base-rate-honest directional accuracy | arXiv:2607.12248 | frontier | `frontier-tsfm-altdata-crypto` + `eval-lab` |
| TSFM as prior not alpha engine | arXiv:2606.27100 | frontier | `frontier-tsfm-altdata-crypto` |
| Crypto PIT audit before alpha | arXiv:2608.25348 | frontier | `frontier-tsfm-altdata-crypto` + `data-cleaning` |
| Qlib Transformer/Localformer | Qlib release notes | frontier | `modern-ml-pipelines（可选对照）` |
| CCXT 兼容 GMX/链上适配 | Trading Strategy / Arbitrum 2025 | frontier | `frontier-tsfm-altdata-crypto` |
| 资金费率/链上指标流水线结构 | 社区开源示例（结构参考） | niche | `frontier-tsfm-altdata-crypto` |

说明：`classic`=主干必教；`niche`=先前 X/Canvas 非主流或糙而实用路径；`frontier`=2024–2026 已核验新方法（强调批判与防泄漏，不承诺收益）。

## 5. 分课大纲（课时/难度/Basis 与 `src/lib/curriculum.ts` 同步，由 `tools/check-hours.mjs` 校验）

### P0 · 零基础准备（可测验跳过）（Zero-basis foundations (test-out OK)）— 20h / 3 课

**阶段目标：** 补齐 Python/pandas、统计概率、基础金融。

**6h/周 ≈ 3.3 周；12h/周 ≈ 1.7 周。**

#### `python-pandas-timeseries` — Python / pandas 时间序列入门 / Python / pandas for time series
- **Hours:** 7h · **Difficulty:** 1/5 · **Basis:** 3h concepts + 3h lab + 1h quiz
- **Test-out:** 能独立 CSV→DatetimeIndex→pct_change→rolling→画图则跳过。
- **Prereqs:** —
- **Summary:** 索引、对齐、滚动、缺失；程序员可测验跳过。
- **Goals:**
  - 熟练 DatetimeIndex/reindex/align。
  - 会 rolling 与缺失处理。
  - OHLC 整理成可复现输入。
- **Must-teach:**
  - 时间索引第一公民；错位=隐性前瞻。
  - 向量化优于行循环。
  - 断言与 dtype 检查。
- **Exercises:**
  - 假 OHLC 算收益与均线。
  - 故意错位观察后果。
  - 三条断言。
- **Quiz topics:**
  - reindex+ffill 危险
  - pct_change 首行 NaN
- **Completion criteria:**
  - 可复现小 notebook+断言。
- **Method tags:** classic: Self-contained local pandas labs; QuantStart Python stack; Chinese supplement: JoinQuant community tutorials | niche: XQuant Learning: run first then fill gaps (@_zheergen)

#### `stats-probability-basics` — 统计与概率基础 / Statistics & probability basics
- **Hours:** 8h · **Difficulty:** 2/5 · **Basis:** 4h concepts + 3h sim lab + 1h quiz
- **Test-out:** 熟悉分布/相关/p值误用/多重比较则可跳过。
- **Prereqs:** `python-pandas-timeseries`
- **Summary:** 均值方差分位相关；多重比较直觉；可跳过。
- **Goals:**
  - 解释均值方差分位。
  - 区分样本噪声与相关。
  - 说明多重检验虚假发现。
- **Must-teach:**
  - 金融中 IID 常不成立。
  - 相关≠因果且会漂移。
  - 多次试错需打折显著性。
- **Exercises:**
  - 收益直方图与分位。
  - 滚动 vs 全样本相关。
  - 100 次随机策略假阳性。
- **Quiz topics:**
  - 标准差与方差
  - 多重比较
- **Completion criteria:**
  - 假阳性模拟+结论。
- **Method tags:** classic: AFML multiple-testing spirit; CFA-ish stats literacy

#### `basic-finance-markets` — 基础金融与市场概念 / Basic finance & market concepts
- **Hours:** 5h · **Difficulty:** 1/5 · **Basis:** 3h reading + 1.5h writing + 0.5h quiz
- **Test-out:** 能解释多空杠杆基准复利则测验通过可跳过。
- **Prereqs:** —
- **Summary:** 现货期货ETF、多空杠杆、复利、基准；可部分跳过。
- **Goals:**
  - 区分现货期货ETF直觉。
  - 解释多空杠杆损益。
  - 选择简单基准。
- **Must-teach:**
  - 收益与风险成对；无免费午餐。
  - 基准须可投资可复现。
  - 本课是研究流程非荐股。
- **Exercises:**
  - 单利 vs 复利净值。
  - 研究市场与基准一段。
- **Quiz topics:**
  - 多空与杠杆
  - 基准选择
- **Completion criteria:**
  - 市场/基准一页纸。
- **Method tags:** classic: QuantStart beginner books; Default: US-listed stocks/ETFs in USD; Chinese supplement: JoinQuant 初识量化

### P1 · 市场语言与度量（Market language & measurement）— 36.50h / 4 课

**阶段目标：** 用交易语言说话，并用收益/风险指标诚实评价玩具信号。

**6h/周 ≈ 4.8 周；12h/周 ≈ 2.4 周。**

#### `markets-language` — 市场与交易语言 / Markets & trading vocabulary
- **Hours:** 5.5h · **Difficulty:** 2/5 · **Basis:** 2h concepts + 2.5h exercises + 0.5h quiz + 0.5h ETF NAV/premium-discount (Rule 6c-11)
- **Prereqs:** `basic-finance-markets`
- **Summary:** 假设→信号→风险→归因；Alpha/Beta；可复现。
- **Goals:**
  - 三句话研究目标。
  - 区分 Alpha/Beta。
  - 列出市场摩擦。
- **Must-teach:**
  - 主目标是约束下风险调整后表现。
  - 程序员优势在工程化研究链。
  - 策略必须可复现。
- **Exercises:**
  - CSV→收益→净值。
  - 研究目标三句话。
  - 摩擦清单≥5。
- **Quiz topics:**
  - Alpha/Beta
  - 目标是否可检验
- **Completion criteria:**
  - 目标三句话+净值 notebook。
- **Method tags:** classic: Canvas m1; QuantStart SAT process | niche: Awesome Systematic Trading (paperswithbacktest GitHub)

#### `microstructure-orders` — 微观结构与订单 / Microstructure & orders
- **Hours:** 14.75h · **Difficulty:** 2/5 · **Basis:** 3h concepts + 3h exercises + 1h quiz + 2h US mechanics (T+1/cash vs margin/NBBO·SIP·IEX/sessions/Rule 611 proposal status/best execution) + 0.5h overnight trading & overnight LULD bands (planned 2026-12-06) + 0.25h Rule 612/610(c) version trap + 0.25h HK T+1 plan comparison (target H2 2028, not in effect) + 0.5h official close/closing auction/NYSE MOC cutoff + 0.5h tiered round lots & odd-lot quotes (2025-11-03 / 2026-04-27) + 0.25h SIPC account protection (SIPC limits; not FDIC) + 0.25h tokenized-stock venue (TSV) data separation (SEC 34-106402; TSV prints are not exchange prints) + 0.25h official open, opening auction & MOO cutoff (NYSE DMM open may print after 9:30; Nasdaq NOOP, MOO cutoff 9:28 ET) + 0.25h NYSE early-close MOC cutoff (12:50 ET when close is 13:00) + 0.25h Nasdaq vs NYSE close cutoffs (Nasdaq MOC 15:55 / LOC 15:58) + 0.25h cash-account freeriding (Reg T payment period and 90-day freeze) + 0.25h Rule 15c3-3 customer protection (possession or control and the reserve account) + 0.25h Texas Stock Exchange (TXSE) launch and sessions + 0.25h intermarket sweep orders (ISO as a current-law Rule 611 exception) + 0.25h stop / stop-limit / trailing stop + 0.25h Rule 610(e) locked/crossed quotations (current law; S7-2026-20 would also rescind it) + 0.5h SIP sale conditions M / Q / T (plus 6 vs M) + 0.25h Rule 611(b) exceptions beyond ISO + 0.25h Rule 15c6-1 / FINRA 11320 delivery-date types
- **Prereqs:** `markets-language`
- **Summary:** 价差、mid、市价/限价、滑点；同bar零成本过乐观。
- **Goals:**
  - 手算 mid 与市价买 bps。
  - 写成交成本假设一页。
  - 对比收盘vs次日开盘。
- **Must-teach:**
  - mid=(bid+ask)/2。
  - 市价买贴近 ask。
  - 冲击/延迟只建直觉不做HFT配方。
- **Exercises:**
  - 手算 bps。
  - 成本假设一页。
  - 两种成交时点叙述。
- **Quiz topics:**
  - 市价单成交侧
  - 价差是否成本
- **Completion criteria:**
  - 成本假设一页+测验。
- **Method tags:** classic: Canvas m2; NYU MATH-GA 2708 | niche: (moved @sera00111 crypto data notes to data-cleaning)

#### `returns-vol-corr` — 收益、波动与相关 / Returns, volatility & correlation
- **Hours:** 9.25h · **Difficulty:** 2/5 · **Basis:** 3h formulas + 4h coding + 1h quiz + 0.5h leveraged/inverse ETF daily reset + 0.5h risk-free rate from T-bill quotes (TreasuryDirect price formula, ~3:30 PM quote time) + 0.25h NY Fed SOFR publication timestamp
- **Prereqs:** `python-pandas-timeseries`, `stats-probability-basics`, `markets-language`
- **Summary:** 年化、夏普、MDD、滚动统计；压力期相关。
- **Goals:**
  - 正确年化波动。
  - 实现夏普与MDD。
  - 展示滚动相关升高。
- **Must-teach:**
  - σ_ann≈σ_day×√252。
  - 夏普需声明频率与Rf。
  - 回撤路径依赖。
- **Exercises:**
  - 实现 max_drawdown。
  - 滚动波动图。
  - 滚动相关+压力标注。
- **Quiz topics:**
  - 年化因子
  - 夏普定义
- **Completion criteria:**
  - 可复用指标函数+测验。
- **Method tags:** classic: Canvas m3; QuantStart performance; Chinese supplement: JoinQuant returns/risk tutorial

#### `eval-lab` — 评估实验：基准与诚实指标 / Evaluation lab: benchmarks & honest metrics
- **Hours:** 7h · **Difficulty:** 2/5 · **Basis:** 1.5h concepts + 3h lab + 0.5h PyFolio map + 0.5h base-rate pointer + 1.5h quiz
- **Prereqs:** `returns-vol-corr`, `microstructure-orders`
- **Summary:** 成本后指标表；玩具信号 vs 买入持有。
- **Goals:**
  - 做成本后对照表。
  - 解释胜率≠好策略。
- **Must-teach:**
  - 只报毛收益不诚实。
  - 换手放大成本。
- **Exercises:**
  - 指标对照表。
  - 滑点升档实验。
- **Quiz topics:**
  - 为何需要基准
  - 换手与成本
- **Completion criteria:**
  - 对照表+三句结论。
- **Method tags:** classic: Canvas eval; pyfolio tear-sheet docs; Chinese supplement: JoinQuant 策略评价 | niche: @FG731314/2115609441748001008 risk-adjusted traits

### P2 · 数据与诚实回测（Data & honest backtests）— 80.50h / 4 课

**阶段目标：** 可版本化数据+陷阱审讯+成本+引擎假设。

**6h/周 ≈ 12.5 周；12h/周 ≈ 6.3 周。**

#### `data-cleaning` — 数据与清洗 / Data & cleaning
- **Hours:** 32.75h · **Difficulty:** 3/5 · **Basis:** 5h concepts + 6h pipeline lab incl mask-first + 2h info-bars + 1h crypto-PIT + 3h docs/quiz + 2h data-versions/corporate-actions/calendar lab + 3h US data sources/licensing/PIT lab (EDGAR/FRED terms R16/Ken French/CRSP/yfinance/Massive/Alpaca) + 2h corporate actions & delisting (R21) + 1h ALFRED revision as-of + 0.5h dividend dates under T+1 (investor.gov) + 0.25h yfinance auto_adjust version trap + 0.5h filing deadlines & EDGAR 5:30pm rule (10-K/10-Q/8-K/13F) + 0.5h delisting returns & permanent IDs (CRSP CIZ) + 0.5h spin-offs & mergers in price series (CRSP split events, DisPERMNO, Form 8937 timing) + 0.5h insider & large-holder filing lags (Form 4 / 13D / 13G, FPI insiders from 2026-03-18) + 0.5h reverse splits & Nasdaq bid-price rule status (30 business days below $1, prior-year reverse split, $0.10 rule, stayed $5M MVLS rule) + 0.5h SEC XBRL API as-of (filed date; frames = last filed; fy describes the filing) + 0.25h Rule 10b5-1 plan check box (Forms 4/5 from 2023-04-01) & cooling-off + 0.5h NYSE price criteria (30-day average, 200:1 reverse-split limit, $0.25 floor from 2027-07-01) + 0.5h Rule 10b-18 buyback safe harbor + 0.25h Item 703 repurchase disclosure lag (Form SR vacated) + 0.5h tender offers (Rule 14e-1 minimum period) + 0.25h Rule 10b-18 after-hours prong (no official 23/5 mapping) + 0.25h Rule 10b-17 issuer notice of record dates + 0.25h Form 4 transaction codes and Form 3 / Form 5 clocks + 0.5h 13G-to-13D switch and 13d-3 beneficial ownership + 0.25h Rule 14e-5 purchases outside a tender offer + 0.25h when-issued / when-distributed contracts (FINRA 11130; Nasdaq CQS WI) + 0.25h 12b-2 filer thresholds and hysteresis
- **Prereqs:** `eval-lab`
- **Summary:** 复权、停牌、缺失、幸存者、PIT；数据说明书。
- **Goals:**
  - 版本化下载与哈希。
  - 举例幸存者偏差。
  - 写数据说明书。
- **Must-teach:**
  - 今日成分≠历史宇宙。
  - 基本面需PIT。
  - 时区混乱可前瞻一天。
- **Exercises:**
  - reindex+缺失断言。
  - 复权对照。
  - 数据说明书。
- **Quiz topics:**
  - 幸存者偏差
  - PIT含义
- **Completion criteria:**
  - 管线可复跑+说明书。
- **Method tags:** classic: Canvas m4; QuantStart securities master; Qlib data layer; US source map: SEC EDGAR / ALFRED / Ken French / CRSP docs; Chinese supplement: JoinQuant data docs | niche: @pyquantnews 45 APIs (2116517809920327801); OpenBB quantitative docs; Binance Vision + @sera00111 crypto data notes | frontier: Alt-data awareness; deeper in P8

#### `backtest-traps` — 回测陷阱与过拟合审讯 / Backtest traps & overfitting interrogation
- **Hours:** 32.25h · **Difficulty:** 4/5 · **Basis:** 5h concepts + 19h multi-labs (CPCV + one-switch + PBO/CSCV + admission gates) + 4h write-up + 0.5h index membership as-of (Russell semi-annual 2026) + 0.25h FOMC release times as event timestamps + 0.5h IPO data traps (offering price vs fill, short history, lock-ups) + 0.25h Nasdaq-100 rule versions (2026-05-01) and December 2026 reconstitution dates + 0.5h S&P 500 addition rules as of a date (committee discretion, dated cap thresholds, 05:15 PM ET announcements) + 0.25h earnings release times as event timestamps (8-K Item 2.02, Reg FD) + 0.5h Rule 144 resales of restricted and control stock + 0.5h follow-on offerings and Regulation M Rule 105 + 0.5h Regulation M Rule 101/102 restricted period and shelf takedowns + 0.25h BLS PFEI vs non-PFEI release times + 0.25h Fed G.17 monthly 9:15 a.m. vs annual revision at noon — HEAVY
- **Prereqs:** `data-cleaning`, `stats-probability-basics`
- **Summary:** 前瞻、walk-forward、PSR/DSR、试验次数、幸存者回顾。
- **Goals:**
  - 作弊vs诚实对照。
  - 样本外/walk-forward。
  - 记录失败与试验次数。
- **Must-teach:**
  - 未shift用当日收益=前瞻。
  - 多重试错制造虚假发现。
  - 冻结规则后再看样本外。
- **Exercises:**
  - 均线作弊/诚实。
  - 参数网格过拟合。
  - 末段hold-out。
  - 失败日志模板。
- **Quiz topics:**
  - lookahead定义
  - 为何记录试验次数
  - walk-forward目的
- **Completion criteria:**
  - 陷阱报告含对照与OOS。
- **Method tags:** classic: Canvas m5; Backtest interrogation discipline; Chinese supplement: JoinQuant 审讯室 posts; AFML backtest-as-CV; @AfuOnTheWay三坑; @lopezdeprado虚假发现 | niche: (XQuant tag dropped — unverified this batch) | classic+: Bailey-LdP 2012 PSR / 2014 DSR; AFML ch.7/14 | frontier: Quant-Arena arXiv:2610.30113 sealed hold-out; When Alpha Disappears arXiv:2605.23959 one-switch

#### `costs-in-backtest` — 成本写入回测 / Costs in the backtest
- **Hours:** 7.5h · **Difficulty:** 3/5 · **Basis:** 2h concepts + 3.5h coding + 0.5h quiz + 0.75h Rule 605 effective spread (FAQ Example 27-1, covered-order filters) + 0.5h SEC Section 31 fee & FINRA TAF on sells (dated fee schedules; TAF pause 2026-10-01 to 2026-12-31) + 0.25h CAT fees on both sides (dated per-share rates; CAT Fee 2026-1 $0.000001)
- **Prereqs:** `backtest-traps`
- **Summary:** 四段成本+√冲击；堆叠分解与容量。
- **Goals:**
  - 实现换手成本公式。
  - ≥3档成本敏感。
- **Must-teach:**
  - 零成本曲线≠实盘论据。
  - 显性vs隐性成本。
- **Exercises:**
  - 写入净收益。
  - 成本阶梯图。
- **Quiz topics:**
  - 隐性成本例子
  - 换手如何进公式
- **Completion criteria:**
  - 成本后主回测可运行。
- **Method tags:** classic: Canvas costs; QuantStart TCA; NYU TCA themes

#### `engines-vectorized-event` — 回测引擎：向量化与事件驱动 / Backtest engines: vectorized & event-driven
- **Hours:** 8h · **Difficulty:** 3/5 · **Basis:** 3h concepts + 4h compare lab + 1h docs
- **Prereqs:** `costs-in-backtest`
- **Summary:** VectorBT vs Zipline/Backtrader；同构引擎概念。
- **Goals:**
  - 陈述向量化默认风险。
  - 对比两成交时点净值。
  - 用initialize/handle_data描述事件循环。
- **Must-teach:**
  - 引擎选择=成交与日历假设。
  - 先诚实向量化再事件验证。
  - 同构引擎降低研究≠实盘缝隙（概念）。
- **Exercises:**
  - 同信号两成交时点。
  - 写回测假设段。
  - （可选）浏览VectorBT与Zipline示例。
- **Quiz topics:**
  - 向量化乐观默认
  - 事件驱动解决什么
- **Completion criteria:**
  - 假设段+双成交对照。
- **Method tags:** classic: VectorBT; Zipline Reloaded; Backtrader; Canvas engines | niche: @RoundtableSpace/2111272232249143360 engine list | frontier: NautilusTrader shared-kernel architecture docs

### P3 · 经典策略族（Classic strategy families）— 35.25h / 4 课

**阶段目标：** 复现动量/回归/配对并做对照。

**6h/周 ≈ 5.7 周；12h/周 ≈ 2.9 周。**

#### `momentum-trend` — 动量与趋势 / Momentum & trend
- **Hours:** 8h · **Difficulty:** 3/5 · **Basis:** 3h concepts + 4.5h labs + 0.5h quiz
- **Prereqs:** `engines-vectorized-event`
- **Summary:** 时序/截面动量、12-1、换手与波动目标。
- **Goals:**
  - 双均线与简化动量对照。
  - 报告换手与分年。
- **Must-teach:**
  - 跳过近一月减弱短期反转。
  - 拥挤与换手侵蚀优势。
- **Exercises:**
  - 双均线vs动量。
  - 波动目标10%。
  - 分年表。
- **Quiz topics:**
  - 12-1动机
  - 时序vs截面
- **Completion criteria:**
  - 两套动量结果含成本。
- **Method tags:** classic: Canvas m6; JT 1993; Moskowitz–Ooi–Pedersen 2012; Stern trend | niche: quants.md trend samples as foils; QuantJourney browse critically | further reading: Ernest P. Chan, Algorithmic Trading (Wiley 2013, ISBN 978-1-118-46014-6)

#### `mean-reversion` — 均值回归 / Mean reversion
- **Hours:** 7h · **Difficulty:** 3/5 · **Basis:** 2.5h concepts + 4h labs + 0.5h quiz
- **Prereqs:** `momentum-trend`
- **Summary:** z-score开平仓、止损、趋势市失效。
- **Goals:**
  - 实现z规则。
  - 写失效清单。
- **Must-teach:**
  - 强趋势中回归易反复止损。
  - 阈值再估计。
  - AR(1)/OU 半衰期选回看与持有；z[t] 仅从 t+1 改仓。
- **Exercises:**
  - z<-2/z>2。
  - 有无止损A/B。
  - 失效清单。
- **Quiz topics:**
  - 回归策略趋势市表现
  - 为何再估计阈值
- **Completion criteria:**
  - 回归notebook+失效讨论。
- **Method tags:** classic: Canvas m7; Stern counter-trend; OU/AR(1) half-life | niche: quants.md reversal samples as foils | further reading: Chan Algorithmic Trading (Wiley 2013, ISBN 978-1-118-46014-6)

#### `pairs-stat-arb` — 配对与统计套利入门 / Pairs & intro statistical arb
- **Hours:** 15.25h · **Difficulty:** 3/5 · **Basis:** 4h concepts + 5h lab + 1h write-up + 2h optional Kalman hedge ratio (filter vs smoother) + 1h US short-sale constraints (Reg SHO layers, borrow, dividends) + 1h short-side public data (FINRA 4560 short interest by publish date, short volume ≠ short interest, FTD balance; SR-FINRA-2026-012 withdrawn) + 0.25h Form SHO & Rule 10c-1a status (exempted to 2028-01-02 / 2029-03-29) + 0.25h Reg SHO locate ≠ borrow & Rule 204 close-out under T+1 + 0.25h Rule 201 NBB test & threshold-security definition + 0.25h Rule 10b-21 (deception and a fail) + 0.25h Rule 200 long-marking test
- **Prereqs:** `mean-reversion`
- **Summary:** 价差、滚动对冲比、相关≠可交易。
- **Goals:**
  - 滚动beta价差。
  - 讨论腿断裂。
- **Must-teach:**
  - 高相关不足够。
  - 协整直觉。
  - 对冲比再估计。
- **Exercises:**
  - 滚动价差与z。
  - 静态vs滚动。
  - 冲击情景段。
- **Quiz topics:**
  - 相关vs协整
  - 为何滚动估计
- **Completion criteria:**
  - 含成本配对notebook。
- **Method tags:** classic: Canvas m8; Stern spreads; Engle–Granger/MacKinnon | niche: quants.md W13/W14 | further reading: Ernest P. Chan, Algorithmic Trading (Wiley 2013, ISBN 978-1-118-46014-6)

#### `strategy-compare-lab` — 策略对照实验 / Strategy comparison lab
- **Hours:** 5h · **Difficulty:** 3/5 · **Basis:** 1h framing + 3.5h report + 0.5h quiz
- **Prereqs:** `momentum-trend`, `mean-reversion`, `pairs-stat-arb`
- **Summary:** 同一宇宙/成本/指标；复杂须胜过简单基准。
- **Goals:**
  - 三策略并排报告。
  - 判定是否胜过基准。
- **Must-teach:**
  - 控制隐藏假设；统一成本模型（配对含冲击）。
  - 简单是基准线。
  - 显式试验数 N 上对所选策略算 DSR（须用与选赢家相同的 OOS 序列）。
- **Exercises:**
  - 三策略报告。
  - 指定基准并判定。
- **Quiz topics:**
  - 对照实验要素
- **Completion criteria:**
  - 对照报告入库。
- **Method tags:** classic: Canvas comparison spirit; Same-protocol comparison rules | niche: Critique open strategy dumps (quants.md) as hypothesis sources only | further reading: Chan Algorithmic Trading (Wiley 2013, ISBN 978-1-118-46014-6)

### P4 · 因子研究（Factor research）— 33h / 2 课

**阶段目标：** IC/分层/组合化的可重复因子工作流。

**6h/周 ≈ 5.5 周；12h/周 ≈ 2.8 周。**

#### `factor-workflow` — 因子研究工作流 / Factor research workflow
- **Hours:** 25h · **Difficulty:** 4/5 · **Basis:** 5h concepts + 15h labs (incl Detzel + NMV 2016 taxonomy + w34898 + HXZ + admission) + 3h write-up + 1h crowding→LLM bridge — HEAVY + 1h US factor benchmark alignment (percent, missing markers, Mkt-RF+RF, compounding)
- **Prereqs:** `strategy-compare-lab`, `backtest-traps`
- **Summary:** IC、分层、衰减、中性化直觉；拒绝堆参数。
- **Goals:**
  - 实现Spearman IC。
  - 分层多空。
  - 真/假因子对照。
- **Must-teach:**
  - IC=截面排序一致性；RankIC / ICIR / IC 衰减。
  - 因子构建：去极值、z 标准化、行业与市值中性化。
  - 分层多空 + 换手成本；Fama–MacBeth（及 FF3/FF5 文献）。
  - 因子海市蜃楼与多重检验（Harvey–Liu–Zhu t>3）。
  - 从经济假设出发；Alphalens/Qlib 风格工作流。
- **Exercises:**
  - ic(factor,fwd)。
  - 分层净值。
  - 打乱因子对照。
  - IC衰减图。
- **Quiz topics:**
  - Spearman IC
  - 为何空因子对照
  - IC衰减含义
- **Completion criteria:**
  - IC+分层+空因子报告。
- **Method tags:** classic: Canvas m9; AFML/Factor Mirage; @alin_alphapilot IC-first; Qlib Alpha158 ref | niche: quant-wiki factor map (@bkdgiffug) | frontier: LLM formulaic alpha mining after this; formalized in P8

#### `factor-portfolio-lab` — 因子到组合实验 / Factor-to-portfolio lab
- **Hours:** 8h · **Difficulty:** 4/5 · **Basis:** 2.5h concepts + 4.5h lab + 1h quiz
- **Prereqs:** `factor-workflow`
- **Summary:** 换手、简单中性化、多因子合成诚实评估。
- **Goals:**
  - 估计因子组合换手。
  - 简易市值中性化示意。
  - 单因子vs等权多因子。
- **Must-teach:**
  - 合成不自动提高可交易性。
  - 换手与成本再决定净收益（共享成本模型）。
  - 中性化前后对照；拥挤与衰减。
- **Exercises:**
  - 中性化前后IC。
  - 多因子等权对照。
  - 换手-成本表。
- **Quiz topics:**
  - 中性化目的
  - 多因子过拟合风险
- **Completion criteria:**
  - 因子→组合小报告。
- **Method tags:** classic: Canvas m9 ext; Qlib portfolio/backtest optional

### P5 · 机器学习与现代流水线（ML & modern pipelines）— 32h / 2 课

**阶段目标：** 防泄漏ML + 可复现现代流水线基线。

**6h/周 ≈ 5.3 周；12h/周 ≈ 2.7 周。**

#### `ml-leakage-control` — 机器学习防泄漏 / ML anti-leakage
- **Hours:** 21h · **Difficulty:** 5/5 · **Basis:** 6h AFML concepts + 12h labs (fracdiff/uniqueness/meta/CPCV + one-switch + KTD/Mirage pointers) + 3h write-up — HEAVY
- **Prereqs:** `factor-workflow`, `backtest-traps`
- **Summary:** 时间切分、特征shift、标签直觉、purge/embargo、元标签、试验次数。
- **Goals:**
  - 演示shuffle泄漏。
  - 时间切分并shift特征。
  - 用IC而非仅准确率评价。
- **Must-teach:**
  - 失败常在管线。
  - 禁止时序shuffle。
  - 完整 purged K-fold + embargo（标签跨度重叠 purge；AFML ch.7）；scaler 仅 fit 训练折。
  - 标签：远期收益、三重势垒、元标签（AFML ch.3）；检查前瞻。
  - 用 IC / 净 SR / DSR 评价，而非准确率。
  - 元标签：先方向再是否交易。
- **Exercises:**
  - 随机vs时间切分。
  - 修复三处泄漏。
  - 用IC评价预测。
  - 记录试验次数。
- **Quiz topics:**
  - 为何不能shuffle
  - purge解决什么
  - 标签泄漏例子
- **Completion criteria:**
  - 防泄漏notebook+试验日志。
- **Method tags:** classic: Canvas m10; AFML labeling/CV; ML4T notebooks | frontier: LLM-generated features still need these controls (bridge to P8)

#### `modern-ml-pipelines` — 现代ML量化流水线（Qlib等） / Modern ML quant pipelines (Qlib et al.)
- **Hours:** 11h · **Difficulty:** 4/5 · **Basis:** 3h architecture + 5h mini-pipeline + 2h SFI/Transformer foil + 1h optional Qlib
- **Prereqs:** `ml-leakage-control`, `data-cleaning`
- **Summary:** 简单模型打底的可复现流水线；可选Qlib；不神话深度学习。
- **Goals:**
  - 特征→模型→预测→简单组合草图。
  - 说明为何先树/线性再深度。
  - （可选）跑通Qlib quickstart思路。
- **Must-teach:**
  - 流水线可版本化比花哨模型重要。
  - Qlib：Data/Model/Portfolio/Analysis（Alpha158 + LGBModel；pandas 等价）。
  - 特征重要度 MDI/MDA/SHAP 与相关重复的替代效应；概率校准与 AFML ch.10 下注。
  - 公开数据≠可交易优势；TSFM 零样本在收益上常弱于树模型（须核验论文）。
- **Exercises:**
  - LightGBM/线性截面排序小实验。
  - （可选）读Qlib workflow配置。
  - 泄漏检查清单。
- **Quiz topics:**
  - 流水线阶段顺序
  - 简单模型优先理由
- **Completion criteria:**
  - 可复现小流水线+检查清单。
- **Method tags:** classic: Qlib Quick Start; ML4T end-to-end; Canvas m10 | niche: @quantscience_ stack; ML4T high-engagement X posts | frontier: Qlib Transformer/Localformer as optional controls under same anti-leakage protocol; RD-Agent automation deferred to P8

### P6 · 风险、仓位与执行（Risk, sizing & execution）— 65.50h / 4 课

**阶段目标：** 仓位层、执行成本与硬约束工程化。

**6h/周 ≈ 9.7 周；12h/周 ≈ 4.8 周。**

#### `portfolio-risk-sizing` — 组合、风险与仓位 / Portfolio, risk & position sizing
- **Hours:** 24h · **Difficulty:** 4/5 · **Basis:** 5h concepts + 13h labs (incl HRP + Brandt no-trade + alpha-decay band) + 4h writing + 1h weight-drift lab + 0.5h margin accounts (Reg T / FINRA 4210) + 0.25h portfolio margin (FINRA 4210(g) toy) + 0.25h short-sale margin (Reg T 150% / FINRA 4210(c)(2)-(3)) — HEAVY
- **Prereqs:** `returns-vol-corr`, `strategy-compare-lab`
- **Summary:** 波动目标、回撤熔断、Kelly上界直觉、历史VaR。
- **Goals:**
  - 三种仓位层对照。
  - 解释满Kelly危险。
  - 陈述VaR局限。
- **Must-teach:**
  - 仓位是策略层。
  - 半Kelly/更保守。
  - 风险预算与硬约束。
- **Exercises:**
  - 固定/波动目标/回撤熔断。
  - VaR95+局限段。
  - 风险偏好一页。
- **Quiz topics:**
  - 满Kelly问题
  - 波动目标直觉
  - VaR不是承诺
- **Completion criteria:**
  - 仓位对照表+风险一页。
- **Method tags:** classic: Canvas m11; QuantStart VaR/Kelly; UChicago FINM risk

#### `execution-slippage` — 执行与滑点 / Execution & slippage
- **Hours:** 15.75h · **Difficulty:** 3/5 · **Basis:** 5h concepts (√/Gatheral + public metaorder IRF) + 6.5h experiments + 1.5h quiz + 1h feed-aware TCA (IEX vs SIP arrival, stale NBBO, capacity) + 0.25h Rule 605 vs FINRA 21-23 + 0.5h Rule 606 routing & PFOF + 0.5h NMS Stock ATS and Form ATS-N + 0.25h Rule 604 customer-limit display + 0.25h FINRA 5320 trading ahead of customer equity orders
- **Prereqs:** `costs-in-backtest`, `portfolio-risk-sizing`
- **Summary:** 参与率、冲击示意、TWAP/VWAP直觉。
- **Goals:**
  - 加参与率约束。
  - 写执行假设一页。
- **Must-teach:**
  - 执行是策略一部分。
  - 研究与纸面共用成本模型。
- **Exercises:**
  - 参与率约束。
  - 开盘vs收盘。
  - 执行一页纸。
- **Quiz topics:**
  - 隐性成本
  - 参与率含义
- **Completion criteria:**
  - 执行假设纳入主配置。
- **Method tags:** classic: Canvas m12; NYU impact/TCA; QuantStart execution | niche: @sera00111 execution/venue notes

#### `risk-systems-lab` — 风险系统小实验 / Mini risk-systems lab
- **Hours:** 8h · **Difficulty:** 3/5 · **Basis:** 2.5h concepts (Kupiec+Christoffersen+Basel) + 4.5h labs + 1h quiz
- **Prereqs:** `portfolio-risk-sizing`, `execution-slippage`
- **Summary:** 数据缺口暂停、回撤降仓、密钥不进git。
- **Goals:**
  - 陈旧数据拒单。
  - 回撤熔断。
  - 自查无密钥。
- **Must-teach:**
  - 熔断是工程不是预测。
- **Exercises:**
  - 缺口→暂停。
  - 回撤→降仓。
  - 密钥扫描。
- **Quiz topics:**
  - 硬约束
- **Completion criteria:**
  - 三道硬约束演示通过。
- **Method tags:** classic: Canvas m13 bits; ML4T ops | niche: Cookbook/Qbot config ideas


#### `market-regimes-crisis` — 市场状态与危机剧本 / Market regimes & crisis playbooks
- **Hours:** 17.75h · **Difficulty:** 4/5 · **Basis:** 4.5h concepts + 5h labs (path/overlays/corr/HMM) + 1.5h quiz/review + 1h options/VIX risk box + 1h MWCB/LULD/Reg SHO 201 comparison (R12 tiers, Amendment 18) + 0.5h overnight LULD price bands (Amendment 27/29, Phase 1) + 1.5h US options basics (OCC ODD June 2024; parity; BSM as reference) + 0.25h MWCB Level 3 resumption under 23/5 (SR-NYSE-2026-43 / SR-NASDAQ-2026-080) + 0.25h SEC trading suspensions vs exchange halts (15 U.S.C. 78l(k), up to 10 business days; SEC 34-106668) + 0.25h expiration exercise-by-exception (OCC Rule 805) + 0.5h clearly erroneous prints (FINRA 11892; 2026 overnight extension operative at 23/5 start scheduled 2026-12-06) + 0.25h OCC assignment to clearing members (firm method may be random or FIFO) + 0.5h AM-settled index SOQ (current last trading day usually Thursday; GTH change Effective TBD) + 0.25h OCC cash-dividend adjustments ($12.50 per contract) + 0.25h LULD Plan Section VII reopen clocks + 0.25h Cboe Rule 5.1(e)(3) early-close Curb
- **Prereqs:** `risk-systems-lab`
- **Summary:** 可操作 regime、因果检测栈、四场景剧本、HMM 过滤 vs 平滑泄漏、熔断识字、新闻≠regime。
- **Goals:**
  - 写出可操作、可因果的 regime 定义。
  - 用 shift(1) 检测栈标出教学路径。
  - 区分过滤与平滑 HMM；新闻日 ≠ 已定义 regime。
- **Must-teach:**
  - 状态输入一律滞后；平滑概率禁止用于决策。
  - 四剧本各含失败模式；Moreira–Muir vs Cederburg 波动管理识字。
  - 美股熔断 7/13/20% 与 2016 A 股熔断暂停 = 机制 ≠ 信号。
- **Exercises:**
  - 因果标签路径 + 急跌窗命中率。
  - 固定 / 波动目标 / DD 刹车：只比 vol 与 maxDD。
  - 相关→1 压力 PnL；HMM 过滤 vs 平滑。
- **Quiz topics:**
  - 因果滞后与平滑泄漏
  - 危机 vs 普通回调
  - 熔断 / 新闻 ≠ 交易信号
- **Completion criteria:**
  - 四场景卡片 + 实验数字一致 + 新闻≠regime 短文。
- **Method tags:** classic: Hamilton 1989; NYSE Rule 7.12; CPPI literacy | niche: CSRC/SSE 2016 suspension | frontier: Moreira–Muir 2017 JF; Cederburg et al. 2020 JFE

### P7 · 纸面与伦理（Paper trading & ethics）— 41.50h / 2 课

**阶段目标：** 纸面闭环与合规/研究伦理。

**6h/周 ≈ 6.0 周；12h/周 ≈ 3.0 周。**

#### `paper-trading-infra` — 纸面交易与迷你基建 / Paper trading & mini infra
- **Hours:** 17.5h · **Difficulty:** 3/5 · **Basis:** 3h design + 6h running/logging + 3h parity checklist + 1h template + 1h infra name-map + 2h US broker paper differences & adapter fixture + 1h Shanghai-timezone reconciliation + 0.5h overnight-session fixture (trade date, Shanghai time, order limits)
- **Prereqs:** `market-regimes-crisis`
- **Summary:** 信号→目标→日志；≥5日；冻结版本。
- **Goals:**
  - CSV纸面撮合。
  - 出日报。
  - 解释纸面验流程。
- **Must-teach:**
  - 纸面期间不按盈亏改规则。
  - 对账与异常日志。
- **Exercises:**
  - CSV撮合。
  - 5日日志。
  - 日报模板。
- **Quiz topics:**
  - 纸面验证什么
  - 为何冻结版本
- **Completion criteria:**
  - ≥5日日志包。
- **Method tags:** classic: Canvas m13; QuantStart paper-before-live; Alpaca / IBKR paper docs (document-level only); Chinese supplement: JoinQuant 模拟交易 | niche: Qbot/Atlas reference architecture; Nautilus isomorphic paper/sim concept

#### `compliance-ethics` — 合规、风险心态与研究伦理 / Compliance, risk mindset & research ethics
- **Hours:** 24h · **Difficulty:** 2/5 · **Basis:** 8h reading (Northbound + PDA withdrawal + FY2026/FINRA GenAI + SFC 24EC55 + ESMA74 algo briefing) + 4.5h writing + 2.5h quiz + 1h rule versions (FINRA main example + SSE 2026 comparison) + 0.5h US four-date table & phase-in status (R04) + 2.5h cross-border tax/FX/CRS literacy box (R25/R28/R29) + 0.5h wash-sale basis lab (IRS Pub 550 examples, purchase-order matching) + 0.5h holding period & qualified dividends (IRS Topic 409 / Pub 550 / Pub 519) + 0.5h manipulation red lines & self-trade lab (15 U.S.C. 78i / FINRA 5210 / CAT review) + 0.25h tokenized NMS stock Innovation Exemption status (SEC 34-106402, until 2031-09-17) + 0.25h tax lots: FIFO vs adequate identification (IRS Pub 550; Form 1099-B basis for covered securities) + 0.25h Section 16(b) short-swing profit (15 U.S.C. 78p(b)) + 0.25h constructive sales (IRC §1259) + 0.25h Section 1256 60/40 (nonequity / broad-based index options) + 0.25h return of capital (Form 1099-DIV box 3) + 0.5h short-over-ex-div cash obligation, payments in lieu (not QDI), and preferred QDI 90/181 + 0.25h Form 13H large-trader identification (identifying activity level; confidential) + 0.25h capital-loss deduction cap and carryover (IRS Pub 550) + 0.25h short-sale tax character (IRS Pub 550 Ace example) + 0.25h worthless securities sold on the last day of the tax year (IRC §165(g)) + 0.25h investment interest (Pub 550 margin interest, net-investment-income limit) + 0.25h stock dividends and stock rights (Pub 550 basis and holding period)
- **Prereqs:** `paper-trading-infra`
- **Summary:** 先生存；学习≠投顾；拒绝选择性汇报。
- **Goals:**
  - 写风险偏好。
  - 记录失败。
  - 拆穿保证夏普话术。
- **Must-teach:**
  - 本站学习材料非投资建议。
  - 不懂则零仓位。
- **Exercises:**
  - 风险一页。
  - 三次失败。
  - 话术审计。
- **Quiz topics:**
  - 选择性汇报危害
  - 学习与受监管业务边界
- **Completion criteria:**
  - 伦理清单勾选完成。
- **Method tags:** classic: Canvas m14; AFML scientific ethics | frontier: LLM/agent research must obey same ethics/hold-out (link P8)

### P8 · 前沿与非主流方法（Frontier & unconventional methods）— 48h / 2 课

**阶段目标：** 在经典纪律之上批判性接触LLM agent、TSFM、另类数据与Crypto/链上。

**6h/周 ≈ 8.0 周；12h/周 ≈ 4.0 周。**

#### `frontier-llm-agents` — 前沿：LLM / 多智能体量化研发 / Frontier: LLM / multi-agent quant R&D
- **Hours:** 29h · **Difficulty:** 5/5 · **Basis:** 5h reading + 12h critical exercises (KTD/Xia/Mirage/five sins/FINSABER/OpenPM/CLQT/AQuA/recoverability) + 2h rules + 3h sealed leaderboard + 7h process diagnosis — HEAVY
- **Prereqs:** `factor-workflow`, `ml-leakage-control`, `modern-ml-pipelines`, `compliance-ethics`
- **Summary:** RD-Agent(Q)、公式化alpha挖掘、Quant-Arena：批判性试用，不替代防泄漏。
- **Goals:**
  - 陈述RD-Agent(Q)闭环。
  - 列出LLM挖因子失败模式。
  - 设计密封样本外验收。
- **Must-teach:**
  - 自动化放大试错→更需多重检验。
  - 论文指标≠你的可复现优势。
  - Agent输出须进同一陷阱审讯。
- **Exercises:**
  - 读RD-Agent/Qlib说明写半页风险清单。
  - 对LLM生成因子做空假设与成本审讯提纲。
  - 用Quant-Arena冻结后再测密封年规则改写守则。
- **Quiz topics:**
  - 为何agent增加过拟合风险
  - 密封hold-out是什么
- **Completion criteria:**
  - 前沿风险清单+更新研究守则。
- **Method tags:** niche: XQuant Spec+AI run-first as motivation only (@_zheergen) | frontier: microsoft/RD-Agent + R&D-Agent(Q) arXiv:2505.15155 (NeurIPS 2025 only as arXiv comment — verify proceedings); Chain-of-Alpha arXiv:2508.06312; LLM+MCTS arXiv:2505.11122; Quant-Arena arXiv:2610.30113; Glasserman&Lin arXiv:2309.17322; Lopez-Lira/Tang/Zhu arXiv:2504.14765; Five sins arXiv:2602.14233; FINSABER arXiv:2505.07078; OpenPM arXiv:2608.09988

#### `frontier-tsfm-altdata-crypto` — 前沿：时序基础模型 · 另类数据 · Crypto/链上 / Frontier: TSFMs · alt-data · crypto/on-chain
- **Hours:** 19h · **Difficulty:** 4/5 · **Basis:** 5h papers + 6h design + 5h funding/liquidation/ADL/EWS/path-funding foils + 2h structure/PIT + 1h SaR name-drop — HEAVY
- **Prereqs:** `modern-ml-pipelines`, `data-cleaning`, `execution-slippage`
- **Summary:** Chronos/TimesFM金融评测的谨慎结论；另类数据；CCXT/资金费率/链上。
- **Goals:**
  - 概括TSFM日频超额收益谨慎结论。
  - 设计另类数据PIT/滞后检查。
  - 说明CEX CCXT与链上适配差异与额外风险。
- **Must-teach:**
  - 零样本TSFM常弱于强传统基准；领域预训练仍须防前瞻。
  - 另类数据时间戳与修订是第一风险。
  - 资金费率/链上指标不是免费alpha。
- **Exercises:**
  - 读TSFM金融评测摘要列5条不可直接实盘理由。
  - 为假情绪序列设计延迟与修订规则。
  - （可选）CCXT拉一种资金费率并画图。
- **Quiz topics:**
  - TSFM零样本局限
  - 另类数据前瞻
  - 链上执行额外风险
- **Completion criteria:**
  - TSFM谨慎备忘+另类数据时间规则一页。
- **Method tags:** niche: @sera00111 Crypto toolchain; Funding/on-chain pipeline examples as structure refs | frontier: Chronos/TimesFM finance evals e.g. arXiv:2511.18578; Trading Strategy GMX CCXT adapters 2025; OpenBB-style alt/market data aggregation

### P9 · 结业项目（Capstone）— 26h / 1 课

**阶段目标：** 端到端诚实交付。

**6h/周 ≈ 4.3 周；12h/周 ≈ 2.2 周。**

#### `capstone` — 结业项目：诚实的小策略 / Capstone: an honest small strategy
- **Hours:** 26h · **Difficulty:** 5/5 · **Basis:** 6h design/data + 10h backtest/OOS + 4h paper + 4h writing — project + 2h US research contract (offline JSON checker)
- **Prereqs:** `paper-trading-infra`, `compliance-ethics`, `factor-workflow`, `portfolio-risk-sizing`
- **Summary:** 假设→PIT→含成本walk-forward→DSR(N=全部)→仓位→TCA→纸面对账→合规→报告模板与量规。
- **Goals:**
  - 交付可复现研究包。
  - 含成本敏感与密封样本外及DSR(N)。
  - 附纸面独立对账、合规清单与量规自评。
- **Must-teach:**
  - 评分看诚实与工程不看是否赚钱。
  - DSR须计入全部试错且用决策同一序列。
  - 可选前沿附录不得削弱核心纪律。
- **Exercises:**
  - 一页假设（含PIT与决策规则）。
  - 含成本+embargo的walk-forward。
  - 密封OOS+DSR(N=全部)及N=1对照。
  - 仓位限制与TCA估计。
  - ≥5日纸面+独立账本检出注入差错。
  - 量规自评（Must全过）。
  - （可选）前沿失败对照附录。
- **Completion criteria:**
  - 结业包通过自评量规全部Must行。
- **Method tags:** classic: Canvas capstone; US research contract (offline); Chinese supplement: JoinQuant 综合/模拟; Bailey–LdP 2014 DSR; Perold 1988 IS | niche: Open strategy libs sparingly as hypothesis inspiration only | frontier: Optional negative-result appendix on RD-Agent/TSFM/on-chain signal

## 6. 可选工具阅读顺序（OPTIONAL）

1. pandas/NumPy → 2. VectorBT → 3. Zipline Reloaded / Backtrader → 4. Qlib → 5. ML4T → 6. NautilusTrader → 7. RD-Agent（仅 P8 后）

链接见 `src/lib/curriculum.draft.ts` 的 `OPTIONAL_TOOL_LINKS` 与 `CURRICULUM_RESEARCH.md`。

## 7. Gaps / disputed

| 主题 | 立场 |
|------|------|
| 零售人人可盈利 | 只教流程与诚实，不承诺 edge |
| HFT 赚钱配方 | 不做；微观结构仅直觉 |
| 满 Kelly | 上界直觉；实务保守 |
| 因子动物园 | 强调多重检验与 OOS |
| LLM agent 挖因子 | 前沿选修；默认增加过拟合；必须密封 OOS |
| TSFM 直接当 alpha | 实证偏谨慎；作研究对照 |
| Crypto/链上 | 独立摩擦与托管风险；非主市场默认 |

## 8. 与 V1 / Canvas 映射

| Canvas | V2 |
|--------|----|
| m1 | markets-language |
| m2 | microstructure-orders |
| m3 | returns-vol-corr + eval-lab |
| m4 | data-cleaning |
| m5 | backtest-traps + costs-in-backtest + engines-vectorized-event |
| m6–m8 | P3 |
| m9 | P4 |
| m10 | P5 |
| m11–m12 | P6 |
| m13–m14 | P7 |
| 结业 | P9 |
| （新）基础 | P0 |
| （新）前沿 | P8 |


### Advanced deepenings (no new phases) — 2026-11-04

Inventory items woven into existing lessons (zh+en, offline toys):

1. **CPCV teaching sketch** → `backtest-traps` (+ reuse note in `ml-leakage-control`); AFML ch.12 spirit, NOT production CombinatorialPurgedKFold.
2. **Fracdiff / uniqueness / meta-label filter** → `ml-leakage-control` (`examples/p5/03_afml_depth.py`); AFML ch.3–5.
3. **Info bars** → `data-cleaning`; AFML ch.2; explicitly not an HFT recipe.
4. **SFI + Localformer/Transformer foil** → `modern-ml-pipelines`; AFML ch.8; Qlib arXiv:2009.11189 + benchmarks; no “DL wins” claim.
5. **PyFolio tear-sheet map** → `eval-lab`.
6. **Atlas name-drop** beside Qbot → `paper-trading-infra`.
7. **HRP** → `portfolio-risk-sizing`; López de Prado 2016 JPM 42(4) + AFML ch.16.

Net hours ≈ +18h deepen (b07393d) then +11h Phase B (055faaf) then +20h Phase B next (2a1a28d) → **287h full / 267h skip P0**.


## Enrich3 (Phase B) mapping notes

- PBO/CSCV + evaporation + DSR≠leakage → `backtest-traps` (+ pointers `ml-leakage-control`, `frontier-llm-agents`); teaching CSCV sketch ≠ production CombinatorialPurgedKFold.
- CLQT / AQuA protocol-only / Yao&Zheng recoverability → `frontier-llm-agents` (+ AQuA/PBO bridges in `ml-leakage-control`; recoverability row in `backtest-traps` research log).
- Harvey–Sancetta–Zhao NBER w34898 → `factor-workflow` next to HLZ + Detzel.
- ADL trilemma + SaR name-drop → `frontier-tsfm-altdata-crypto`.
- SEC FR 2025-11110 S7-12-23 withdrawal → `compliance-ethics` (awareness; withdrawn ≠ no duties).
- Hours: **304 full / 284 skip-P0**.


## Enrich4 (Phase B) mapping notes

- KTD-Fin (2605.28359) + Xia survey (2605.19337) + Profit Mirage Part I–II (2510.07920) → `frontier-llm-agents` (+ pointers in `ml-leakage-control`).
- Admission gates / injected-truth (2610.07701) → `backtest-traps` + pointer `factor-workflow`; MinervaScore 2608.23808 NAME-ONLY.
- EWS heterogeneity (2607.27070) + funding path-dependent literacy (2506.08573) → `frontier-tsfm-altdata-crypto`.
- Alpha decay + costs → no-trade (2502.04284) → `portfolio-risk-sizing` + thin `execution-slippage` pointer.
- SEC FY2026 Exam Priorities + FINRA 2026 GenAI/Agents → `compliance-ethics`.
- Hou–Xue–Zhang 2020 RFS (hhy131) → `factor-workflow` next to HLZ/HSZ.
- Hours: **320 full / 300 skip-P0** (~+16h from enrich3 tip).


## Enrich5 (Phase B) mapping notes

- Square-root / double-√ impact literacy (arXiv:2502.16246 + 2411.13965) + Gatheral 2010 no-dynamic-arbitrage para → `execution-slippage` (+ one-line bridge `costs-in-backtest`).
- Christoffersen 1998 IND + CC + Basel traffic-light counting → `risk-systems-lab` (extends Kupiec).
- Backtest↔live parity six defects + 10-point checklist (arXiv:2610.21846) → `paper-trading-infra` (protocol only).
- Novy-Marx & Velikov RFS 2016 costs×turnover taxonomy (NBER w20721 / DOI 10.1093/rfs/hhv063) + FIM capacity name-drop → `factor-workflow` next to Detzel.
- SFC Circular 24EC55 (2024-11-12) GenAI LM → `compliance-ethics` (Asia peer to FINRA GenAI).
- Rewrite-harder: `markets-language` SUCCESS “beat the benchmark” → “above the benchmark” / 高于 (zh+en lab+MDX).
- Hours: **344 full / 324 skip-P0** (~+13h from enrich4 tip 882995b).


## Enrich6 (Phase B LIGHT) mapping notes

- Mask-first / upstream contamination (arXiv:2507.07107) → `data-cleaning` (+ pointer `costs-in-backtest`; quiz bridge `ml-leakage-control`). mask-first optional conservative protocol only; REJECT paper Sharpe 2.05/1.63 / 213-factor / AdjMSE as course alpha.
- ESMA Supervisory Briefing on Algorithmic Trading ESMA74-1505669079-10311 (2026-02-26 PDF) → `compliance-ethics` (non-binding literacy; Asia peers; not HFT how-to).
- Public-data metaorder impact challenge (arXiv:2501.17096) → `execution-slippage` (+ one-line `microstructure-orders`). Protocol/warn; NO calibrate-α-for-alpha; no LOB HFT.
- Rewrite-harder: execution-slippage 「跑赢 VWAP」→「高于 VWAP」 / beat→above; factor-portfolio-lab toy net_SR≈3.67/4.36 hardened as synthetic MU not live edge.
- Hours: **344 full / 324 skip-P0** (~+11h from enrich5 tip ebd4b35). Quality pause after this pack — no enrich7 unless new brief.

### market-regimes-crisis (new lesson)
- New P6 lesson after `risk-systems-lab` (+11h): operational regimes, causal detectors, four playbooks, Hamilton filter vs smoother leak, MWCB/2016 CN halt literacy, 2026-11-05 news≠regime box (CNBC/AP verified).
- Fixed `portfolio-risk-sizing` table/opener inconsistency → **22h** (aligned with curriculum.ts).
- Hours: **355 full / 335 skip-P0**; lessonCount 28.

## Formal-audit revision pack (base 50c33f9)

- Q1 hour sub-items now sum to totals: `backtest-traps` 5+19+4=28; `factor-workflow` 5+15+3+1=24; `frontier-tsfm-altdata-crypto` 5+6+5+2+1=19.
- Q2 removed third-party `joinquant-8w` (lookmori.cn, persistent 500); `quantstart-sat` 503 noted, unchanged; removed 2026-11-10 (R52: site unreachable, entry unused).
- Q3 Gatheral 2010 (QF 10(7) 749–759) verified via Crossref; link → RePEc journal record.
- Q6 SSE Trading Rules 2026 revision (上证发〔2026〕41号, effective 2026-07-06, 2023 rev. repealed, some provisions deferred) → `compliance-ethics` (+1h).
- Q7 Ken French FIZ→CIZ (Jan 2025 release) + corporate actions + calendars lab → `data-cleaning` (+2h, `examples/p2/05`).
- Q8 Optional Kalman hedge ratio, filter vs smoother (statsmodels docs) → `pairs-stat-arb` (+2h, `examples/p3/05`).
- Q9 Options/VIX risk box (OIC + Cboe) → `market-regimes-crisis` (+1h).
- Q10 Weight drift & constraint consistency mini-lab → `portfolio-risk-sizing` (+1h, `examples/p6/05`).
- Hours: **362 full / 342 skip-P0**; lessonCount 28.

## US-first content pack (2026-11-08)

- Default scope: US-listed stocks / non-leveraged ETFs, USD. Chinese is the teaching language, not the default market. A-share / Stock Connect / EU material is labelled comparison reading.
- Hours: **382 full / 362 skip-P0**; lessonCount 28; P0 stays 20h. MUST +16h, SHOULD +4h:
  microstructure-orders 7→9 (+2 US mechanics); market-regimes-crisis 12→13 (+1 MWCB/LULD/Reg SHO); data-cleaning 19→25 (+3 sources/licensing/PIT, +2 corporate actions/delisting, +1 ALFRED as-of); paper-trading-infra 14→17 (+2 broker paper/adapter fixture, +1 Shanghai-timezone reconciliation); pairs-stat-arb 12→13 (+1 short constraints); compliance-ethics 16→19 (+0.5 FINRA four dates/phase-in, +2.5 cross-border tax/FX/CRS box); capstone 24→26 (+2 US research contract); factor-workflow 24→25 (+1 benchmark alignment); execution-slippage 13→14 (+1 feed-aware TCA).
- Phase totals: P0 20, P1 29, P2 67, P3 33, P4 33, P5 32, P6 58, P7 36, P8 48, P9 26.
- Review items implemented with the review's wording: R04, R12, R16, R21, R25, R28, R29.
- New offline labs: p1/05, p2/06 (+ data/us_fixtures), p2/05 section D, p3/06, p4/03, p6/06, p6/07, p7/03, p9/02 (+ us_research_contract.json); p7/02 rewritten (n_sources=33, US first). No real FRED / yfinance downloads or caches.
- Section 5 per-lesson Hours/Difficulty/Basis lines and phase headings are synced from `src/lib/curriculum.ts` (R31) and checked in CI by `tools/check-hours.mjs`; other prose in section 5 (summaries, task wording) may lag curriculum.ts, which remains the source of truth.


## Recheck fixes R30–R37 (2026-11-08)

- Hours unchanged: 382 full / 362 skip-P0, 28 lessons. `npm run check` (CI) runs `tools/check-hours.mjs` (curriculum.ts, README, messages zh/en, V2 knowledge map + phase table + section 5, 56 MDX headers), `tools/check-quiz.mjs` (zero-based answers, zh/en parity, p6mrc-q5 semantics) and `tools/check-structure.mjs` (zh/en heading/quiz order).
- New offline lab: `examples/p7/04_finra_migration_fixture.py` (R34). LULD toy separates prior-close price tier from moving reference price with 7 boundary tests (R32).

## Daily new content N1–N3 (2026-11-08)

- Hours: **384.75 full / 364.75 skip-P0**; 28 lessons; P0 stays 20h. `tools/check-hours.mjs` now accepts decimal hours (0.25 / 0.5).
- N1 overnight trading + overnight LULD bands Phase 1 (SEC 34-106042 Amendment 27; 34-106624 Amendment 29, 19:45→19:30 ET, temporary ≤120 days; planned 2026-12-06, dependent on systems changes): `microstructure-orders` +0.5h, `market-regimes-crisis` +0.5h (one comparison-table row + `examples/p6/08_overnight_bands_toy.py`), `paper-trading-infra` +0.5h (`examples/p7/05_overnight_session_fixture.py` + `examples/p7/fixtures/overnight_sessions_fixture.json`).
- N2 amended Rule 605 (SEC staff FAQ): `costs-in-backtest` +0.75h (`examples/p2/07_rule605_effective_spread.py`, FAQ Examples 27-1 and 38-1), `execution-slippage` +0.25h (605 vs FINRA 21-23). No 605 field names (schema source not read).
- N3 Rule 612 $0.005 tick / 610(c) access-fee caps (34-101070; compliance extended to the first business day of November 2027 by 34-105656; scope per eCFR §242.612): `microstructure-orders` +0.25h, next to the Rule 611 status box.
- N4 (2026-11-09): HK T+1 plan table in `microstructure-orders` (+0.25h). Hours: **385 full / 365 skip-P0**; P1 30h; 28 lessons.
- enrich7 (2026-11-10, US-first): official close / MOC 15:50 ET + tiered round lots & BOLO (`microstructure-orders` +1h); dividend dates under T+1 + yfinance `auto_adjust` trap (`data-cleaning` +0.75h); short interest / short volume / FTD point-in-time (`pairs-stat-arb` +1h); US options basics + MWCB Level 3 resumption under 23/5 (`market-regimes-crisis` +1.75h); wash-sale basis lab (`compliance-ethics` +0.5h). Hours: **390 full / 370 skip-P0**; 28 lessons.
- enrich8 (2026-11-10, US-first): ETF NAV & premium/discount under Rule 6c-11 (`markets-language` +0.5h); leveraged/inverse ETF daily reset (`returns-vol-corr` +0.5h); filing deadlines & EDGAR 5:30 p.m. rule + delisting returns & PERMNO (CRSP CIZ) (`data-cleaning` +1h); index membership as-of, Russell semi-annual from 2026 (`backtest-traps` +0.5h); margin accounts Reg T 50% / FINRA 4210 25% (`portfolio-risk-sizing` +0.5h); Rule 606 routing & PFOF (`execution-slippage` +0.5h); holding period & qualified dividends (`compliance-ethics` +0.5h). Form 10-S semiannual reporting: proposed 2026-05-05, not adopted as of 2026-11-10. Hours: **394 full / 374 skip-P0**; 28 lessons; 265 quiz pairs.
- enrich9 (2026-11-10, US-first): spin-offs & mergers in price series + insider/large-holder filing lags incl. FPI insiders from 2026-03-18 (`data-cleaning` +1h, `examples/p2/11`); risk-free rate from T-bill quotes (`returns-vol-corr` +0.5h, `examples/p1/08`); FOMC release times + IPO data traps (`backtest-traps` +0.75h, `examples/p2/12`); manipulation red lines (15 U.S.C. 78i, FINRA 5210 SM .02/.03, CAT review 2026-37) + self-trade toy (`compliance-ethics` +0.5h, `examples/p7/08`; ledger n_sources=36) and FY2027 exam priorities pointer (press release 2026-109); SIPC protection (`microstructure-orders` +0.25h); portfolio margin FINRA 4210(g) toy (`portfolio-risk-sizing` +0.25h, `examples/p6/11` section D). Hours: **397.25 full / 377.25 skip-P0**; 28 lessons; 273 quiz pairs.
- enrich10 (2026-11-10, US-first): N5 SEC Innovation Exemption for tokenized NMS stock (Release 34-106402, File 4-927, 91 FR 60168 published 2026-09-22; effective 2026-09-17 until 2031-09-17; no comment closing date set) — status subsection + quiz `ce-tsv-exemption` (`compliance-ethics` +0.25h; ledger n_sources=39 with the order and the Atkins/Uyeda statements) and TSV prints are not exchange prints + quiz `mo-tsv-data` (`microstructure-orders` +0.25h). R67 second reading of the portfolio-margin valuation points (no hour change); R69 78i ledger status compared through PL 119-138 + CAT comment period closed 2026-06-22 (S7-2026-12, 34-105251); R70 Form 4 deadline counted from the execution date / deemed execution date. Hours: **397.75 full / 377.75 skip-P0**; P1 33h, P7 38.25h; 28 lessons; 275 quiz pairs.
- enrich11 (2026-11-11, US-first): sell-side regulatory fees — SEC Section 31 ($0.00 from 2025-05-14, $20.60 per million from 2026-04-04) and FINRA TAF (2026 $0.000195/share, max $9.79; paused 2026-10-01 to 2026-12-31 by SR-FINRA-2026-021) as dated fee tables (`costs-in-backtest` +0.5h, `examples/p2/13_regulatory_fees_toy.py`, quiz `cb-regfee`); reverse splits & Nasdaq bid-price rule status (34-102245, 34-104318 $0.10 rule, 34-105971 $5M MVLS rule stayed) (`data-cleaning` +0.5h, `examples/p2/14_bid_price_rule_toy.py`, quiz `dc-bidprice`); official open, NYSE DMM open after 9:30, Nasdaq NOOP and MOO 9:28 ET cutoff (`microstructure-orders` +0.25h, `examples/p1/09_open_auction_toy.py`, quiz `mo-open`); SEC trading suspensions under 15 U.S.C. 78l(k) vs exchange halts, 34-106668 example (`market-regimes-crisis` +0.25h, quiz `rc-suspend`); tax lots FIFO vs adequate identification per IRS Pub 550 (`compliance-ethics` +0.25h, `examples/p7/09_tax_lot_toy.py`, quiz `ce-lots`); R72 TSV not a trading/market center under Reg NMS, broker-dealer participants get no Reg NMS relief (VI Q7 asks for comment). Hours: **399.5 full / 379.5 skip-P0**; 28 lessons; 280 quiz pairs.
- enrich12 (2026-11-11, US-first): N6 Nasdaq-100 methodology effective 2026-05-01 (Fast Entry top 40 with IPO 7th/10th/15th trading days, top-125 quarterly removal replacing the 10 bp rule, ranking on listed+unlisted shares, Modified Market Cap with TSO capped at 3x free float, 10% minimum float removed) and December 2026 annual reconstitution dates derived from the methodology (reference 2026-11-30, announcement after the close 2026-12-11, effective open 2026-12-21; Nasdaq announcement authoritative) (`backtest-traps` +0.25h, quiz `bt-ndx-recon`); R80 settlement-holiday set in `examples/p2/13_regulatory_fees_toy.py` (Good Friday 2026-04-03, NSCC notice a9732); R79 $0.10-rule prior version + Hearings Panel 180-day exception (`data-cleaning`), Rule 15c2-11 quotes after an SEC suspension incl. 60-day piggyback bar (`market-regimes-crisis`), Treas. Reg. 1.1012-1(c)(8) standing orders and settlement-date deadline (`compliance-ethics`); no hour change for R79/R80. Hours: **399.75 full / 379.75 skip-P0**; 28 lessons; 281 quiz pairs.
- enrich13 (2026-11-11, US-first): SEC XBRL `data.sec.gov` APIs as point-in-time data (pick by `filed`; `frames` returns the last filed value; `fy`/`fp` describe the filing; Apple FY2009 NetIncomeLoss 5,704m in the 10-K of 2009-10-27 vs 8,235m in the 10-K/A of 2010-01-25), Rule 10b5-1 cooling-off (later of 90 days or 2 business days after the 10-Q/10-K, max 120; others 30) and the Form 4 plan check box for filings from 2023-04-01, NYSE 802.01C price criteria (30-trading-day average below $1, month-end cure test, 200:1 reverse-split limit from 34-102201) and the $0.25 Minimum Trading Price effective 2027-07-01 (34-106133) (`data-cleaning` +1.25h, `examples/p2/15_nyse_price_criteria_toy.py`, `examples/p2/17_xbrl_pit_10b51_toy.py`, quizzes `dc-nyse-price`, `dc-xbrl-filed`, `dc-10b51`); S&P 500 addition rules per the November 2026 S&P U.S. Indices Methodology (committee discretion, dated cap thresholds 18.0/20.5/22.7 bn, evaluation date two business days before announcement, 05:15 PM ET announcements with at least three business days' notice) and earnings release times as event timestamps (8-K Item 2.02, four-business-day 8-K deadline, Regulation FD) (`backtest-traps` +0.75h, `examples/p2/16_index_add_earnings_time_toy.py`, quizzes `bt-sp500-add`, `bt-earnings-time`); CAT fees billed to both executing brokers per executed share (CAT Fee 2025-1 $0.000022, 2025-2 $0.000009, none invoiced 2025-12..2026-04, 2026-1 $0.000001) and the 2027 SEC fee row marked as an FY2026-rate placeholder (no FY2027 Section 31 advisory as of 2026-11-11) (`costs-in-backtest` +0.25h, `examples/p2/13_regulatory_fees_toy.py` section D, quiz `cb-catfee`); Form SHO / Rule 10c-1a exemptions to 2028-01-02 / 2028-09-28 / 2029-03-29 after the Fifth Circuit remand (SEC 34-104303) (`pairs-stat-arb` +0.25h, quiz `ps-formsho`). Hours: **402.25 full / 382.25 skip-P0**; P2 75.25h, P3 34.25h; 28 lessons; 288 quiz pairs.
- R84–R86 + R88 (2026-11-11, after enrich13): Historical CAT Assessment 1A ($0.000002 from May 2026 transactions until about $38.96 million is collected) and Assessment 1 ceased after November 2025 transactions (CAT Fee Alert 2025-4, SR-FINRA-2026-011); 2025-2 last invoice December 2025 for November transactions; CAT Fee 2026-1 described as budget-priced for 2026-05-01 through 2026-12-31 and continuing in 2027 until a new fee or a CAT LLC stop notice; `data-cleaning` en common-mistakes list brought to 18 items to match zh. Quiz answers and hours unchanged.
- enrich15 (2026-11-11, US-first): Rule 144 resale safe harbor and Form 144 notice threshold + follow-on / secondary offerings and Regulation M Rule 105 (`backtest-traps` +1.0h, `examples/p2/19_rule144_followon_tender_toy.py` sections A–C, quizzes `bt-rule144` / `bt-rule105`); tender-offer minimum window under Rule 14e-1 and the conditional 2026-04-16 equity exemptive order (`data-cleaning` +0.5h, lab 19 section D, quiz `dc-tender`); Form ATS-N / NMS Stock ATS off-exchange liquidity (`execution-slippage` +0.5h, quiz `es-atsn`); Rule 15c3-3 possession-or-control and the customer reserve account + cash-account freeriding under Regulation T (payment period = settlement cycle plus two business days; 90-calendar-day freeze) + Texas Stock Exchange approval, official sessions, SIP id F and 2026-07-31 NMS rollout (`microstructure-orders` +0.75h, `examples/p1/11_freeride_txse_15c33_toy.py`, quizzes `mo-freeride` / `mo-15c33` / `mo-txse`); OCC exercise-by-exception at expiration (Rule 805 / Interpretation .02, not unqualified automatic exercise) (`market-regimes-crisis` +0.25h, `examples/p6/13_exercise_by_exception_toy.py`, quiz `rc-exbyex`). Hours: **407.25 full / 387.25 skip-P0**; 28 lessons; 302 quiz pairs. Also aligned the `backtest-traps` zh common-mistakes list to the existing 19 English items (DSR/PBO, CSCV sketch, DSR(N) logging, admission gates, Minerva Seal).
- enrich17 (2026-11-12, US-first): stop / stop-limit / trailing stop (the stop price is not a guaranteed fill) + Rule 610(e) locked/crossed protected quotations as current law, with S7-2026-20 still a proposal that would also rescind 610(e) (`microstructure-orders` +0.50h, `examples/p1/12_stop_order_toy.py`, quizzes `mo-stop` / `mo-610e`); AM-settled index SOQ (settlement is SET of constituent official opens, not the prior close or a later spot; current last trading day usually Thursday close; GTH 9:25 a.m. Friday change remains Effective TBD) + OCC cash-dividend adjustments (ordinary dividends do not adjust regardless of size; non-ordinary normally only if ≥ $12.50 per contract) (`market-regimes-crisis` +0.75h, `examples/p6/15_soq_occ_adj_toy.py`, quizzes `rc-soq` / `rc-occadj`); short-sale margin under Reg T 150% and FINRA 4210(c)(2)–(3) (`portfolio-risk-sizing` +0.25h, add-on to `examples/p6/11_margin_call_toy.py`, quiz `prs-shortmargin`); short-over-ex-div cash obligation, payments in lieu are not QDI, and preferred-stock QDI 90/181 when periods total more than 366 days (`compliance-ethics` +0.5h, add-on to `examples/p7/11_tax_1259_1256_roc_toy.py`, quizzes `ce-pil` / `ce-prefqdi`; one-line pointer from `pairs-stat-arb` with no hour shift). Also R94: LULD Amendment No. 29 wording only (temporary basis not to exceed February 10, 2027, 91 FR 65016; comments were due 2026-11-03 and have closed; no hour or quiz-answer change). Hours: **411.5 full / 391.5 skip-P0**; 28 lessons; 317 quiz pairs.
- R95 / R96 (2026-11-12): Form 5 Rule 0-3 example rolls past Washington’s Birthday (2026-02-16 on the [OPM 2026 Holiday Schedule](https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/#url=2026)) to 2026-02-17; the 13d-1(g) five-business-day example skips Columbus Day (2026-10-12) to 2026-10-13. The lab’s toy calendar now rolls official 2026 federal holidays, and the “example dates avoid holidays” wording is removed. Hours and quiz answers unchanged.
- enrich20 (2026-11-12, US-first): Federal Reserve G.17 clocks (monthly Industrial Production issued at 9:15 a.m.; annual revision issued at noon; a monthly 9:15 a.m. release can fill at that day’s 09:30 open, a noon revision cannot; BEA GDP second estimate 2026-11-25 8:30 AM can, a 10:00 AM BEA item cannot; do not copy the BLS “all seven PFEIs are 8:30” sentence onto every US PFEI; no invented G.19 clock) (`backtest-traps` +0.25h, add-on to `examples/p2/12_event_time_ipo_toy.py`, quiz `bt-g17-time`); Rule 611(b) exceptions beyond ISO, especially (b)(2) not regular way, (b)(3) single-priced opening/reopening/closing, and (b)(7) price not based on the quoted price / material terms not reasonably determinable at commitment (S7-2026-20 remains a proposal; 611 is not repealed) (`microstructure-orders` +0.25h, quiz `mo-611b`); LULD Plan Section VII reopen clocks (five-minute attempt; pause ends at a Reopening Price; ten-minute all-centers branch; last ten minutes of Regular Trading Hours go to a closing transaction, not a mid-session reopen; do not copy onto overnight Phase 1) (`market-regimes-crisis` +0.25h, add-on to `examples/p6/06_luld_halt_toy.py`, quiz `rc-reopen`); Pub 550 short-sale tax character (gain or loss not realized until delivery; official Ace Corporation 13-month example is short-term because the delivered holding period is less than 1 day) (`compliance-ethics` +0.25h, add-on to `examples/p7/11_tax_1259_1256_roc_toy.py`, quiz `ce-shorttax`); worthless securities treated as sold on the last day of the tax year under IRC §165(g) / Pub 550 (calendar-year 2026 → 2026-12-31; not the bankruptcy, halt, or delisting date) (`compliance-ethics` +0.25h, same lab, quiz `ce-worthless`); when-issued / when-distributed contracts under FINRA 11130 (settlement date determined later, not automatic T+1 from the WI trade date; contracts canceled if not issued or distributed; official Nasdaq CQS suffix WI; do not splice into the regular outstanding symbol) (`data-cleaning` +0.25h, add-on to `examples/p2/11_spinoff_insider_lag_toy.py`, quiz `dc-whenissued`). Item sum **+1.50h**. Hours: **416.75 full / 396.75 skip-P0**; 28 lessons; 335 quiz pairs.
- enrich21 (2026-11-12, US-first): Rule 15c6-1 default and FINRA 11320 delivery-date types (T+1 is the default unless the parties expressly agree otherwise at the time of the transaction; official types are cash, regular way, seller’s option, buyer’s option, and delayed-delivery; 11320(e) rolls a non-business due date to the next business day; 15c6-1(c) after-4:30 p.m. ET firm-commitment offerings can be up to the second business day unless otherwise agreed; no current-law “next day” category) (`microstructure-orders` +0.25h, add-on to `examples/p1/11_freeride_txse_15c33_toy.py`, quiz `mo-15c61`); current 17 CFR 240.12b-2 filer thresholds and hysteresis ($75 million / $700 million entry; $60 million / $560 million exit; last business day of the most recently completed second fiscal quarter; twelve months and one annual report; S7-2026-18 remains Proposed) (`data-cleaning` +0.25h, quiz-only `dc-12b2`; `examples/p2/09_filing_dates_toy.py` not edited); Pub 550 investment interest (margin-account interest to buy taxable securities is investment interest, generally limited to net investment income, with a carryover) (`compliance-ethics` +0.25h, add-on to `examples/p7/11_tax_1259_1256_roc_toy.py`, quiz `ce-invint`); Pub 550 stock dividends and stock rights (generally not taxable; official Example 1 $45 → three shares at $15; holding period of nontaxable new stock begins on the same day as the old stock; fractional-share cash is a sale, not a dividend) (same lesson +0.25h, same lab, quiz `ce-stodiv`); NY Fed SOFR clocks (published at approximately 8:00 a.m. ET, one business day after the value date; yesterday’s SOFR can fill at today’s 09:30 open; today’s value-date SOFR cannot; EFFR/OBFR are about 9:00 a.m.; do not copy the T-bill 15:30 clock onto SOFR) (`returns-vol-corr` +0.25h, add-on to `examples/p1/08_tbill_rf_toy.py`, quiz `rv-sofr`); Cboe Rule 5.1(e)(3) early-close Curb for Curb-eligible options (starts at the end of shortened RTH and lasts 15 minutes, official example 1:00 p.m. to 1:15 p.m.; immediately effective SRO filing SR-CBOE-2026-078 / 34-106620, designated operative upon filing; FAQ/FIX operational parenthetical still “(effective 11/16/26)”; AM-settled last-trading-day change remains Effective TBD; not the stock 12:50 p.m. MOC cutoff) (`market-regimes-crisis` +0.25h, add-on to `examples/p6/15_soq_occ_adj_toy.py`, quiz `rc-earlycurb`). Item sum **+1.50h**. Hours: **418.25 full / 398.25 skip-P0**; 28 lessons; 341 quiz pairs.
- enrich19 (2026-11-12, US-first): Rule 10b-17 issuer notice of a dividend, stock split, or rights offering generally no later than 10 days prior to the record date (not 10 business days; open-end / UIT excepted; a late or missing notice is a timing flag, not proof the dividend did not happen) (`data-cleaning` +0.25h, add-on to `examples/p2/08_dividend_dates_yf_shapes.py`, quiz `dc-10b17`); Form 4 Instruction 8 transaction codes (P / S vs A / M / F / G; V is an earlier-reporting flag) and Form 3 / Form 5 clocks (15 U.S.C. 78p(a)(2)(B) “within 10 days … or within such shorter time as the Commission may establish by rule”; Form 5 within 45 days after FYE, none if already reported; no invented shorter Form 3 clock) (`data-cleaning` +0.25h, add-on to `examples/p2/11_spinoff_insider_lag_toy.py`, quiz `dc-form4codes`); 13G→13D switch under 13d-1(e)–(g) (five-business-day filing clock; standstill until the tenth day from the 13D filing; 20% path is paragraph (c) only) and 13d-3 beneficial ownership (voting and/or investment power; 60-day right-to-acquire, immediate if control purpose) (`data-cleaning` +0.50h, same lab, quiz `dc-13g13d`); BLS PFEI 8:30 a.m. ET vs non-PFEI 10:00 a.m. ET (CPI for November 2026 scheduled December 10, 2026, at 8:30 A.M. Eastern Time; an 8:30 release is out before the 09:30 open, a 10:00 release is look-ahead at that open) (`backtest-traps` +0.25h, add-on to `examples/p2/12_event_time_ipo_toy.py`, quiz `bt-bls-time`); Rule 14e-5 purchases outside a tender offer from public announcement until expiration (`data-cleaning` +0.25h, add-on to `examples/p2/19_rule144_followon_tender_toy.py`, quiz `dc-14e5`); Pub 550 capital-loss deduction cap ($3,000 / $1,500 MFS) and carryover that remains long-term or short-term (`compliance-ethics` +0.25h, add-on to `examples/p7/11_tax_1259_1256_roc_toy.py`, quiz `ce-caploss`). No R95. Hours: **415.25 full / 395.25 skip-P0**; 28 lessons; 329 quiz pairs.
- enrich18 (2026-11-12, US-first): SIP sale-condition codes M / Q / T (plus 6 vs M; CTA ETH FAQ v1.2 for the overnight T clock; UTP September 2026 Note 1 is stale on the 23/5 window) (`microstructure-orders` +0.50h, `examples/p1/13_sale_condition_toy.py`, quiz `mo-salecond`); Form 13H large-trader identification (identifying activity level; confidential; do not invent a 10-day “promptly” clock) (`compliance-ethics` +0.25h, `examples/p7/12_form13h_toy.py`, quiz `ce-13h`); Rule 10b-18 after-hours prong, with official sources not mapping 21:00–04:00 overnight / 23/5 (`data-cleaning` +0.25h, add-on to `examples/p2/18_buyback_10b18_disclosure_toy.py`, quiz `dc-10b18ah`); Rule 604 customer-limit display and FINRA 5320 trading ahead of a customer equity order (`execution-slippage` +0.50h, quizzes `es-604` / `es-5320`); Regulation M Rules 101/102 restricted period and shelf-takedown analysis (`backtest-traps` +0.50h, add-on to `examples/p2/19_rule144_followon_tender_toy.py`, quiz `bt-regm101`). No R95. Hours: **413.5 full / 393.5 skip-P0**; 28 lessons; 323 quiz pairs.
- enrich16 (2026-11-12, US-first): clearly erroneous prints (FINRA 11892 / exchange parallels) and the 2026 overnight extension operative only at the start of 23/5 trading scheduled 2026-12-06 (`market-regimes-crisis` +0.5h, `examples/p6/14_clearly_erroneous_toy.py`, quiz `rc-ceprint`); Rule 10b-21 (deception about delivery and a fail; not every FTD) and the Rule 200 long-marking test (`pairs-stat-arb` +0.50h, `examples/p3/09_rule200_10b21_toy.py`, quizzes `ps-10b21` / `ps-mark200`); intermarket sweep orders as a current-law Rule 611 exception (S7-2026-20 remains a proposal) (`microstructure-orders` +0.25h, quiz `mo-iso`); OCC random assignment to clearing members, with the firm's exchange-approved method (random or FIFO, not necessarily random) (`market-regimes-crisis` +0.25h, add-on to `examples/p6/13_exercise_by_exception_toy.py`, quiz `rc-assign`); constructive sales under IRC §1259, Section 1256 60/40 for nonequity / broad-based index options (not ordinary equity options), and return of capital (Form 1099-DIV box 3; Pub 550 Example 1) (`compliance-ethics` +0.75h, `examples/p7/11_tax_1259_1256_roc_toy.py`, quizzes `ce-1259` / `ce-1256` / `ce-roc`). Also R93: Rule 14e-1(d) extension-notice wording only (disclose the approximate number of securities deposited to date; English second limb timed on the next business day after the scheduled expiration date); no hour or quiz-answer change. Hours: **409.5 full / 389.5 skip-P0**; 28 lessons; 310 quiz pairs.
- enrich14 (2026-11-11, US-first): Rule 10b-18 buyback safe harbor + Item 703 monthly disclosure lag (Form SR vacated 2023-12-19) (`data-cleaning` +0.75h, `examples/p2/18_buyback_10b18_disclosure_toy.py`, quizzes `dc-10b18` / `dc-item703`); NYSE early-close MOC cutoff 12:50 ET on 2026-11-27 and 2026-12-24 + Nasdaq vs NYSE close cutoffs (Nasdaq MOC 15:55 / LOC 15:58) (`microstructure-orders` +0.5h, `examples/p1/10_early_close_nasdaq_moc_toy.py`, quizzes `mo-earlyclose` / `mo-nasdaq-moc`); Reg SHO locate ≠ borrow, Rule 204 close-out under T+1, Rule 201 NBB test and threshold-security definition (`pairs-stat-arb` +0.5h, `examples/p3/08_regsho_locate_closeout_toy.py`, quiz `ps-locate204`); Section 16(b) short-swing profit (`compliance-ethics` +0.25h, `examples/p7/10_section16b_toy.py`, quiz `ce-16b`). Also leftover wording/source fixes R87 (cite SEC 34-105003 / 91 FR 13410 for the CAT pass-through quote), R89 (Reg FD “promptly” means as soon as reasonably practicable, and no later than the 24h / next-open cap), R90 (2026 agenda RIN 3235-AN72; no proposal published as of 2026-11-11), R91 (XBRL companyconcept URL on one line), R92 (lab counts only CAT Fee 2026-1, not Assessment 1A). Hours: **404.25 full / 384.25 skip-P0**; 28 lessons; 294 quiz pairs.
