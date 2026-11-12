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
| `microstructure-orders` | P1 | 20.00 | 2 | 否 | markets-language |
| `returns-vol-corr` | P1 | 9.25 | 2 | 否 | python-pandas-timeseries, stats-probability-basics, markets-language |
| `eval-lab` | P1 | 7 | 2 | 否 | returns-vol-corr, microstructure-orders |
| `data-cleaning` | P2 | 38.50 | 3 | 否 | eval-lab |
| `backtest-traps` | P2 | 34.00 | 4 | 否 | data-cleaning, stats-probability-basics |
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
| `portfolio-risk-sizing` | P6 | 24.25 | 4 | 否 | returns-vol-corr, strategy-compare-lab |
| `execution-slippage` | P6 | 20.50 | 3 | 否 | costs-in-backtest, portfolio-risk-sizing |
| `risk-systems-lab` | P6 | 8 | 3 | 否 | portfolio-risk-sizing, execution-slippage |
| `market-regimes-crisis` | P6 | 18.25 | 4 | 否 | risk-systems-lab |
| `paper-trading-infra` | P7 | 17.5 | 3 | 否 | market-regimes-crisis |
| `compliance-ethics` | P7 | 31.25 | 2 | 否 | paper-trading-infra |
| `frontier-llm-agents` | P8 | 29 | 5 | 否 | factor-workflow, ml-leakage-control, modern-ml-pipelines, compliance-ethics |
| `frontier-tsfm-altdata-crypto` | P8 | 19 | 4 | 否 | modern-ml-pipelines, data-cleaning, execution-slippage |
| `capstone` | P9 | 26 | 5 | 否 | paper-trading-infra, compliance-ethics, factor-workflow, portfolio-risk-sizing |

**程序员建议：** 对 P0 三课做测验；通过则跳过，把时间补给 P2/P4/P5/P6 的重课。

## 2. 阶段总览（由依赖簇导出，非日历格）

| 阶段 | 名称 | 课数 | 总课时 | 6h/周 | 12h/周 | 依赖簇 |
|------|------|-----:|-------:|------:|-------:|--------|
| P0 | 零基础准备（可测验跳过） / Zero-basis foundations (test-out OK) | 3 | 20h | ~3.3 周 | ~1.7 周 | Foundational skills before market microstructure |
| P1 | 市场语言与度量 / Market language & measurement | 4 | 41.75h | ~7.0 周 | ~3.5 周 | Market concepts + evaluation language |
| P2 | 数据与诚实回测 / Data & honest backtests | 4 | 88.00h | ~14.7 周 | ~7.3 周 | Research infrastructure / scientific method for backtests |
| P3 | 经典策略族 / Classic strategy families | 4 | 35.25h | ~5.9 周 | ~2.9 周 | Classic alpha templates before factors/ML |
| P4 | 因子研究 / Factor research | 2 | 33h | ~5.5 周 | ~2.8 周 | Cross-sectional research methods |
| P5 | 机器学习与现代流水线 / ML & modern pipelines | 2 | 32h | ~5.3 周 | ~2.7 周 | Supervised ML methodology for finance |
| P6 | 风险、仓位与执行 / Risk, sizing & execution | 4 | 71.00h | ~11.8 周 | ~5.9 周 | Portfolio construction / execution / controls / regimes |
| P7 | 纸面与伦理 / Paper trading & ethics | 2 | 48.75h | ~8.1 周 | ~4.1 周 | Operationalization and professional norms |
| P8 | 前沿与非主流方法 / Frontier & unconventional methods | 2 | 48h | ~8.0 周 | ~4.0 周 | Post-prerequisite frontier / niche methods |
| P9 | 结业项目 / Capstone | 1 | 26h | ~4.3 周 | ~2.2 周 | Synthesis |

**全量（含 P0）：精确 443.75 学时（跳过 P0 为 423.75）。** 6h/周 ≈ 74.0 周；12h/周 ≈ 37.0 周。
**跳过 P0 后：精确 423.75 学时。** 6h/周 ≈ 70.6 周；12h/周 ≈ 35.3 周。

精确合计：**443.75h 全量 / 423.75h 跳过 P0**。对外可表述为约 **350–443.75h 全量 / 330–423.75h 跳过基础**（含个人复盘缓冲）。

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

### P1 · 市场语言与度量（Market language & measurement）— 41.75h / 4 课

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
- **Hours:** 20.00h · **Difficulty:** 2/5 · **Basis:** 3h concepts + 3h exercises + 1h quiz + 2h US mechanics (T+1/cash vs margin/NBBO·SIP·IEX/sessions/Rule 611 proposal status/best execution) + 0.5h overnight trading & overnight LULD bands (planned 2026-12-06) + 0.25h Rule 612/610(c) version trap + 0.25h HK T+1 plan comparison (target H2 2028, not in effect) + 0.5h official close/closing auction/NYSE MOC cutoff + 0.5h tiered round lots & odd-lot quotes (2025-11-03 / 2026-04-27) + 0.25h SIPC account protection (SIPC limits; not FDIC) + 0.25h tokenized-stock venue (TSV) data separation (SEC 34-106402; TSV prints are not exchange prints) + 0.25h official open, opening auction & MOO cutoff (NYSE DMM open may print after 9:30; Nasdaq NOOP, MOO cutoff 9:28 ET) + 0.25h NYSE early-close MOC cutoff (12:50 ET when close is 13:00) + 0.25h Nasdaq vs NYSE close cutoffs (Nasdaq MOC 15:55 / LOC 15:58) + 0.25h cash-account freeriding (Reg T payment period and 90-day freeze) + 0.25h Rule 15c3-3 customer protection (possession or control and the reserve account) + 0.25h Texas Stock Exchange (TXSE) launch and sessions + 0.25h intermarket sweep orders (ISO as a current-law Rule 611 exception) + 0.25h stop / stop-limit / trailing stop + 0.25h Rule 610(e) locked/crossed quotations (current law; S7-2026-20 would also rescind it) + 0.5h SIP sale conditions M / Q / T (plus 6 vs M) + 0.25h Rule 611(b) exceptions beyond ISO + 0.25h Rule 15c6-1 / FINRA 11320 delivery-date types + 0.25h FINRA 6380A 10-second off-exchange TRF reporting + 0.25h Rule 602 firm quote + 0.25h FINRA 5220 offers at stated prices + 0.25h FINRA 2265 extended hours trading risk disclosure + 0.25h FINRA 2266 written SIPC information + 0.25h FINRA 5330 adjustment of open orders + 0.25h FINRA 2264 margin disclosure statement + 0.25h FINRA 2267 Investor Education and Protection / BrokerCheck + 0.25h FINRA 2261 disclosure of financial condition / most recent balance sheet + 0.25h FINRA 2231 customer account statements + 0.25h FINRA 2090 Know Your Customer + 0.25h FINRA 4370 business continuity plan / customer disclosure + 0.25h FINRA 4340 callable securities allocation + 0.25h FINRA 2140 no interference with customer account transfer + 0.25h Rule 15c6-2 same-day allocation, confirmation, and affirmation + 0.25h FINRA 4330 written authorization to lend customers' margin securities + 0.25h FINRA 3150 holding of customer mail + 0.25h FINRA 2251 processing and forwarding of proxy and other issuer-related materials + 0.25h 17 CFR 240.14b-1 broker-dealer prompt forwarding of certain communications to beneficial owners + 0.25h FINRA 2268 predispute arbitration agreement highlighting and customer copy + 0.25h FINRA 4590 synchronization of member business clocks
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

### P2 · 数据与诚实回测（Data & honest backtests）— 88.00h / 4 课

**阶段目标：** 可版本化数据+陷阱审讯+成本+引擎假设。

**6h/周 ≈ 12.5 周；12h/周 ≈ 6.3 周。**

#### `data-cleaning` — 数据与清洗 / Data & cleaning
- **Hours:** 38.50h · **Difficulty:** 3/5 · **Basis:** 5h concepts + 6h pipeline lab incl mask-first + 2h info-bars + 1h crypto-PIT + 3h docs/quiz + 2h data-versions/corporate-actions/calendar lab + 3h US data sources/licensing/PIT lab (EDGAR/FRED terms R16/Ken French/CRSP/yfinance/Massive/Alpaca) + 2h corporate actions & delisting (R21) + 1h ALFRED revision as-of + 0.5h dividend dates under T+1 (investor.gov) + 0.25h yfinance auto_adjust version trap + 0.5h filing deadlines & EDGAR 5:30pm rule (10-K/10-Q/8-K/13F) + 0.5h delisting returns & permanent IDs (CRSP CIZ) + 0.5h spin-offs & mergers in price series (CRSP split events, DisPERMNO, Form 8937 timing) + 0.5h insider & large-holder filing lags (Form 4 / 13D / 13G, FPI insiders from 2026-03-18) + 0.5h reverse splits & Nasdaq bid-price rule status (30 business days below $1, prior-year reverse split, $0.10 rule, stayed $5M MVLS rule) + 0.5h SEC XBRL API as-of (filed date; frames = last filed; fy describes the filing) + 0.25h Rule 10b5-1 plan check box (Forms 4/5 from 2023-04-01) & cooling-off + 0.5h NYSE price criteria (30-day average, 200:1 reverse-split limit, $0.25 floor from 2027-07-01) + 0.5h Rule 10b-18 buyback safe harbor + 0.25h Item 703 repurchase disclosure lag (Form SR vacated) + 0.5h tender offers (Rule 14e-1 minimum period) + 0.25h Rule 10b-18 after-hours prong (no official 23/5 mapping) + 0.25h Rule 10b-17 issuer notice of record dates + 0.25h Form 4 transaction codes and Form 3 / Form 5 clocks + 0.5h 13G-to-13D switch and 13d-3 beneficial ownership + 0.25h Rule 14e-5 purchases outside a tender offer + 0.25h when-issued / when-distributed contracts (FINRA 11130; Nasdaq CQS WI) + 0.25h 12b-2 filer thresholds and hysteresis + 0.25h Rule 12b-25 / Form 12b-25 late-filing notification + 0.25h Nasdaq CQS suffixes beyond WI/WD + 0.25h Form 8-K items beyond Item 2.02 + 0.25h Form 20-F four-month / Form 6-K promptly-furnished clocks + 0.25h Rule 13d-2 1% material test and 13G amendment clocks + 0.25h Rule 14e-2 subject-company position statement + 0.25h Rule 14d-11 subsequent offering period + 0.25h Rule 14d-10 all-holders / best-price + 0.25h Rule 14e-4 short tendering / net long in a partial tender + 0.25h Section 12(g) / Rule 12g-1 registration thresholds + 0.25h Rule 14e-3 disclose-or-abstain + 0.25h Rule 12g-4 / section 12(g)(4) termination + 0.25h Rule 14d-2 commencement + 0.25h Form 8-K Item 5.07 special clock + 0.25h Rule 14d-3 Schedule TO filing and transmittal + 0.25h Rule 13e-1 issuer purchases during a third-party tender + 0.25h Rule 14a-9 false or misleading proxy statements + 0.25h Rule 12b-20 additional material information + 0.25h Rule 13a-14 certification of disclosure in annual and quarterly reports + 0.25h Rule 10D-1 recovery of erroneously awarded compensation + 0.25h Regulation G 244.100 non-GAAP financial measure presentation and reconciliation + 0.25h Rule 14a-3(b) annual report to security holders accompanying or preceding the proxy + 0.25h Rule 14c-3(a) annual report to security holders accompanying or preceding the information statement
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
- **Hours:** 34.00h · **Difficulty:** 4/5 · **Basis:** 5h concepts + 19h multi-labs (CPCV + one-switch + PBO/CSCV + admission gates) + 4h write-up + 0.5h index membership as-of (Russell semi-annual 2026) + 0.25h FOMC release times as event timestamps + 0.5h IPO data traps (offering price vs fill, short history, lock-ups) + 0.25h Nasdaq-100 rule versions (2026-05-01) and December 2026 reconstitution dates + 0.5h S&P 500 addition rules as of a date (committee discretion, dated cap thresholds, 05:15 PM ET announcements) + 0.25h earnings release times as event timestamps (8-K Item 2.02, Reg FD) + 0.5h Rule 144 resales of restricted and control stock + 0.5h follow-on offerings and Regulation M Rule 105 + 0.5h Regulation M Rule 101/102 restricted period and shelf takedowns + 0.25h BLS PFEI vs non-PFEI release times + 0.25h Fed G.17 monthly 9:15 a.m. vs annual revision at noon + 0.25h FINRA 5130 new issues + 0.25h Regulation M Rule 104 stabilizing vs greenshoe + 0.25h FINRA 5131 spinning and market-order ban + 0.25h Beige Book 2:00 p.m. as printed on the official Board calendar + 0.25h FINRA 5131 flipping and lock-up-waiver news-service mechanics + 0.25h Rule 10b-9 all-or-none / contingency-offering representations + 0.25h FINRA 5131(e)(3) covered-non-public-company financial tests — HEAVY
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

### P6 · 风险、仓位与执行（Risk, sizing & execution）— 71.00h / 4 课

**阶段目标：** 仓位层、执行成本与硬约束工程化。

**6h/周 ≈ 9.7 周；12h/周 ≈ 4.8 周。**

#### `portfolio-risk-sizing` — 组合、风险与仓位 / Portfolio, risk & position sizing
- **Hours:** 24.25h · **Difficulty:** 4/5 · **Basis:** 5h concepts + 13h labs (incl HRP + Brandt no-trade + alpha-decay band) + 4h writing + 1h weight-drift lab + 0.5h margin accounts (Reg T / FINRA 4210) + 0.25h portfolio margin (FINRA 4210(g) toy) + 0.25h short-sale margin (Reg T 150% / FINRA 4210(c)(2)-(3)) + 0.25h Rule 10b-16 disclosure of credit terms in margin transactions — HEAVY
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
- **Hours:** 20.50h · **Difficulty:** 3/5 · **Basis:** 5h concepts (√/Gatheral + public metaorder IRF) + 6.5h experiments + 1.5h quiz + 1h feed-aware TCA (IEX vs SIP arrival, stale NBBO, capacity) + 0.25h Rule 605 vs FINRA 21-23 + 0.5h Rule 606 routing & PFOF + 0.5h NMS Stock ATS and Form ATS-N + 0.25h Rule 604 customer-limit display + 0.25h FINRA 5320 trading ahead of customer equity orders + 0.25h FINRA 5250 payments for market making + 0.25h FINRA 5270 front running of block transactions + 0.25h FINRA 5230 payments involving publications + 0.25h FINRA 5280 trading ahead of research reports + 0.25h Rule 10b-10 written confirmation + 0.25h FINRA 5240 anti-intimidation / coordination + 0.25h FINRA 5290 no splitting for credits or rebates + 0.25h FINRA 2262 control-relationship disclosure + 0.25h FINRA 2269 distribution-participation written notification + 0.25h FINRA 2121 fair prices and commissions / the official "5% Policy" + 0.25h FINRA 2122 charges for services performed + 0.25h FINRA 2124 disclosure and consent for "net" transactions + 0.25h 17 CFR 242.607 written PFOF and routing-policy notifications upon opening a new account and annually thereafter + 0.25h FINRA 2232(b)(1) NMS settlement-date confirmation disclosure + 0.25h FINRA 2232(b)(2) callable-equity confirmation disclosure + 0.25h 17 CFR 240.15c2-4 transmission or maintenance of payments received in connection with underwritings (other than a firm-commitment underwriting) + 0.25h FINRA 5310 best execution and interpositioning + 0.25h 17 CFR 240.15c1-5 disclosure of control + 0.25h 17 CFR 240.15c1-6 disclosure of interest in distribution
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
- **Hours:** 18.25h · **Difficulty:** 4/5 · **Basis:** 4.5h concepts + 5h labs (path/overlays/corr/HMM) + 1.5h quiz/review + 1h options/VIX risk box + 1h MWCB/LULD/Reg SHO 201 comparison (R12 tiers, Amendment 18) + 0.5h overnight LULD price bands (Amendment 27/29, Phase 1) + 1.5h US options basics (OCC ODD June 2024; parity; BSM as reference) + 0.25h MWCB Level 3 resumption under 23/5 (SR-NYSE-2026-43 / SR-NASDAQ-2026-080) + 0.25h SEC trading suspensions vs exchange halts (15 U.S.C. 78l(k), up to 10 business days; SEC 34-106668) + 0.25h expiration exercise-by-exception (OCC Rule 805) + 0.5h clearly erroneous prints (FINRA 11892; 2026 overnight extension operative at 23/5 start scheduled 2026-12-06) + 0.25h OCC assignment to clearing members (firm method may be random or FIFO) + 0.5h AM-settled index SOQ (current last trading day usually Thursday; GTH change Effective TBD) + 0.25h OCC cash-dividend adjustments ($12.50 per contract) + 0.25h LULD Plan Section VII reopen clocks + 0.25h Cboe Rule 5.1(e)(3) early-close Curb + 0.25h Nasdaq halt codes T1 / H10 / LUDP / MWC1–3 + 0.25h FINRA 5260 no transacting or quoting during a halt
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

### P7 · 纸面与伦理（Paper trading & ethics）— 48.75h / 2 课

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
- **Hours:** 31.25h · **Difficulty:** 2/5 · **Basis:** 8h reading (Northbound + PDA withdrawal + FY2026/FINRA GenAI + SFC 24EC55 + ESMA74 algo briefing) + 4.5h writing + 2.5h quiz + 1h rule versions (FINRA main example + SSE 2026 comparison) + 0.5h US four-date table & phase-in status (R04) + 2.5h cross-border tax/FX/CRS literacy box (R25/R28/R29) + 0.5h wash-sale basis lab (IRS Pub 550 examples, purchase-order matching) + 0.5h holding period & qualified dividends (IRS Topic 409 / Pub 550 / Pub 519) + 0.5h manipulation red lines & self-trade lab (15 U.S.C. 78i / FINRA 5210 / CAT review) + 0.25h tokenized NMS stock Innovation Exemption status (SEC 34-106402, until 2031-09-17) + 0.25h tax lots: FIFO vs adequate identification (IRS Pub 550; Form 1099-B basis for covered securities) + 0.25h Section 16(b) short-swing profit (15 U.S.C. 78p(b)) + 0.25h constructive sales (IRC §1259) + 0.25h Section 1256 60/40 (nonequity / broad-based index options) + 0.25h return of capital (Form 1099-DIV box 3) + 0.5h short-over-ex-div cash obligation, payments in lieu (not QDI), and preferred QDI 90/181 + 0.25h Form 13H large-trader identification (identifying activity level; confidential) + 0.25h capital-loss deduction cap and carryover (IRS Pub 550) + 0.25h short-sale tax character (IRS Pub 550 Ace example) + 0.25h worthless securities sold on the last day of the tax year (IRC §165(g)) + 0.25h investment interest (Pub 550 margin interest, net-investment-income limit) + 0.25h stock dividends and stock rights (Pub 550 basis and holding period) + 0.25h Pub 550 gift and inherited basis + 0.25h 1099-DIV box 2a capital-gain distributions + 0.25h Pub 550 puts and calls + 0.25h Pub 550 put option as short sale holding-period rule + 0.25h 1099-B box 5 / 12 / 1g + 0.25h Pub 550 liquidating distributions (1099-DIV box 9 or 10) + 0.25h Exchange Act section 28(e) brokerage-and-research safe harbor + 0.25h Regulation AC § 242.501 research-analyst certification + 0.25h FINRA 2150 improper use of customers' securities or funds / no guarantee against loss + 0.25h FINRA 3220 gifts in excess of $300 per individual per year + 0.25h Rule 10b-5 antifraud + 0.25h FINRA 2010 commercial honor + 0.25h FINRA 2165 Specified Adult temporary-hold safe harbor + 0.25h FINRA 3310 written AML program + 0.25h FINRA 2060 fiduciary-capacity information + 0.25h FINRA 3210 associated-person accounts at other firms + 0.25h FINRA 3270 outside business activities + 0.25h FINRA 3280 private securities transactions + 0.25h FINRA 4513 written customer-complaint records + 0.25h Regulation S-P 248.30 written customer-information safeguards + 0.25h FINRA 4514 authorization records for negotiable instruments + 0.25h FINRA 1122 misleading membership or registration filings + 0.25h FINRA 8210 provision of information and testimony + 0.25h FINRA 2273 recruited-person educational communication + 0.25h FINRA 2040 payments to unregistered persons + 0.25h Rule 10b5-2 duty of trust or confidence + 0.25h FINRA 3130 designation of a chief compliance officer and annual CEO certification + 0.25h FINRA 2270 day-trading risk disclosure statement + 0.25h 17 CFR 240.15c1-7 discretionary accounts
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
- enrich22 (2026-11-12, US-first): FINRA 6380A current 10-second off-exchange last-sale reporting to the FINRA/Nasdaq TRF (as soon as practicable but no later than 10 seconds during current TRF hours; midnight–4:00 a.m. ET due by 4:15 a.m. on trade date; 8:00 p.m.–midnight or a non-business day the following business day by 4:15 a.m. as/of; execution time in hours, minutes and seconds ET; exchange prints are not reported to the FINRA/Nasdaq TRF; Supplementary Material .02 forbids purposely withholding reports until the last permissible second; Supplementary Material .05 is a narrow temporary exception for specified qualifying overnight transactions until the earlier of a further TRF-hours amendment’s effective date or December 31, 2027; SR-FINRA-2026-015 / 34-105922 / 91 FR 45299 was filed for immediate effectiveness but the implementation date is the SIP Amendment implementation date, anticipated December 6, 2026 and may move later; future 10-second / 15-minutes-after-open clocks are not current law; official May 22 and July 10, 2026 notices say ADF hours are not changing at this time; 6380B is the parallel FINRA/NYSE TRF rule) (`microstructure-orders` +0.25h, add-on to `examples/p1/13_sale_condition_toy.py`, quiz `mo-6380a`); Rule 602 firm-quote obligation (a responsible broker-dealer’s published bid or offer is generally firm up to the published size, other than an odd-lot order; 602(b)(3) revision exceptions and 602(a)(3) unusual-market relief; do not treat displayed NBBO size as a guaranteed fill) (same lesson +0.25h, add-on to `examples/p1/05_us_market_mechanics.py`, quiz `mo-602`); Rule 12b-25 / Form 12b-25 late-filing notification (due no later than one business day after the prescribed due date; a 10-K or 10-Q is deemed timely only if the official conditions are met, including actual filing within 15 calendar days (annual) or 5 calendar days (quarterly); EDGAR often labels the notification NT 10-K or NT 10-Q; the official form is Form 12b-25; statutory 60 / 75 / 90 and 40 / 45 clocks are unchanged) (`data-cleaning` +0.25h, quiz-only `dc-12b25`; `examples/p2/09_filing_dates_toy.py` and `examples/p2/17_xbrl_pit_10b51_toy.py` not edited); Nasdaq CQS suffixes beyond the already-taught WI / WD labels (official table columns include CQS and CMS: Preferred CQS p / CMS PR, Preferred Class A PRA, Class A / Class B, Warrants WS, Rights RT, Units U; CQS convention is for reference purposes only and is not used for Nasdaq integrated-platform order entry; do not invent one universal suffix) (same lesson +0.25h, add-on to `examples/p2/11_spinoff_insider_lag_toy.py`, quiz `dc-cqssuffix`; Form 5 2026-02-17 and 13d-1(g) 2026-10-13 unchanged); official Nasdaq halt reason codes T1 / H10 / LUDP / LUDS / MWC1–3 as a map onto already-taught news-pending, SEC-suspension, LULD-style volatility-pause, and MWCB halt types (MWC0 is a previous-day carry-over; the official table’s T5 “10% or more price move in a five-minute period” sentence is not current LULD and must not overwrite Plan text) (`market-regimes-crisis` +0.25h, add-on to `examples/p6/06_luld_halt_toy.py`, quiz `rc-haltcodes`); Pub 550 gift and inherited basis (inherited capital-asset shares generally take FMV at the date of death or alternate valuation and a later sale is long-term regardless of holding period; gifted stock generally takes the donor’s adjusted basis, with an official dual-basis rule when FMV at the gift is lower; official $10,000 / $9,000 / $9,500 neither-gain-nor-loss example; holding period follows the donor if basis is the donor’s adjusted basis, or starts the day after the gift if basis is FMV; general information, not tax advice) (`compliance-ethics` +0.25h, add-on to `examples/p7/11_tax_1259_1256_roc_toy.py`, quiz `ce-giftbasis`). Item sum **+1.50h**. Hours: **419.75 full / 399.75 skip-P0**; 28 lessons; 347 quiz pairs.
- enrich23 (2026-11-12, US-first): FINRA 5130 new-issue allocation (a member may not sell a “new issue” — an equity IPO — to an account in which a restricted person has a beneficial interest, except as the rule permits; official carve-outs include preferred, convertibles, already-traded-abroad ordinary shares / Form F-6 ADRs, a registered investment company, and an account in which restricted-person beneficial interests do not exceed in the aggregate 10%; the offering-price first-day return is not a fill every account could have earned; FINRA 5131 is a different rule) (`backtest-traps` +0.25h, add-on section F of `examples/p2/12_event_time_ipo_toy.py`, quiz `bt-5130`; sections A–E, including FOMC, IPO offering price, BLS, and G.17, unchanged); Form 8-K items beyond Item 2.02 (official captions: 1.01 Entry into a Material Definitive Agreement; 1.05 Material Cybersecurity Incidents; 4.02 Non-Reliance on Previously Issued Financial Statements or a Related Audit Report or Completed Interim Review; 5.02 Departure of Directors or Certain Officers; Election of Directors; Appointment of Certain Officers; Compensatory Arrangements of Certain Officers; usual clock still four business days, but Item 1.05 is due within four business days after the registrant determines the incident is material; Instruction 1: materiality determination must be made without unreasonable delay after discovery — do not start the clock on discovery; Item 2.02 / 7.01 are furnished, not deemed filed for Section 18 in the usual case; Form 12b-25 does not apply to an 8-K) (`data-cleaning` +0.25h, add-on section D of `examples/p2/16_index_add_earnings_time_toy.py`, quiz `dc-8kitems`; sections A–C, including the S&P addition screen and the Thursday 16:05 / Friday day-0 earnings example, unchanged; the Item 2.02 earnings-time box in `backtest-traps` stays as written); Form 20-F / 6-K clocks (a foreign private issuer’s annual report on Form 20-F is due within four months after fiscal year-end, not on the 10-K 60 / 75 / 90 clocks; Form 6-K is furnished promptly after the material is made public in the official home-market / exchange / shareholder channels, and is not deemed filed for Section 18 in the usual case; Form 40-F is a different MJDS form; 13a-16 does not apply to issuers already filing 10-K / 10-Q / 8-K, or to issuers of ADRs for securities of a foreign issuer (the depositary)) (`data-cleaning` +0.25h, quiz-only `dc-20f6k`; `examples/p2/09_filing_dates_toy.py` and `examples/p2/17_xbrl_pit_10b51_toy.py` not edited; Form 10-S still “not adopted as of 2026-11-11”); narrow Regulation M Rule 104 / greenshoe slice (official 104 activities are stabilizing, syndicate covering, and penalty bids, with the official 242.100 definitions; they are distinct from an overallotment option / “greenshoe” (Form 20-F Item 9.B.5); stabilizing is prohibited in an ATM and allowed only to prevent or retard a decline (104(b)/(e)); a prior-notice requirement exists; do not invent a 15% cap or teach the 104(f) stabilizing-level catalog) (`backtest-traps` +0.25h, add-on section G of `examples/p2/19_rule144_followon_tender_toy.py`, quiz `bt-regm104`; sections A–F, including Rule 105, 14e-1, 101/102, and 14e-5, unchanged); 1099-DIV box 2a capital-gain distributions (long-term capital gain regardless of how long the shareholder held the fund or REIT shares, even if no shares were sold; not ordinary income, QDI, or box 3 ROC; boxes 2b/2c/2d/2f are official subsets; undistributed capital gains can appear on Form 2439; general information, not tax advice) (`compliance-ethics` +0.25h, add-on section J of `examples/p7/11_tax_1259_1256_roc_toy.py`, quiz `ce-cgdist`; sections A–I, including box 3, the capital-loss cap, and the gift / inherited official $10,000 / $9,000 / $9,500 example, unchanged); Pub 550 puts and calls (official holder/writer rules and the official $4,000 expiration / $6,000 closing-transaction examples: ten JJJ calls issued April 8, 2025, for $4,000, expired December 2025 — holder STCL $4,000, writer STCG $4,000; same options sold May 6, 2025, for $6,000 — holder STCG $2,000, writer STCL $2,000; if instead they are nonequity section 1256 contracts, the $4,000 is split $1,600 short-term and $2,400 long-term, which is the already-taught 60/40 rule, not the ordinary-equity rule; a later “Straddles” heading and a “Put option as short sale” holding-period rule exist; the official text’s “such as the Chicago Board Options Exchange” is an example of a national securities exchange, not a venue recommendation; general information, not tax advice) (`compliance-ethics` +0.25h, add-on section K of the same tax toy, quiz `ce-optstax`; sections A–J unchanged once J is added). Item sum **+1.50h**. Hours: **421.25 full / 401.25 skip-P0**; 28 lessons; 353 quiz pairs.
- enrich24 (2026-11-12, US-first): FINRA 5131 spinning and the market-order ban (spinning is a different prohibition from 5130: a member may not allocate a new issue to an account in which an executive officer or director of a public company or a covered non-public company, or a person materially supported by them, has a beneficial interest, if official IB conditions (A)/(B)/(C) are met; a member may not accept a market order for a new issue in the secondary market before secondary trading commences; name the official 25% / 5130(c) / Supplementary Material .01 issuer-directed carve-outs, do not build that engine; 5131(a) quid pro quo is a different official paragraph, name only; “new issue” has the same meaning as 5130(i)(9); no product, broker, or allocation recommendation) (`backtest-traps` +0.25h, add-on section G of `examples/p2/12_event_time_ipo_toy.py`, quiz `bt-5131`; section F, including the line “FINRA 5131 is a different rule (new-issue allocation / spinning) and is not taught here,” and 28/28 after F, unchanged); Rule 13d-2 amendments (a 1% acquisition or disposition is deemed material, and smaller changes may still be material; a 13D amendment is within two business days; a 13G generally amends within 45 days after calendar quarter-end if there are material changes, not on the 13D 1% / two-business-day clock; a percent change solely from a change in shares outstanding need not be a 13G amendment; name official 13d-2(c)/(d) intra-period 10% / more-than-5% clocks, do not build that engine; do not reopen R95/R96; do not rewrite the already-taught two-business-day 13D sentence, initial lags, switch clocks, or the Form 10-S “not adopted as of 2026-11-11” sentence) (`data-cleaning` +0.25h, add-on section I of `examples/p2/11_spinoff_insider_lag_toy.py`, quiz `dc-13d2`; sections A–H, including Form 5 due date 2026-02-17, 13d-1(g) fifth business day 2026-10-13, and 54/54 after H, unchanged); Rule 14e-2 subject-company position statement (no later than 10 business days from the date the offer is first published, sent, or given, the subject company must state its position — recommend acceptance or rejection, remain neutral, or unable to take a position — with the reason(s); a material change is published promptly, with no invented fixed number of days; this is not the 14e-1 20-business-day duration and not a 10-calendar-day clock; Schedule 14D-9 is the form, filed as soon as practicable on the date the recommendation is published — do not invent a second 10-business-day 14D-9 filing clock; do not rewrite already-taught Rule 14e-1 / 14e-5 paragraphs, including 14e-1(d)’s extension-notice 9:00 a.m. clock) (`data-cleaning` +0.25h, add-on section H of `examples/p2/19_rule144_followon_tender_toy.py`, quiz `dc-14e2`; sections A–G, including Rule 105, 14e-1, 101/102, 14e-5, and Rule 104, and 29/29 after G, unchanged); Rule 14d-11 subsequent offering period (optional; a bidder may elect at least three business days only if official conditions are met: the initial period of at least 20 business days has expired; the offer is for all outstanding securities of the class; immediate accept and prompt pay; results announced no later than 9:00 a.m. Eastern time on the next business day after initial expiration and the subsequent period begins immediately; same form and amount of consideration; official note: no withdrawal rights during the subsequent period (14d-7(a)(2)); withdrawal rights do apply during the initial open period (14d-7(a)(1)); do not invent a 15-business-day cap or any unofficial maximum; do not flatten this 9:00 a.m. results clock into already-taught 14e-1(d) extension-notice language; cross-link the already-taught 14e-5 same-consideration carve-out, do not rewrite it; no bidder or strategy recommendation) (`data-cleaning` +0.25h, add-on section I of the same tender toy, quiz `dc-14d11`; sections A–H unchanged once H is added); Pub 550 “Put option as short sale” holding-period rule (buying a put is generally treated as a short sale; exercise, sale, or expiration of the put is a closing of that short sale; if the underlying stock has been held for 1 year or less when the put is bought, or if the stock is bought after the put and before the put is exercised, sold, or expires, any gain on the put is short-term, and the holding period of the underlying stock begins on the earliest of the date the stock is disposed of, the put is exercised, the put is sold, or the put expires; do not invent a married-put exception; do not invent a rule for stock already held more than one year beyond the official sentences; do not apply §1256 60/40; do not rewrite the already-taught puts-and-calls paragraph, short-sale tax character box, §1256 60/40 box, or official $4,000 / $6,000 examples; general information, not tax advice) (`compliance-ethics` +0.25h, add-on section L of `examples/p7/11_tax_1259_1256_roc_toy.py`, quiz `ce-putss`; section K, including the line “a Put option as short sale holding-period rule exists in Pub 550; this toy is not that engine,” and 26/26 after K, unchanged); 1099-B box 5 / 12 / 1g (box 5 marks a noncovered security: the broker may leave boxes 1b / 1e / 1f / 1g / 2 blank and need not check box 12; a blank basis is not a zero cost; official Arlo June 2026 single sale is reported on separate 1099-B forms — April 2025 long-term covered, August 2025 short-term covered, April 2024 noncovered, and box 5 may be checked on the noncovered form; box 12, if checked, means basis in box 1e was reported to the IRS; box 1g must report a §1091 wash-sale loss when both the sale and purchase occur in the same account in covered securities with the same CUSIP, and the broker is permitted but not required to report all §1091 losses; do not treat a blank box 1g as proof that no wash sale occurred; do not conflate 1099-B box 5 with 1099-DIV box 5 / §199A; do not build a complete 1091 engine; do not rewrite the already-taught FIFO / adequate-identification / covered-security 2011-01-01 / 2012-01-01 paragraph, the 61-day wash-sale box, or the 1099-DIV box 2a / box 3 boxes; general information, not tax advice) (`compliance-ethics` +0.25h, add-on section D of `examples/p7/09_tax_lot_toy.py`, quiz `ce-1099b`; sections A–C, including the official Pub 550 FIFO $1,380 example and 3/3 after C, unchanged). Item sum **+1.50h**. Hours: **422.75 full / 402.75 skip-P0**; 28 lessons; 359 quiz pairs.
- enrich25 (2026-11-12, US-first): Pub 550 liquidating distributions (also called liquidating dividends) are, at least in part, one form of a return of capital, reported on Form 1099-DIV in box 9 or 10 (not box 1a / 1b, and not already-taught box 3); they are not taxable until basis is recovered; after basis is zero, later amounts are capital gain; a capital loss may be reported only after the final distribution that results in the redemption or cancellation of the stock; official complete-liquidation allocation among blocks may be named, not built; do not rewrite already-taught box 3 ROC, box 2a, the capital-loss cap, FIFO, or 1099-B box 5 paragraphs; general information, not tax advice (`compliance-ethics` +0.25h, add-on section M of `examples/p7/11_tax_1259_1256_roc_toy.py`, quiz `ce-liqdist`; sections A–L, including the official $4,000 / $6,000 examples, the section K “this toy is not that engine” line, section L, and 32/32 after L, unchanged); Rule 14d-10 all-holders / best-price (the offer must be open to all security holders of the class, and the consideration paid to any holder for securities tendered must be the highest consideration paid to any other holder; official (b)–(f) exceptions named only; do not flatten into already-taught 14d-11 same-consideration language or the 14e-5 same-consideration subsequent-period carve-out; do not rewrite the 14e-1(b) 10-business-day change-of-consideration window or the 14e-1(d) extension-notice sentence) (`data-cleaning` +0.25h, add-on section J of `examples/p2/19_rule144_followon_tender_toy.py`, quiz `dc-14d10`; sections A–I, including Rule 105, 14e-1, 101/102, 14e-5, Rule 104, 14e-2, 14d-11, and 39/39 after I, unchanged); Rule 14e-4 short tendering / net long in a partial tender (the net-long test applies at the time of tender and at the end of the proration or lot-acceptance period, including extensions; official 14e-4(a)(5) includes a less-than-all offer accepted by lot or pro rata and an all-outstanding offer that offers a choice of consideration accepted by lot or pro rata — do not apply the limit to every tender; equivalent securities and options enter the official net-long definition, do not build that engine; supporting 14d-8: if more securities are deposited than will be taken up, they are taken up as nearly as may be pro rata, disregarding fractions; do not pack 14d-8 as its own MUST; do not invent a 14d-11 maximum or flatten proration into already-taught 14d-11 election language) (`data-cleaning` +0.25h, add-on section K of the same tender toy, quiz `dc-14e4`; sections A–J identical once J is added); FINRA 5250 payments for market making (a member may not accept payment or other consideration, directly or indirectly, from an issuer, or any affiliate or promoter thereof, for publishing a quotation, acting as market maker, or submitting an application in connection therewith; official (b) exceptions for bona fide services including underwriting compensation and fees, reimbursement of SEC/state registration fees and SRO listing fees, and payments expressly provided for under exchange rules effective after being filed with, or filed with and approved by, the SEC, are named only; do not rewrite already-taught PFOF / Rule 606, Rule 605, or FINRA 5320; do not build a promoter / 5121-affiliate / exchange-fee-schedule engine) (`execution-slippage` +0.25h, add-on after the existing prints of `examples/p6/12_rule606_toy.py`, quiz `es-5250`; the current 606 table, 4/4, `ASSERT_rule606_ok`, and the reminder line unchanged); FINRA 5270 front running of block transactions (a different prohibition from already-taught 5320: a member with material, non-public market information about an imminent block may not cause an order in that security or a related financial instrument to be executed before that information has been made publicly available or has otherwise become stale or obsolete; SM .03: in equities, 10,000 shares or more is generally deemed a block, although fewer than 10,000 could be a block; splitting into non-block pieces does not change identity if the full transaction may have a material impact; SM .02: public availability is not satisfied until the entire block has been completed and publicly reported; official SM .04 exceptions named only; do not treat 10,000 shares as a rigid floor; do not rewrite 5320) (`execution-slippage` +0.25h, add-on after the new 5250 section of the same 606 toy, quiz `es-5270`; existing 606 prints and the new 5250 section unchanged once added); Section 12(g) / Rule 12g-1 (an issuer is not required to register a class of equity under 12(g) if, on the last day of its most recent fiscal year, it had total assets not exceeding $10 million, or the class was held of record by fewer than 2,000 persons and fewer than 500 of those persons were not accredited investors; banks / S&L holding companies / bank holding companies use a fewer-than-2,000-person test without the 500 prong; the statutory trigger is assets exceeding $10,000,000 and holders of record of either 2,000 persons or 500 unaccredited, with a 120-day post-FYE clock; a registration statement becomes effective sixty days after filing, or such shorter period as the Commission may direct; official current texts still use $10 million / $10,000,000 — do not invent an inflation-adjusted asset figure; do not swap the official 12g-1 “and” exemption for a sloppy “or”; “accredited investor” is defined by reference to § 230.501(a) as of that day; “held of record” is defined in Rule 12g5-1, and an employee-compensation-plan carve-out exists; 12(g)(4) termination exists — name only, do not build those engines; do not flatten into already-taught 12b-2, 10-K/10-Q, or Form 13F 45-day sentences; do not bump the Form 10-S “not adopted as of 2026-11-11” sentence) (`data-cleaning` +0.25h, quiz-only `dc-12g1`; `examples/p2/09_filing_dates_toy.py` and `examples/p2/17_xbrl_pit_10b51_toy.py` were not edited). Item sum **+1.50h**. Hours: **424.25 full / 404.25 skip-P0**; 28 lessons; 365 quiz pairs.
- enrich26 (2026-11-12, US-first): Rule 14e-3 disclose-or-abstain (once a substantial step or commencement has occurred, a person with material nonpublic tender information from the official sources may not buy or sell, or cause a buy or sell, unless that information and its source are publicly disclosed within a reasonable time beforehand; official (b) entity procedures / information-barrier defense, (c) offering-person purchase and sale-to-offering-person exceptions, and (d) anti-tipping named only; official typographical artifact “to contrary” quoted, not silently corrected; do not invent a fixed number of days for “a reasonable time”; do not flatten into already-taught 14e-2, 14e-1, 14d-10, 14e-4, 14e-5, or 10b5-1) (`data-cleaning` +0.25h, add-on section L of `examples/p2/19_rule144_followon_tender_toy.py`, quiz `dc-14e3`; sections A–K, including Rule 105, 14e-1, 101/102, 14e-5, Rule 104, 14e-2, 14d-11, 14d-10, 14e-4, and 48/48 after K, unchanged); FINRA 5230 payments involving publications that influence the market price (a member may not, directly or indirectly, give, permit to be given, or offer to give anything of value to influence or reward a publication intended to affect the market price of any security; official (b) exceptions for a communication clearly distinguishable as paid advertising, a communication that discloses compensation and the amount thereof in accordance with Securities Act 17(b), and a research report as defined in Rule 2241, named only; do not rewrite already-taught 5250 or PFOF / Rule 606) (`execution-slippage` +0.25h, add-on after the existing prints of `examples/p6/12_rule606_toy.py`, quiz `es-5230`; the current 606 table, 4/4, `ASSERT_rule606_ok`, the reminder line, the 5250 section, the 5270 section, and 12/12 after 5270 unchanged); FINRA 5280 trading ahead of research reports (a different prohibition from already-taught 5270 and 5320: a member may not establish, increase, decrease, or liquidate an inventory position in a security or a derivative of that security based on non-public advance knowledge of the content or timing of a research report; official 5280(b) information-flow procedures named only; do not rewrite 5270 or 5320) (`execution-slippage` +0.25h, add-on after the new 5230 section of the same 606 toy, quiz `es-5280`; existing 606, 5250, and 5270 prints and the new 5230 section unchanged once added); Rule 12g-4 / 15 U.S.C. 78l(g)(4) termination (registration terminates 90 days, or such shorter period as the Commission may determine, after a Form 15 certification; statutory holder tests are less than 300 persons, or 1,200 for a bank / savings-and-loan holding company / bank holding company; Rule 12g-4 also has a second prong — fewer than 500 persons, where total assets have not exceeded $10 million on the last day of each of the issuer’s most recent three fiscal years; 12g-4(b): the 13(a) duty “shall be suspended immediately upon filing a certification on Form 15,” with a 60-day restoration clock if the certification is withdrawn or denied; do not treat the Form 15 filing date as the termination date; do not invent an inflation-adjusted $10 million; official current 12g-4 still uses $10 million, last amended May 10, 2016; do not flatten the statute and the rule or silently tidy the LII typographical artifact “1,200 persons persons. [1]”; do not bump the Form 10-S “not adopted as of 2026-11-11” sentence) (`data-cleaning` +0.25h, quiz-only `dc-12g4`; `examples/p2/09_filing_dates_toy.py` and `examples/p2/17_xbrl_pit_10b51_toy.py` were not edited); Beige Book 2:00 p.m. as printed on the official Board calendar (official publication page lists 2026 dates eight times per year with no clock and no time zone; official Board monthly calendars print 2:00 p.m. for January 14, March 4, June 3, July 15, September 2, October 14, and November 25, with no time zone on those cards; do not invent “Eastern,” “ET,” “EST,” or “EDT,” or copy the January calendar’s FOMC “2 p.m. EST” notice onto Beige Book; do not invent 2:00 p.m. for April 15, whose monthly calendar page was not available; a 2:00 p.m. release cannot fill at that day’s 09:30 open; do not invent a G.19 clock; event-timestamp literacy only) (`backtest-traps` +0.25h, add-on section H of `examples/p2/12_event_time_ipo_toy.py`, quiz `bt-beigebook`; sections A–G, including G.17, “this toy does not invent a G.19 clock or a first-Friday rule,” already-taught 5131 spinning / market-order ban, and 32/32 after G, unchanged); FINRA 5131 flipping / lock-up-waiver news-service mechanics (a later official slice, not a rewrite of spinning or the 5131(d)(4) market-order ban: “Flipped” means the initial sale of new-issue shares purchased in an offering within 30 days following the offering date; a member may not recoup a selling commission after a flip unless a syndicate-wide penalty bid has been assessed; at least two business days before a lock-up release or waiver, the book-running lead manager notifies the issuer and announces through a major news service; official (d)(2) exceptions and SM .03 named only; do not pack covered-non-public-company financial tests; leave the already-taught spinning paragraph, including the instruction not to build a flipping engine, as written) (`backtest-traps` +0.25h, add-on section I of the same IPO toy, quiz `bt-5131flip`; sections A–H identical once H is added). Item sum **+1.50h**. Hours: **425.75 full / 405.75 skip-P0**; 28 lessons; 371 quiz pairs.
- enrich27 (2026-11-12, US-first): Rule 10b-10 written confirmation (a broker shall give or send the customer written notification at or before completion of the transaction; requested additional information generally within five business days of receipt of the request, or fifteen business days if the transaction is more than 30 days old; do not invent a T+1 or trade-date confirmation clock; do not rewrite already-taught 10b-10(d)(8) PFOF; official typographical artifact “this paragraph (a)(9) shall not apply” quoted, not silently corrected, if 10b-10(a)(8) is quoted; official 10b-10(a) catalog, (b), and (e) exceptions, and 15c1-1 as named by (d)(2) for “completion,” named only) (`execution-slippage` +0.25h, add-on section F of `examples/p6/12_rule606_toy.py`, quiz `es-10b10`; the current 606 table, 4/4, `ASSERT_rule606_ok`, the reminder line, the 5250 section, the 5270 section, 12/12 after 5270, the 5230 section, 15/15 after 5230, the 5280 section, and 18/18 after 5280 unchanged); Exchange Act section 28(e) brokerage-and-research commission safe harbor (the fact that a person pays a commission in excess of what another broker would have charged does not itself violate 28(e)(1), if the person determined in good faith that the commission was reasonable in relation to the brokerage and research services; official (3) categories named from the statute; do not invent a “soft-dollar list”; do not rewrite already-taught PFOF; official (2) and (4) named only) (`compliance-ethics` +0.25h, quiz-only `ce-28e`; `examples/p2/09_filing_dates_toy.py` and `examples/p2/17_xbrl_pit_10b51_toy.py` were not edited; no tax or self-trade toy was stretched to carry this item); FINRA 5240 anti-intimidation / coordination (a different prohibition from already-taught 5230, 5250, 5270, 5280, and 5320: a member may not coordinate prices, trades, or trade reports, direct or request another member to alter a price (including a quotation), or threaten, harass, coerce, intimidate, or otherwise attempt improperly to influence another member or market participant; official (b) unilateral exceptions exist — this is not a ban on every unilateral quote; official (b)(1)–(7) catalog named only) (`execution-slippage` +0.25h, add-on section G of the same 606 toy after the new 10b-10 section, quiz `es-5240`; the new 10b-10 section identical once added); FINRA 5260 no transacting or quoting during a halt (except as permitted under the LULD Plan, a member may not transact in or publish a quotation, a bid wanted, an offer wanted, or an indication of interest in any security as to which a trading halt is currently in effect; a FINRA-only close under 6120(a)(3) does not constitute a halt of other markets; do not rewrite already-taught halt codes, LULD Plan clocks, MWCB, or SEC suspensions; do not treat the official table’s T5 “10% in five minutes” wording as current LULD; official (b) futures and 6120 named only) (`market-regimes-crisis` +0.25h, add-on section 6 of `examples/p6/06_luld_halt_toy.py`, quiz `rc-5260`; sections 1–5, including 7/7, 4/4, and 6/6 after the halt-code map, unchanged); Rule 14d-2 commencement (a bidder commences a tender offer, for purposes of Exchange Act section 14(d) and the rules under that section, at 12:01 a.m. on the date when the bidder has first published, sent, or given the means to tender to security holders; official 14d-2(a) prints “12:01 a.m.” with no time zone — do not invent a zone, and do not copy already-taught 14d-11’s “9:00 a.m. Eastern” onto 14d-2; a qualifying pre-commencement communication that does not include the means to tender and is filed under cover of Schedule TO is not commencement; do not flatten into already-taught 14e-3 or 14e-1; official (c) 14d-3 / 14d-4 / 14d-6 named only) (`data-cleaning` +0.25h, add-on section M of `examples/p2/19_rule144_followon_tender_toy.py`, quiz `dc-14d2`; sections A–L, including 52/52 after L, unchanged); Form 8-K Item 5.07 special clock (the four-business-day period for Item 5.07, other than 5.07(d), begins to run on the day the meeting ended; preliminary voting results then final results by amended 8-K within four business days after they are known, or finals only if already disclosed; official 5.07(d) uses a different clock — no later than 150 calendar days after the end of the meeting, and in no event later than 60 calendar days prior to the deadline for submission of shareholder proposals under Rule 14a-8; do not invent a four-business-day clock for (d); do not flatten 5.07 into already-taught Instruction B.1 or Item 1.05; keep the existing “do not flatten Item 5.07 or other special clocks into the same trigger” line; Rule 14a-8 named only) (`data-cleaning` +0.25h, add-on section E of `examples/p2/16_index_add_earnings_time_toy.py`, quiz `dc-8k507`; sections A–D, including 13/13 after C and 18/18 after D, and the existing flatten-warning line, unchanged). Item sum **+1.50h**. Hours: **427.25 full / 407.25 skip-P0**; 28 lessons; 377 quiz pairs.
- enrich28 (2026-11-12, US-first): FINRA 5220 offers at stated prices / firmness of quotations (a different firmness rule from already-taught Rule 602: a member may not offer to buy or sell any security at a stated price unless prepared to purchase or sell at that price and under the stated conditions; official .01 expects at least a normal unit at the prevailing quotation unless clearly designated as not firm or firm for less than a normal unit; official in-process revised-size clause exists; a “normal unit of trading” for an NMS stock is the official Rule 600(b) round lot, not an invented 100-share unit; Rule 6420 named only) (`microstructure-orders` +0.25h, add-on section E of `examples/p1/05_us_market_mechanics.py`, quiz `mo-5220`; sections A–D, including **3/3 after D / Rule 602**, unchanged); FINRA 5290 no splitting orders or executions for the primary purpose of maximizing a monetary or in-kind amount (credits, commissions, gratuities, payments for or rebates of fees, or any other payments of value; this is not a ban on every TWAP / VWAP slice; quote “this Rule” as written) (`execution-slippage` +0.25h, add-on section H of `examples/p6/12_rule606_toy.py`, quiz `es-5290`; the current 606 table, 4/4, `ASSERT_rule606_ok`, the reminder line, 5250, 5270, 12/12 after 5270, 5230, 15/15 after 5230, 5280, 18/18 after 5280, 10b-10, 22/22 after 10b-10, 5240, and **25/25 after 5240** unchanged); FINRA 2262 control-relationship disclosure before the customer contract (if that first disclosure is not in writing, written disclosure must be given or sent at or before completion; do not invent that the first disclosure must be in writing; not a rewrite of already-taught 10b-10) (`execution-slippage` +0.25h, add-on section I of the same 606 toy, quiz `es-2262`; earlier prints, including **25/25 after 5240** and the new 5290 section, identical once H is added); FINRA 2269 written notification at or before completion of participation or interest in a primary or secondary distribution, in the official broker / adviser-dealer scope (unlike 2262, 2269 requires written notification; do not invent a broader scope; not a flatten into 2262 or 10b-10) (`execution-slippage` +0.25h, add-on section J of the same 606 toy, quiz `es-2269`; earlier prints identical once I is added); Regulation AC § 242.501 research-analyst certification in a report provided to a U.S. person in the United States (official (a)(1) personal-views statement and official (a)(2) compensation prongs as written; official (b) exempts a report prepared by a “third party research analyst” if official (b)(1)–(2) conditions are satisfied, named only; official § 242.500 definitions exist, including “research report,” named only; this is a content requirement in the report itself, not a filing clock or a form; do not rewrite already-taught 28(e) or 5280) (`compliance-ethics` +0.25h, quiz-only `ce-501`; `examples/p2/09_filing_dates_toy.py`, `examples/p2/17_xbrl_pit_10b51_toy.py`, and `examples/p2/11_spinoff_insider_lag_toy.py` were not edited; no tax or self-trade toy was stretched to carry this item); Rule 10b-9 all-or-none / contingency-offering representations (it is a “manipulative or deception device or contrivance,” as used in section 10(b), to make an “all-or-none” or other refund-if-not-sold representation unless the official refund conditions in (a)(1) or (a)(2) are met; official typographical artifact quoted, not silently corrected; official (b) firm-commitment exception, subject only to customary conditions precedent, including “market outs,” named only; do not invent a clock, a form, or a percentage; not a flatten into already-taught Rule 144, Regulation M, or Rule 14e-1) (`backtest-traps` +0.25h, add-on section N of `examples/p2/19_rule144_followon_tender_toy.py`, quiz `bt-10b9`; sections A–M, including **56/56 after M**, unchanged). Item sum **+1.50h**. Hours: **428.75 full / 408.75 skip-P0**; 28 lessons; 383 quiz pairs.
- enrich29 (2026-11-12, US-first): FINRA 2121 fair prices and commissions / the official “5% Policy” (the official “5% Policy” is a guide, not a rule; a mark-up pattern of 5% or even less may be considered unfair or unreasonable; fairness must be based on all the relevant factors, of which the percentage of mark-up is only one; a transaction at a price not reasonably related to the current market price, or an unreasonable commission, is a violation of Rule 2010 and Rule 2121; official Rule 2010 is named only; official .01(d) exclusion for sales at the specific public offering price where a prospectus or offering circular is required to be delivered is named only; do not invent a hard 5% cap; do not build the SM .01(b) relevant-factor catalog or .02 additional debt mark-up policy; not a rewrite of already-taught 10b-10, 2262, 2269, or 5290) (`execution-slippage` +0.25h, add-on section K of `examples/p6/12_rule606_toy.py`, quiz `es-2121`; the current 606 table, 4/4, `ASSERT_rule606_ok`, the reminder line, 5250, 5270, 12/12 after 5270, 5230, 15/15 after 5230, 5280, 18/18 after 5280, 10b-10, 22/22 after 10b-10, 5240, 25/25 after 5240, 5290, **28/28 after H**, 2262, **31/31 after I**, 2269, and **34/34 after J** unchanged); Rule 14d-3 Schedule TO filing and transmittal (a bidder who would beneficially own more than 5 percent of the class after the tender must, as soon as practicable on the date of commencement, file Schedule TO and transmit it as officially provided, including telephonic notice “which telephonic notice shall be made when practicable before the opening of each such exchange,” and the still-printed NASD / NASDAQ clause quoted as written; official (b) promptly any material changes and a final amendment reporting promptly the results, and official (c), named only; not a substitute for already-taught 14d-2; do not invent a clock or zone; do not silently modernize NASD / NASDAQ) (`data-cleaning` +0.25h, add-on section O of `examples/p2/19_rule144_followon_tender_toy.py`, quiz `dc-14d3`; sections A–N, including **56/56 after M** and **60/60 after N**, unchanged); FINRA 5131(e)(3) covered-non-public-company financial tests (any non-public company, except for an unaffiliated charitable organization, satisfying official (i) $1 million income and $15 million shareholders' equity, (ii) $30 million shareholders' equity and a two-year operating history, or (iii) $75 million total assets and total revenue; official (e)(9) defines “unaffiliated charitable organization,” named only; do not invent different dollar amounts; do not flatten this into already-taught 5130 restricted persons; not a rewrite of already-taught spinning, the 5131(d)(4) market-order ban, or flipping / lock-up-waiver) (`backtest-traps` +0.25h, add-on section J of `examples/p2/12_event_time_ipo_toy.py`, quiz `bt-5131cnp`; sections A–I, including **44/44 after I** and the section-I line “this toy packs covered-non-public-company financial tests? False,” unchanged); FINRA 2265 extended hours trading risk disclosure (no member shall permit a customer to engage in extended hours trading unless the member has furnished, individually, in paper or electronic form, a disclosure statement highlighting the risks specific to extended hours trading; official regular trading hours are generally 9:30 a.m. to 4:00 p.m. Eastern Standard Time, quoted as written; official model wording includes “upon the opening the next morning”; official typography includes “on-line” and “Web site”; official (b) substantially similar alternative addressing, at a minimum, the official six risks, and official (c) additional disclosures as necessary, named only; do not invent that the model statement is the only permitted text; not a flatten into already-taught ETH sale-condition T, overnight LULD bands, 23/5 session facts, 6380A, or 5220) (`microstructure-orders` +0.25h, add-on section F of `examples/p1/13_sale_condition_toy.py`, quiz `mo-2265`; sections A–E, including ETH sale-condition T, **18/18 after D**, 6380A, and **25/25 after E**, unchanged); Rule 13e-1 issuer purchases of its equity during a commenced 14(d)(1) third-party tender (the issuer must not purchase any of its equity securities during the tender offer unless it first files a statement containing official (a)(1)–(7) information, pays the fee required by § 240.0-11, and submits the official (a)(7) exhibit; official core text requires “a statement,” not a named form; do not invent a form number or flatten this into Schedule 13E-3 or Rule 13e-3; cite § 240.13e-1; official (d) ordinary-course employee-benefit-plan exception; official (a)(7) / (b) / (c) named only; not a flatten into already-taught 14e-5 or 14d-2) (`data-cleaning` +0.25h, add-on section P of the same tender toy after the 14d-3 add-on, quiz `dc-13e1`; earlier prints, including **60/60 after N** and the new 14d-3 section, identical once O is added); FINRA 2266 written SIPC information (members, with official (a)–(b) exceptions, shall advise all new customers, in writing, at the opening of an account, that they may obtain information about SIPC, including the SIPC brochure, by contacting SIPC, and shall provide the Web site address and telephone number of SIPC; the same written information must be provided at least once each year; introducing/clearing firms may assign these requirements to one of the firms; official typography is “Web site” as two words; official (a)–(b) exceptions named only; do not rewrite already-taught SIPC coverage limits, and do not invent a coverage amount, form, or clock this rule does not state) (`microstructure-orders` +0.25h, add-on section G of `examples/p1/11_freeride_txse_15c33_toy.py`, quiz `mo-2266`; sections A–F, including the 15c3-3 line “this is separate from SIPC,” **14/14 after E**, 15c6-1 / 11320, and **19/19 after F**, unchanged). Item sum **+1.50h**. Hours: **430.25 full / 410.25 skip-P0**; 28 lessons; 389 quiz pairs.
- enrich30 (2026-11-12, US-first): FINRA 2122 charges for services performed (charges, if any, for services performed, including miscellaneous services such as collection of monies, exchange or transfer, appraisals, and safe-keeping or custody, “shall be reasonable and not unfairly discriminatory among customers”; quote official “monies” and “safe-keeping”; do not invent a hard 5% cap; do not flatten into packed 2121; not a rewrite of already-taught 10b-10 / 2262 / 2269 / 5290 / 2121) (`execution-slippage` +0.25h, add-on section L of `examples/p6/12_rule606_toy.py`, quiz `es-2122`; the current 606 table, 4/4, `ASSERT_rule606_ok`, the reminder line, 5250, 5270, 5230, 5280, 10b-10, 5240, 5290, 2262, 2269, 2121, and **37/37 after K** unchanged); FINRA 2264 margin disclosure statement (a member may not open a Regulation T margin account for a non-institutional customer unless, prior to or at the time of opening the account, it has furnished the official margin disclosure statement individually, in paper or electronic form, in a separate document (or on a separate page); official typography is “Web site” and official model text includes “short fall” as two words; official (b) not less than once a calendar year; official (c) substantially similar alternative exists; official (d) defines “non-institutional customer” by Rule 4512(c), named only; do not build the prescribed-statement catalog or a 4512 engine; do not flatten into Rule 10b-16 or already-taught Reg T, or flatten the clock into packed 2266 / 2267) (`microstructure-orders` +0.25h, add-on section H of `examples/p1/11_freeride_txse_15c33_toy.py`, quiz `mo-2264`; sections A–G, including the 15c3-3 line “this is separate from SIPC,” **14/14 after E**, 15c6-1 / 11320, **19/19 after F**, 2266, and **22/22 after G**, unchanged); FINRA 5330 adjustment of orders (a member holding an open order shall, prior to executing or permitting the order to be executed, adjust the price and/or number of shares on the day the security is quoted ex-dividend, ex-rights, ex-distribution, or ex-interest, except where a cash dividend or distribution is less than one cent ($0.01); official markings “Do Not Reduce” / “Do Not Increase” (straight quotation marks); official (b) reverse-split cancellation; official (d) definition of “open order,” including “good 'til cancelled” and “stop limit”; official (e) exceptions include open stop orders to buy, open sell orders, and “SEA Rule 10b-17”; do not invent that every open order is adjusted; do not build the rounding-formula catalog; not a rewrite of already-taught Rule 10b-17 or sections A–C of the stop-order toy) (`microstructure-orders` +0.25h, add-on section D of `examples/p1/12_stop_order_toy.py`, quiz `mo-5330`; sections A–C, including **5/5** and the staff-bulletin disclaimer, unchanged as a strict prefix); Rule 10b-16 disclosure of credit terms in margin transactions (a broker or dealer that extends credit in connection with a securities transaction must have procedures assuring a written statement or statements at the time of opening the account, written statements at least quarterly, and generally not less than thirty (30) days written notice of changes, except that no such prior notice is necessary where changes are required by law; if a change results in a lower interest charge, notice may be given within a reasonable time after the effective date; official (a)(1) telephone proviso named only; official typographic quotation marks around “equity funding programs”; cite § 240.10b-16; do not invent a form number; do not build the (a)(1)(i)–(vii) catalog; do not flatten into 2264 or already-taught Reg T) (`portfolio-risk-sizing` +0.25h, add-on section F of `examples/p6/11_margin_call_toy.py`, quiz `prs-10b16`; sections A–E, including `ASSERT_short_margin_ok` and the section-E disclaimer, unchanged); FINRA 2267 Investor Education and Protection (once every calendar year, a member must provide in writing, which may be electronic, the FINRA BrokerCheck Hotline Number, the FINRA Web site address, and a statement as to the availability of an investor brochure describing FINRA BrokerCheck; official typography is “Web site” as two words; official (b) exceptions exist, including a limited introducing-firm alternative at or prior to the customer's initial purchase, and a carrying-firm / no-customers exemption, named only; do not invent that the general 2267 duty is an account-opening disclosure; do not flatten the clock into packed 2266; do not invent a hotline number or a Web site address from page chrome; not a rewrite of packed 2266 or already-taught SIPC coverage limits) (`microstructure-orders` +0.25h, add-on section I of the same freeride toy after the 2264 add-on, quiz `mo-2267`; earlier prints, including **22/22 after G / 2266** and the new 2264 section, identical once 2264 is added); FINRA 2124 net transactions with customers (prior to executing a transaction for or with a customer on a “net” basis, a member must provide disclosure and obtain consent; official (b): non-institutional customers — written consent on an order-by-order basis; official (e)(2) defines a “net” transaction; official typography includes “e.g. an investment adviser” with no comma after “e.g.”; official (c) institutional methods and official (d) fiduciary consent exist, named only; do not flatten into packed 2121 / 2122 or already-taught Rule 10b-10) (`execution-slippage` +0.25h, add-on section M of the 606 toy after 2122, quiz `es-2124`; earlier prints, including **37/37 after K / 2121** and the new 2122 section, identical once 2122 is added). Item sum **+1.50h**. Hours: **431.75 full / 411.75 skip-P0**; 28 lessons; 395 quiz pairs.
- enrich31 (2026-11-12, US-first): FINRA 2261 disclosure of financial condition (a member shall make its most recent balance sheet available to inspection by any bona fide regular customer upon request, or may deliver it in paper or electronic form; electronic delivery requires the customer's consent; official typography is “bona fide regular customer” and “most recent balance sheet”; official (b) member-to-member written-request delivery and official (c) definition of "customer" for paragraph (a) are named only; no invented periodic clock, form number, or coverage amount; not a flatten into already-taught 15c3-3 or SIPC, or into packed 2266 / 2267) (`microstructure-orders` +0.25h, add-on section J of `examples/p1/11_freeride_txse_15c33_toy.py`, quiz `mo-2261`; sections A–I, including the 15c3-3 line “this is separate from SIPC,” **14/14 after E**, 15c6-1 / 11320, **19/19 after F**, 2266, **22/22 after G**, 2264, 2267, and **28/28 after I**, unchanged); FINRA 2231 customer account statements (each general securities member shall, with a frequency of not less than once every calendar quarter, send a statement of account ("account statement"); official (a) also requires an advisory to report promptly any inaccuracy or discrepancy, a both-firms reference when introducing and carrying firms both service the account, and that any oral communications should be “re-confirmed” in writing, including rights under SIPA; official (b) DVP/RVP exceptions exist (official typography “SEA Rule 17a-4”); official closing sentence of (b) names “SEA Rule 15c3-3(j)(1)” only as a foil; official (c) DPP / unlisted REIT catalog and official (d)(2) exemption exist, named only; official SM .02(a)(2) wording is “accounts statements”; do not flatten this quarterly clock into packed 10b-16 or into 15c3-3(j)(1), and do not rewrite already-taught 15c3-3 possession-or-control / reserve teaching) (`microstructure-orders` +0.25h, add-on section K of the same freeride toy after 2261, quiz `mo-2231`; earlier prints, including **28/28 after I / 2267** and the new 2261 section, identical once 2261 is added); 17 CFR 242.607 written PFOF and routing-policy information upon opening a new account and on an annual basis thereafter (official (a)(1) payment-for-order-flow policies and official (a)(2) routing policies, including a description of the extent to which orders can be executed at prices superior to the national best bid and national best offer; cite § 242.607; official typography includes “broker's or dealer's”; official (b) Commission exemptions named only; do not silently replace the official phrase with “NBBO” inside a quoted sentence; not a flatten into already-taught Rule 606 or Rule 10b-10, or into packed 2121 / 2122 / 2124 or 2266 / 2267 / 2231 clocks) (`execution-slippage` +0.25h, add-on section N of `examples/p6/12_rule606_toy.py`, quiz `es-607`; the current 606 table, 4/4, `ASSERT_rule606_ok`, the reminder line, 5250, 5270, 5230, 5280, 10b-10, 5240, 5290, 2262, 2269, 2121, **37/37 after K**, 2122, 2124, and **43/43 after M** unchanged); FINRA 2150 Improper Use of Customers' Securities or Funds (no improper use of a customer's securities or funds; no guarantee against loss in connection with any securities transaction or in any securities account of such customer; official (c) written-authorization and direct-proportion sharing conditions, with official family and Advisers Act Rule 205-3 alternatives, named only; official SM .01 issuer guarantees generally not subject to the prohibition; official SM .02 a member, but not an associated person, may reimburse a customer for transaction losses after the fact (subject to applicable reporting) and may correct a bona fide error; official SM .03 preserve the required written authorization(s) for at least six years after the date the account is closed; do not invent that a member may never reimburse a loss; not a flatten into already-taught 15c3-3 or SIPC, or into packed 2261) (`compliance-ethics` +0.25h, add-on section D of `examples/p7/08_self_trade_pattern_toy.py` after the current last line, quiz `ce-2150`; sections A–C, including **7/7**, `ASSERT_self_trade_pattern_ok`, and the disclaimer, unchanged as a strict byte-prefix); FINRA 2090 Know Your Customer (every member shall use reasonable diligence, in regard to the opening and maintenance of every account, to know (and retain) the essential facts concerning every customer and concerning the authority of each person acting on behalf of such customer; official SM .01 four categories, with official quotation marks around "essential" / "knowing the customer"; this is a diligence-and-facts duty, not an account-opening disclosure clock; not a flatten into FINRA 2111 or Regulation Best Interest / Form CRS, or into packed 2264 / 2266 / 2267 / 2261 / 2231) (`microstructure-orders` +0.25h, add-on section L of the same freeride toy after 2261 and 2231, quiz `mo-2090`; earlier prints, including **28/28 after I / 2267** and the new 2261 / 2231 sections, identical once those are added); FINRA 3220 Influencing or Rewarding Employees of Others (current official gift limit is $300 per individual per year, SR-FINRA-2025-003 eff. Mar. 30, 2026, already effective; official (a): anything of value, including gratuities, in excess of $300 per individual per year, where the payment or gratuity is in relation to the business of the employer of the recipient; a gift of any kind is considered a gratuity; official SM .09 does not apply to gifts from a member to its own associated persons, or to gifts from a member or an associated person to individual retail customers; official (b)–(d) and SM .01–.08 named only; do not teach the pre-amendment $100 cap as current law; do not invent that the $300 limit applies to gifts to individual retail customers; supporting Notice 26-05 says “per person per year” — quote the official rule wording; not a flatten into already-taught FINRA 5230 or 5250) (`compliance-ethics` +0.25h, add-on section E of the same self-trade toy after 2150, quiz `ce-3220`; A–C, including **7/7**, `ASSERT_self_trade_pattern_ok`, the disclaimer, and the new 2150 section, identical once 2150 is added). Item sum **+1.50h**. Hours: **433.25 full / 413.25 skip-P0**; 28 lessons; 401 quiz pairs.
- enrich32 (2026-11-12, US-first): FINRA 4370 written business continuity plan and customer disclosure (each member must create and maintain a written business continuity plan identifying procedures relating to an emergency or significant business disruption, reasonably designed to enable the member to meet its existing obligations to customers; official (e) written disclosure at account opening, posted on the member's **Web site** (if the member maintains a Web site), and mailed to customers upon request; official typography is “Web site” as two words; official (c) ten-element catalog, official (b) annual review, official (d) senior-management / registered-principal approval, and official (f) emergency-contact reporting named only; do not invent that a member without a Web site must still post the disclosure on a website; not a flatten into already-taught 15c3-3 or SIPC, or into packed 2261 / 2266 / 2267 / 2231 / 2090) (`microstructure-orders` +0.25h, add-on section M of `examples/p1/11_freeride_txse_15c33_toy.py`, quiz `mo-4370`; earlier prints, including **37/37 after L / 2090**, unchanged); FINRA 4340 callable-securities fair-and-impartial allocation (a member that has in its possession or under its control any security which, by its terms, may be called or redeemed prior to maturity shall establish and make available on the member's **website** fair-and-impartial allocation procedures, and shall provide written notice (which may be electronic) to new customers at the opening of an account, and all customers at least once every calendar year; official typography is one-word lowercase “website”; official (b) favorable redemptions and official (c) unfavorable redemptions named; official SM .02 may name an impartial lottery system / pro-rata / such other means as will achieve a fair and impartial allocation, named only; official SM .01 / .03 named only; do not invent that every common stock is callable; not a flatten into already-taught 15c3-3 “possession or control,” or into FINRA 2232(b)(2)) (`microstructure-orders` +0.25h, add-on section N of the same freeride toy after 4370, quiz `mo-4340`; earlier prints, including **37/37 after L / 2090** and the new 4370 section, identical once 4370 is added); 17 CFR 240.10b-5 Employment of manipulative and deceptive devices (it shall be unlawful for any person, directly or indirectly, by the use of any means or instrumentality of interstate commerce, or of the mails or of any facility of any national securities exchange, (a) / (b) / (c), in connection with the purchase or sale of any security; official typography is “in the light of the circumstances under which they were made”; the closing “in connection with the purchase or sale of any security” applies to (a), (b), and (c); cite § 240.10b-5; title 17 up_to_date_as_of 2026-11-09; do not pack Rule 10b5-2, and do not build a scienter, materiality, or judicial-opinion catalog; not a flatten into already-taught 10b-18, 10b5-1, 14e-3, 10b-9, or 15 U.S.C. 78i / FINRA 5210) (`compliance-ethics` +0.25h, add-on section F of `examples/p7/08_self_trade_pattern_toy.py` after the current last disclaimer line, quiz `ce-10b5`; **7/7**, `ASSERT_self_trade_pattern_ok`, the first disclaimer, 2150 including `ASSERT_2150_ok`, and 3220 including **13/13**, `ASSERT_3220_ok`, and the last disclaimer, identical as a strict byte-prefix); FINRA 2010 commercial honor (a member, in the conduct of its business, shall observe high standards of commercial honor and just and equitable principles of trade; official caption typography is “STANDARDS OF COMMERCIAL HONOR AND PRINCIPLES OF TRADE”; official Cross References exist, including already-taught 2121, 5130, 5210, 5220, 5270, and 5320, and named-only 2111, named only; do not rewrite the already-shipped 2121 or 5270 SM .05 foil sentences; not a substitute for packed 10b-5 or packed 2150 / 3220) (`compliance-ethics` +0.25h, add-on section G of the same self-trade toy after 10b-5, quiz `ce-2010`; the new 10b-5 section identical once 10b-5 is added); FINRA 2165 Specified Adult temporary-hold safe harbor (a member **may** place a temporary hold on a disbursement of funds or securities from the Account of a Specified Adult, or a transaction in securities in that Account, if the member reasonably believes that financial exploitation of the Specified Adult has occurred, is occurring, has been attempted, or will be attempted; official “Specified Adult” means a natural person age 65 and older, or a natural person age 18 and older who the member reasonably believes has a qualifying mental or physical impairment; official typography uses typographic quotes around “Specified Adult,” “Account,” “Trusted Contact Person,” and “financial exploitation”; official SM .01 is a safe harbor from FINRA Rules 2010, 2150 and 11870 (no Oxford comma) and “This Rule does not require members to place temporary holds”; official (b)(2) expires not later than 15 business days; official (b)(3) / (b)(4) “no longer than 10 business days” and then “no longer than 30 business days” extension slices named only; official (b)(1)(B) notification not later than two business days, orally or in writing, which may be electronic; official (a)(3) “Trusted Contact Person” in accordance with Rule 4512, named only; amended by SR-FINRA-2021-016 eff. March 17, 2022, already effective; do not teach a pre-2022 disbursement-only version as current law; the hold is permissive, not a duty to freeze; not a flatten into packed 2010 or 2150, or already-taught 15c3-3 / SIPC, or dropped ACATS / Rule 11870) (`compliance-ethics` +0.25h, add-on section H of the same self-trade toy after 2010, quiz `ce-2165`; F–G identical once those are added); FINRA 3310 written anti-money laundering program (each member shall develop and implement a written anti-money laundering program reasonably designed to achieve and monitor the member's compliance with the Bank Secrecy Act (31 U.S.C. 5311, et seq.) and the Treasury implementing regulations; the program must be approved, in writing, by a member of senior management; official typography is hyphenated “anti-money laundering” and official (d) “e-mail address”; official (a)–(f) minimum elements exist, including official (c) annual (on a calendar-year basis) independent testing, or every two years if the member does not execute transactions for customers or otherwise hold customer accounts or act as an introducing broker, official (d) designation of an associated person to FINRA, official (e) ongoing training, and official (f) risk-based ongoing customer due diligence, named only; official example typography is “e.g., engages solely in proprietary trading or conducts business only with other broker-dealers”; official Selected Notices typography includes “17-40 18-19” with no comma between those two numbers if quoted; do not build a CIP, SAR, beneficial-owner, or 31 CFR 1010.230 engine; not a flatten into packed 2090, Regulation Best Interest, or Form CRS; learning-only BSA/AML literacy, not a how-to for evading reporting) (`compliance-ethics` +0.25h, add-on section I of the same self-trade toy after 2165, quiz `ce-3310`; F–H identical once those are added). Item sum **+1.50h**. Hours: **434.75 full / 414.75 skip-P0**; 28 lessons; 407 quiz pairs.
- enrich33 (2026-11-12, US-first): FINRA 2140 no interference with a customer's account-transfer request (no member or person associated with a member shall interfere with a customer's request to transfer his or her account in connection with the change in employment of the customer's registered representative where the account is not subject to any lien for monies owed by the customer or other bona fide claim; quote “Nothing in this Rule shall affect the operation of Rule 11870” with a normal single space; official caption typography is “Interfering With the Transfer of Customer Accounts in the Context of Employment Disputes”; official typography is “his or her account,” “includes, but is not limited to,” and “written request from a customer to transfer his or her account”; name Rule 11870 only; do not recast 2140 as a street-name / ACATS primer, and do not invent a 11870 engine; do not invent that every account transfer is covered; not a flatten into packed 2165, packed 4370 / 4340 / 2090 / 2231, or already-taught 15c3-3 / SIPC) (`microstructure-orders` +0.25h, add-on section O of `examples/p1/11_freeride_txse_15c33_toy.py` after the last line, quiz `mo-2140`; earlier prints, including **43/43 after N / 4340**, unchanged); FINRA 2060 fiduciary-capacity ownership information (a member who received ownership information as paying agent, transfer agent, trustee, or in a similar capacity shall under no circumstances make use of such information for the purpose of soliciting purchases, sales or exchanges except at the request and on behalf of the issuer; official typography is “purchases, sales or exchanges” with no Oxford comma, and “Cross Reference–” with an en-dash, not a hyphen; official caption typography is “Use of Information Obtained in Fiduciary Capacity”; official Cross Reference is packed FINRA 2150, named only; do not drop the official “except at the request and on behalf of the issuer” clause; not a flatten into packed 2150, packed 10b-5, packed 2010, or packed 3310, and the already-shipped 2150 box is not rewritten) (`compliance-ethics` +0.25h, add-on section J of `examples/p7/08_self_trade_pattern_toy.py` after the current last 3310 disclaimer line, quiz `ce-2060`; **7/7**, `ASSERT_self_trade_pattern_ok`, the first disclaimer, 2150, 3220, 10b-5, 2010, 2165, and 3310 including **25/25**, `ASSERT_3310_ok`, and the last disclaimer, identical as a strict byte-prefix); FINRA 3210 prior written consent for associated-person accounts at other firms (current post-amendment text, already amended by SR-FINRA-2026-013 eff. June 17, 2026; official caption typography is “Accounts At Other Broker-Dealers and Financial Institutions”; official typography uses straight quotes around "employer member" and "executing member"; official (a) prior written consent; official (b) written notification to the executing member or other financial institution; official SM .01 “within 30 calendar days”; official (c) and official SM .02 / .03 / .04 / .05 named only; do not build the SM .02 family-presumption or SM .03 product-carve-out catalogs; do not teach a pre-June 17, 2026 version as current law; not a flatten into packed 2090, packed 2165 / 4512, or later-packed 3280) (`compliance-ethics` +0.25h, add-on section K of the same self-trade toy after 2060, quiz `ce-3210`; the new 2060 section identical once 2060 is added); FINRA 3270 outside business activities (no registered person may have an outside business activity unless he or she has provided prior written notice; official typography is “officer, director or partner” with no Oxford comma; official exemption: “Passive investments and activities subject to the requirements of Rule 3280 shall be exempted from this requirement”; official caption typography is “Outside Business Activities of Registered Persons”; official SM .01 and “SEA Rule 17a-4(e)(1)” named only; do not invent that passive investments require prior written notice under 3270; not a flatten into 3280, or into packed 2231’s 17a-4 foil) (`compliance-ethics` +0.25h, add-on section L of the same self-trade toy after 3210, quiz `ce-3270`; J–K identical once those are added); FINRA 3280 private securities transactions (no associated person shall participate in any manner in a private securities transaction except in accordance with this Rule; official (b) prior written notice, typography “provided however that” with no comma after “provided” in official (b) and official (e)(1); official caption typography is “Private Securities Transactions of an Associated Person”; official (c) / (d) named only; official (e)(1) exclusions include transactions subject to the notification requirements of Rule 3210, transactions among immediate family members as defined in FINRA Rule 5130 for which no associated person receives any selling compensation, and personal transactions in investment company and variable annuity securities, named only; not a flatten into packed 3210 or already-taught 5130; learning-only associated-person literacy, not a how-to for selling away) (`compliance-ethics` +0.25h, add-on section M of the same self-trade toy after 3270, quiz `ce-3280`; J–L identical once those are added); 17 CFR 240.14a-9 false or misleading statements (no solicitation subject to this regulation shall be made by means of any proxy statement, form of proxy, notice of meeting or other communication, written or oral, containing any statement which, at the time and in the light of the circumstances under which it is made, is false or misleading with respect to any material fact, or which omits to state any material fact necessary in order to make the statements therein not false or misleading; official typography is “in the light of the circumstances under which it is made,” singular “it is made”; do not tidy that into packed 10b-5’s “under which they were made”; official caption is “False or misleading statements”; official (a) is “notice of meeting or other communication, written or oral”; cite 17 CFR 240.14a-9; title 17 up_to_date_as_of 2026-11-09; official (b), official (c), and the Note named only; not a flatten into already-taught Rule 14a-8 or Form 8-K Item 5.07) (`data-cleaning` +0.25h, add-on section F of `examples/p2/16_index_add_earnings_time_toy.py` after the current last Item 5.07 disclaimer line, quiz `dc-14a9`; sections A–E, including **13/13 after C**, **18/18 after D**, the existing line “do not flatten Item 5.07 or other special clocks into the same trigger,” and **22/22 after E** plus the last disclaimer, identical). Item sum **+1.50h**. Hours: **436.25 full / 416.25 skip-P0**; 28 lessons; 413 quiz pairs.
- enrich34 (2026-11-12, US-first): 17 CFR 240.15c6-2 same-day allocation, confirmation, and affirmation (official caption typography is “Same-day allocation, confirmation, and affirmation,” Oxford comma; official typography is “as soon as technologically practicable and no later than the end of the day on trade date,” with no “the” before “trade date”; official (a) is a written-agreement or written-policies disjunction for a transaction subject to § 240.15c6-1(a); cite 17 CFR 240.15c6-2; title 17 up_to_date_as_of 2026-11-09; official (b) named only; do not flatten into already-taught 15c6-1 / T+1 / FINRA 11320, and do not invent that settlement itself is T+0) (`microstructure-orders` +0.25h, add-on section P of `examples/p1/11_freeride_txse_15c33_toy.py` after the last line, quiz `mo-15c62`; earlier prints, including **46/46 after O / 2140**, unchanged); FINRA 4330(a) written authorization before lending a customer's margin securities (official caption typography is “Customer Protection — Permissible Use of Customers' Securities,” em dash U+2014; official (a) requires written authorization first; official SM .02 permits a single customer account agreement/margin agreement/loan consent with clear and prominent disclosure in lieu of a separate writing, named; official (b) including “SEA Rule 15c3-3” and official SM .01 / .03–.06 named only; do not invent that a separate writing is always required; not a flatten into already-taught 15c3-3 or SIPC, or into packed 2264) (`microstructure-orders` +0.25h, add-on section Q of the same freeride toy after P, quiz `mo-4330`; P identical once 15c6-2 is added); FINRA 2232(b)(1) NMS settlement-date confirmation disclosure (official caption typography is “Customer Confirmations.”; official typography is “shall further disclose” and “SEA Rule 10b-10,” with no space before the comma after “FINRA Rule 6420”; packed slice is official (b)(1) only; official (a), official (b)(2), and official (c)–(f) named only; do not pack official (a) as the teaching core; do not flatten official (b)(1) into already-taught T+1 / 15c6-1 or into packed 15c6-2; the packed 4340 foil is updated so it no longer says 2232 is unpacked, while remaining not a flatten into official 2232(b)(2)) (`execution-slippage` +0.25h, add-on section O of `examples/p6/12_rule606_toy.py` after the last line, quiz `es-2232`; **46/46 after N / 607** unchanged); FINRA 4513 written customer-complaint records (official caption typography is “Records of Written Customer Complaints.”; official typography is “office of supervisory jurisdiction” and “Customer complaint records shall be preserved for a period of at least four years”; official (b) "customer complaint" named only; records may be made promptly available at the OSJ upon request of FINRA; adopted by SR-FINRA-2010-052 eff. Dec. 5, 2011; Selected Notice: 11-19; not a flatten into packed 2231, packed 2165, packed 3270's 17a-4 foil, or already-named 4511 / 4512) (`compliance-ethics` +0.25h, add-on section N of `examples/p7/08_self_trade_pattern_toy.py` after the last 3280 disclaimer, quiz `ce-4513`; **37/37**, `ASSERT_3280_ok`, and the last 3280 disclaimer identical as a strict byte-prefix); 17 CFR 240.12b-20 additional material information (official caption is “Additional information.”; official typography is “in the light of the circumstances under which they are made not misleading,” with no comma after “made”; do not tidy that into packed 10b-5’s “they were made” or packed 14a-9’s “it is made”; cite 17 CFR 240.12b-20; title 17 up_to_date_as_of 2026-11-09; not a flatten into packed 14a-9, packed 10b-5, already-taught Regulation FD, Form 8-K Item 5.07, or 14a-8) (`data-cleaning` +0.25h, add-on section G of `examples/p2/16_index_add_earnings_time_toy.py` after the last 14a-9 disclaimer, quiz `dc-12b20`; **25/25 after F** plus the last 14a-9 disclaimer identical); 17 CFR 248.30(a)(1)/(a)(2) written administrative, technical, and physical safeguards (Oxford comma; every covered institution must develop, implement, and maintain written policies and procedures that address those safeguards, reasonably designed to ensure the security and confidentiality of customer information, protect against any anticipated threats or hazards to the security or integrity of customer information, and protect against unauthorized access to or use of customer information that could result in substantial harm or inconvenience to any customer; cite 17 CFR 248.30; title 17 up_to_date_as_of 2026-11-09; official (a)(3)–(a)(5), official (b), official (c), and official (d) including “Covered institution” named only; do not invent that the packed slice is the 30-day notice rule; not a flatten into packed 3310, and § 248.10 remains unpacked) (`compliance-ethics` +0.25h, add-on section O of the same self-trade toy after 4513, quiz `ce-24830`; N identical once 4513 is added). Item sum **+1.50h**. Hours: **437.75 full / 417.75 skip-P0**; 28 lessons; 419 quiz pairs.
- enrich35 (2026-11-12, US-first): FINRA 3150 holding of customer mail (official caption typography is “Holding of Customer Mail.”; official typography is “his or her usual address” and one-word lowercase “website”; official (a) is permissive “may hold mail,” not a duty to hold mail; longer than three consecutive months needs an acceptable reason, e.g., safety or security concerns; “Convenience is not an acceptable reason for holding mail longer than three months.”; official (b) names packed Rule 2266; official (c) named only; adopted by SR-FINRA-2013-025 eff. Dec. 1, 2014; Selected Notice: 14-10; do not tidy 3150’s “website” into packed 4370 / 2264 “Web site,” and do not flatten 3150 into packed 2266) (`microstructure-orders` +0.25h, add-on section R of `examples/p1/11_freeride_txse_15c33_toy.py` after the last line, quiz `mo-3150`; **52/52 after Q / 4330** unchanged); FINRA 4514 authorization records for negotiable instruments drawn from a customer's account (official `<h1>` typography uses a straight apostrophe U+0027 in “Customer's”; official typography is “check, draft or other form” and “checking, savings, share or similar account,” no Oxford comma, and “three years following the date the authorization expires”; “This provision shall not, however, require members to preserve copies of negotiable instruments signed by customers.”; adopted by SR-FINRA-2010-052 eff. Dec. 5, 2011; Selected Notice: 11-19; do not invent that signed instruments must be preserved, and do not flatten into packed 2150, packed 4330(a), packed 4513, or already-named 4511 / 4512) (`compliance-ethics` +0.25h, add-on section P of `examples/p7/08_self_trade_pattern_toy.py` after the last 248.30 disclaimer, quiz `ce-4514`; **43/43**, `ASSERT_24830_ok`, and the last 248.30 disclaimer identical as a strict byte-prefix); FINRA 1122 filing of misleading information as to membership or registration (official typography is “which is incomplete or inaccurate so as to be misleading”; official core is one sentence; official text is “after notice thereof,” not a numbered clock; amended by SR-FINRA-2009-009 eff. Aug. 17, 2009; Selected Notice: 09-33; do not flatten into packed 10b-5 / 2010 / 3210 / 3280) (`compliance-ethics` +0.25h, add-on section Q of the same self-trade toy after P, quiz `ce-1122`; P identical once 4514 is added); FINRA 8210(a)/(c) provision of information and testimony (official caption typography is “Provision of Information and Testimony and Inspection and Copying of Books.”; packed slice is official (a) and official (c) only; official typography is “investigation, complaint, examination, or proceeding,” “orally, in writing, or electronically,” official (a)(2) “books, records, and accounts” and “possession, custody or control,” and official (c) “books, records, or accounts”; official amendment typography is “Feb 25, 2013”; official (b) and official (d)–(g), including Rule 9134(a)(1), named only; literacy only, not an investigation-procedure how-to) (`compliance-ethics` +0.25h, add-on section R of the same self-trade toy after Q, quiz `ce-8210`; Q identical once 1122 is added); 17 CFR 240.13a-14(a)/(c) certification of disclosure in annual and quarterly reports (official caption typography is “Certification of disclosure in annual and quarterly reports.”; official typography is “Form 10-Q, Form 10-K, Form 20-F or Form 40-F,” no Oxford comma; official (c) bars a power of attorney or other form of confirming authority; cite 17 CFR 240.13a-14; title 17 up_to_date_as_of 2026-11-09; official (b) 18 U.S.C. 1350 furnished certifications, official (d)/(e) ABS, official (f) Interactive Data File, § 240.13a-15 / § 240.15d-15, and 17 CFR 240.15d-14 named only; do not pack official (b) or 15d-14 as the teaching core, and do not flatten into already-taught 10-K / 10-Q clocks, packed 12b-20, or Form 8-K Item 4.02) (`data-cleaning` +0.25h, add-on section H of `examples/p2/16_index_add_earnings_time_toy.py` after the last 12b-20 disclaimer, quiz `dc-13a14`; **28/28 after G** plus the last 12b-20 disclaimer identical); 17 CFR 240.10D-1(b)(1) opening written recovery policy for erroneously awarded compensation (official caption typography is “Listing standards relating to recovery of erroneously awarded compensation.”; official typography is “recover reasonably promptly”; packed slice is official (b)(1)’s opening sentence only; official (a) 2023 transition machinery, official (b)(1)(i)–(v) including “An issuer's obligation to recover erroneously awarded compensation is not dependent on if or when the restated financial statements are filed,” official (c) exemptions, and official (d) definitions named only; official (b)(1)(iv)(C) typography is “the requirements of26 U.S.C. 401(a)(13)” with no space after “of”; do not invent a numeric clock for “reasonably promptly,” and do not flatten into already-taught Form 8-K Item 4.02, packed 12b-20, packed 13a-14, or already-taught 10-K / 10-Q clocks; cite 17 CFR 240.10D-1; title 17 up_to_date_as_of 2026-11-09) (`data-cleaning` +0.25h, add-on section I of the same index-add toy after H, quiz `dc-10d1`; H identical once 13a-14 is added). Item sum **+1.50h**. Hours: **439.25 full / 419.25 skip-P0**; 28 lessons; 425 quiz pairs.
- enrich36 (2026-11-12, US-first): FINRA 2251 official (a) opening + official (b) processing and forwarding of proxy and other issuer-related materials (official typography is “process and forward promptly” and a straight apostrophe in “beneficial owner's”; official (a)(1) equity list has no Oxford comma before “and other material”; official (a)(2) debt duty is only “make reasonable efforts to process and forward,” and official typography is “prepared by or on behalf of, the issuer” with the comma after “of”; official (c) later uses “process and transmit promptly”; official (c)–(g), including the reimbursement-rate catalog, named only; 17 CFR 240.14b-1 named only; do not pack 14b-1, tidy official 14b-1 “by indicting” / “addresses,and,” recast equity and debt duties as the same standard, or recast 2251 as a street-name or ACATS primer) (`microstructure-orders` +0.25h, add-on section S of `examples/p1/11_freeride_txse_15c33_toy.py` after the last line, quiz `mo-2251`; **55/55 after R / 3150** unchanged); FINRA 2232(b)(2) callable-equity confirmation disclosure (official (b) chapeau “shall further disclose”; official (b)(2)(A) the security is a callable equity security; and official (b)(2)(B) a customer may contact the member for more information concerning the security; official (a) named only, not packed as a 10b-10 flatten; official (c)–(f) named only; do not invent that every common stock is callable, or invent an effective date for SR-FINRA-2019-008; the packed 4340 foil is updated so official 2232(b)(1) and official 2232(b)(2) are packed in the execution lesson, while remaining not a flatten into those confirmation disclosures) (`execution-slippage` +0.25h, add-on section P of `examples/p6/12_rule606_toy.py` after the last line, quiz `es-2232b2`; **49/49 after O / 2232(b)(1)** unchanged; the already-printed O foil that official (b)(2) “exists and is named only” is updated only in the new add-on); FINRA 2273 recruited-person educational communication (quote both official clock phrasings and do not merge them: “not later than three business days after the contact” and “within three business days from such oral contact” … “whichever is earlier”; official (b)(3) three-month window; official SM header typography is exactly `• • • Supplementary Material:---------------` (U+2022, ordinary U+0020 spaces, no NBSP, 15 ASCII hyphens immediately after the colon); official SM .01 typographic quotes around “former customer”; SM .01 / .02 named only; do not flatten packed/named 4512 or packed 2140 / already-named 11870) (`compliance-ethics` +0.25h, add-on section S of `examples/p7/08_self_trade_pattern_toy.py` after the last line, quiz `ce-2273`; **52/52** + `ASSERT_8210_ok` + closing disclaimer unchanged); FINRA 2040(a) payments to unregistered persons (official (a) heading is “General” (no period); official chapeau has no Oxford comma before “commissions or other allowances”; do not quote a run-on “GeneralNo member”; official (a)(2) has a comma after “federal securities laws” and no Oxford comma before “and SEA rules and regulations”; official (b)/(c) named only) (`compliance-ethics` +0.25h, add-on section T of the same self-trade toy after S, quiz `ce-2040`); 17 CFR 240.10b5-2 duty of trust or confidence in misappropriation insider trading cases (official typography uses typographic quotes around “misappropriation,” and official (b) heading typography is “Enumerated “duties of trust or confidence.”” with the period inside the closing quote; official typography is “material nonpublic information,” “history, pattern, or practice,” “spouse, parent, child, or sibling,” “provided, however,” and a straight apostrophe in “parties'”; pack the official introductory non-exclusive-definition sentence plus official (b); official (a) and the official (b)(3) proviso named only; do not invent that this section is a complete insider-trading code, and do not flatten into packed 10b-5, already-taught 10b5-1, 14e-3, or 15 U.S.C. 78i / FINRA 5210; title 17 up_to_date_as_of 2026-11-09) (`compliance-ethics` +0.25h, add-on section U of the same self-trade toy after T, quiz `ce-10b52`); 17 CFR 244.100(a) Regulation G non-GAAP financial measure presentation and reconciliation (official (a)(1) typography is “Generally Accepted Accounting Principles (GAAP)” with initial capitals; official (c)(2) later uses lowercase “generally accepted accounting principles in the United States”; official (b) typography is “in light of the circumstances under which it is presented, not misleading”; official Note 1 typography is “by Web cast” and cites “paragraphs (a)(1)(i) and (a)(1)(ii)” even though official (a) is numbered (a)(1)/(a)(2); official Note 1(i) “the registrant's Web site,” official Note 1(ii) “the location of the web site,” official Note 2(iii) “web sites”; official (d) typography is “the entity resulting therefrom or an entity that is a party thereto,” no Oxford comma; official (b)/(c)/(d) and 17 CFR 244.101 / 244.102 and Regulation S-K Item 10(e) / 17 CFR 229.10 named only; do not tidy “Web site” / “web site” / “Web cast” into “website” or “webcast,” packed 4370 / 2264 “Web site,” or packed 3150 “website,” and do not flatten into already-taught earnings / 10-K / 10-Q clocks, packed 13a-14, packed 12b-20, or packed 10D-1; title 17 up_to_date_as_of 2026-11-09) (`data-cleaning` +0.25h, add-on section J of `examples/p2/16_index_add_earnings_time_toy.py` after the last 10D-1 disclaimer, quiz `dc-244100`; **34/34** + closing disclaimer unchanged). Item sum **+1.50h**. Hours: **440.75 full / 420.75 skip-P0**; 28 lessons; 431 quiz pairs.
- enrich37 (2026-11-12, US-first): 17 CFR 240.14b-1 official (b)(1) seven-business-day search-card / inquiry response + official (b)(2) five-business-day forwarding (official typography is “by indicting,” “addresses,and,” “first class mail,” “and/or annual report to security holders,” typographic quotes around official (a) “registrant,” and a straight apostrophe in “registrant's”; official (a), official (b)(3), householding / 14a-3(e)(1), official (c) and later, 17 CFR 240.14b-2, and 17 CFR 240.14a-13 named only; packing 14b-1 as a second core of the packed 2251 box remains wrong, but packing it as this later separate item is accurate; do not flatten into packed 2251 or recast 2251 as this rule; title 17 up_to_date_as_of 2026-11-09) (`microstructure-orders` +0.25h, new companion `examples/p1/14_rule14b1_toy.py` section A, quiz `mo-14b1`; already-printed section S of `examples/p1/11_freeride_txse_15c33_toy.py`, including “this toy does not pack 14b-1,” **333 lines / 26770 bytes**, **58/58** after S, unchanged); FINRA 2268 official (a) opening + official (b) + official (c)(1) in full (including the earlier-of sentence that references (b)(2)) + official (d) opening and official (d)(1)–(4) (official typography is one-word lowercase “predispute,” “thirty days,” “ten business days,” and no trailing period on the official caption; official (a)(1)–(7), official (c)(2), official (e)/(f) and later, and FINRA 2263 named only; if official (f) is quoted, typography there uses hyphenated “pre-dispute” inside a statement in straight quotes; if official (a)(3) is quoted, typography is “documents, witness statements and other discovery” with no Oxford comma; do not invent that every customer must arbitrate, and do not flatten into packed 2140, packed 2273, packed 2251, or already-named 11870) (`microstructure-orders` +0.25h, add-on section T of `examples/p1/11_freeride_txse_15c33_toy.py` after the last line, quiz `mo-2268`; **58/58** after S unchanged); 17 CFR 240.15c2-4 official opening + official (a)/(b) (official typography uses typographic quotes around “fraudulent, deceptive, or manipulative act or practice” and “all-or-none,” hyphenated “firm-commitment,” and “municipal securities dealer”; official “promptly” has no numeric clock; official source line “[41 FR 22826, June 7, 1976].”; do not invent a T+1 or other numeric clock, do not teach that this rule applies to a firm-commitment underwriting, and do not flatten into packed 10b-5, already-taught 10b-9, or already-taught Regulation M Rule 105; title 17 up_to_date_as_of 2026-11-09) (`execution-slippage` +0.25h, add-on section Q of `examples/p6/12_rule606_toy.py` after the last line, quiz `es-15c24`; **52/52** after P / 2232(b)(2) unchanged); FINRA 3130 official (a) + official (b), including footnote 1’s anniversary clock (official caption typography is “3130. Annual Certification of Compliance and Supervisory Processes” with no period after Processes; official headings are “Designation of Chief Compliance Officer(s),” “Annual Certification Requirement,” and “Certification,” each with no period; official typography is “certify annually,1 as set forth,” official “(s),” “preceding 12 months,” and “no later than on the anniversary date of the previous year's certification”; official (c) and official SM .01–.10 named only; if the official SM header is quoted, typography is `• • • Supplementary Material: --------------` (U+2022, U+00A0 NBSP, 14 ASCII hyphens); do not copy packed 2273’s ordinary-space / 15-hyphen SM header onto 3130, and do not flatten into packed 2010, packed 3310, or still-unpacked 3110 / 3120) (`compliance-ethics` +0.25h, add-on section V of `examples/p7/08_self_trade_pattern_toy.py` after the last line, quiz `ce-3130`; **61/61** + `ASSERT_10b52_ok` + closing disclaimer unchanged); FINRA 2270 official (a) opening only (official typography is two-word “Web site,” a straight apostrophe in “member's Web site,” hyphenated “day-trading strategy” and “non-institutional,” “paper or electronic form,” and “clear and conspicuous manner”; official caption typography is “2270. Day-Trading Risk Disclosure Statement” with no period after Statement; the prescribed statement, including model figures $50,000, $16, 29 transactions, and $111,360, official (b), official SM, and FINRA 2130 named only; those model figures are not legal thresholds and are not a substitute for already-taught IML/IMD / the former $25,000 PDT minimum equity; do not invent that Notice 26-10 / 26-11 repealed 2270, and do not flatten into packed 2264 / 2265 / 2267, packed 2090, or still-unpacked 2130) (`compliance-ethics` +0.25h, add-on section W of the same self-trade toy after V, quiz `ce-2270`); 17 CFR 240.14a-3(b) opening only, through “as follows:” (official typography is two-word “security holders,” “accompanied or preceded,” and official caption “Information to be furnished to security holders.”; official (a), official (b)(1) and later, official typo “this paragraph 9(b)(1)” if quoted, official 14a-3(e) householding, and 17 CFR 240.14a-4 / 14a-6 named only; do not invent that every proxy mailing requires an annual report, do not treat the annual report to security holders as the same filing as the Form 10-K, and do not flatten into packed 14a-9, packed 12b-20, already-taught 14a-8, Form 8-K Item 5.07, already-taught 10-K / 10-Q clocks, packed 13a-14, or packed 244.100; title 17 up_to_date_as_of 2026-11-09) (`data-cleaning` +0.25h, add-on section K of `examples/p2/16_index_add_earnings_time_toy.py` after the last line, quiz `dc-14a3`; **37/37** after J / 244.100(a) + closing disclaimer unchanged). Item sum **+1.50h**. Hours: **442.25 full / 422.25 skip-P0**; 28 lessons; 437 quiz pairs.
- enrich38 (2026-11-12, US-first): FINRA 4590 official (a) + official (b) including (b)(1)–(3) + official (c) (official caption typography is “4590. Synchronization of Member Business Clocks” with no trailing period; official (a) “mechanical time stamping devices,” official (b) “manual time stamp machines,” and official (c) “Computer system and mechanical clocks” are not tidied into one another; official typography is “one second tolerance” (no hyphen) versus “50-millisecond tolerance” (hyphen), “hours, minutes and seconds” (no Oxford comma), a straight apostrophe in “Standards'” / “provider's” / “member's,” and official “re-synchronized”; official “every business day before market open” has no numeric clock and no time zone; official SM .01 and FINRA 6420 named only; if the official SM header is quoted, typography is `• • • Supplementary Material: --------------` (U+2022, ordinary U+0020 spaces, 14 ASCII hyphens), not official 3130 / 5310 NBSP and not packed 2273’s ordinary-space / 15-hyphen header; do not invent that the 50-millisecond tolerance applies to every business clock, and do not flatten into packed 6380A, already-taught CAT / Rule 613, or leftover 6730) (`microstructure-orders` +0.25h, add-on section U of `examples/p1/11_freeride_txse_15c33_toy.py` after the last line, quiz `mo-4590`; **61/61** after T / 2268 unchanged; do not append this item to `examples/p1/14_rule14b1_toy.py`); FINRA 5310 official (a) only — official (a)(1) including (A)–(E) + official (a)(2) (official caption typography is “5310. Best Execution and Interpositioning” with no trailing period; official (a) uses straight ASCII quotes around "reasonable diligence"; do not copy official SM typographic quotes onto official (a); official (A) has an Oxford comma; official (b)–(e) and official SM .01–.09 named only, including SM .01 “fully and promptly” with no numeric clock, SM .09, and official SM .07 heading typography `07. Orders Involving Foreign Securities.` without the leading dot used in official `.01`–`.06` and `.08`–`.09`; if the official SM header is quoted, typography is `• • • Supplementary Material: --------------` (U+2022, U+00A0 NBSP, 14 ASCII hyphens), the same as official 3130, not official 4590’s ordinary-space header, and not packed 2273; do not invent that best execution is solely about price, and do not flatten into packed 605 / 606 / 5320 / 2121, packed 15c2-4, or packed 10b-10; Notice 21-23 is not the official rule text) (`execution-slippage` +0.25h, add-on section R of `examples/p6/12_rule606_toy.py` after the last line, quiz `es-5310`; **55/55** after Q / 15c2-4 unchanged); 17 CFR 240.15c1-5 the whole current section (official caption typography is “Disclosure of control.”; official typography italicizes the defined term, including the trailing comma, and does not put quotation marks around it; official typography is “broker, dealer or municipal securities dealer” (no Oxford comma), “controlled by, controlling, or under common control with, the issuer” (comma after “with”), and “at or before the completion of the transaction.”; official source line “[41 FR 22825, June 7, 1976].”; packed 2262 stays as written; packing 15c1-5 as a second core of the 2262 box remains wrong; the first disclosure is not officially required to be in writing; no numeric clock for “completion of the transaction”; name packed 2262, already-taught 10b-10, 15c1-1, and leftover 15c1-2 / 10b-3 only; title 17 up_to_date_as_of 2026-11-09) (`execution-slippage` +0.25h, add-on section S of the same 606 toy after R, quiz `es-15c15`); 17 CFR 240.15c1-6 the whole current section (official caption typography is “Disclosure of interest in distribution.”; the same italic-term typography, with no quotes; official typography is “at or before the completion of each such transaction gives or sends” with no comma after “transaction,” official “each such transaction,” and official “gives or sends”; official source line “[41 FR 22826, June 7, 1976].”; packed 2269 stays as written; packing 15c1-6 as a second core of the 2269 box remains wrong; do not flatten into packed 2269, packed 2262, packed 15c2-4, already-taught 10b-10, or already-taught Rule 105; name 15c1-1 and leftover 15c1-8 only; title 17 up_to_date_as_of 2026-11-09) (`execution-slippage` +0.25h, add-on section T of the same 606 toy after S, quiz `es-15c16`); 17 CFR 240.15c1-7 official (a) + official (b) (the whole current section; official caption typography is “Discretionary accounts.”; the same italic-term typography, with no quotes; official (a) cites “section 15(c) of the Act” without “(1),” while official (b) cites “section 15(c)(1) of the Act”; official (a) typography is “any transactions or purchase or sale which are excessive” and “or his agent or employee”; official (b) typography is “the name, amount and price of the security” (no Oxford comma) and “immediately after effecting such transaction” with no numeric clock; a straight apostrophe in “customer's account”; official source line “[41 FR 22826, June 7, 1976].”; do not flatten into packed 2270, packed 2150, packed 4513, packed 10b-5, or packed 2010; title 17 up_to_date_as_of 2026-11-09) (`compliance-ethics` +0.25h, add-on section X of `examples/p7/08_self_trade_pattern_toy.py` after the last line, quiz `ce-15c17`; V **64/64**, W **67/67** + `ASSERT_3130_2270_ok` + closing disclaimer unchanged); 17 CFR 240.14c-3(a) opening only, through “security holders:.” (official caption typography is “Annual report to be furnished security holders.” — no “to” before “security holders,” and a period after “holders.”; official typography is two-word “security holders” and “accompanied or preceded”; official (a) word order is not identical to packed 14a-3(b); official (a)(1)/(a)(2)/(b)/(c)/(d), 14c-2, and 14c-5 named only; packing 14c-3(c) householding as a new core remains wrong; do not invent that every information statement requires an annual report, or that 14c-3(a) and packed 14a-3(b) are the same rule, or that the annual report to security holders is the Form 10-K; do not flatten into packed 14a-3(b) / 14a-9 / 12b-20 / 13a-14 / 244.100, already-taught 14a-8, Form 8-K Item 5.07, or already-taught 10-K / 10-Q clocks; if official (b) is quoted, official typographic quotes around “filed.”; title 17 up_to_date_as_of 2026-11-09) (`data-cleaning` +0.25h, add-on section L of `examples/p2/16_index_add_earnings_time_toy.py` after the last line, quiz `dc-14c3`; **40/40** after K / 14a-3(b) + closing disclaimer unchanged; do not append 14c-3 to `examples/p1/14_rule14b1_toy.py`). Item sum **+1.50h**. Hours: **443.75 full / 423.75 skip-P0**; 28 lessons; 443 quiz pairs.
- enrich21 (2026-11-12, US-first): Rule 15c6-1 default and FINRA 11320 delivery-date types (T+1 is the default unless the parties expressly agree otherwise at the time of the transaction; official types are cash, regular way, seller’s option, buyer’s option, and delayed-delivery; 11320(e) rolls a non-business due date to the next business day; 15c6-1(c) after-4:30 p.m. ET firm-commitment offerings can be up to the second business day unless otherwise agreed; no current-law “next day” category) (`microstructure-orders` +0.25h, add-on to `examples/p1/11_freeride_txse_15c33_toy.py`, quiz `mo-15c61`); current 17 CFR 240.12b-2 filer thresholds and hysteresis ($75 million / $700 million entry; $60 million / $560 million exit; last business day of the most recently completed second fiscal quarter; twelve months and one annual report; S7-2026-18 remains Proposed) (`data-cleaning` +0.25h, quiz-only `dc-12b2`; `examples/p2/09_filing_dates_toy.py` not edited); Pub 550 investment interest (margin-account interest to buy taxable securities is investment interest, generally limited to net investment income, with a carryover) (`compliance-ethics` +0.25h, add-on to `examples/p7/11_tax_1259_1256_roc_toy.py`, quiz `ce-invint`); Pub 550 stock dividends and stock rights (generally not taxable; official Example 1 $45 → three shares at $15; holding period of nontaxable new stock begins on the same day as the old stock; fractional-share cash is a sale, not a dividend) (same lesson +0.25h, same lab, quiz `ce-stodiv`); NY Fed SOFR clocks (published at approximately 8:00 a.m. ET, one business day after the value date; yesterday’s SOFR can fill at today’s 09:30 open; today’s value-date SOFR cannot; EFFR/OBFR are about 9:00 a.m.; do not copy the T-bill 15:30 clock onto SOFR) (`returns-vol-corr` +0.25h, add-on to `examples/p1/08_tbill_rf_toy.py`, quiz `rv-sofr`); Cboe Rule 5.1(e)(3) early-close Curb for Curb-eligible options (starts at the end of shortened RTH and lasts 15 minutes, official example 1:00 p.m. to 1:15 p.m.; immediately effective SRO filing SR-CBOE-2026-078 / 34-106620, designated operative upon filing; FAQ/FIX operational parenthetical still “(effective 11/16/26)”; AM-settled last-trading-day change remains Effective TBD; not the stock 12:50 p.m. MOC cutoff) (`market-regimes-crisis` +0.25h, add-on to `examples/p6/15_soq_occ_adj_toy.py`, quiz `rc-earlycurb`). Item sum **+1.50h**. Hours: **418.25 full / 398.25 skip-P0**; 28 lessons; 341 quiz pairs.
- enrich19 (2026-11-12, US-first): Rule 10b-17 issuer notice of a dividend, stock split, or rights offering generally no later than 10 days prior to the record date (not 10 business days; open-end / UIT excepted; a late or missing notice is a timing flag, not proof the dividend did not happen) (`data-cleaning` +0.25h, add-on to `examples/p2/08_dividend_dates_yf_shapes.py`, quiz `dc-10b17`); Form 4 Instruction 8 transaction codes (P / S vs A / M / F / G; V is an earlier-reporting flag) and Form 3 / Form 5 clocks (15 U.S.C. 78p(a)(2)(B) “within 10 days … or within such shorter time as the Commission may establish by rule”; Form 5 within 45 days after FYE, none if already reported; no invented shorter Form 3 clock) (`data-cleaning` +0.25h, add-on to `examples/p2/11_spinoff_insider_lag_toy.py`, quiz `dc-form4codes`); 13G→13D switch under 13d-1(e)–(g) (five-business-day filing clock; standstill until the tenth day from the 13D filing; 20% path is paragraph (c) only) and 13d-3 beneficial ownership (voting and/or investment power; 60-day right-to-acquire, immediate if control purpose) (`data-cleaning` +0.50h, same lab, quiz `dc-13g13d`); BLS PFEI 8:30 a.m. ET vs non-PFEI 10:00 a.m. ET (CPI for November 2026 scheduled December 10, 2026, at 8:30 A.M. Eastern Time; an 8:30 release is out before the 09:30 open, a 10:00 release is look-ahead at that open) (`backtest-traps` +0.25h, add-on to `examples/p2/12_event_time_ipo_toy.py`, quiz `bt-bls-time`); Rule 14e-5 purchases outside a tender offer from public announcement until expiration (`data-cleaning` +0.25h, add-on to `examples/p2/19_rule144_followon_tender_toy.py`, quiz `dc-14e5`); Pub 550 capital-loss deduction cap ($3,000 / $1,500 MFS) and carryover that remains long-term or short-term (`compliance-ethics` +0.25h, add-on to `examples/p7/11_tax_1259_1256_roc_toy.py`, quiz `ce-caploss`). No R95. Hours: **415.25 full / 395.25 skip-P0**; 28 lessons; 329 quiz pairs.
- enrich18 (2026-11-12, US-first): SIP sale-condition codes M / Q / T (plus 6 vs M; CTA ETH FAQ v1.2 for the overnight T clock; UTP September 2026 Note 1 is stale on the 23/5 window) (`microstructure-orders` +0.50h, `examples/p1/13_sale_condition_toy.py`, quiz `mo-salecond`); Form 13H large-trader identification (identifying activity level; confidential; do not invent a 10-day “promptly” clock) (`compliance-ethics` +0.25h, `examples/p7/12_form13h_toy.py`, quiz `ce-13h`); Rule 10b-18 after-hours prong, with official sources not mapping 21:00–04:00 overnight / 23/5 (`data-cleaning` +0.25h, add-on to `examples/p2/18_buyback_10b18_disclosure_toy.py`, quiz `dc-10b18ah`); Rule 604 customer-limit display and FINRA 5320 trading ahead of a customer equity order (`execution-slippage` +0.50h, quizzes `es-604` / `es-5320`); Regulation M Rules 101/102 restricted period and shelf-takedown analysis (`backtest-traps` +0.50h, add-on to `examples/p2/19_rule144_followon_tender_toy.py`, quiz `bt-regm101`). No R95. Hours: **413.5 full / 393.5 skip-P0**; 28 lessons; 323 quiz pairs.
- enrich16 (2026-11-12, US-first): clearly erroneous prints (FINRA 11892 / exchange parallels) and the 2026 overnight extension operative only at the start of 23/5 trading scheduled 2026-12-06 (`market-regimes-crisis` +0.5h, `examples/p6/14_clearly_erroneous_toy.py`, quiz `rc-ceprint`); Rule 10b-21 (deception about delivery and a fail; not every FTD) and the Rule 200 long-marking test (`pairs-stat-arb` +0.50h, `examples/p3/09_rule200_10b21_toy.py`, quizzes `ps-10b21` / `ps-mark200`); intermarket sweep orders as a current-law Rule 611 exception (S7-2026-20 remains a proposal) (`microstructure-orders` +0.25h, quiz `mo-iso`); OCC random assignment to clearing members, with the firm's exchange-approved method (random or FIFO, not necessarily random) (`market-regimes-crisis` +0.25h, add-on to `examples/p6/13_exercise_by_exception_toy.py`, quiz `rc-assign`); constructive sales under IRC §1259, Section 1256 60/40 for nonequity / broad-based index options (not ordinary equity options), and return of capital (Form 1099-DIV box 3; Pub 550 Example 1) (`compliance-ethics` +0.75h, `examples/p7/11_tax_1259_1256_roc_toy.py`, quizzes `ce-1259` / `ce-1256` / `ce-roc`). Also R93: Rule 14e-1(d) extension-notice wording only (disclose the approximate number of securities deposited to date; English second limb timed on the next business day after the scheduled expiration date); no hour or quiz-answer change. Hours: **409.5 full / 389.5 skip-P0**; 28 lessons; 310 quiz pairs.
- enrich14 (2026-11-11, US-first): Rule 10b-18 buyback safe harbor + Item 703 monthly disclosure lag (Form SR vacated 2023-12-19) (`data-cleaning` +0.75h, `examples/p2/18_buyback_10b18_disclosure_toy.py`, quizzes `dc-10b18` / `dc-item703`); NYSE early-close MOC cutoff 12:50 ET on 2026-11-27 and 2026-12-24 + Nasdaq vs NYSE close cutoffs (Nasdaq MOC 15:55 / LOC 15:58) (`microstructure-orders` +0.5h, `examples/p1/10_early_close_nasdaq_moc_toy.py`, quizzes `mo-earlyclose` / `mo-nasdaq-moc`); Reg SHO locate ≠ borrow, Rule 204 close-out under T+1, Rule 201 NBB test and threshold-security definition (`pairs-stat-arb` +0.5h, `examples/p3/08_regsho_locate_closeout_toy.py`, quiz `ps-locate204`); Section 16(b) short-swing profit (`compliance-ethics` +0.25h, `examples/p7/10_section16b_toy.py`, quiz `ce-16b`). Also leftover wording/source fixes R87 (cite SEC 34-105003 / 91 FR 13410 for the CAT pass-through quote), R89 (Reg FD “promptly” means as soon as reasonably practicable, and no later than the 24h / next-open cap), R90 (2026 agenda RIN 3235-AN72; no proposal published as of 2026-11-11), R91 (XBRL companyconcept URL on one line), R92 (lab counts only CAT Fee 2026-1, not Assessment 1A). Hours: **404.25 full / 384.25 skip-P0**; 28 lessons; 294 quiz pairs.
