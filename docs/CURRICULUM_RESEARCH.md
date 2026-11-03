# Quantitative Trading Curriculum Research
# 量化交易课程大纲研究（双语就绪 · 中文主）

> **Disclaimer / 声明（学习用途 · 非投资建议）**  
> This document outlines a **learning-only** curriculum for a self-contained website. It does **not** constitute investment advice, trading recommendations, solicitations, or guarantees of profit. Strategies, code sketches, and metrics are pedagogical. Live trading involves capital loss risk and must comply with local laws and regulations.  
> 本文档仅用于自学网站课程设计，**不构成**任何投资建议、买卖推荐或收益承诺。示例策略与指标仅供教学。实盘有本金损失风险，须自行合规。

**Audience:** Programmer / algorithm engineer with light investing experience（程序员/算法工程师，有少量投资经验）.  
**Goal:** Zero → ready for honest simple backtests, risk metrics, paper-trading mindset（零基础到能做诚实的小回测、风险度量与纸面心态）.  
**Primary language:** Chinese; English titles/fields included for bilingual UI.

**Related in-platform Pages:**
- [量化交易一站式学习项目](https://cursor.com/canvas/store-2382cb79-a91c-438a-bb75-0d38cd2e4b0d/e986247c-63a6-4a33-8d8e-97eb8be22290) — 14 modules / 5 phases
- [量化交易学习：X 策展 · 教程 · 课程](https://cursor.com/canvas/store-2382cb79-a91c-438a-bb75-0d38cd2e4b0d/1c5e6f58-9ce1-4602-b188-cb69366123db) — curated X + 10-week outline

---

## 1. Synthesis: how reputable sources sequence learning

| Source | What to take for beginners | URL |
|--------|----------------------------|-----|
| QuantStart (Successful Algo Trading + beginner books) | Process order: strategy research → securities master → rigorous backtest → performance stats → mean-reversion/momentum stats → VaR/Kelly intuition → execution; start with Ernest Chan *Quantitative Trading*, then microstructure (Johnson), then Chan *Algorithmic Trading* | https://www.quantstart.com/successful-algorithmic-trading-ebook/ · https://www.quantstart.com/articles/Top-5-Essential-Beginner-Books-for-Algorithmic-Trading/ |
| Ernest Chan (overview via QuantStart) | Retail-friendly loop: alpha model → risk → automated execution; momentum & mean reversion first | (same QuantStart beginner books article) |
| López de Prado AFML (methodology only) | Failures are pipeline failures: bars/labeling → sample weights → fracdiff → purged/embargoed CV → feature importance → backtest-as-CV / CPCV / Deflated Sharpe; **do not** teach HFT recipes as “beginner alpha” | https://www.oreilly.com/library/view/advances-in-financial/9781119482086/ · community notes e.g. https://rzeng0812.github.io/quant-atlas/80-Books/Lopez-de-Prado-Advances-Financial-ML |
| Microsoft Qlib docs | Optional AI research workflow: install → prepare data → `qrun` / workflow notebook → Data Layer → Forecast → Portfolio/Backtest → Analysis | https://qlib.readthedocs.io/en/stable/ · https://github.com/microsoft/qlib |
| Zipline Reloaded | Event-driven mental model: `initialize` / `handle_data`, calendars, ingest; good after vectorized honesty | https://zipline.ml4trading.io/ · https://github.com/stefan-jansen/zipline-reloaded |
| VectorBT | Vectorized screening & parameter sweeps; teach optimistic defaults (costs, same-bar) explicitly | https://vectorbt.dev/ |
| NYU Courant MATH-GA 2708 | Mechanics → strategies → HF data modeling → TCA/impact → portfolio/robust opt → simulation/backtest/performance → model-risk mitigation | https://math-finance.cims.nyu.edu/academics/ |
| UChicago Summer FINM 25000 | Half: allocation/attribution/pricing/risk; half: design/code/test automations, market models, infra, execution | https://summer.uchicago.edu/courses/quantitative-portfolio-management-and-algorithmic-trading/ |
| NYU Stern Trading Strategies (Dhar, public PDF) | Markets & performance metrics → trend → counter-trend → spreads/pairs → FX/carry → news/HFT awareness | https://web-docs.stern.nyu.edu/ioms/SYLLABI/Dhar_MULT-UB.0035_Fall13.pdf |
| 聚宽 JoinQuant 零基础教程 / 社区 8 周路线 | Python+策略骨架 → 收益风险指标 → 回测审讯（未来函数/幸存者/成本/过拟合）→ 选股动量 → 因子 → 组合 → 模拟 | https://www.joinquant.com/community/post/detailMobile?postId=13149 · http://lookmori.cn/ |
| 米筐 Ricequant docs | SDK / RQAlphaPlus：`init` + `handle_bar` → 回测指标 → 进阶账户与频率 | https://www.ricequant.com/doc/ · https://www.ricequant.com/doc/rqalpha-plus/doc/quick-start |
| Existing Canvas (14 modules) | Keep quant-native phases: language → research infra → strategies/factors → ML/risk/execution → paper+ethics | canvas `e986247c-…` |

### Consensus ordering (adopted)

1. **Market language & microstructure** before “strategies that print money.”  
2. **Returns / risk metrics** as the evaluation language.  
3. **Data hygiene** (corporate actions, PIT, survivorship) before fancy signals.  
4. **Backtest traps** as a first-class module (lookahead, costs, OOS) — JoinQuant “审讯室” + AFML backtest-as-CV.  
5. **Classic strategies** (momentum, mean reversion, pairs) before ML.  
6. **Factor workflow** (IC, quantiles) before black-box models.  
7. **ML with leakage controls** (time split, purge/embargo themes) — methodology, not magic.  
8. **Portfolio / sizing / drawdown** as a layer on top of signals.  
9. **Execution & costs** before claiming “live ready.”  
10. **Paper infra + compliance mindset** as exit criteria — not broker marketing.

Programmer advantage: treat the site like a **research engineering** course (assertions, logs, versioned data, reproducible notebooks), not tip-sharing.

---

## 2. Recommended phase / month / week structure

**Total:** ~5 months · ~20–22 weeks · ~100–130 hours (8–12 h/week).  
Maps to website **months** (Hardware-learning style) and optional week checkpoints.

| Month | Phase (zh) | Weeks | Hours | Outcome |
|-------|------------|-------|-------|---------|
| M1 | 市场语言与度量 | 1–4 | 20–28h | Speak markets; compute return/vol/Sharpe/MDD; mid/spread intuition |
| M2 | 数据与诚实回测 | 5–8 | 24–32h | Versioned OHLC pipeline; trap experiments; cost-aware vectorized backtest |
| M3 | 经典策略与因子 | 9–13 | 28–36h | Momentum / mean-reversion / pairs notebooks; IC & quantile research |
| M4 | ML方法、组合与执行 | 14–17 | 24–32h | Leakage-safe ML sketch; sizing/VaR/drawdown; execution sensitivity |
| M5 | 纸面、合规与结业 | 18–22 | 16–24h | Mini paper loop; research log ethics; capstone report |

**Week checkpoints (optional UI):** W1 OHLC language · W2 microstructure · W3 metrics · W4 lab · W5 data · W6 traps · W7 costs/OOS · W8 engine compare · W9–11 strategies · W12–13 factors · W14–15 ML · W16 risk · W17 execution · W18–19 paper · W20–22 capstone.

---

## 3. Lesson catalog (self-contained must-teach)

Each lesson: `id`, zh/en titles, goals, must-teach concepts, Python exercises, pitfalls.  
Content for the website must stand alone; open-source tools are **optional** later.

### Month 1 — 市场语言与度量

#### L01 `markets-language`
- **zh:** 市场与交易语言 · **en:** Markets & trading vocabulary  
- **Goals:** Distinguish assets, exchanges, long/short/leverage; describe a strategy as hypothesis → signal → risk → attribution.  
- **Must-teach:** Cash vs margin; long/short; Alpha vs Beta (plain language); research must be reproducible; programmer edge = engineering the research loop.  
- **Exercises:** Compute simple returns & equity curve from CSV; write a 3-sentence research goal; list frictions (fee, spread, tax awareness).  
- **Pitfalls:** Treating “accuracy” as the primary objective; confusing investing advice with research method.

#### L02 `microstructure-orders`
- **zh:** 微观结构与订单 · **en:** Microstructure & order types  
- **Goals:** Read bid/ask/mid; contrast market vs limit; put slippage into mental model of fills.  
- **Must-teach:** LOB intuition; mid = (bid+ask)/2; spread as immediate cost; market buy near ask; impact & latency at high level; same-bar zero-cost fills are optimistic.  
- **Exercises:** Hand-compute buy cost in bps vs mid; write cost assumptions one-pager; compare “fill at close” vs “next open.”  
- **Pitfalls:** Ignoring spread; assuming textbook mid fills; copying HFT lore without data.

#### L03 `returns-vol-corr`
- **zh:** 收益、波动与相关 · **en:** Returns, volatility & correlation  
- **Goals:** Annualize correctly; compute Sharpe & max drawdown; see crisis correlation rise.  
- **Must-teach:** Simple vs log return; σ_ann ≈ σ_day × √252; Sharpe definition & Rf convention; MDD path dependence; rolling stats.  
- **Exercises:** Implement `max_drawdown`; rolling vol; rolling pairwise correlation.  
- **Pitfalls:** Annualizing mean with √252 by mistake; Sharpe without stating frequency; using full-sample corr only.

#### L04 `eval-lab`
- **zh:** 评估实验：基准与诚实指标表 · **en:** Evaluation lab: benchmarks & honest metric tables  
- **Goals:** Compare a toy signal to buy-and-hold with the same cost assumptions.  
- **Must-teach:** Benchmark choice; turnover; win rate ≠ good strategy; report net of costs.  
- **Exercises:** Build a metric table (ann. ret, vol, Sharpe, MDD, turnover); stress one cost bump.  
- **Pitfalls:** Cherry-picking start dates; reporting gross only.

### Month 2 — 数据与诚实回测

#### L05 `data-cleaning`
- **zh:** 数据与清洗 · **en:** Data & cleaning  
- **Goals:** Versioned pipeline; adjust for corporate actions; measure missingness.  
- **Must-teach:** Split/dividend adjustment; suspensions; calendar alignment; survivorship bias; point-in-time (PIT) alignment for fundamentals.  
- **Exercises:** Reindex to business days + missingness assert; compare adjusted vs raw returns; write a data sheet (source, download time, hash).  
- **Pitfalls:** Using today’s index constituents for 10y history; mixing timezones; silent NaN forward-fill across halt.

#### L06 `backtest-traps`
- **zh:** 回测陷阱 · **en:** Backtesting traps  
- **Goals:** Demonstrate and fix lookahead; document trial count; insist on OOS.  
- **Must-teach:** Lookahead / future function; survivorship; overfitting & multiple testing; walk-forward; “beautiful curve → interrogate harder” (JoinQuant ethos).  
- **Exercises:** Cheating vs honest MA crossover (`shift`); parameter grid that overfits in-sample; hold-out last N years.  
- **Pitfalls:** Tuning on full history then claiming OOS; not logging failed experiments.

#### L07 `costs-in-backtest`
- **zh:** 成本写入回测 · **en:** Putting costs into the backtest  
- **Goals:** Net PnL after commission + slippage; sensitivity table.  
- **Must-teach:** Explicit vs implicit costs; turnover × cost; A-share constraints overview (limit-up/down, lot size) as awareness — site stays market-agnostic with plugins.  
- **Exercises:** `net = pos*ret - Δpos.abs()*(fee+slip)`; cost ladder chart.  
- **Pitfalls:** Zero-cost claim of live readiness; constant bps that understates illiquids.

#### L08 `vectorized-vs-event`
- **zh:** 向量化 vs 事件驱动直觉 · **en:** Vectorized vs event-driven intuition  
- **Goals:** Know when a fast vectorized screen lies about fill timing.  
- **Must-teach:** Bar assumptions; order state; calendar; why engines matter (Zipline/Backtrader mental model without requiring install).  
- **Exercises:** Same signal: vectorized close fill vs next-bar open; write differences paragraph.  
- **Pitfalls:** Trusting library defaults unread; confusing research speed with realism.

### Month 3 — 经典策略与因子

#### L09 `momentum-trend`
- **zh:** 动量与趋势 · **en:** Momentum & trend  
- **Goals:** Time-series vs cross-sectional momentum; report turnover & drawdowns.  
- **Must-teach:** 12–1 skip-month intuition; ranking portfolios; crowding risk; vol targeting overlay.  
- **Exercises:** Dual MA vs 12–1 style; vol-target 10%; year-by-year table.  
- **Pitfalls:** Ignoring skip-month short-term reversal; capacity fantasy.

#### L10 `mean-reversion`
- **zh:** 均值回归 · **en:** Mean reversion  
- **Goals:** z-score entries/exits; recognize trend-regime failure.  
- **Must-teach:** Deviation-pullback intuition; rolling z; half-life intuition; stop / invalidation.  
- **Exercises:** z<-2 / z>2 rules with/without stop; OOS window scan.  
- **Pitfalls:** Forcing reversion in strong trends; full-sample thresholds.

#### L11 `pairs-stat-arb`
- **zh:** 配对与统计套利入门 · **en:** Pairs & intro to statistical arb  
- **Goals:** Trade the spread, not a single price forecast; rolling hedge ratio.  
- **Must-teach:** High correlation ≠ tradeable; cointegration intuition (not full theory dump); residual z; leg break / liquidity.  
- **Exercises:** Rolling beta spread; full-sample vs rolling; asymmetric shock thought experiment.  
- **Pitfalls:** Static hedge forever; ignoring borrow/short constraints.

#### L12 `factor-workflow`
- **zh:** 因子研究工作流 · **en:** Factor research workflow  
- **Goals:** Compute IC & quantile returns; neutralize simple size exposure conceptually.  
- **Must-teach:** Spearman IC; quantile long-short; IC decay; turnover of factor portfolios; “factor mirage” / false discoveries awareness (LdP theme).  
- **Exercises:** True vs scrambled factor IC; quantile NAV; one neutralization sketch.  
- **Pitfalls:** Stacking parameters instead of economic hypothesis; reporting only winners.

#### L13 `strategy-compare-lab`
- **zh:** 策略对照实验 · **en:** Strategy comparison lab  
- **Goals:** Same universe/costs/metrics across M3 strategies.  
- **Must-teach:** Controlled comparison; complexity must beat simple baseline.  
- **Exercises:** One HTML/Markdown report with three strategies side-by-side.  
- **Pitfalls:** Different hidden assumptions per strategy.

### Month 4 — ML方法、组合与执行

#### L14 `ml-leakage`
- **zh:** 机器学习进量化：防泄漏 · **en:** ML for quant: anti-leakage  
- **Goals:** Time-safe split; shift features; prefer simple models first.  
- **Must-teach:** Labeling pitfalls (fixed horizon vs barrier *idea*); no shuffle on time series; purge/embargo **concept**; meta-labeling *idea*; report number of trials (AFML spirit).  
- **Exercises:** Random vs chronological split A/B; fix three planted leaks; evaluate with IC not only accuracy.  
- **Pitfalls:** sklearn default CV; peeking at test while tuning; deep models before clean labels.

#### L15 `portfolio-risk-sizing`
- **zh:** 组合、风险与仓位 · **en:** Portfolio, risk & position sizing  
- **Goals:** Vol targeting; drawdown circuit breaker; Kelly as upper-bound intuition.  
- **Must-teach:** Risk budget; half-Kelly caution; historical VaR quantile; hard constraints in config.  
- **Exercises:** Fixed size vs vol-target vs DD brake; write risk preference one-pager.  
- **Pitfalls:** Full Kelly with noisy edge; VaR as promise.

#### L16 `execution-slippage`
- **zh:** 执行与滑点 · **en:** Execution & slippage  
- **Goals:** Treat execution as part of strategy; participation vs impact sketch.  
- **Must-teach:** Explicit vs implicit; TWAP/VWAP awareness; participation rate; open vs close fill experiments.  
- **Exercises:** Cap participation; cost ladder; one-page execution assumptions.  
- **Pitfalls:** Research with zero impact then live large size.

#### L17 `risk-systems-lab`
- **zh:** 风险系统小实验 · **en:** Mini risk-systems lab  
- **Goals:** Config-driven limits that halt trading on data gaps / DD.  
- **Must-teach:** Kill switches; monitoring metrics; secrets not in git.  
- **Exercises:** Simulate gap → pause; DD → flatten; fake secret scan in repo.  
- **Pitfalls:** Manual “I’ll watch it” as only control.

### Month 5 — 纸面、合规与结业

#### L18 `paper-trading-infra`
- **zh:** 纸面交易与迷你基建 · **en:** Paper trading & mini infra  
- **Goals:** Signal → target → log loop for ≥5 sessions.  
- **Must-teach:** State machine & reconciliation; paper validates process not profits; daily report template.  
- **Exercises:** CSV paper matcher; interrupt on stale data; 5-day log pack.  
- **Pitfalls:** Changing rules mid-paper because of P&L.

#### L19 `compliance-ethics`
- **zh:** 合规、风险心态与研究伦理 · **en:** Compliance, risk mindset & research ethics  
- **Goals:** Survival first; log failures; no misleading selective reporting.  
- **Must-teach:** Learning ≠ regulated advice business; jurisdiction awareness; don’t trade what you don’t understand; record failed trials.  
- **Exercises:** Risk preference sheet; three failures into log; audit a fake “guaranteed Sharpe” pitch.  
- **Pitfalls:** Marketing backtests; ignoring local rules.

#### L20 `capstone`
- **zh:** 结业项目：诚实的小策略 · **en:** Capstone: an honest small strategy  
- **Goals:** Hypothesis → data sheet → signal → costed backtest → OOS → sizing → paper log.  
- **Must-teach:** Delivery rubric (reproducibility, honesty, evaluation, engineering, communication).  
- **Exercises:** Full report per canvas capstone checklist.  
- **Pitfalls:** Pretty in-sample curve only; zero-cost same-bar as “proof.”

---

## 4. Ordered OPTIONAL open-source tools (verified links)

Mention only after core pandas notebooks; never block learning on installs.

| Order | Tool | Role | Link |
|------:|------|------|------|
| 1 | pandas / NumPy | Core (required conceptually) | https://pandas.pydata.org/ |
| 2 | VectorBT | Fast vectorized sweeps | https://vectorbt.dev/ |
| 3 | Zipline Reloaded | Event-driven pedagogy | https://zipline.ml4trading.io/ · https://github.com/stefan-jansen/zipline-reloaded |
| 4 | Backtrader | Alternative event-driven | https://www.backtrader.com/ |
| 5 | Alphalens Reloaded / custom IC | Factor tear sheets | (pair with ML4T ecosystem) |
| 6 | microsoft/qlib | AI quant research platform | https://github.com/microsoft/qlib · https://qlib.readthedocs.io/en/stable/ |
| 7 | stefan-jansen/machine-learning-for-trading | End-to-end notebooks | https://github.com/stefan-jansen/machine-learning-for-trading |
| 8 | LLMQuant/quant-wiki | Chinese knowledge map | https://github.com/LLMQuant/quant-wiki · https://quant-wiki.com/ |
| 9 | JoinQuant / Ricequant (cloud) | A-share practice sandboxes | https://www.joinquant.com/ · https://www.ricequant.com/doc/ |
| 10 | NautilusTrader | Later: research≈live engine | https://github.com/nautechsystems/nautilus_trader |

**Book pointers (optional reading, not required to progress):** Ernest Chan *Quantitative Trading* / *Algorithmic Trading*; López de Prado *AFML* (methodology chapters); Barry Johnson *Algorithmic Trading & DMA* (microstructure depth); QuantStart reading lists.

---

## 5. X (Twitter) high-engagement learning-path signals (API, capped)

Engagement score used previously: `likes + 2*bookmarks + 3*reposts`. Metrics below are from X API responses this research turn / prior curated Page — **not invented**.

Relevant posts found in capped searches (2026-10 → 2026-11):

| Note | Author | URL | likes | bookmarks | reposts |
|------|--------|-----|------:|----------:|--------:|
| End-to-end Python algo system roadmap (bookmark-heavy) | @quantscience_ | https://x.com/quantscience_/status/2112881868890599917 | 61 | 199 | 10 |
| “Complete roadmap” algo trading system | @quantscience_ | https://x.com/quantscience_/status/2112574842738204911 | 33 | 54 | 8 |
| XQuant Learning / reverse order (do strategy first) — Chinese | @_zheergen | https://x.com/_zheergen/status/2114885286039789576 | 63 | 71 | 13 |
| Awesome Systematic Trading resource list (Chinese) | @bkdgiffug | https://x.com/bkdgiffug/status/2114666850147610945 | 60 | 43 | 5 |

**Interpretation for curriculum:** English high-engagement posts often push **tool stacks + roadmaps** (Quant Science / PyQuant News). Chinese high-engagement often pushes **resource repos + “run something first.”** Our site should: (1) allow early tiny runnable labs, (2) still force trap/cost modules before celebrating curves — aligning JoinQuant “审讯室” with AFML skepticism.

Chinese keyword search also returned many **off-topic** “学习路径” posts (AI agents, guitar, etc.); those were ignored.

---

## 6. Gaps / disputed topics

| Topic | Status | Curriculum stance |
|-------|--------|-------------------|
| Retail profitability / “anyone can do it” (Chan tone vs industry) | Disputed | Teach process & honesty; never promise edge |
| HFT / microstructure alpha for beginners | Out of scope | Concepts only; no latency-arb recipes |
| Deep RL for trading | Speculative / easy to misuse | Optional footnote after M4; not core |
| Crypto-specific microstructure | Fragmented | Optional track; same trap rules |
| Exact Kelly fraction | Disputed | Teach as noisy upper bound; prefer vol targeting + DD brakes |
| Factor zoo persistence | Highly disputed (LdP false discoveries) | Emphasize multiple testing & OOS |
| Which backtester is “best” | Preference | Teach assumptions; compare ≥2 mental models |
| A-share vs US rules | Jurisdiction-specific | Core site market-agnostic; locale callouts |
| QuantLib | More derivatives pricing | Mention later; not beginner trading path |
| Progress sync across devices | Product gap (existing Canvas) | Website should persist progress server-side if productized |

---

## 7. Mapping to existing Canvas modules

| Canvas module | Lesson ids |
|---------------|------------|
| m1 市场与交易语言 | L01 |
| m2 微观结构与订单 | L02 |
| m3 收益波动相关 | L03–L04 |
| m4 数据与清洗 | L05 |
| m5 回测陷阱 | L06–L08 |
| m6–m8 动量/回归/配对 | L09–L11 |
| m9 因子工作流 | L12–L13 |
| m10 ML | L14 |
| m11 组合风险 | L15, L17 |
| m12 执行 | L16 |
| m13 纸面 | L18 |
| m14 合规伦理 | L19 |
| Capstone | L20 |

---

## 8. Implementation note for OpenCode / Hardware-style site

Drop-in TypeScript draft: `/workspace/quant-trading-learn/src/lib/curriculum.draft.ts`  
Shape matches Hardware-learning: `Month[]` with bilingual `title`/`goal`/`topics`/`milestones` and `Lesson` with `slug`, `objectives`, `tasks`, `prereqs`, `minutes`.

Website knowledge must be **embedded** (explanations, formulas, quizzes, code). External links = optional deeper refs only.
