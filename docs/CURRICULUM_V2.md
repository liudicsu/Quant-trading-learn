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
| `markets-language` | P1 | 5 | 2 | 否 | basic-finance-markets |
| `microstructure-orders` | P1 | 7 | 2 | 否 | markets-language |
| `returns-vol-corr` | P1 | 8 | 2 | 否 | python-pandas-timeseries, stats-probability-basics, markets-language |
| `eval-lab` | P1 | 6 | 2 | 否 | returns-vol-corr, microstructure-orders |
| `data-cleaning` | P2 | 12 | 3 | 否 | eval-lab |
| `backtest-traps` | P2 | 18 | 4 | 否 | data-cleaning, stats-probability-basics |
| `costs-in-backtest` | P2 | 6 | 3 | 否 | backtest-traps |
| `engines-vectorized-event` | P2 | 8 | 3 | 否 | costs-in-backtest |
| `momentum-trend` | P3 | 8 | 3 | 否 | engines-vectorized-event |
| `mean-reversion` | P3 | 7 | 3 | 否 | momentum-trend |
| `pairs-stat-arb` | P3 | 10 | 3 | 否 | mean-reversion |
| `strategy-compare-lab` | P3 | 5 | 3 | 否 | momentum-trend, mean-reversion, pairs-stat-arb |
| `factor-workflow` | P4 | 14 | 4 | 否 | strategy-compare-lab, backtest-traps |
| `factor-portfolio-lab` | P4 | 7 | 4 | 否 | factor-workflow |
| `ml-leakage-control` | P5 | 20 | 5 | 否 | factor-workflow, backtest-traps |
| `modern-ml-pipelines` | P5 | 11 | 4 | 否 | ml-leakage-control, data-cleaning |
| `portfolio-risk-sizing` | P6 | 17 | 4 | 否 | returns-vol-corr, strategy-compare-lab |
| `execution-slippage` | P6 | 7 | 3 | 否 | costs-in-backtest, portfolio-risk-sizing |
| `risk-systems-lab` | P6 | 5 | 3 | 否 | portfolio-risk-sizing, execution-slippage |
| `paper-trading-infra` | P7 | 11 | 3 | 否 | risk-systems-lab |
| `compliance-ethics` | P7 | 4 | 2 | 否 | paper-trading-infra |
| `frontier-llm-agents` | P8 | 8 | 5 | 否 | factor-workflow, ml-leakage-control, modern-ml-pipelines, compliance-ethics |
| `frontier-tsfm-altdata-crypto` | P8 | 8 | 4 | 否 | modern-ml-pipelines, data-cleaning, execution-slippage |
| `capstone` | P9 | 24 | 5 | 否 | paper-trading-infra, compliance-ethics, factor-workflow, portfolio-risk-sizing |

**程序员建议：** 对 P0 三课做测验；通过则跳过，把时间补给 P2/P4/P5/P6 的重课。

## 2. 阶段总览（由依赖簇导出，非日历格）

| 阶段 | 名称 | 课数 | 总课时 | 6h/周 | 12h/周 | 依赖簇 |
|------|------|-----:|-------:|------:|-------:|--------|
| P0 | 零基础准备（可测验跳过） / Zero-basis foundations (test-out OK) | 3 | 20h | ~3.3 周 | ~1.7 周 | Foundational skills before market microstructure |
| P1 | 市场语言与度量 / Market language & measurement | 4 | 25h | ~4.2 周 | ~2.1 周 | Market concepts + evaluation language |
| P2 | 数据与诚实回测 / Data & honest backtests | 4 | 40h | ~6.7 周 | ~3.3 周 | Research infrastructure / scientific method for backtests |
| P3 | 经典策略族 / Classic strategy families | 4 | 30h | ~5.0 周 | ~2.5 周 | Classic alpha templates before factors/ML |
| P4 | 因子研究 / Factor research | 2 | 21h | ~3.5 周 | ~1.8 周 | Cross-sectional research methods |
| P5 | 机器学习与现代流水线 / ML & modern pipelines | 2 | 22h | ~3.7 周 | ~1.8 周 | Supervised ML methodology for finance |
| P6 | 风险、仓位与执行 / Risk, sizing & execution | 3 | 26h | ~4.3 周 | ~2.2 周 | Portfolio construction / execution / controls |
| P7 | 纸面与伦理 / Paper trading & ethics | 2 | 14h | ~2.3 周 | ~1.2 周 | Operationalization and professional norms |
| P8 | 前沿与非主流方法 / Frontier & unconventional methods | 2 | 16h | ~2.7 周 | ~1.3 周 | Post-prerequisite frontier / niche methods |
| P9 | 结业项目 / Capstone | 1 | 24h | ~4.0 周 | ~2.0 周 | Synthesis |

**全量（含 P0）：精确 256 学时（跳过 P0 为 236）。** 6h/周 ≈ 42.7 周；12h/周 ≈ 21.3 周。
**跳过 P0 后：约 218 学时。** 6h/周 ≈ 36.3 周；12h/周 ≈ 18.2 周。

精确合计：**256h 全量 / 236h 跳过 P0**。对外可表述为约 **240–270h 全量 / 220–250h 跳过基础**（含个人复盘缓冲）。

## 3. 阶段 ← 来源映射

| 阶段 | 主要来源（经典/平台） | Canvas / X 策展 | 前沿来源（已核验） |
|------|----------------------|-----------------|-------------------|
| P0 | 聚宽零基础 Python；QuantStart Python 清单 | JoinQuant W01 风格 | — |
| P1 | QuantStart；NYU MATH-GA 2708；Stern metrics | Canvas m1–m3；手册教程 | — |
| P2 | JoinQuant 审讯室；AFML；VectorBT/Zipline；QuantStart | Canvas m4–m5；@AfuOnTheWay；@RoundtableSpace；@pyquantnews | Nautilus 同构；Quant-Arena 密封 hold-out 精神 |
| P3 | Stern；Canvas m6–m8；JT；Moskowitz et al. 2012 | quants.md 对照样本；QuantJourney | further reading: Chan Algorithmic Trading (Wiley 2013) |
| P4 | AFML；Factor Mirage；Qlib Alpha；@alin_alphapilot | Canvas m9；quant-wiki | LLM alpha mining（练习在 P8） |
| P5 | AFML CV/labeling；ML4T；Qlib Quick Start | Canvas m10；@quantscience_；ML4T 帖 | Qlib 深度模型可选对照 |
| P6 | QuantStart VaR/Kelly/execution；NYU TCA；UChicago FINM | Canvas m11–m12；@sera00111 | — |
| P7 | JoinQuant 模拟；QuantStart paper-before-live | Canvas m13–m14；Qbot/Atlas | — |
| P8 | — | XQuant / Crypto 工具链等非主流 | RD-Agent(Q)；Chain-of-Alpha；Quant-Arena；TSFM 评测；GMX CCXT |
| P9 | Canvas 结业量规；聚宽综合 | 开源策略库仅灵感 | 可选前沿负结果附录 |

## 4. 非主流 / 前沿条目清单 → 归属课

| 条目 | 来源 | 类型 | 归属课 |
|------|------|------|--------|
| 假设→数据→回测→风险→执行主链 | QuantStart SAT；Canvas 教程 | classic | `贯穿 P1–P7` |
| JoinQuant 审讯室 | lookmori 8周；聚宽教程 | classic | `backtest-traps` |
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
| 纸面先于实盘 | JoinQuant W08；Canvas m13 | classic | `paper-trading-infra` |
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
| Chain-of-Alpha | arXiv:2508.06312 | frontier | `frontier-llm-agents` |
| LLM+MCTS 公式因子 | arXiv:2505.11122 | frontier | `frontier-llm-agents` |
| Quant-Arena 密封年基准 | arXiv:2610.30113 | frontier | `frontier-llm-agents / backtest-traps` |
| Chronos/TimesFM 金融评测 | arXiv:2511.18578 等 | frontier | `frontier-tsfm-altdata-crypto` |
| Qlib Transformer/Localformer | Qlib release notes | frontier | `modern-ml-pipelines（可选对照）` |
| CCXT 兼容 GMX/链上适配 | Trading Strategy / Arbitrum 2025 | frontier | `frontier-tsfm-altdata-crypto` |
| 资金费率/链上指标流水线结构 | 社区开源示例（结构参考） | niche | `frontier-tsfm-altdata-crypto` |

说明：`classic`=主干必教；`niche`=先前 X/Canvas 非主流或糙而实用路径；`frontier`=2024–2026 已核验新方法（强调批判与防泄漏，不承诺收益）。

## 5. 分课大纲（自洽）

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
- **Method tags:** classic: JoinQuant W01 pandas; QuantStart Python stack | niche: XQuant Learning: run first then fill gaps (@_zheergen)

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
- **Method tags:** classic: QuantStart beginner books; JoinQuant 初识量化

### P1 · 市场语言与度量（Market language & measurement）— 25h / 4 课

**阶段目标：** 用交易语言说话，并用收益/风险指标诚实评价玩具信号。

**6h/周 ≈ 4.2 周；12h/周 ≈ 2.1 周。**

#### `markets-language` — 市场与交易语言 / Markets & trading vocabulary
- **Hours:** 5h · **Difficulty:** 2/5 · **Basis:** 2h concepts + 2.5h exercises + 0.5h quiz
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
- **Hours:** 7h · **Difficulty:** 2/5 · **Basis:** 3h concepts + 3h exercises + 1h quiz
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
- **Hours:** 8h · **Difficulty:** 2/5 · **Basis:** 3h formulas + 4h coding + 1h quiz
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
- **Method tags:** classic: Canvas m3; JoinQuant W02; QuantStart performance

#### `eval-lab` — 评估实验：基准与诚实指标 / Evaluation lab: benchmarks & honest metrics
- **Hours:** 5h · **Difficulty:** 2/5 · **Basis:** 1.5h concepts + 3h lab + 0.5h quiz
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
- **Method tags:** classic: JoinQuant 策略评价; Canvas eval | niche: @FG731314/2115609441748001008 risk-adjusted traits

### P2 · 数据与诚实回测（Data & honest backtests）— 40h / 4 课

**阶段目标：** 可版本化数据+陷阱审讯+成本+引擎假设。

**6h/周 ≈ 6.7 周；12h/周 ≈ 3.3 周。**

#### `data-cleaning` — 数据与清洗 / Data & cleaning
- **Hours:** 10h · **Difficulty:** 3/5 · **Basis:** 4h concepts + 5h pipeline lab + 1h docs/quiz
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
- **Method tags:** classic: Canvas m4; QuantStart securities master; Qlib data layer; JoinQuant data | niche: @pyquantnews 45 APIs (2116517809920327801); OpenBB quantitative docs; Binance Vision + @sera00111 crypto data notes | frontier: Alt-data awareness; deeper in P8

#### `backtest-traps` — 回测陷阱与过拟合审讯 / Backtest traps & overfitting interrogation
- **Hours:** 16h · **Difficulty:** 4/5 · **Basis:** 5h concepts + 9h multi-labs + 2h write-up — HEAVY
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
- **Method tags:** classic: Canvas m5; JoinQuant审讯室; AFML backtest-as-CV; @AfuOnTheWay三坑; @lopezdeprado虚假发现 | niche: (XQuant tag dropped — unverified this batch) | classic+: Bailey-LdP 2012 PSR / 2014 DSR; AFML ch.7/14 | frontier: Quant-Arena arXiv:2610.30113 sealed hold-out

#### `costs-in-backtest` — 成本写入回测 / Costs in the backtest
- **Hours:** 6h · **Difficulty:** 3/5 · **Basis:** 2h concepts + 3.5h coding + 0.5h quiz
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
- **Hours:** 8h · **Difficulty:** 3/5 · **Basis:** 3h concepts + 4h compare lab + 1h optional docs
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

### P3 · 经典策略族（Classic strategy families）— 30h / 4 课

**阶段目标：** 复现动量/回归/配对并做对照。

**6h/周 ≈ 5.0 周；12h/周 ≈ 2.5 周。**

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
- **Hours:** 10h · **Difficulty:** 3/5 · **Basis:** 4h concepts + 5h lab + 1h write-up
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
- **Method tags:** classic: Canvas comparison spirit; JoinQuant research rules | niche: Critique open strategy dumps (quants.md) as hypothesis sources only | further reading: Chan Algorithmic Trading (Wiley 2013, ISBN 978-1-118-46014-6)

### P4 · 因子研究（Factor research）— 21h / 2 课

**阶段目标：** IC/分层/组合化的可重复因子工作流。

**6h/周 ≈ 3.5 周；12h/周 ≈ 1.8 周。**

#### `factor-workflow` — 因子研究工作流 / Factor research workflow
- **Hours:** 14h · **Difficulty:** 4/5 · **Basis:** 5h concepts + 7h labs + 2h write-up — HEAVY
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
- **Hours:** 7h · **Difficulty:** 4/5 · **Basis:** 2h concepts + 4.5h lab + 0.5h quiz
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

### P5 · 机器学习与现代流水线（ML & modern pipelines）— 22h / 2 课

**阶段目标：** 防泄漏ML + 可复现现代流水线基线。

**6h/周 ≈ 3.7 周；12h/周 ≈ 1.8 周。**

#### `ml-leakage-control` — 机器学习防泄漏 / ML anti-leakage
- **Hours:** 14h · **Difficulty:** 5/5 · **Basis:** 5h AFML concepts + 7h labs + 2h write-up — HEAVY
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
- **Hours:** 8h · **Difficulty:** 4/5 · **Basis:** 3h architecture + 4h mini-pipeline + 1h optional Qlib
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

### P6 · 风险、仓位与执行（Risk, sizing & execution）— 26h / 3 课

**阶段目标：** 仓位层、执行成本与硬约束工程化。

**6h/周 ≈ 4.3 周；12h/周 ≈ 2.2 周。**

#### `portfolio-risk-sizing` — 组合、风险与仓位 / Portfolio, risk & position sizing
- **Hours:** 14h · **Difficulty:** 4/5 · **Basis:** 5h concepts + 7h labs + 2h writing — HEAVY
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
- **Hours:** 7h · **Difficulty:** 3/5 · **Basis:** 2.5h concepts + 4h experiments + 0.5h quiz
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
- **Hours:** 5h · **Difficulty:** 3/5 · **Basis:** 1.5h concepts + 3h labs + 0.5h quiz
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

### P7 · 纸面与伦理（Paper trading & ethics）— 14h / 2 课

**阶段目标：** 纸面闭环与合规/研究伦理。

**6h/周 ≈ 2.3 周；12h/周 ≈ 1.2 周。**

#### `paper-trading-infra` — 纸面交易与迷你基建 / Paper trading & mini infra
- **Hours:** 10h · **Difficulty:** 3/5 · **Basis:** 3h design + 6h running/logging + 1h template
- **Prereqs:** `risk-systems-lab`
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
- **Method tags:** classic: Canvas m13; JoinQuant W08; QuantStart paper-before-live | niche: Qbot/Atlas reference architecture; Nautilus isomorphic paper/sim concept

#### `compliance-ethics` — 合规、风险心态与研究伦理 / Compliance, risk mindset & research ethics
- **Hours:** 4h · **Difficulty:** 2/5 · **Basis:** 2h reading + 1.5h writing + 0.5h quiz
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

### P8 · 前沿与非主流方法（Frontier & unconventional methods）— 16h / 2 课

**阶段目标：** 在经典纪律之上批判性接触LLM agent、TSFM、另类数据与Crypto/链上。

**6h/周 ≈ 2.7 周；12h/周 ≈ 1.3 周。**

#### `frontier-llm-agents` — 前沿：LLM / 多智能体量化研发 / Frontier: LLM / multi-agent quant R&D
- **Hours:** 8h · **Difficulty:** 5/5 · **Basis:** 4h guided reading + 3h critical exercises + 1h rules rewrite
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
- **Method tags:** niche: XQuant Spec+AI run-first as motivation only (@_zheergen) | frontier: microsoft/RD-Agent + R&D-Agent(Q) NeurIPS 2025 / arXiv:2505.15155; Chain-of-Alpha arXiv:2508.06312; LLM+MCTS arXiv:2505.11122; Quant-Arena arXiv:2610.30113; Glasserman&Lin arXiv:2309.17322; Lopez-Lira/Tang/Zhu arXiv:2504.14765

#### `frontier-tsfm-altdata-crypto` — 前沿：时序基础模型 · 另类数据 · Crypto/链上 / Frontier: TSFMs · alt-data · crypto/on-chain
- **Hours:** 8h · **Difficulty:** 4/5 · **Basis:** 4h paper/docs + 3h design exercises + 1h optional pull
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

### P9 · 结业项目（Capstone）— 24h / 1 课

**阶段目标：** 端到端诚实交付。

**6h/周 ≈ 4.0 周；12h/周 ≈ 2.0 周。**

#### `capstone` — 结业项目：诚实的小策略 / Capstone: an honest small strategy
- **Hours:** 24h · **Difficulty:** 5/5 · **Basis:** 6h design/data + 10h backtest/OOS + 4h paper + 4h writing — project
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
- **Method tags:** classic: Canvas capstone; JoinQuant综合+模拟; Bailey–LdP 2014 DSR; Perold 1988 IS | niche: Open strategy libs sparingly as hypothesis inspiration only | frontier: Optional negative-result appendix on RD-Agent/TSFM/on-chain signal

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

Net hours ≈ +18h (256h full / 236h skip P0).
