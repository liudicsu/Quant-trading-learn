/**
 * Quant trading curriculum V2 (official site data) — phase → lesson (content-dependency driven).
 * Not forced into a Hardware-learning month grid.
 * Chinese primary; bilingual fields. Learning only -- not investment advice.
 */

export type Locale = "zh" | "en";
export type L10n = Record<Locale, string>;

export interface Task {
  id: string;
  text: L10n;
}

export interface Lesson {
  slug: string;
  title: L10n;
  summary: L10n;
  hours: number;
  difficulty: number;
  skippable: boolean;
  skipNote?: L10n;
  hourBasis: string;
  prereqs: string[];
  goals: L10n[];
  mustTeach: L10n[];
  exercises: L10n[];
  quizTopics: L10n[];
  doneWhen: L10n[];
  methodTags: { classic: string[]; niche: string[]; frontier: string[] };
  tasks: Task[];
  /** Site body status: P0–P9 written. */
  status: "ready" | "outline";
}

export interface Phase {
  id: string;
  slug: string;
  title: L10n;
  goal: L10n;
  cluster: string;
  lessons: Lesson[];
}

export const COURSE_META = {
  version: 2,
  disclaimer: {
    zh: "学习用途，非投资建议。不构成买卖推荐或收益承诺。",
    en: "Learning only -- not investment advice. No trade recommendations or profit promises.",
  },
  audience: {
    zh: "从零基础到程序员背景均可；P0 可测验跳过",
    en: "Zero-basis to programmer backgrounds; P0 is test-out",
  },
  pacingNote: {
    zh: "阶段由知识依赖簇导出，不是月历格子",
    en: "Phases come from dependency clusters, not a calendar grid",
  },
  hoursFull: 397.75,
  hoursSkipFoundations: 377.75,
  hoursRangeLabel: {
    zh: "精确 397.75h 全量 / 377.75h 跳过 P0（对外约 350–397.75h / 330–377.75h）；默认场景：美国上市股票、美元",
    en: "Exact 397.75h full / 377.75h skip P0 (public range ~350–397.75h / 330–377.75h); default scope: US-listed stocks, USD",
  },
  lessonCount: 28,
  phaseCount: 10,
};

const phase_P0_lessons: Lesson[] = [
  {
    slug: "python-pandas-timeseries",
    status: "ready",
    title: { zh: "Python / pandas 时间序列入门", en: "Python / pandas for time series" },
    summary: { zh: "索引、对齐、滚动、缺失；程序员可测验跳过。", en: "Indexing, alignment, rolling, missingness; programmers may test out." },
    hours: 7,
    difficulty: 1,
    skippable: true,
    skipNote: { zh: "能独立 CSV→DatetimeIndex→pct_change→rolling→画图则跳过。", en: "Skip if you can CSV→DatetimeIndex→pct_change→rolling→plot." },
    hourBasis: "3h concepts + 3h lab + 1h quiz",
    prereqs: [],
    goals: [
      { zh: "熟练 DatetimeIndex/reindex/align。", en: "Use DatetimeIndex/reindex/align." },
      { zh: "会 rolling 与缺失处理。", en: "Rolling and missingness." },
      { zh: "OHLC 整理成可复现输入。", en: "OHLC as reproducible input." },
    ],
    mustTeach: [
      { zh: "时间索引第一公民；错位=隐性前瞻。", en: "Time index first-class; misalignment=lookahead." },
      { zh: "向量化优于行循环。", en: "Vectorize over row loops." },
      { zh: "断言与 dtype 检查。", en: "Asserts and dtype checks." },
    ],
    exercises: [
      { zh: "CSV→DatetimeIndex。", en: "CSV→DatetimeIndex." },
      { zh: "reindex/align 错位日历。", en: "reindex/align calendars." },
      { zh: "缺失：dropna/ffill/interpolate。", en: "Missing: dropna/ffill/interpolate." },
      { zh: "pct_change+rolling 作图。", en: "pct_change+rolling plot." },
      { zh: "lookahead vs shift(1)。", en: "lookahead vs shift(1)." },
      { zh: "三条断言 ASSERTS_OK。", en: "Three asserts ASSERTS_OK." },
    ],
    quizTopics: [
      { zh: "reindex+ffill 危险", en: "reindex+ffill danger" },
      { zh: "pct_change 首行 NaN", en: "First-row NaN" },
    ],
    doneWhen: [
      { zh: "可复现小 notebook+断言。", en: "Reproducible mini-notebook+asserts." },
    ],
    methodTags: {
      classic: ["Self-contained local pandas labs", "QuantStart Python stack", "Chinese supplement: JoinQuant community tutorials"],
      niche: [],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "从 examples/p0/data/synthetic_ohlc.csv 读入并设 DatetimeIndex，打印 head；完成标准：索引为 DatetimeIndex 且含 open/high/low/close。", en: "Load examples/p0/data/synthetic_ohlc.csv with DatetimeIndex; done when index is DatetimeIndex with OHLC columns." } },
      { id: "ex2", text: { zh: "对两条日历不完全重合的序列做 reindex/align，写出对齐后非空行数；完成标准：展示 inner 与 outer 对齐结果各一张表。", en: "reindex/align two misaligned calendars; done when you show both inner and outer alignment tables." } },
      { id: "ex3", text: { zh: "对故意插入的缺失收盘分别用 dropna / ffill / interpolate，对比收益均值；完成标准：三列结果并排且能口头说明取舍。", en: "Apply dropna/ffill/interpolate to planted missing closes; done when three side-by-side results plus trade-off notes." } },
      { id: "ex4", text: { zh: "计算 pct_change 与 rolling(3).mean，并保存收益/均线图；完成标准：本地生成与课内一致的 PNG。", en: "Compute pct_change and rolling(3).mean and save the plot; done when PNG matches the lesson figure." } },
      { id: "ex5", text: { zh: "构造 lookahead 信号并与 shift(1) 仓位对比错位天数；完成标准：打印 misaligned_days 并解释。", en: "Build a lookahead signal vs shift(1) position; done when misaligned_days is printed and explained." } },
      { id: "ex6", text: { zh: "保留至少三条断言（DatetimeIndex、数值 dtype、首行 NaN）；完成标准：脚本打印 ASSERTS_OK。", en: "Keep ≥3 asserts (DatetimeIndex, numeric dtype, leading NaN); done when script prints ASSERTS_OK." } },
    ],
  },
  {
    slug: "stats-probability-basics",
    status: "ready",
    title: { zh: "统计与概率基础", en: "Statistics & probability basics" },
    summary: { zh: "均值方差分位相关；多重比较直觉；可跳过。", en: "Mean/var/quantiles/corr; multiple-comparison intuition; test-out OK." },
    hours: 8,
    difficulty: 2,
    skippable: true,
    skipNote: { zh: "熟悉分布/相关/p值误用/多重比较则可跳过。", en: "Skip if comfortable with distributions/correlation/p-values/multiple testing." },
    hourBasis: "4h concepts + 3h sim lab + 1h quiz",
    prereqs: ["python-pandas-timeseries"],
    goals: [
      { zh: "解释均值方差分位。", en: "Explain mean/var/quantiles." },
      { zh: "区分样本噪声与相关。", en: "Sample noise vs correlation." },
      { zh: "说明多重检验虚假发现。", en: "State multiple-testing false discoveries." },
    ],
    mustTeach: [
      { zh: "金融中 IID 常不成立。", en: "IID often fails in finance." },
      { zh: "相关≠因果且会漂移。", en: "Corr≠causation; drifts." },
      { zh: "多次试错需打折显著性。", en: "Many trials discount significance." },
    ],
    exercises: [
      { zh: "直方图与分位。", en: "Histogram/quantiles." },
      { zh: "滚动 vs 全样本相关。", en: "Rolling vs full-sample corr." },
      { zh: "100 次多重检验循环。", en: "100-trial multiple-testing loop." },
      { zh: "p 值误用走读。", en: "p-value misuse walk-through." },
      { zh: "IID 与回测过拟合三句（AFML）。", en: "IID vs overfitting (AFML) three sentences." },
    ],
    quizTopics: [
      { zh: "标准差与方差", en: "Std vs variance" },
      { zh: "多重比较", en: "Multiple comparisons" },
    ],
    doneWhen: [
      { zh: "假阳性模拟+结论。", en: "False-positive sim + write-up." },
    ],
    methodTags: {
      classic: ["AFML multiple-testing spirit", "CFA-ish stats literacy"],
      niche: [],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "打印合成收益的均值/方差/分位并保存直方图 PNG；完成标准：数字与图和课内输出一致（同种子）。", en: "Print mean/var/quantiles and save histogram PNG; done when numbers/figure match the lesson (same seed)." } },
      { id: "ex2", text: { zh: "计算全样本相关与 63 日滚动相关并对比；完成标准：打印 full_corr 与滚动末五值。", en: "Compute full-sample vs 63-day rolling correlation; done when full_corr and last five rolling values print." } },
      { id: "ex3", text: { zh: "实现完整 100 次随机仓位多重检验循环并统计 |Sharpe|>2；完成标准：输出 trials/false_hits/max_abs_sharpe。", en: "Implement the full 100-trial random-position loop; done when trials/false_hits/max_abs_sharpe print." } },
      { id: "ex4", text: { zh: "用一次「看似显著」的单次试验演示 p 值误用；完成标准：写出原假设、p 值与为何不能直接宣称有效。", en: "Show p-value misuse on one seemingly significant trial; done when H0, p-value, and misuse note are written." } },
      { id: "ex5", text: { zh: "用三句话联系 IID 不成立与回测过拟合风险（参考 AFML 精神）；完成标准：三句都出现「波动聚集/多次试错/过拟合」之一。", en: "Three sentences linking non-IID to backtest overfitting (AFML spirit); done when each mentions clustering, many trials, or overfitting." } },
    ],
  },
  {
    slug: "basic-finance-markets",
    status: "ready",
    title: { zh: "基础金融与市场概念", en: "Basic finance & market concepts" },
    summary: { zh: "现货期货ETF、多空杠杆、复利、基准；可部分跳过。", en: "Spot/futures/ETF, long/short/leverage, compounding, benchmarks; partial skip OK." },
    hours: 5,
    difficulty: 1,
    skippable: true,
    skipNote: { zh: "能解释多空杠杆基准复利则测验通过可跳过。", en: "Skip after pretest if you explain long/short/leverage/benchmark/compounding." },
    hourBasis: "3h reading + 1.5h writing + 0.5h quiz",
    prereqs: [],
    goals: [
      { zh: "区分现货期货ETF直觉。", en: "Distinguish spot/futures/ETF." },
      { zh: "解释多空杠杆损益。", en: "Explain long/short/leverage P&L." },
      { zh: "选择简单基准。", en: "Pick a simple benchmark." },
    ],
    mustTeach: [
      { zh: "收益与风险成对；无免费午餐。", en: "Return/risk pair; no free lunch." },
      { zh: "基准须可投资可复现。", en: "Benchmark investable/reproducible." },
      { zh: "本课是研究流程非荐股。", en: "Research process not stock tips." },
    ],
    exercises: [
      { zh: "现货/期货/ETF 数例。", en: "Spot/futures/ETF numerics." },
      { zh: "多空 ±2% 损益。", en: "Long/short ±2% P&L." },
      { zh: "保证金与强平。", en: "Margin & liquidation." },
      { zh: "单利 vs 复利净值。", en: "Simple vs compound NAV." },
      { zh: "跟踪误差。", en: "Tracking error." },
      { zh: "市场/基准一页纸。", en: "Market/benchmark one-pager." },
    ],
    quizTopics: [
      { zh: "多空与杠杆", en: "Long/short leverage" },
      { zh: "基准选择", en: "Benchmark choice" },
    ],
    doneWhen: [
      { zh: "市场/基准一页纸。", en: "Market/benchmark one-pager." },
    ],
    methodTags: {
      classic: ["QuantStart beginner books", "Default: US-listed stocks/ETFs in USD", "Chinese supplement: JoinQuant 初识量化"],
      niche: [],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "分别用文字+数例说明现货、期货、ETF 的差异；完成标准：三类各有定义与一个数字例子。", en: "Explain spot vs futures vs ETF with a numeric example each; done when all three have definition+number." } },
      { id: "ex2", text: { zh: "手算并代码验证多头与空头在 ±2% 价格变动下的损益；完成标准：多空各一行损益表。", en: "Hand-calc and code long vs short P&L for ±2% moves; done when both sides have a P&L row." } },
      { id: "ex3", text: { zh: "保证金与强平数值例子（含维持保证金）；完成标准：给出初始保证金、价格跌幅触发强平的临界价。", en: "Margin/liquidation numeric example; done when initial margin and liquidation trigger price are stated." } },
      { id: "ex4", text: { zh: "单利 vs 复利净值对比（跑 03 脚本）；完成标准：终值与课内输出一致。", en: "Simple vs compound NAV via script 03; done when finals match the lesson output." } },
      { id: "ex5", text: { zh: "构造基准与组合收益，计算跟踪误差；完成标准：打印 TE 年化值并解释含义。", en: "Build benchmark vs portfolio returns and tracking error; done when annualized TE prints with meaning." } },
      { id: "ex6", text: { zh: "写「市场/基准」一页纸（可投资、可复现、事先指定）；完成标准：含市场、基准、频率、摩擦四节。", en: "Market/benchmark one-pager (investable, reproducible, pre-specified); done with market, benchmark, frequency, frictions." } },
    ],
  },
];

const phase_P1_lessons: Lesson[] = [
  {
    slug: "markets-language",
    status: "ready",
    title: { zh: "市场与交易语言", en: "Markets & trading vocabulary" },
    summary: { zh: "假设→信号→风险→归因；Alpha/Beta；可复现。", en: "Hypothesis→signal→risk→attribution; Alpha/Beta; reproducibility." },
    hours: 5.5,
    difficulty: 2,
    skippable: false,
    hourBasis: "2h concepts + 2.5h exercises + 0.5h quiz + 0.5h ETF NAV/premium-discount (Rule 6c-11)",
    prereqs: ["basic-finance-markets"],
    goals: [
      { zh: "三句话研究目标。", en: "Three-sentence research goal." },
      { zh: "区分 Alpha/Beta。", en: "Distinguish Alpha/Beta." },
      { zh: "列出市场摩擦。", en: "List frictions." },
    ],
    mustTeach: [
      { zh: "主目标是约束下风险调整后表现。", en: "Constrained risk-adjusted performance." },
      { zh: "程序员优势在工程化研究链。", en: "Programmer edge is research engineering." },
      { zh: "策略必须可复现。", en: "Strategies must be reproducible." },
    ],
    exercises: [
      { zh: "CSV→收益→净值。", en: "CSV→returns→NAV." },
      { zh: "研究目标三句话。", en: "Three-sentence goal." },
      { zh: "摩擦清单≥5。", en: "Friction list ≥5." },
      { zh: "Alpha/Beta 玩具。", en: "Alpha/Beta toy." },
      { zh: "约束下风险调整目标说明。", en: "Constrained risk-adjusted goal note." },
    ],
    quizTopics: [
      { zh: "Alpha/Beta", en: "Alpha/Beta" },
      { zh: "目标是否可检验", en: "Testable goal" },
    ],
    doneWhen: [
      { zh: "目标三句话+净值 notebook。", en: "Goal paragraph + NAV notebook." },
    ],
    methodTags: {
      classic: ["Canvas m1", "QuantStart SAT process"],
      niche: ["Awesome Systematic Trading (paperswithbacktest GitHub map)"],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "从 examples/p1/data/synthetic_ohlc_ba.csv 计算收益与净值；完成标准：final_nav 与课内一致。", en: "CSV→returns→NAV from examples/p1/data/synthetic_ohlc_ba.csv; done when final_nav matches the lesson." } },
      { id: "ex2", text: { zh: "写出三句话研究目标；完成标准：含市场/约束/成功标准。", en: "Write a three-sentence research goal; done when market/constraints/success appear." } },
      { id: "ex3", text: { zh: "摩擦清单≥5；完成标准：每条一句话定义。", en: "Friction list ≥5; done when each has a one-line definition." } },
      { id: "ex4", text: { zh: "复现 Alpha/Beta 玩具并报告 beta_hat；完成标准：写明 seed/n/Rf。", en: "Reproduce Alpha/Beta toy and report beta_hat; done when seed/n/Rf are stated." } },
      { id: "ex5", text: { zh: "说明主目标是约束下风险调整后表现；完成标准：≥3 句且提到约束与基准。", en: "Explain constrained risk-adjusted performance as the main goal; done when ≥3 sentences mention constraints and a benchmark." } },
    ],
  },
  {
    slug: "microstructure-orders",
    status: "ready",
    title: { zh: "微观结构与订单", en: "Microstructure & orders" },
    summary: { zh: "价差、mid、市价/限价、滑点；同bar零成本过乐观。", en: "Spread, mid, market/limit, slippage; same-bar zero-cost optimism." },
    hours: 11.5,
    difficulty: 2,
    skippable: false,
    hourBasis: "3h concepts + 3h exercises + 1h quiz + 2h US mechanics (T+1/cash vs margin/NBBO·SIP·IEX/sessions/Rule 611 proposal status/best execution) + 0.5h overnight trading & overnight LULD bands (planned 2026-12-06) + 0.25h Rule 612/610(c) version trap + 0.25h HK T+1 plan comparison (target H2 2028, not in effect) + 0.5h official close/closing auction/NYSE MOC cutoff + 0.5h tiered round lots & odd-lot quotes (2025-11-03 / 2026-04-27) + 0.25h SIPC account protection (SIPC limits; not FDIC) + 0.25h tokenized-stock venue (TSV) data separation (SEC 34-106402; TSV prints are not exchange prints)",
    prereqs: ["markets-language"],
    goals: [
      { zh: "手算 mid 与市价买 bps。", en: "Hand mid and market-buy bps." },
      { zh: "写成交成本假设一页。", en: "Write fill/cost sheet." },
      { zh: "对比收盘vs次日开盘。", en: "Compare close vs next-open." },
    ],
    mustTeach: [
      { zh: "mid=(bid+ask)/2。", en: "mid=(bid+ask)/2." },
      { zh: "市价买贴近 ask。", en: "Market buys lean ask." },
      { zh: "冲击/延迟只建直觉不做HFT配方。", en: "Impact/latency intuition only; no HFT recipes." },
    ],
    exercises: [
      { zh: "手算 mid/bps。", en: "Hand mid/bps." },
      { zh: "成本假设一页。", en: "Cost page." },
      { zh: "同 bar vs 诚实时点。", en: "Same-bar vs honest timing." },
      { zh: "跑脚本核净值。", en: "Run script; check NAVs." },
      { zh: "冲击/延迟边界说明。", en: "Impact/latency boundary note." },
      { zh: "T+1 交收日与上海时间交易时段手算。", en: "Hand-compute T+1 settlement and Shanghai-time sessions." },
      { zh: "隔夜交易时间换算与 Rule 612 合规日。", en: "Overnight time conversion and the Rule 612 compliance date." },
      { zh: "收盘竞价截止时间与分档整手。", en: "Closing-auction cutoff and tiered round lots." },
    ],
    quizTopics: [
      { zh: "市价单成交侧", en: "Market-buy side" },
      { zh: "价差是否成本", en: "Spread as cost" },
    ],
    doneWhen: [
      { zh: "成本假设一页+测验。", en: "Cost page + quiz." },
    ],
    methodTags: {
      classic: ["Canvas m2", "NYU MATH-GA 2708"],
      niche: [],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "手算 mid 与市价买 bps；完成标准：写出 mid 与 bps。", en: "Hand mid and market-buy bps; done when both numbers are written." } },
      { id: "ex2", text: { zh: "写成交成本假设一页；完成标准：含半价差/滑点/佣金/往返。", en: "Cost assumption one-pager; done when half-spread/slippage/commission/round-trip appear." } },
      { id: "ex3", text: { zh: "对比同 bar vs shift(1)/次日开盘；完成标准：点名 LOOK-AHEAD。", en: "Contrast same-bar vs shift(1)/next-open; done when LOOK-AHEAD is named." } },
      { id: "ex4", text: { zh: "跑 02 脚本核对乐观 vs 诚实净值；完成标准：与课内输出一致。", en: "Run script 02; done when optimistic vs honest NAVs match the lesson." } },
      { id: "ex5", text: { zh: "说明冲击/延迟只留直觉；完成标准：≥2 句且拒绝 HFT 配方。", en: "Why impact/latency stay intuitive; done when ≥2 sentences refuse an HFT recipe." } },
      { id: "ex-us1", text: { zh: "运行 05 脚本并手算 2026-11-25/11-27 交收日；完成标准：一致并解释感恩节。", en: "Run script 05 and hand-compute settlement for 2026-11-25/11-27; done when they match and Thanksgiving is explained." } },
      { id: "ex-overnight", text: { zh: "运行前读隔夜与版本陷阱一节，换算周一 21:00 ET；完成标准：北京时间周二 10:00、交易日周二，并引用 34-105656。", en: "Read the overnight & version-trap section and convert Monday 21:00 ET; done when Beijing Tuesday 10:00, trade date Tuesday, and 34-105656 is cited." } },
      { id: "ex-close", text: { zh: "运行 06 脚本，写出 NYSE 按收盘价成交的信号截止时间（15:50 ET，北京时间次日 03:50/04:50）和 250.01/1,000.01 美元的一手股数；完成标准：40/10 股，与输出一致。", en: "Run script 06; state the NYSE close-fill signal cutoff (15:50 ET, 03:50/04:50 next day Beijing) and the round lot at $250.01/$1,000.01; done when 40/10 shares match the output." } },
    ],
  },
  {
    slug: "returns-vol-corr",
    status: "ready",
    title: { zh: "收益、波动与相关", en: "Returns, volatility & correlation" },
    summary: { zh: "年化、夏普、MDD、滚动统计；压力期相关。", en: "Annualization, Sharpe, MDD, rolling stats; stress corr." },
    hours: 9,
    difficulty: 2,
    skippable: false,
    hourBasis: "3h formulas + 4h coding + 1h quiz + 0.5h leveraged/inverse ETF daily reset + 0.5h risk-free rate from T-bill quotes (TreasuryDirect price formula, ~3:30 PM quote time)",
    prereqs: ["python-pandas-timeseries", "stats-probability-basics", "markets-language"],
    goals: [
      { zh: "正确年化波动。", en: "Annualize vol correctly." },
      { zh: "实现夏普与MDD。", en: "Implement Sharpe and MDD." },
      { zh: "展示滚动相关升高。", en: "Show rolling corr rise." },
    ],
    mustTeach: [
      { zh: "σ_ann≈σ_day×√252。", en: "σ_ann≈σ_day×√252." },
      { zh: "夏普需声明频率与Rf。", en: "Sharpe needs frequency and Rf." },
      { zh: "回撤路径依赖。", en: "Drawdown path-dependent." },
    ],
    exercises: [
      { zh: "实现 max_drawdown。", en: "Implement max_drawdown." },
      { zh: "滚动波动图。", en: "Rolling vol plot." },
      { zh: "滚动相关+压力标注。", en: "Rolling corr + stress mark." },
      { zh: "双 Rf 夏普。", en: "Sharpe at two Rf." },
      { zh: "路径依赖三句。", en: "Path-dependence three sentences." },
    ],
    quizTopics: [
      { zh: "年化因子", en: "Annualization factor" },
      { zh: "夏普定义", en: "Sharpe definition" },
    ],
    doneWhen: [
      { zh: "可复用指标函数+测验。", en: "Reusable metrics + quiz." },
    ],
    methodTags: {
      classic: ["Canvas m3", "QuantStart performance", "Chinese supplement: JoinQuant returns/risk tutorial"],
      niche: [],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "实现 max_drawdown(nav)；完成标准：与课内 MDD 一致。", en: "Implement max_drawdown(nav); done when MDD matches the lesson." } },
      { id: "ex2", text: { zh: "画滚动 21 日年化波动并保存 PNG；完成标准：文件在 public/p1/。", en: "Plot 21d ann. vol PNG; done when the file is under public/p1/." } },
      { id: "ex3", text: { zh: "滚动相关+压力窗标注；完成标准：打印压力窗均值相关。", en: "Rolling corr + stress mark; done when stress-window mean corr prints." } },
      { id: "ex4", text: { zh: "Rf=0 与 Rf_daily=0.0001 各算夏普；完成标准：两数并写明参数。", en: "Sharpe at Rf=0 and Rf_daily=0.0001; done when both numbers and params are written." } },
      { id: "ex5", text: { zh: "三句话解释回撤路径依赖；完成标准：提到顺序/峰值。", en: "Three sentences on path-dependent drawdown; done when order/peaks are mentioned." } },
    ],
  },
  {
    slug: "eval-lab",
    status: "ready",
    title: { zh: "评估实验：基准与诚实指标", en: "Evaluation lab: benchmarks & honest metrics" },
    summary: { zh: "成本后指标表；玩具信号 vs 买入持有。", en: "Net-of-cost table; toy signal vs buy-and-hold." },
    hours: 7,
    difficulty: 2,
    skippable: false,
    hourBasis: "1.5h concepts + 3h lab + 0.5h PyFolio map + 0.5h base-rate pointer + 1.5h quiz",
    prereqs: ["returns-vol-corr", "microstructure-orders"],
    goals: [
      { zh: "做成本后对照表。", en: "Build net-of-cost table." },
      { zh: "解释胜率≠好策略。", en: "Win rate ≠ good strategy." },
    ],
    mustTeach: [
      { zh: "只报毛收益不诚实。", en: "Gross-only dishonest." },
      { zh: "换手放大成本。", en: "Turnover amplifies costs." },
    ],
    exercises: [
      { zh: "成本后对照表。", en: "Net-of-cost table." },
      { zh: "滑点升档。", en: "Slippage bump." },
      { zh: "三句结论。", en: "Three-sentence conclusion." },
      { zh: "年化换手。", en: "Annualized turnover." },
      { zh: "基准必要性。", en: "Why benchmarks." },
    ],
    quizTopics: [
      { zh: "为何需要基准", en: "Why benchmarks" },
      { zh: "换手与成本", en: "Turnover and costs" },
    ],
    doneWhen: [
      { zh: "对照表+三句结论。", en: "Table + three-sentence conclusion." },
    ],
    methodTags: {
      classic: ["Canvas eval", "pyfolio tear-sheet docs", "Chinese supplement: JoinQuant 策略评价"],
      niche: ["@FG731314 good-strategy traits (X post 2115609441748001008)"],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "复现成本后指标对照表；完成标准：含 buy&hold 与至少两档成本。", en: "Reproduce net-of-cost metric table; done when buy&hold and ≥2 cost levels appear." } },
      { id: "ex2", text: { zh: "滑点升档（如再加 10 bps）；完成标准：新行+一句结论。", en: "Slippage bump (e.g. add 10 bps); done when a new row + one-sentence conclusion appear." } },
      { id: "ex3", text: { zh: "写三句结论（毛vs净、换手、胜率陷阱）；完成标准：三句都出现。", en: "Three-sentence conclusion (gross vs net, turnover, win-rate trap); done when all three appear." } },
      { id: "ex4", text: { zh: "报告年化换手；完成标准：与课内量级一致。", en: "Report annualized turnover; done when it matches the lesson’s order of magnitude." } },
      { id: "ex5", text: { zh: "说明为何需要基准；完成标准：≥2 句提到相对评价。", en: "Why benchmarks are required; done when ≥2 sentences mention relative evaluation." } },
    ],
  },
];

const phase_P2_lessons: Lesson[] = [
  {
    slug: "data-cleaning",
    status: "ready",
    title: { zh: "数据与清洗", en: "Data & cleaning" },
    summary: { zh: "复权、停牌、缺失、幸存者、PIT；mask-first 反上游污染；数据说明书。", en: "Adjustments,halts,missingness,survivorship,PIT; mask-first vs upstream contamination; data sheet." },
    hours: 27.75,
    difficulty: 3,
    skippable: false,
    hourBasis: "5h concepts + 6h pipeline lab incl mask-first + 2h info-bars + 1h crypto-PIT + 3h docs/quiz + 2h data-versions/corporate-actions/calendar lab + 3h US data sources/licensing/PIT lab (EDGAR/FRED terms R16/Ken French/CRSP/yfinance/Massive/Alpaca) + 2h corporate actions & delisting (R21) + 1h ALFRED revision as-of + 0.5h dividend dates under T+1 (investor.gov) + 0.25h yfinance auto_adjust version trap + 0.5h filing deadlines & EDGAR 5:30pm rule (10-K/10-Q/8-K/13F) + 0.5h delisting returns & permanent IDs (CRSP CIZ) + 0.5h spin-offs & mergers in price series (CRSP split events, DisPERMNO, Form 8937 timing) + 0.5h insider & large-holder filing lags (Form 4 / 13D / 13G, FPI insiders from 2026-03-18)",
    prereqs: ["eval-lab"],
    goals: [
      { zh: "版本化下载与哈希。", en: "Version downloads and hashes." },
      { zh: "举例幸存者偏差。", en: "Survivorship examples." },
      { zh: "写数据说明书。", en: "Write data sheet." },
    ],
    mustTeach: [
      { zh: '玩具协议保守设定触限收盘价对指定方向/数量不可执行，且不可在行过滤前进入滚动算子（mask-first）；这不是触限即无成交的定律，信息可用性、信息质量与按方向/数量的可执行性分开判断。', en: 'The toy protocol conservatively treats limit closes as non-executable for the given side/size and keeps them out of rolling ops before row filters (mask-first); this is not a law that touching the limit means no fill — judge information availability, information quality and side/size executability separately.' },
      { zh: "今日成分≠历史宇宙。", en: "Today's constituents ≠ historical universe." },
      { zh: "基本面需PIT。", en: "Fundamentals need PIT." },
      { zh: "时区混乱可前瞻一天。", en: "Timezone mess can lookahead a day." },
    ],
    exercises: [
      { zh: "reindex+缺失断言；完成标准：missing=0 且 ASSERT。", en: "reindex+missingness assert; done when missing=0 and ASSERT." },
      { zh: "复权对照；完成标准：拆分日 raw/adj 收益。", en: "Adj vs raw; done when split-day raw/adj returns are stated." },
      { zh: "数据说明书四节；完成标准：来源/字段/时区/宇宙。", en: "Data sheet four sections; done when source/fields/timezone/universe appear." },
      { zh: "幸存者均值对比；完成标准：两均值与课内一致。", en: "Survivorship means; done when both means match the lesson." },
      { zh: "说明 PIT 滞后；完成标准：lag=5 + lookahead 一句。", en: "PIT lag note; done when lag=5 and a look-ahead sentence appear." },
      { zh: "信息 bar 时钟；完成标准：与课内表一致。", en: "Info-bar clocks; done when counts match the lesson table." },
      { zh: "跑 mask-first 玩具；完成标准：表观 vs 可实现 IC、MA 草图、三 mask（obs/quality/trade[t,i,side,size]）ASSERT_A–E 与 ASSERT_mask_first_demo_ok。", en: "Run mask-first toy; done when apparent vs realisable IC, MA sketch, three-mask (obs/quality/trade[t,i,side,size]) ASSERT_A–E and ASSERT_mask_first_demo_ok print." },
      { zh: "数据版本/公司行为/交易日历实验。", en: "Data versions / corporate actions / calendar lab." },
      { zh: "三个数据源的许可与可用时间行。", en: "Licence and availability rows for three sources." },
      { zh: "分红日期与 yfinance 返回形状。", en: "Dividend dates and yfinance return shapes." },
    ],
    quizTopics: [
      { zh: "幸存者偏差", en: "Survivorship" },
      { zh: "PIT含义", en: "PIT meaning" },
      { zh: "上游污染 / mask-first", en: "Upstream contamination / mask-first" },
    ],
    doneWhen: [
      { zh: "管线可复跑+说明书。", en: "Rerunnable pipeline + sheet." },
    ],
    methodTags: {
      classic: ["Canvas m4", "QuantStart securities master", "Qlib data layer", "US source map: SEC EDGAR / ALFRED / Ken French / CRSP docs", "Chinese supplement: JoinQuant data docs"],
      niche: ["@pyquantnews 45 APIs (status/2116517809920327801 → public-apis finance)", "OpenBB quantitative docs", "Binance Vision + @sera00111 crypto data notes"],
      frontier: ["Mask-first / upstream contamination arXiv:2507.07107 (optional conservative protocol + diagnosis only; REJECT headline Sharpes)", "Alt-data awareness; deeper in P8"],
    },
    tasks: [
      { id: "ex1", text: { zh: "reindex+缺失断言；完成标准：missing=0 且 ASSERT。", en: "reindex+missingness assert; done when missing=0 and ASSERT." } },
      { id: "ex2", text: { zh: "复权对照；完成标准：拆分日 raw/adj 收益。", en: "Adj vs raw; done when split-day raw/adj returns are stated." } },
      { id: "ex3", text: { zh: "数据说明书四节；完成标准：来源/字段/时区/宇宙。", en: "Data sheet four sections; done when source/fields/timezone/universe appear." } },
      { id: "ex4", text: { zh: "幸存者均值对比；完成标准：两均值与课内一致。", en: "Survivorship means; done when both means match the lesson." } },
      { id: "ex5", text: { zh: "说明 PIT 滞后；完成标准：lag=5 + lookahead 一句。", en: "PIT lag note; done when lag=5 and a look-ahead sentence appear." } },
      { id: "ex6", text: { zh: "信息 bar 时钟；完成标准：与课内表一致。", en: "Info-bar clocks; done when counts match the lesson table." } },
      { id: "ex7", text: { zh: "跑 mask-first 玩具；完成标准：表观 vs 可实现 IC、MA 草图、三 mask（obs/quality/trade[t,i,side,size]）ASSERT_A–E 与 ASSERT_mask_first_demo_ok。", en: "Run mask-first toy; done when apparent vs realisable IC, MA sketch, three-mask (obs/quality/trade[t,i,side,size]) ASSERT_A–E and ASSERT_mask_first_demo_ok print." } },
      { id: "ex8", text: { zh: "跑数据版本/公司行为/日历实验；完成标准：口径差≈−18.28bp、拆分raw/adj、日历交集，并补说明书三行。", en: "Run data-version/corporate-action/calendar lab; done when ≈−18.28bp convention gap, split raw/adj, calendar intersection print and data sheet gains three lines." } },
      { id: "ex-us-src", text: { zh: "为三个数据源写 source/licence/availability_ts/allowed_use_checked_on；完成标准：FRED 写明服务条款、yfinance 写明仅个人使用。", en: "Write source/licence/availability_ts/allowed_use_checked_on for three sources; done when FRED notes service terms and yfinance notes personal use only." } },
      { id: "ex-us-ca", text: { zh: "解释 05 脚本 D 节分红重复计入的 0.0230；完成标准：点出重复步骤。", en: "Explain the 0.0230 double-counted dividend in section D of script 05; done when the duplicate step is named." } },
      { id: "ex-div", text: { zh: "运行 08 脚本，写出周日登记日与 30% 特别分红的除息日，以及哪种 yfinance 调用返回 Adj Close；完成标准：2026-03-13、2026-03-18、auto_adjust=False。", en: "Run script 08; give the ex-dates for a Sunday record date and a 30% dividend, and which yfinance call returns Adj Close; done when 2026-03-13, 2026-03-18 and auto_adjust=False." } },
    ],
  },
  {
    slug: "backtest-traps",
    status: "ready",
    title: { zh: "回测陷阱与过拟合审讯", en: "Backtest traps & overfitting interrogation" },
    summary: { zh: "前瞻、walk-forward、PSR/DSR、试验次数、幸存者回顾。", en: "Lookahead,walk-forward,PSR/DSR,trial counts,survivorship recap." },
    hours: 29.25,
    difficulty: 4,
    skippable: false,
    hourBasis: "5h concepts + 19h multi-labs (CPCV + one-switch + PBO/CSCV + admission gates) + 4h write-up + 0.5h index membership as-of (Russell semi-annual 2026) + 0.25h FOMC release times as event timestamps + 0.5h IPO data traps (offering price vs fill, short history, lock-ups) — HEAVY",
    prereqs: ["data-cleaning", "stats-probability-basics"],
    goals: [
      { zh: "作弊vs诚实对照。", en: "Cheat vs honest controls." },
      { zh: "样本外/walk-forward。", en: "OOS/walk-forward." },
      { zh: "PSR/DSR 与试验次数。", en: "PSR/DSR and trial counts." },
    ],
    mustTeach: [
      { zh: "未shift用当日收益=前瞻。", en: "Same-bar return without shift=lookahead." },
      { zh: "多重试错制造虚假发现；记录 N。", en: "Multiple trials → false discoveries; log N." },
      { zh: "冻结规则后再看样本外；walk-forward 表。", en: "Freeze rules before OOS; walk-forward table." },
      { zh: "PSR/DSR：DSR 随试验数 N 下降。", en: "PSR/DSR: DSR falls as trial count N grows." },
      { zh: "TEMP_CENTER/EXEC_OPEN 一键泄漏增益（arXiv:2605.23959）。", en: "TEMP_CENTER/EXEC_OPEN one-switch Leakage Gain (arXiv:2605.23959)." },
    ],
    exercises: [
      { zh: "均线作弊/诚实；完成标准：两套夏普/净值与课内一致。", en: "MA cheat/honest; done when both Sharpe/NAV match the lesson." },
      { zh: "Walk-forward 表；完成标准：逐折 + 训练/测试均值。", en: "Walk-forward table; done when per-fold + mean train/test print." },
      { zh: "PSR/DSR 随 N；完成标准：表 + dsr_vs_N.png 且 DSR 下降。", en: "PSR/DSR vs N; done when table + dsr_vs_N.png and DSR falls." },
      { zh: "假阳性零假设上下文；完成标准：SE≈0.918、期望≈3.07 与 mean_false_hits。", en: "False-hit null context; done when SE≈0.918, expected≈3.07, and mean_false_hits." },
      { zh: "幸存者/数据挖掘回顾并链到 data-cleaning。", en: "Survivorship/snooping recap + link to data-cleaning." },
      { zh: "（可选）purge/embargo；完成标准：打印计数。", en: "(Optional) purge/embargo; done when counts print." },
    ],
    quizTopics: [
      { zh: "lookahead定义", en: "Lookahead def" },
      { zh: "为何记录试验次数", en: "Why log trials" },
      { zh: "walk-forward目的", en: "Walk-forward purpose" },
      { zh: "PSR/DSR", en: "PSR/DSR" },
    ],
    doneWhen: [
      { zh: "陷阱报告含 walk-forward、PSR/DSR 与对照。", en: "Trap report with walk-forward, PSR/DSR, and controls." },
    ],
    methodTags: {
      classic: ["Canvas m5", "Backtest interrogation discipline", "Chinese supplement: JoinQuant 审讯室 posts", "AFML ch.7/14", "Bailey-LdP 2012 PSR", "Bailey-LdP 2014 DSR", "@AfuOnTheWay三坑"],
      niche: [],
      frontier: ["Quant-Arena sealed hold-out (arXiv:2610.30113)", "When Alpha Disappears one-switch (arXiv:2605.23959)"],
    },
    tasks: [
      { id: "ex1", text: { zh: "均线作弊/诚实；完成标准：两套夏普/净值与课内一致。", en: "MA cheat/honest; done when both Sharpe/NAV match the lesson." } },
      { id: "ex2", text: { zh: "Walk-forward 表；完成标准：逐折 + 训练/测试均值。", en: "Walk-forward table; done when per-fold + mean train/test print." } },
      { id: "ex3", text: { zh: "PSR/DSR 随 N；完成标准：表 + dsr_vs_N.png 且 DSR 下降。", en: "PSR/DSR vs N; done when table + dsr_vs_N.png and DSR falls." } },
      { id: "ex4", text: { zh: "假阳性零假设上下文；完成标准：SE≈0.918、期望≈3.07 与 mean_false_hits。", en: "False-hit null context; done when SE≈0.918, expected≈3.07, and mean_false_hits." } },
      { id: "ex5", text: { zh: "幸存者/数据挖掘回顾并链到 data-cleaning。", en: "Survivorship/snooping recap + link to data-cleaning." } },
      { id: "ex6", text: { zh: "（可选）purge/embargo；完成标准：打印计数。", en: "(Optional) purge/embargo; done when counts print." } },
    ],

  },
  {
    slug: "costs-in-backtest",
    status: "ready",
    title: { zh: "成本写入回测", en: "Costs in the backtest" },
    summary: { zh: "四段成本+√冲击；堆叠分解与容量。", en: "Four-part costs+√ impact; stacked breakdown & capacity." },
    hours: 6.75,
    difficulty: 3,
    skippable: false,
    hourBasis: "2h concepts + 3.5h coding + 0.5h quiz + 0.75h Rule 605 effective spread (FAQ Example 27-1, covered-order filters)",
    prereqs: ["backtest-traps"],
    goals: [
      { zh: "实现四段成本与堆叠分解。", en: "Implement four-part costs and stacked breakdown." },
      { zh: "容量敏感性图。", en: "Capacity sensitivity chart." },
    ],
    mustTeach: [
      { zh: "零成本曲线≠实盘论据。", en: "Zero-cost ≠ live evidence." },
      { zh: "成本四段：佣金、半价差、滑点、√冲击。", en: "Four parts: commission, half-spread, slippage, √ impact." },
      { zh: "容量随资金放大冲击。", en: "Capacity: impact grows with capital." },
    ],
    exercises: [
      { zh: "四段成本各一例；完成标准：佣金/半价差/滑点/√冲击数字。", en: "Four-part costs; done when commission/half-spread/slippage/√ impact numbers appear." },
      { zh: "堆叠分解图；完成标准：cost_breakdown.png。", en: "Stacked breakdown; done when cost_breakdown.png exists." },
      { zh: "合并 bps 阶梯；完成标准：≥3 档单调变差。", en: "Combined bps ladder; done when ≥3 tiers worsen." },
      { zh: "容量表+图；完成标准：资金升则净夏普降。", en: "Capacity table+chart; done when Sharpe falls as capital rises." },
      { zh: "引用 Almgren 2005 √ vs 3/5；完成标准：一句准确。", en: "Cite Almgren 2005 √ vs 3/5; done when one accurate sentence appears." },
      { zh: "Rule 605 有效价差手算。", en: "Hand-compute a Rule 605 effective spread." },
    ],
    quizTopics: [
      { zh: "四段成本", en: "Four cost parts" },
      { zh: "平方根冲击与容量", en: "Sqrt impact & capacity" },
    ],
    doneWhen: [
      { zh: "四段净回测+分解+容量图可运行。", en: "Four-part net backtest + breakdown + capacity charts run." },
    ],
    methodTags: {
      classic: ["Canvas costs", "QuantStart TCA", "NYU TCA themes", "Almgren et al. 2005 market impact"],
      niche: [],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "四段成本各一例；完成标准：佣金/半价差/滑点/√冲击数字。", en: "Four-part costs; done when commission/half-spread/slippage/√ impact numbers appear." } },
      { id: "ex2", text: { zh: "堆叠分解图；完成标准：cost_breakdown.png。", en: "Stacked breakdown; done when cost_breakdown.png exists." } },
      { id: "ex3", text: { zh: "合并 bps 阶梯；完成标准：≥3 档单调变差。", en: "Combined bps ladder; done when ≥3 tiers worsen." } },
      { id: "ex4", text: { zh: "容量表+图；完成标准：资金升则净夏普降。", en: "Capacity table+chart; done when Sharpe falls as capital rises." } },
      { id: "ex5", text: { zh: "引用 Almgren 2005 √ vs 3/5；完成标准：一句准确。", en: "Cite Almgren 2005 √ vs 3/5; done when one accurate sentence appears." } },
      { id: "ex-605", text: { zh: "运行 07 脚本手算例 27-1；完成标准：0.24 美元、解释带符号 ES 与 −2.8555 bps，并列出三类排除订单和两类 NMLO 例外。", en: "Run script 07 and hand-compute Example 27-1; done when $0.24, the signed ES and −2.8555 bps are explained, and three excluded order types plus two NMLO exceptions are listed." } },
    ],

  },
  {
    slug: "engines-vectorized-event",
    status: "ready",
    title: { zh: "回测引擎：向量化与事件驱动", en: "Backtest engines: vectorized & event-driven" },
    summary: { zh: "最小事件引擎匹配向量化；止损；库对照。", en: "Minimal event engine matches vectorized; stops; library compare." },
    hours: 8,
    difficulty: 3,
    skippable: false,
    hourBasis: "3h concepts + 4h compare lab + 1h docs",
    prereqs: ["costs-in-backtest"],
    goals: [
      { zh: "实现事件/订单/成交并匹配向量化。", en: "Implement events/orders/fills matching vectorized." },
      { zh: "演示止损需要事件引擎。", en: "Show stops need an event engine." },
      { zh: "按场景对照四库。", en: "Compare four libraries by use case." },
    ],
    mustTeach: [
      { zh: "引擎选择=成交与日历假设。", en: "Engine choice = fill/calendar assumptions." },
      { zh: "事件净值应能对齐诚实向量化。", en: "Event NAV should match honest vectorized." },
      { zh: "止损/限价等路径依赖需要事件。", en: "Stops/limits need events." },
      { zh: "同构引擎降低研究≠实盘缝隙（概念）。", en: "Isomorphic engines reduce research≠live gap." },
    ],
    exercises: [
      { zh: "两向量化成交净值；完成标准：解释同日vs次日开盘。", en: "Two vectorized fill NAVs; done when same-bar vs next-open explained." },
      { zh: "事件引擎匹配；完成标准：max diff≈0。", en: "Event engine match; done when max diff≈0." },
      { zh: "止损演示；完成标准：stop_exits+两净值。", en: "Stop demo; done when stop_exits + both NAVs print." },
      { zh: "四库对照各一句+链接。", en: "Four-library compare with links." },
      { zh: "假设段含成交/日历/止损/时区。", en: "Assumptions paragraph with fill/calendar/stop/timezone." },
    ],
    quizTopics: [
      { zh: "向量化乐观默认", en: "Optimistic vectorized defaults" },
      { zh: "事件驱动解决什么", en: "What event-driven buys" },
      { zh: "止损为何难向量化", en: "Why stops resist pure vectors" },
    ],
    doneWhen: [
      { zh: "匹配assert+止损演示+库对照。", en: "Match assert + stop demo + library compare." },
    ],
    methodTags: {
      classic: ["VectorBT", "Zipline Reloaded", "Backtrader", "Canvas engines"],
      niche: ["@RoundtableSpace engine list (Nautilus/Hummingbot/vectorbt)"],
      frontier: ["NautilusTrader shared kernel (architecture docs)"],
    },
    tasks: [
      { id: "ex1", text: { zh: "两向量化成交净值；完成标准：解释同日vs次日开盘。", en: "Two vectorized fill NAVs; done when same-bar vs next-open explained." } },
      { id: "ex2", text: { zh: "事件引擎匹配；完成标准：max diff≈0。", en: "Event engine match; done when max diff≈0." } },
      { id: "ex3", text: { zh: "止损演示；完成标准：stop_exits+两净值。", en: "Stop demo; done when stop_exits + both NAVs print." } },
      { id: "ex4", text: { zh: "四库对照各一句+链接。", en: "Four-library compare with links." } },
      { id: "ex5", text: { zh: "假设段含成交/日历/止损/时区。", en: "Assumptions paragraph with fill/calendar/stop/timezone." } },
    ],

  },
];

const phase_P3_lessons: Lesson[] = [
  {
    slug: "momentum-trend",
    status: "ready",
    title: { zh: "动量与趋势", en: "Momentum & trend" },
    summary: { zh: "时序/截面动量、12-1 精神、换手与波动目标。", en: "TS/CS momentum, 12-1 spirit, turnover and vol targeting." },
    hours: 8,
    difficulty: 3,
    skippable: false,
    hourBasis: "3h concepts + 4.5h labs + 0.5h quiz",
    prereqs: ["engines-vectorized-event"],
    goals: [
      { zh: "双均线与简化动量对照（含成本）。", en: "Dual-MA vs simplified momentum (net of costs)." },
      { zh: "报告换手与分年。", en: "Report turnover and by-year." },
    ],
    mustTeach: [
      { zh: "跳过近窗减弱短期反转（期望值动机）。", en: "Skip-window dampens short-term reversal (EV motive)." },
      { zh: "拥挤与换手侵蚀优势。", en: "Crowding/turnover erode edges." },
      { zh: "TSMOM（Moskowitz et al.）≠ 截面动量（JT）。", en: "TSMOM (Moskowitz et al.) ≠ cross-sectional momentum (JT)." },
    ],
    exercises: [
      { zh: "双均线vs动量净夏普表。", en: "Dual-MA vs mom net-SR table." },
      { zh: "波动目标10%。", en: "10% vol target." },
      { zh: "分年表（解释 NaN）。", en: "By-year table (explain NaN)." },
    ],
    quizTopics: [
      { zh: "12-1动机", en: "12-1 motive" },
      { zh: "时序vs截面", en: "TS vs CS" },
      { zh: "换手与成本", en: "Turnover and costs" },
    ],
    doneWhen: [
      { zh: "两套动量结果含成本与 OOS。", en: "Two momentum results net of costs with OOS." },
    ],
    methodTags: {
      classic: ["Canvas m6", "Jegadeesh-Titman 1993", "Moskowitz-Ooi-Pedersen 2012 TSMOM", "Stern trend", "Further reading: Ernest P. Chan, Algorithmic Trading (Wiley 2013, ISBN 978-1-118-46014-6)"],
      niche: ["quants.md trend cards as foils"],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "双均线vs动量净夏普表；完成标准：两净夏普+换手。", en: "Dual-MA vs mom table; done when both net SR + turnover print." } },
      { id: "ex2", text: { zh: "波动目标10%；完成标准：缩放净值/夏普。", en: "10% vol target; done when scaled NAV/SR print." } },
      { id: "ex3", text: { zh: "分年表；完成标准：年份行+NaN解释。", en: "By-year table; done when year rows + NaN explained." } },
      { id: "done1", text: { zh: "两套动量结果含成本与 OOS。", en: "Two momentum results net of costs with OOS." } },
    ],
  },
  {
    slug: "mean-reversion",
    status: "ready",
    title: { zh: "均值回归", en: "Mean reversion" },
    summary: { zh: "z-score开平仓、止损、趋势市失效。", en: "z-score entries, stops, failure in trends." },
    hours: 7,
    difficulty: 3,
    skippable: false,
    hourBasis: "2.5h concepts + 4h labs + 0.5h quiz",
    prereqs: ["momentum-trend"],
    goals: [
      { zh: "实现z规则。", en: "Implement z rules." },
      { zh: "写失效清单。", en: "Write invalidation list." },
    ],
    mustTeach: [
      { zh: "强趋势中回归易反复止损。", en: "In trends reversion dies by repeated stops." },
      { zh: "阈值再估计。", en: "Re-estimate thresholds." },
      { zh: "半衰期选回看/持有；z[t] 仅从 t+1 改仓。", en: "Half-life sets lookback/hold; z[t] changes position only from t+1." },
    ],
    exercises: [
      { zh: "z<-2/z>0 路径。", en: "z<-2 / z>=0 path." },
      { zh: "有无止损A/B。", en: "Stop A/B." },
      { zh: "失效清单≥5条。", en: "Invalidation list ≥5 bullets." },
    ],
    quizTopics: [
      { zh: "回归策略趋势市表现", en: "Reversion in trends" },
      { zh: "为何再估计阈值", en: "Why re-estimate" },
      { zh: "止损路径依赖", en: "Stop path dependence" },
    ],
    doneWhen: [
      { zh: "回归notebook+失效讨论。", en: "MR notebook + failure discussion." },
    ],
    methodTags: {
      classic: ["Canvas m7", "Stern counter-trend", "OU/AR(1) half-life", "Further reading: Ernest P. Chan, Algorithmic Trading (Wiley 2013, ISBN 978-1-118-46014-6)"],
      niche: ["quants.md reversal cards as foils"],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "z规则路径；完成标准：净夏普打印。", en: "z-rule path; done when net SR prints." } },
      { id: "ex2", text: { zh: "止损A/B；完成标准：两净值+stop_exits。", en: "Stop A/B; done when both NAVs + stop_exits." } },
      { id: "ex3", text: { zh: "失效清单≥5条。", en: "Invalidation list ≥5 bullets." } },
      { id: "done1", text: { zh: "回归notebook+失效讨论。", en: "MR notebook + failure discussion." } },
    ],
  },
  {
    slug: "pairs-stat-arb",
    status: "ready",
    title: { zh: "配对与统计套利入门", en: "Pairs & intro statistical arb" },
    summary: { zh: "价差、滚动对冲比、相关≠可交易。", en: "Spreads, rolling hedge, correlation≠tradeable." },
    hours: 14,
    difficulty: 3,
    skippable: false,
    hourBasis: "4h concepts + 5h lab + 1h write-up + 2h optional Kalman hedge ratio (filter vs smoother) + 1h US short-sale constraints (Reg SHO layers, borrow, dividends) + 1h short-side public data (FINRA 4560 short interest by publish date, short volume ≠ short interest, FTD balance; SR-FINRA-2026-012 withdrawn)",
    prereqs: ["mean-reversion"],
    goals: [
      { zh: "滚动beta价差。", en: "Rolling-beta spread." },
      { zh: "讨论腿断裂。", en: "Discuss broken legs." },
    ],
    mustTeach: [
      { zh: "高相关不足够。", en: "High corr insufficient." },
      { zh: "Engle–Granger 两步 + MacKinnon 临界值。", en: "Engle–Granger two-step + MacKinnon critical values." },
      { zh: "对冲比再估计；勿只做一次全样本协整。", en: "Re-estimate hedge; do not check coint only once in-sample." },
    ],
    exercises: [
      { zh: "滚动价差与z。", en: "Rolling spread and z." },
      { zh: "静态vs滚动。", en: "Static vs rolling." },
      { zh: "冲击/断腿说明。", en: "Shock/broken-leg note." },
      { zh: "（选修）Kalman动态对冲比filter vs smoother。", en: "(Optional) Kalman hedge ratio filter vs smoother." },
      { zh: "借券费敏感性。", en: "Borrow-fee sensitivity." },
      { zh: "做空公开数据的发布日对齐。", en: "Publish-date alignment for short-side data." },
    ],
    quizTopics: [
      { zh: "相关vs协整", en: "Corr vs cointegration" },
      { zh: "为何滚动估计", en: "Why rolling" },
      { zh: "双腿成本", en: "Two-leg costs" },
    ],
    doneWhen: [
      { zh: "含成本配对notebook。", en: "Costed pairs notebook." },
    ],
    methodTags: {
      classic: ["Canvas m8", "Stern spreads", "Engle-Granger / MacKinnon", "Further reading: Ernest P. Chan, Algorithmic Trading (Wiley 2013, ISBN 978-1-118-46014-6)"],
      niche: ["quants.md W13/W14 pairs foils"],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "滚动价差与z；完成标准：序列/图。", en: "Rolling spread and z; done when series/chart print." } },
      { id: "ex2", text: { zh: "静态vs滚动；完成标准：两净夏普。", en: "Static vs rolling; done when both net SR print." } },
      { id: "ex3", text: { zh: "冲击/断腿说明段。", en: "Shock/broken-leg paragraph." } },
      { id: "done1", text: { zh: "含成本配对notebook。", en: "Costed pairs notebook." } },
      { id: "ex4", text: { zh: "（选修）Kalman对冲比；完成标准：t=149 filtered/smoothed β与未来扰动测试两行。", en: "(Optional) Kalman hedge; done when t=149 filtered/smoothed β and the two future-perturbation lines print." } },
      { id: "ex-short-pit", text: { zh: "运行 07 脚本，把信号日改为 2026-10-26；完成标准：用到 2026-10-15 快照并解释 10-23 为何仍用 09-30。", en: "Run script 07 with signal date 2026-10-26; done when it uses the 2026-10-15 snapshot and you explain why 10-23 still uses 09-30." } },
      { id: "ex-us-short", text: { zh: "把 06 脚本借券费翻倍；完成标准：报告 constrained_pair 变化与方向。", en: "Double the borrow fee in script 06; done when the constrained_pair change and direction are reported." } },
    ],
  },
  {
    slug: "strategy-compare-lab",
    status: "ready",
    title: { zh: "策略对照实验", en: "Strategy comparison lab" },
    summary: { zh: "同一宇宙/成本/指标；复杂须胜过简单基准。", en: "Same universe/costs/metrics; complexity must beat baseline." },
    hours: 5,
    difficulty: 3,
    skippable: false,
    hourBasis: "1h framing + 3.5h report + 0.5h quiz",
    prereqs: ["momentum-trend", "mean-reversion", "pairs-stat-arb"],
    goals: [
      { zh: "三策略并排报告。", en: "Three-strategy report." },
      { zh: "判定是否胜过基准。", en: "Judge vs baseline." },
    ],
    mustTeach: [
      { zh: "控制隐藏假设；统一成本（配对含冲击）。", en: "Control hidden assumptions; one cost model (pairs include impact)." },
      { zh: "简单是基准线；显式 N 上算 DSR。", en: "Simple is the baseline; DSR with explicit trial count N." },
    ],
    exercises: [
      { zh: "三策略(+基准)报告。", en: "Three-strategy (+baseline) report." },
      { zh: "指定基准并判定。", en: "Name baseline and call." },
    ],
    quizTopics: [
      { zh: "对照实验要素", en: "Controlled comparison elements" },
      { zh: "相对vs绝对判定", en: "Relative vs absolute judgment" },
    ],
    doneWhen: [
      { zh: "对照报告入库。", en: "Comparison report filed." },
    ],
    methodTags: {
      classic: ["Canvas comparison spirit", "Same-protocol comparison rules", "Bailey-LdP DSR via P2", "Further reading: Ernest P. Chan, Algorithmic Trading (Wiley 2013, ISBN 978-1-118-46014-6)"],
      niche: ["Critique quants.md dumps as hypothesis sources only"],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "三策略(+基准)报告表。", en: "Three-strategy (+baseline) report table." } },
      { id: "ex2", text: { zh: "指定基准并用OOS净夏普判定。", en: "Name baseline and call with OOS net SR." } },
      { id: "done1", text: { zh: "对照报告入库。", en: "Comparison report filed." } },
    ],
  },
];

const phase_P4_lessons: Lesson[] = [
  {
    slug: "factor-workflow",
    status: "ready",
    title: { zh: "因子研究工作流", en: "Factor research workflow" },
    summary: { zh: "IC、分层、衰减、中性化直觉；拒绝堆参数。", en: "IC, quantiles, decay, neutralization; reject parameter stacking." },
    hours: 25,
    difficulty: 4,
    skippable: false,
    hourBasis: "5h concepts + 15h labs (incl Detzel + NMV 2016 taxonomy + w34898 + HXZ + admission) + 3h write-up + 1h crowding→LLM bridge — HEAVY + 1h US factor benchmark alignment (percent, missing markers, Mkt-RF+RF, compounding)",
    prereqs: ["strategy-compare-lab", "backtest-traps"],
    goals: [
      { zh: "实现Spearman IC。", en: "Implement Spearman IC." },
      { zh: "分层多空。", en: "Quantile long-short." },
      { zh: "真/假因子对照。", en: "True vs null factor." },
    ],
    mustTeach: [
      { zh: "IC=截面排序一致性；RankIC / ICIR / IC 衰减。", en: "IC=cross-sectional rank agreement; RankIC / ICIR / IC decay." },
      { zh: "因子构建：去极值、z 标准化、行业与市值中性化。", en: "Construction: winsorize, z-score, industry and mcap neutralization." },
      { zh: "分层多空 + 换手成本；Fama–MacBeth（及 FF3/FF5 文献）。", en: "Quantile L/S + turnover/costs; Fama–MacBeth (+ FF3/FF5 literature)." },
      { zh: "因子海市蜃楼与多重检验（Harvey–Liu–Zhu t>3）。", en: "Factor mirage & multiple testing (Harvey–Liu–Zhu t>3)." },
      { zh: "从经济假设出发；Alphalens/Qlib 风格工作流。", en: "Start from economic hypothesis; Alphalens/Qlib-style workflow." },
    ],
    exercises: [
      { zh: "ic(factor,fwd)。", en: "ic(factor,fwd)." },
      { zh: "分层净值。", en: "Quantile NAVs." },
      { zh: "打乱因子对照。", en: "Scrambled control." },
      { zh: "IC衰减图。", en: "IC decay chart." },
      { zh: "Ken French 格式对齐。", en: "Ken French format alignment." },
    ],
    quizTopics: [
      { zh: "Spearman IC", en: "Spearman IC" },
      { zh: "为何空因子对照", en: "Why null controls" },
      { zh: "IC衰减含义", en: "IC decay meaning" },
    ],
    doneWhen: [
      { zh: "IC+分层+空因子报告。", en: "IC+quantile+null report." },
    ],
    methodTags: {
      classic: ["Canvas m9", "AFML/Factor Mirage", "@alin_alphapilot IC-first", "Qlib Alpha158 ref"],
      niche: ["quant-wiki factor map (@bkdgiffug)"],
      frontier: ["Novy-Marx & Velikov RFS 2016 NBER w20721 taxonomy", "LLM formulaic alpha mining after this; formalized in P8", "Detzel–Novy-Marx–Velikov JF 2023 DOI 10.1111/jofi.13225"],
    },
    tasks: [
      { id: "ex1", text: { zh: "ic(factor,fwd)。", en: "ic(factor,fwd)." } },
      { id: "ex2", text: { zh: "分层净值。", en: "Quantile NAVs." } },
      { id: "ex3", text: { zh: "打乱因子对照。", en: "Scrambled control." } },
      { id: "ex4", text: { zh: "IC衰减图。", en: "IC decay chart." } },
      { id: "done1", text: { zh: "IC+分层+空因子报告。", en: "IC+quantile+null report." } },
      { id: "ex-us-ff", text: { zh: "运行 03 基准脚本并给出 2026-06 复利与相加差；完成标准：0.00011。", en: "Run benchmark script 03 and give the June 2026 compound-vs-sum gap; done when 0.00011." } },
    ],
  },
  {
    slug: "factor-portfolio-lab",
    status: "ready",
    title: { zh: "因子到组合实验", en: "Factor-to-portfolio lab" },
    summary: { zh: "换手、简单中性化、多因子合成诚实评估。", en: "Turnover, simple neutralization, honest multi-factor combo." },
    hours: 8,
    difficulty: 4,
    skippable: false,
    hourBasis: "2.5h concepts + 4.5h lab + 1h quiz",
    prereqs: ["factor-workflow"],
    goals: [
      { zh: "估计因子组合换手。", en: "Estimate factor-portfolio turnover." },
      { zh: "简易市值中性化示意。", en: "Simple size neutralization sketch." },
      { zh: "单因子vs等权多因子。", en: "Single vs EW multi-factor." },
    ],
    mustTeach: [
      { zh: '玩具净夏普≈3.67/≈4.36 是合成 MU — 不是实盘可复现夏普。', en: 'Toy net SR≈3.67/≈4.36 are synthetic MU — not live-reproducible Sharpes.' },
      { zh: "合成不自动提高可交易性。", en: "Combining ≠ auto tradeability." },
      { zh: "换手与成本再决定净收益（共享成本模型）。", en: "Turnover/costs decide net returns (shared cost model)." },
      { zh: "中性化前后对照；拥挤与衰减。", en: "Before/after neutralization; crowding and decay." },
    ],
    exercises: [
      { zh: "中性化前后IC。", en: "IC before/after neutralization." },
      { zh: "多因子等权对照。", en: "EW multi-factor control." },
      { zh: "换手-成本表。", en: "Turnover-cost table." },
    ],
    quizTopics: [
      { zh: "中性化目的", en: "Neutralization purpose" },
      { zh: "多因子过拟合风险", en: "Multi-factor overfitting" },
    ],
    doneWhen: [
      { zh: "因子→组合小报告。", en: "Factor→portfolio mini-report." },
    ],
    methodTags: {
      classic: ["Canvas m9 ext", "Qlib portfolio/backtest optional"],
      niche: [],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "中性化前后IC。", en: "IC before/after neutralization." } },
      { id: "ex2", text: { zh: "多因子等权对照。", en: "EW multi-factor control." } },
      { id: "ex3", text: { zh: "换手-成本表。", en: "Turnover-cost table." } },
      { id: "done1", text: { zh: "因子→组合小报告。", en: "Factor→portfolio mini-report." } },
    ],
  },
];

const phase_P5_lessons: Lesson[] = [
  {
    slug: "ml-leakage-control",
    status: "ready",
    title: { zh: "机器学习防泄漏", en: "ML anti-leakage" },
    summary: { zh: "时间切分、purge/embargo、分数差分、样本唯一性、完整元标签过滤、CPCV 复用提示。", en: "Time splits, purge/embargo, fracdiff, sample uniqueness, full meta-label filter, CPCV reuse note." },
    hours: 21,
    difficulty: 5,
    skippable: false,
    hourBasis: "6h AFML concepts + 12h labs (fracdiff/uniqueness/meta/CPCV + one-switch + KTD/Mirage pointers) + 3h write-up — HEAVY",
    prereqs: ["factor-workflow", "backtest-traps"],
    goals: [
      { zh: "演示shuffle泄漏。", en: "Demo shuffle leakage." },
      { zh: "时间切分并shift特征。", en: "Chronological split + shifted features." },
      { zh: "用IC而非仅准确率评价。", en: "Evaluate with IC not accuracy alone." },
    ],
    mustTeach: [
      { zh: "失败常在管线；禁止时序 shuffle。", en: "Failures often in pipelines; never shuffle time." },
      { zh: "完整 purged K-fold + embargo；scaler 仅 fit 训练折。", en: "Full purged K-fold + embargo; scalers fit on train fold only." },
      { zh: "标签：远期收益、三重势垒、元标签（AFML ch.3）。", en: "Labels: forward returns, triple-barrier, meta-labeling (AFML ch.3)." },
      { zh: "用 IC/净SR/DSR 评价，而非准确率。", en: "Evaluate with IC / net SR / DSR, not accuracy." },
    ],
    exercises: [
      { zh: "随机vs时间切分。", en: "Random vs time split." },
      { zh: "修复三处泄漏。", en: "Fix three planted leaks." },
      { zh: "用IC评价预测。", en: "Evaluate with IC." },
      { zh: "记录试验次数。", en: "Log trial counts." },
    ],
    quizTopics: [
      { zh: "为何不能shuffle", en: "Why not shuffle" },
      { zh: "purge解决什么", en: "What purge fixes" },
      { zh: "标签泄漏例子", en: "Label-leakage example" },
    ],
    doneWhen: [
      { zh: "防泄漏notebook+试验日志。", en: "Anti-leakage notebook + trial log." },
    ],
    methodTags: {
      classic: ["Canvas m10", "AFML labeling/CV", "ML4T notebooks"],
      niche: [],
      frontier: ["LLM-generated features still need these controls (bridge to P8)"],
    },
    tasks: [
      { id: "ex1", text: { zh: "随机vs时间切分。", en: "Random vs time split." } },
      { id: "ex2", text: { zh: "修复三处泄漏。", en: "Fix three planted leaks." } },
      { id: "ex3", text: { zh: "用IC评价预测。", en: "Evaluate with IC." } },
      { id: "ex4", text: { zh: "记录试验次数。", en: "Log trial counts." } },
      { id: "done1", text: { zh: "防泄漏notebook+试验日志。", en: "Anti-leakage notebook + trial log." } },
    ],
  },
  {
    slug: "modern-ml-pipelines",
    status: "ready",
    title: { zh: "现代ML量化流水线（Qlib等）", en: "Modern ML quant pipelines (Qlib et al.)" },
    summary: { zh: "可复现流水线；MDI/MDA/SHAP/SFI；Localformer/Transformer 对照箔；不神话深度学习。", en: "Reproducible pipelines; MDI/MDA/SHAP/SFI; Localformer/Transformer foil; no DL mythology." },
    hours: 11,
    difficulty: 4,
    skippable: false,
    hourBasis: "3h architecture + 5h mini-pipeline + 2h SFI/Transformer foil + 1h optional Qlib",
    prereqs: ["ml-leakage-control", "data-cleaning"],
    goals: [
      { zh: "特征→模型→预测→简单组合草图。", en: "Feature→model→pred→simple portfolio sketch." },
      { zh: "说明为何先树/线性再深度。", en: "Trees/linear before deep nets." },
      { zh: "（可选）跑通Qlib quickstart思路。", en: "(Optional) Qlib quickstart ideas." },
    ],
    mustTeach: [
      { zh: "流水线可版本化比花哨模型重要。", en: "Versioned pipelines > flashy models." },
      { zh: "Qlib Alpha158 + LGBModel；pandas 等价。", en: "Qlib Alpha158 + LGBModel; pandas equivalent." },
      { zh: "MDI/MDA/SHAP 与相关重复的替代效应；校准与下注。", en: "MDI/MDA/SHAP + substitution; calibration and bet sizing." },
      { zh: "公开数据≠可交易优势；TSFM 零样本常弱于树模型。", en: "Public data ≠ edge; zero-shot TSFMs often trail trees." },
    ],
    exercises: [
      { zh: "LightGBM/线性截面排序小实验。", en: "LightGBM/linear CS-rank mini-exp." },
      { zh: "（可选）读Qlib workflow配置。", en: "(Optional) read Qlib workflow config." },
      { zh: "泄漏检查清单。", en: "Leakage checklist." },
    ],
    quizTopics: [
      { zh: "流水线阶段顺序", en: "Pipeline stage order" },
      { zh: "简单模型优先理由", en: "Why simple models first" },
    ],
    doneWhen: [
      { zh: "可复现小流水线+检查清单。", en: "Reproducible mini-pipeline + checklist." },
    ],
    methodTags: {
      classic: ["Qlib Quick Start", "ML4T end-to-end", "Canvas m10"],
      niche: ["@quantscience_ stack", "ML4T high-engagement X posts"],
      frontier: ["Qlib Transformer/Localformer as optional controls under same anti-leakage protocol", "RD-Agent automation deferred to P8"],
    },
    tasks: [
      { id: "ex1", text: { zh: "LightGBM/线性截面排序小实验。", en: "LightGBM/linear CS-rank mini-exp." } },
      { id: "ex2", text: { zh: "（可选）读Qlib workflow配置。", en: "(Optional) read Qlib workflow config." } },
      { id: "ex3", text: { zh: "泄漏检查清单。", en: "Leakage checklist." } },
      { id: "done1", text: { zh: "可复现小流水线+检查清单。", en: "Reproducible mini-pipeline + checklist." } },
    ],
  },
];

const phase_P6_lessons: Lesson[] = [
  {
    slug: "portfolio-risk-sizing",
    status: "ready",
    title: { zh: "组合、风险与仓位", en: "Portfolio, risk & position sizing" },
    summary: {
      zh: "Kelly/半Kelly、波动目标、逆波动与ERC、HRP层级风险平价、MV vs 1/N、Ledoit–Wolf。",
      en: "Kelly/half-Kelly, vol targeting, inv-vol & ERC, HRP, MV vs 1/N, Ledoit–Wolf.",
    },
    hours: 23.75,
    difficulty: 4,
    skippable: false,
    hourBasis: "5h concepts + 13h labs (incl HRP + Brandt no-trade + alpha-decay band) + 4h writing + 1h weight-drift lab + 0.5h margin accounts (Reg T / FINRA 4210) + 0.25h portfolio margin (FINRA 4210(g) toy) — HEAVY",
    prereqs: ["returns-vol-corr", "strategy-compare-lab"],
    goals: [
      { zh: "三种仓位层对照。", en: "Compare three sizing layers." },
      { zh: "用破产模拟解释满Kelly危险。", en: "Explain full-Kelly danger with a ruin simulation." },
      { zh: "说明估计误差与1/N基准。", en: "State estimation error and the 1/N benchmark." },
    ],
    mustTeach: [
      { zh: "仓位是策略层；半Kelly或更保守（Kelly 1956；Thorp）。", en: "Sizing is a strategy layer; half-Kelly or more conservative (Kelly 1956; Thorp)." },
      { zh: "滞后波动目标；逆波动与ERC风险平价。", en: "Lagged vol targeting; inverse-vol and ERC risk parity." },
      { zh: "Markowitz MV + Michaud误差最大化；DeMiguel等2009的1/N；Ledoit–Wolf 2004 JPM+JMVA（sklearn LedoitWolf）样本外对照。", en: "Markowitz MV + Michaud error maximization; DeMiguel et al. 2009 1/N; Ledoit–Wolf 2004 JPM+JMVA (sklearn LedoitWolf) OOS." },
    ],
    exercises: [
      { zh: "固定/波动目标/回撤熔断。", en: "Fixed/vol-target/DD brake." },
      { zh: "Kelly满/半/2×模拟表。", en: "Kelly full/half/2× simulation table." },
      { zh: "MV vs LedoitWolf vs 1/N滚动。", en: "Walk-forward MV vs LedoitWolf vs 1/N." },
      { zh: "风险偏好一页（半Kelly理由）。", en: "Risk-preference page (half-Kelly rationale)." },
      { zh: "权重漂移与约束一致性。", en: "Weight drift & constraint consistency." },
    ],
    quizTopics: [
      { zh: "满Kelly问题与半Kelly权衡", en: "Full-Kelly problem and half-Kelly trade-off" },
      { zh: "波动目标前瞻规则", en: "Vol-target look-ahead rule" },
      { zh: "1/N与收缩协方差", en: "1/N and shrunk covariance" },
    ],
    doneWhen: [
      { zh: "仓位对照表+风险偏好一页。", en: "Sizing table + risk-preference page." },
    ],
    methodTags: {
      classic: ["Canvas m11", "QuantStart VaR/Kelly", "UChicago FINM risk", "Kelly 1956", "Markowitz 1952", "LedoitWolf 2004"],
      niche: [],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "固定/波动目标/回撤熔断。", en: "Fixed/vol-target/DD brake." } },
      { id: "ex2", text: { zh: "Kelly满/半/2×模拟表。", en: "Kelly full/half/2× simulation table." } },
      { id: "ex3", text: { zh: "逆波动 vs ERC vs 等权。", en: "Inv-vol vs ERC vs EW." } },
      { id: "ex4", text: { zh: "MV vs LedoitWolf vs 1/N滚动。", en: "Walk-forward MV vs LedoitWolf vs 1/N." } },
      { id: "done1", text: { zh: "仓位对照表+风险偏好一页。", en: "Sizing table + risk-preference page." } },
      { id: "ex5", text: { zh: "HRP树状图+配置表对照ERC/逆波动；完成标准：与课内一致。", en: "HRP dendrogram + allocation vs ERC/inv-vol; done when matching the lesson." } },
      { id: "ex6", text: { zh: "权重漂移实验；完成标准：可行/不可行、A=0.3462越限、换手0.0476。", en: "Weight-drift lab; done when feasible/infeasible, A=0.3462 breach, turnover 0.0476 print." } },
    ],
  },
  {
    slug: "execution-slippage",
    status: "ready",
    title: { zh: "执行与滑点", en: "Execution & slippage" },
    summary: {
      zh: "TWAP/VWAP、AC前沿、Perold IS、限价vs市价、到达价TCA、双√冲击识字、公开盘口元订单冲击警告。",
      en: "TWAP/VWAP, AC frontier, Perold IS, limit vs market, arrival TCA, double-√ impact literacy, public-data metaorder impact warn.",
    },
    hours: 14.75,
    difficulty: 3,
    skippable: false,
    hourBasis: "5h concepts (√/Gatheral + public metaorder IRF) + 6.5h experiments + 1.5h quiz + 1h feed-aware TCA (IEX vs SIP arrival, stale NBBO, capacity) + 0.25h Rule 605 vs FINRA 21-23 + 0.5h Rule 606 routing & PFOF",
    prereqs: ["costs-in-backtest", "portfolio-risk-sizing"],
    goals: [
      { zh: "加参与率与日程约束。", en: "Add participation and schedule caps." },
      { zh: "写执行假设一页并接入主配置。", en: "Write execution sheet into main config." },
    ],
    mustTeach: [
      { zh: '公开盘口元订单 IRF 常呈线性+弱回撤；估大单冲击易估歪（2501.17096）。', en: 'Public-tape metaorder IRFs often linear+weak revert; large-impact estimates go wrong (2501.17096).' },
      { zh: "执行是策略一部分；研究与纸面共用成本模型。", en: "Execution is part of strategy; research and paper share cost models." },
      { zh: "TWAP/VWAP；Almgren–Chriss 2000/2001 J.Risk 3(2) 成本–风险前沿与闭式轨迹。", en: "TWAP/VWAP; Almgren–Chriss 2000/2001 J.Risk 3(2) cost–risk frontier and closed-form trajectory." },
      { zh: "Perold 1988实施缺口；限价成交概率与逆向选择；到达价滑点报告。", en: "Perold 1988 IS; limit fill vs adverse selection; arrival-price slippage report." },
    ],
    exercises: [
      { zh: "TWAP/VWAP+参与率上限。", en: "TWAP/VWAP + participation caps." },
      { zh: "AC λ扫描与轨迹。", en: "AC λ sweep and trajectories." },
      { zh: "Perold IS分解。", en: "Perold IS decomposition." },
      { zh: "执行一页纸进主配置。", en: "Execution one-pager in main config." },
      { zh: "feed 感知 TCA。", en: "Feed-aware TCA." },
    ],
    quizTopics: [
      { zh: "隐性成本与IS", en: "Implicit costs and IS" },
      { zh: "AC前沿含义", en: "AC frontier meaning" },
      { zh: "参与率与逆向选择", en: "Participation and adverse selection" },
    ],
    doneWhen: [
      { zh: "执行假设纳入主配置。", en: "Execution assumptions in main config." },
    ],
    methodTags: {
      classic: ["Canvas m12", "NYU impact/TCA", "QuantStart execution", "Almgren-Chriss 2000", "Perold 1988"],
      niche: ["@sera00111 execution/venue notes"],
      frontier: ["arXiv:2502.16246 double-√ + Gatheral 2010"],
    },
    tasks: [
      { id: "ex1", text: { zh: "TWAP/VWAP+参与率上限。", en: "TWAP/VWAP + participation caps." } },
      { id: "ex2", text: { zh: "AC λ扫描与轨迹。", en: "AC λ sweep and trajectories." } },
      { id: "ex3", text: { zh: "Perold IS分解。", en: "Perold IS decomposition." } },
      { id: "ex4", text: { zh: "限价vs市价玩具。", en: "Limit vs market toy." } },
      { id: "done1", text: { zh: "执行假设纳入主配置。", en: "Execution assumptions in main config." } },
      { id: "ex-us-tca", text: { zh: "把 07 脚本成交价改为 100.03；完成标准：报告两种 feed 的滑点。", en: "Set the fill to 100.03 in script 07; done when slippage under both feeds is reported." } },
    ],
  },
  {
    slug: "risk-systems-lab",
    status: "ready",
    title: { zh: "风险系统小实验", en: "Mini risk-systems lab" },
    summary: {
      zh: "滞后VaR/CVaR、Kupiec+Christoffersen、巴塞尔交通灯计数、压力、回撤、集中度/杠杆。",
      en: "Lagged VaR/CVaR, Kupiec+Christoffersen, Basel traffic-light counts, stress, DD, concentration/leverage.",
    },
    hours: 8,
    difficulty: 3,
    skippable: false,
    hourBasis: "2.5h concepts (Kupiec+Christoffersen+Basel) + 4.5h labs + 1h quiz",
    prereqs: ["portfolio-risk-sizing", "execution-slippage"],
    goals: [
      { zh: "陈旧/缺口数据拒单。", en: "Refuse orders on stale/gap data." },
      { zh: "回撤熔断与降仓。", en: "DD kill switch and de-risk." },
      { zh: "自查无密钥进库。", en: "Self-check no secrets in git." },
    ],
    mustTeach: [
      { zh: "熔断是工程不是预测；风险估计一律滞后。", en: "Kill switches are engineering, not forecasts; lag all risk estimates." },
      { zh: "历史/参数/MC VaR与CVaR；Kupiec 1995 + Christoffersen 1998 IND/CC；巴塞尔交通灯只计数。", en: "Hist/param/MC VaR and CVaR; Kupiec 1995 + Christoffersen 1998 IND/CC; Basel traffic-light counting only." },
      { zh: "压力测试；集中度与杠杆上限；密钥卫生。", en: "Stress tests; concentration and leverage limits; secrets hygiene." },
    ],
    exercises: [
      { zh: "缺口→暂停。", en: "Gap→pause." },
      { zh: "回撤→降仓。", en: "DD→de-risk." },
      { zh: "VaR/CVaR+Kupiec表。", en: "VaR/CVaR + Kupiec table." },
      { zh: "密钥扫描。", en: "Secret scan." },
    ],
    quizTopics: [
      { zh: "硬约束与滞后", en: "Hard constraints and lagging" },
      { zh: "Kupiec含义", en: "Kupiec meaning" },
      { zh: "密钥卫生", en: "Secrets hygiene" },
    ],
    doneWhen: [
      { zh: "三道硬约束演示通过。", en: "Three hard-constraint demos pass." },
    ],
    methodTags: {
      classic: ["Canvas m13 bits", "ML4T ops", "Kupiec 1995"],
      niche: ["Cookbook/Qbot config ideas"],
      frontier: ["Christoffersen 1998 IND/CC + Basel traffic-light counting"],
    },
    tasks: [
      { id: "ex1", text: { zh: "缺口→暂停。", en: "Gap→pause." } },
      { id: "ex2", text: { zh: "回撤→降仓。", en: "DD→de-risk." } },
      { id: "ex3", text: { zh: "VaR/CVaR+Kupiec表。", en: "VaR/CVaR + Kupiec table." } },
      { id: "ex4", text: { zh: "密钥扫描。", en: "Secret scan." } },
      { id: "done1", text: { zh: "三道硬约束演示通过。", en: "Three hard-constraint demos pass." } },
    ],
  },
  {
    slug: "market-regimes-crisis",
    status: "ready",
    title: { zh: "市场状态与危机剧本", en: "Market regimes & crisis playbooks" },
    summary: {
      zh: "可操作regime、因果检测栈、四场景剧本、HMM过滤vs平滑泄漏、熔断识字、新闻≠regime。",
      en: "Operational regimes, causal detector stack, four playbooks, HMM filter vs smoother leak, circuit-breaker literacy, news≠regime.",
    },
    hours: 15.25,
    difficulty: 4,
    skippable: false,
    hourBasis: "4.5h concepts + 5h labs (path/overlays/corr/HMM) + 1.5h quiz/review + 1h options/VIX risk box + 1h MWCB/LULD/Reg SHO 201 comparison (R12 tiers, Amendment 18) + 0.5h overnight LULD price bands (Amendment 27/29, Phase 1) + 1.5h US options basics (OCC ODD June 2024; parity; BSM as reference) + 0.25h MWCB Level 3 resumption under 23/5 (SR-NYSE-2026-43 / SR-NASDAQ-2026-080)",
    prereqs: ["risk-systems-lab"],
    goals: [
      { zh: "写出可操作、可因果的regime定义。", en: "Write an operational, causal regime definition." },
      { zh: "用shift(1)检测栈标出教学路径。", en: "Label a teaching path with a shift(1) detector stack." },
      { zh: "区分过滤与平滑HMM；新闻日≠已定义regime。", en: "Separate filtered vs smoothed HMM; news day ≠ defined regime." },
    ],
    mustTeach: [
      { zh: "状态输入一律滞后；平滑概率禁止用于决策。", en: "Lag all state inputs; ban smoothed probs for decisions." },
      { zh: "四剧本：上涨/普通回调vs危机/急跌/震荡，各含失败模式。", en: "Four playbooks: rally / pullback-vs-crisis / crash / range — each with failure modes." },
      { zh: "Moreira–Muir 2017 vs Cederburg 2020：波动目标是风险工程不是课程alpha。", en: "Moreira–Muir 2017 vs Cederburg 2020: vol targeting is risk engineering, not course alpha." },
      { zh: "美股熔断7/13/20%与2016 A股熔断暂停=机制识字≠信号。", en: "US MWCB 7/13/20% and 2016 A-share halt suspension = mechanism literacy ≠ signals." },
    ],
    exercises: [
      { zh: "因果标签路径+急跌窗命中率。", en: "Causal label path + crash-window hit-rate." },
      { zh: "固定/波动目标/DD刹车：只比vol与maxDD。", en: "Fixed/vol-target/DD brake: vol & maxDD only." },
      { zh: "相关→1压力PnL。", en: "Corr→1 stress PnL." },
      { zh: "HMM过滤vs平滑泄漏对照。", en: "HMM filter vs smoother leakage foil." },
      { zh: "期权/VIX风险框手算。", en: "Options/VIX risk-box hand calc." },
      { zh: "LULD 价格档与收盘翻倍解释。", en: "Explain LULD tiers and closing doubling." },
      { zh: "手算隔夜价格带一行。", en: "Hand-compute one overnight-band row." },
      { zh: "期权入门玩具与 Level 3 恢复时间。", en: "Options basics toy and Level 3 resumption time." },
    ],
    quizTopics: [
      { zh: "因果滞后与平滑泄漏", en: "Causal lag and smoother leakage" },
      { zh: "危机vs普通回调", en: "Crisis vs ordinary pullback" },
      { zh: "熔断/新闻≠交易信号", en: "Circuit breaker/news ≠ trade signal" },
    ],
    doneWhen: [
      { zh: "四场景卡片+实验数字一致+新闻≠regime短文。", en: "Four playbook cards + matching lab numbers + news≠regime note." },
    ],
    methodTags: {
      classic: ["Hamilton 1989 Econometrica", "NYSE Rule 7.12 MWCB", "CPPI gap/cash-lock literacy"],
      niche: ["CSRC/SSE 2016 circuit-breaker suspension"],
      frontier: ["Moreira-Muir 2017 JF", "Cederburg et al. 2020 JFE"],
    },
    tasks: [
      { id: "ex1", text: { zh: "因果标签路径+急跌窗命中率。", en: "Causal label path + crash-window hit-rate." } },
      { id: "ex2", text: { zh: "固定/波动目标/DD刹车：只比vol与maxDD。", en: "Fixed/vol-target/DD brake: vol & maxDD only." } },
      { id: "ex3", text: { zh: "相关→1压力PnL。", en: "Corr→1 stress PnL." } },
      { id: "ex4", text: { zh: "HMM过滤vs平滑泄漏对照。", en: "HMM filter vs smoother leakage foil." } },
      { id: "ex5", text: { zh: "四场景三栏卡片（无买卖推荐）。", en: "Four playbook three-column cards (no trade advice)." } },
      { id: "done1", text: { zh: "硬规则+排伪+新闻≠regime短文。", en: "Hard rules + debunk + news≠regime note." } },
      { id: "ex6", text: { zh: "看跌期权玩具手算；完成标准：+13/−2 与 spot VIX≠期货结算一句。", en: "Put toy hand calc; done when +13/−2 and one sentence spot VIX ≠ futures settlement." } },
      { id: "ex-luld", text: { zh: "运行 06 LULD 脚本并解释 Tier2 $50 vs $2；完成标准：引用价格档规则。", en: "Run the 06 LULD script and explain Tier 2 at $50 vs $2; done when the tier rule is cited." } },
      { id: "ex-ovb", text: { zh: "运行 08 脚本手算收盘 50、19:30 价 44 一行；完成标准：35.20 / 60.00。", en: "Run script 08 and hand-compute close 50 / 19:30 price 44; done when 35.20 / 60.00." } },
      { id: "ex-opt", text: { zh: "运行 09、10 脚本：合约费用、卖出看跌最坏亏损、平价误差、Level 3 最早恢复时间；完成标准：400 美元、−9750.00、<1e-9、周四 04:00 ET。", en: "Run scripts 09 and 10: contract cost, short-put worst case, parity gap, earliest Level 3 resumption; done when $400, −9750.00, <1e-9, Thursday 04:00 ET." } },
    ],
  },
];

const phase_P7_lessons: Lesson[] = [
  {
    slug: "paper-trading-infra",
    status: "ready",
    title: { zh: "纸面交易与迷你基建", en: "Paper trading & mini infra" },
    summary: {
      zh: "合成纸面闭环：日志/对账、摩擦阶梯、六缺陷一致性清单（无券商下单）。",
      en: "Synthetic paper loop: logs/recon, friction ladder, six-defect parity checklist (no broker orders).",
    },
    hours: 17.5,
    difficulty: 3,
    skippable: false,
    hourBasis: "3h design + 6h running/logging + 3h parity checklist + 1h template + 1h infra name-map + 2h US broker paper differences & adapter fixture + 1h Shanghai-timezone reconciliation + 0.5h overnight-session fixture (trade date, Shanghai time, order limits)",
    prereqs: ["market-regimes-crisis"],
    goals: [
      { zh: "CSV/模拟撮合与冻结版本。", en: "CSV/sim matching with frozen version." },
      { zh: "出日报并对账。", en: "Emit daily logs and reconcile." },
      { zh: "数值分解实盘−回测缺口。", en: "Numerically decompose live−backtest gaps." },
    ],
    mustTeach: [
      { zh: "纸面期间不按盈亏改规则；冻结版本。", en: "Don't edit rules for P&L; freeze version." },
      { zh: "对账与异常日志；滑点/成交/延迟/数据缺口分解。", en: "Reconciliation; slippage/fills/latency/data gap decomposition." },
      { zh: "熔断是工程；本站无真实券商下单代码。", en: "Kill switches are engineering; no real broker order code." },
    ],
    exercises: [
      { zh: "≥5日纸面日志。", en: "≥5-day paper logs." },
      { zh: "摩擦阶梯表。", en: "Friction ladder table." },
      { zh: "熔断单元演示。", en: "Kill-switch unit demo." },
      { zh: "日报模板。", en: "Daily template." },
      { zh: "纸面适配器幂等测试。", en: "Paper adapter idempotency test." },
      { zh: "隔夜时段 fixture 加一笔订单。", en: "Add one order to the overnight fixture." },
    ],
    quizTopics: [
      { zh: "纸面验证什么", en: "What paper validates" },
      { zh: "为何冻结版本", en: "Why freeze versions" },
      { zh: "缺口分解", en: "Gap decomposition" },
    ],
    doneWhen: [
      { zh: "≥5日日志包+缺口表+熔断演示。", en: "≥5-day log pack + gap table + kill demo." },
    ],
    methodTags: {
      classic: ["Canvas m13", "QuantStart paper-before-live", "Alpaca / IBKR paper docs (document-level only)", "Chinese supplement: JoinQuant 模拟交易"],
      niche: ["Qbot/Atlas reference architecture", "Nautilus isomorphic paper/sim concept"],
      frontier: ["arXiv:2610.21846 BT↔live six defects + checklist"],
    },
    tasks: [
      { id: "ex1", text: { zh: "≥5日纸面日志。", en: "≥5-day paper logs." } },
      { id: "ex2", text: { zh: "摩擦阶梯表。", en: "Friction ladder table." } },
      { id: "ex3", text: { zh: "熔断单元演示。", en: "Kill-switch unit demo." } },
      { id: "ex4", text: { zh: "日报模板。", en: "Daily template." } },
      { id: "done1", text: { zh: "≥5日日志包+缺口表+熔断演示。", en: "≥5-day log pack + gap table + kill demo." } },
      { id: "ex-us-paper", text: { zh: "在 03 适配器 fixture 中加重复 client_order_id；完成标准：unique_orders_sent 不变。", en: "Add a duplicate client_order_id to the 03 adapter fixture; done when unique_orders_sent is unchanged." } },
      { id: "ex-us-overnight", text: { zh: "在 05 fixture 加周二 20:30 ET 限价单；完成标准：交易日周三、北京时间周三 09:30、被接受。", en: "Add a Tuesday 20:30 ET limit order to fixture 05; done when trade date Wednesday, Beijing Wednesday 09:30, accepted." } },
    ],
  },
  {
    slug: "compliance-ethics",
    status: "ready",
    title: { zh: "合规、风险心态与研究伦理", en: "Compliance, risk mindset & research ethics" },
    summary: {
      zh: "美股主线：接入/卖空/保证金（FINRA 26-10 四日期与迁移状态）与跨境税务/外汇/CRS 识字；A 股/港股/欧盟为比较阅读；加密官方状态；非法律意见；研究伦理。",
      en: "US main line: access, short sale, margin (FINRA 26-10 four dates & phase-in status) plus cross-border tax/FX/CRS literacy; A-share/HK/EU as comparison reading; crypto official status; not legal advice; research ethics.",
    },
    hours: 20.75,
    difficulty: 2,
    skippable: false,
    hourBasis: "8h reading (Northbound + PDA withdrawal + FY2026/FINRA GenAI + SFC 24EC55 + ESMA74 algo briefing) + 4.5h writing + 2.5h quiz + 1h rule versions (FINRA main example + SSE 2026 comparison) + 0.5h US four-date table & phase-in status (R04) + 2.5h cross-border tax/FX/CRS literacy box (R25/R28/R29) + 0.5h wash-sale basis lab (IRS Pub 550 examples, purchase-order matching) + 0.5h holding period & qualified dividends (IRS Topic 409 / Pub 550 / Pub 519) + 0.5h manipulation red lines & self-trade lab (15 U.S.C. 78i / FINRA 5210 / CAT review) + 0.25h tokenized NMS stock Innovation Exemption status (SEC 34-106402, until 2031-09-17)",
    prereqs: ["paper-trading-infra"],
    goals: [
      { zh: "分开记录 FINRA 规则四个日期与券商迁移状态（未知输出 needs_broker_verification）。", en: "Record FINRA’s four rule dates separately from broker migration status (unknown → needs_broker_verification)." },
      { zh: "识别 W-8BEN/协定/洗售/中国个税/CRS/外汇额度的边界，不作个人税务判断。", en: "Recognise the boundaries of W-8BEN/treaty/wash sale/China IIT/CRS/FX quota without personal tax judgements." },
      { zh: "写风险偏好。", en: "Write risk preference." },
      { zh: "记录失败。", en: "Log failures." },
      { zh: "拆穿保证夏普话术。", en: "Debunk guaranteed-Sharpe pitches." },
    ],
    mustTeach: [
      { zh: 'ESMA74-1505669079-10311（2026-02-26）非约束：算法定义/重大变更复测/2×压力/PTC/外包责任 — 仅识字。', en: 'ESMA74-1505669079-10311 (2026-02-26) non-binding: algo definition/material-change retest/2× stress/PTC/outsourcing liability — literacy only.' },
      { zh: "本站学习材料非投资建议；不懂则零仓位。", en: "Site materials are not investment advice; zero size if unclear." },
      { zh: "只引用作者按 checked_on 阅读过的官方文本并标注日期；台账脚本只打印本地记录，不联网。", en: "Cite only official texts the author read on checked_on, with the date; the ledger script only prints a local record and does not go online." },
      { zh: "证监会2024程序化规定；沪深细则高频300/20000；15c3-5；Reg SHO；4210/Notice26-10；15-09；银发237号；SEC/CFTC工作人员声明。", en: "CSRC 2024 programmatic rules; SSE/SZSE HFT 300/20000; 15c3-5; Reg SHO; 4210/Notice26-10; 15-09; PBoC 237; SEC/CFTC staff statement." },
    ],
    exercises: [
      { zh: "风险一页。", en: "Risk page." },
      { zh: "三次失败。", en: "Three failures." },
      { zh: "话术审计。", en: "Pitch audit." },
      { zh: "官方来源表。", en: "Official-source table." },
      { zh: "比较示例：上交所交易规则版本表与按日期切换。", en: "Comparison example: SSE trading-rule version table + date switch." },
      { zh: "跨境税务/外汇/CRS 识字卡。", en: "Cross-border tax/FX/CRS literacy card." },
      { zh: "FINRA 四日期 + 会员迁移 fixture 验收。", en: "FINRA four-date + member-migration fixture acceptance." },
      { zh: "洗售成本基础调整玩具。", en: "Wash-sale basis adjustment toy." },
    ],
    quizTopics: [
      { zh: "选择性汇报危害", en: "Harm of selective reporting" },
      { zh: "学习与受监管业务边界", en: "Learning vs regulated advice" },
      { zh: "官方文本核验", en: "Official-text verification" },
    ],
    doneWhen: [
      { zh: "伦理清单勾选完成。", en: "Ethics checklist complete." },
    ],
    methodTags: {
      classic: ["Canvas m14", "AFML scientific ethics", "CSRC/SSE/SZSE", "SEC 15c3-5", "FINRA 15-09/26-10"],
      niche: [],
      frontier: ["SFC Circular 24EC55 GenAI LM", "ESMA74-1505669079-10311 algo-trading supervisory briefing (2026-02-26; non-binding literacy)", "LLM/agent research must obey same ethics/hold-out (link P8)"],
    },
    tasks: [
      { id: "ex1", text: { zh: "风险一页。", en: "Risk page." } },
      { id: "ex2", text: { zh: "三次失败。", en: "Three failures." } },
      { id: "ex3", text: { zh: "话术审计。", en: "Pitch audit." } },
      { id: "ex4", text: { zh: "官方来源表。", en: "Official-source table." } },
      { id: "done1", text: { zh: "伦理清单勾选完成。", en: "Ethics checklist complete." } },
      { id: "ex5", text: { zh: "比较示例：上交所规则版本表；完成标准：2026-07-03→2023，2026-07-06→2026。", en: "Comparison example: SSE rule-version table; done when 2026-07-03→2023 and 2026-07-06→2026." } },
      { id: "ex6", text: { zh: "跨境识字卡六点；完成标准：六点齐全且无个人税额计算或汇路建议。", en: "Six-point cross-border literacy card; done when all six appear with no personal tax calculation or remittance advice." } },
      { id: "ex-wash", text: { zh: "运行 06 脚本，买回日改为 +30 与 +31；完成标准：+30 触发（成本基础 1050），+31 不触发。", en: "Run script 06 with repurchase on day +30 and +31; done when +30 is a wash sale (basis 1050) and +31 is not." } },
      { id: "ex7", text: { zh: "运行 04 FINRA 迁移 fixture 并新增迁移期内 broker_checked_on 为空的案例；完成标准：输出 needs_broker_verification 且 8/8 原案例通过。", en: "Run the 04 FINRA migration fixture and add an in-phase-in case with empty broker_checked_on; done when it outputs needs_broker_verification and the 8/8 original cases pass." } },
    ],
  },
];

const phase_P8_lessons: Lesson[] = [
  {
    slug: "frontier-llm-agents",
    status: "ready",
    title: { zh: "前沿：LLM / 多智能体量化研发", en: "Frontier: LLM / multi-agent quant R&D" },
    summary: { zh: "RD-Agent(Q)、公式化alpha挖掘、Quant-Arena：批判性试用，不替代防泄漏。", en: "RD-Agent(Q), formulaic alpha mining, Quant-Arena: critical trials — never replace anti-leakage." },
    hours: 29,
    difficulty: 5,
    skippable: false,
    hourBasis: "5h reading + 12h critical exercises (KTD/Xia/Mirage/five sins/FINSABER/OpenPM/CLQT/AQuA/recoverability) + 2h rules + 3h sealed leaderboard + 7h process diagnosis — HEAVY",
    prereqs: ["factor-workflow", "ml-leakage-control", "modern-ml-pipelines", "compliance-ethics"],
    goals: [
      { zh: "陈述RD-Agent(Q)闭环。", en: "State RD-Agent(Q) loop." },
      { zh: "列出LLM挖因子失败模式。", en: "List LLM factor-mining failure modes." },
      { zh: "设计密封样本外验收。", en: "Design sealed-OOS acceptance bar." },
    ],
    mustTeach: [
      { zh: "自动化放大试错→更需多重检验。", en: "Automation amplifies trials → stricter multiple testing." },
      { zh: "论文指标≠你的可复现优势。", en: "Paper metrics ≠ your reproducible edge." },
      { zh: "Agent输出须进同一陷阱审讯。", en: "Agent outputs enter same trap interrogation." },
    ],
    exercises: [
      { zh: "读RD-Agent/Qlib说明写半页风险清单。", en: "Read RD-Agent/Qlib notes; half-page risk list." },
      { zh: "对LLM生成因子做空假设与成本审讯提纲。", en: "Null+cost interrogation outline for LLM factor." },
      { zh: "用Quant-Arena冻结后再测密封年规则改写守则。", en: "Rewrite rules using Quant-Arena freeze-then-sealed-year." },
    ],
    quizTopics: [
      { zh: "为何agent增加过拟合风险", en: "Why agents raise overfitting risk" },
      { zh: "密封hold-out是什么", en: "What sealed hold-out means" },
    ],
    doneWhen: [
      { zh: "前沿风险清单+更新研究守则。", en: "Frontier risk list + updated research rules." },
    ],
    methodTags: {
      classic: [],
      niche: ["XQuant Spec+AI run-first as motivation only (@_zheergen)"],
      frontier: ["microsoft/RD-Agent + R&D-Agent(Q) arXiv:2505.15155 (NeurIPS 2025 only as arXiv comment — verify proceedings)", "Chain-of-Alpha arXiv:2508.06312", "LLM+MCTS arXiv:2505.11122", "Quant-Arena arXiv:2610.30113", "Glasserman&Lin arXiv:2309.17322", "Lopez-Lira/Tang/Zhu arXiv:2504.14765", "Five sins arXiv:2602.14233", "FINSABER arXiv:2505.07078", "OpenPM arXiv:2608.09988"],
    },
    tasks: [
      { id: "ex1", text: { zh: "读RD-Agent/Qlib说明写半页风险清单。", en: "Read RD-Agent/Qlib notes; half-page risk list." } },
      { id: "ex2", text: { zh: "对LLM生成因子做空假设与成本审讯提纲。", en: "Null+cost interrogation outline for LLM factor." } },
      { id: "ex3", text: { zh: "用Quant-Arena冻结后再测密封年规则改写守则。", en: "Rewrite rules using Quant-Arena freeze-then-sealed-year." } },
      { id: "done1", text: { zh: "前沿风险清单+更新研究守则。", en: "Frontier risk list + updated research rules." } },
    ],
  },
  {
    slug: "frontier-tsfm-altdata-crypto",
    status: "ready",
    title: { zh: "前沿：时序基础模型 · 另类数据 · Crypto/链上", en: "Frontier: TSFMs · alt-data · crypto/on-chain" },
    summary: { zh: "Chronos/TimesFM金融评测的谨慎结论；另类数据；CCXT/资金费率/链上。", en: "Cautious Chronos/TimesFM finance results; alt-data; CCXT/funding/on-chain." },
    hours: 19,
    difficulty: 4,
    skippable: false,
    hourBasis: "5h papers + 6h design + 5h funding/liquidation/ADL/EWS/path-funding foils + 2h structure/PIT + 1h SaR name-drop — HEAVY",
    prereqs: ["modern-ml-pipelines", "data-cleaning", "execution-slippage"],
    goals: [
      { zh: "概括TSFM日频超额收益谨慎结论。", en: "Summarize cautious TSFM daily excess-return findings." },
      { zh: "设计另类数据PIT/滞后检查。", en: "Design alt-data PIT/lag checks." },
      { zh: "说明CEX CCXT与链上适配差异与额外风险。", en: "Explain CEX CCXT vs on-chain adapter risks." },
    ],
    mustTeach: [
      { zh: "零样本TSFM常弱于强传统基准；领域预训练仍须防前瞻。", en: "Zero-shot TSFMs often lag strong baselines; domain pretraining still needs anti-lookahead." },
      { zh: "另类数据时间戳与修订是第一风险。", en: "Alt-data timestamps/revisions are first-order risks." },
      { zh: "资金费率/链上指标不是免费alpha。", en: "Funding/on-chain metrics ≠ free alpha." },
    ],
    exercises: [
      { zh: "读TSFM金融评测摘要列5条不可直接实盘理由。", en: "Read TSFM-finance eval; list 5 no-naive-live reasons." },
      { zh: "为假情绪序列设计延迟与修订规则。", en: "Design lag/revision rules for fake sentiment." },
      { zh: "（可选）CCXT拉一种资金费率并画图。", en: "(Optional) pull one funding series via CCXT." },
    ],
    quizTopics: [
      { zh: "TSFM零样本局限", en: "TSFM zero-shot limits" },
      { zh: "另类数据前瞻", en: "Alt-data lookahead" },
      { zh: "链上执行额外风险", en: "On-chain execution risks" },
    ],
    doneWhen: [
      { zh: "TSFM谨慎备忘+另类数据时间规则一页。", en: "TSFM caution memo + alt-data timing one-pager." },
    ],
    methodTags: {
      classic: [],
      niche: ["@sera00111 Crypto toolchain", "Funding/on-chain pipeline examples as structure refs"],
      frontier: ["Chronos/TimesFM finance evals e.g. arXiv:2511.18578", "Trading Strategy GMX CCXT adapters 2025", "OpenBB-style alt/market data aggregation", "Perp funding fundamentals arXiv:2212.06888", "Liquidation subcritical arXiv:2608.03616"],
    },
    tasks: [
      { id: "ex1", text: { zh: "读TSFM金融评测摘要列5条不可直接实盘理由。", en: "Read TSFM-finance eval; list 5 no-naive-live reasons." } },
      { id: "ex2", text: { zh: "为假情绪序列设计延迟与修订规则。", en: "Design lag/revision rules for fake sentiment." } },
      { id: "ex3", text: { zh: "（可选）CCXT拉一种资金费率并画图。", en: "(Optional) pull one funding series via CCXT." } },
      { id: "done1", text: { zh: "TSFM谨慎备忘+另类数据时间规则一页。", en: "TSFM caution memo + alt-data timing one-pager." } },
    ],
  },
];

const phase_P9_lessons: Lesson[] = [
  {
    slug: "capstone",
    status: "ready",
    title: { zh: "结业项目：诚实的小策略", en: "Capstone: an honest small strategy" },
    summary: { zh: "假设→PIT→含成本walk-forward→DSR(N=全部)→仓位→TCA→纸面对账→合规→报告模板与量规。", en: "Hypothesis→PIT→costed walk-forward→DSR(N=all)→sizing→TCA→paper recon→compliance→report template+rubric." },
    hours: 26,
    difficulty: 5,
    skippable: false,
    hourBasis: "6h design/data + 10h backtest/OOS + 4h paper + 4h writing — project + 2h US research contract (offline JSON checker)",
    prereqs: ["paper-trading-infra", "compliance-ethics", "factor-workflow", "portfolio-risk-sizing"],
    goals: [
      { zh: "交付可复现研究包。", en: "Deliver reproducible research pack." },
      { zh: "含成本敏感与密封样本外及DSR(N)。", en: "Include cost sensitivity, sealed OOS, and DSR(N)." },
      { zh: "附纸面独立对账、合规清单与量规自评。", en: "Attach paper independent recon, compliance checklist, rubric self-score." },
    ],
    mustTeach: [
      { zh: "评分看诚实与工程不看是否赚钱。", en: "Grade honesty and engineering, not profits." },
      { zh: "DSR须计入全部试错且用决策同一序列。", en: "DSR must count all trials on the decision series." },
      { zh: "可选前沿附录不得削弱核心纪律。", en: "Optional frontier appendix must not weaken core discipline." },
    ],
    exercises: [
      { zh: "一页假设（含PIT与决策规则）。", en: "One-page hypothesis (PIT+decision rule)." },
      { zh: "含成本+embargo的walk-forward。", en: "Costed walk-forward with embargo." },
      { zh: "密封OOS+DSR(N=全部)及N=1对照。", en: "Sealed OOS+DSR(N=all) and N=1 foil." },
      { zh: "仓位限制与TCA估计。", en: "Sizing limits and TCA estimate." },
      { zh: "≥5日纸面+独立账本检出注入差错。", en: "≥5-day paper+independent ledger detects injected break." },
      { zh: "量规自评（Must全过）。", en: "Rubric self-score (all Must pass)." },
      { zh: "（可选）前沿失败对照附录。", en: "(Optional) frontier failure appendix." },
      { zh: "美股研究合同校验。", en: "US research contract check." },
    ],
    quizTopics: [
      { zh: "DSR的N与决策序列", en: "DSR N and decision series" },
      { zh: "独立账本对账", en: "Independent ledger reconciliation" },
      { zh: "量规看诚实不看盈利", en: "Rubric grades honesty not profits" },
    ],
    doneWhen: [
      { zh: "结业包通过自评量规全部Must行。", en: "Capstone pack meets all Must rubric rows." },
    ],
    methodTags: {
      classic: ["Canvas capstone", "US research contract (offline)", "Chinese supplement: JoinQuant 综合/模拟", "Bailey–LdP 2014 DSR", "Perold 1988 IS"],
      niche: ["Open strategy libs sparingly as hypothesis inspiration only"],
      frontier: ["Optional negative-result appendix on RD-Agent/TSFM/on-chain signal"],
    },
    tasks: [
      { id: "ex1", text: { zh: "一页假设（含PIT与决策规则）；完成标准：五要素齐全。", en: "One-page hypothesis (PIT+decision rule); done when five fields present." } },
      { id: "ex2", text: { zh: "含成本+embargo的walk-forward；完成标准：参数与折表写出。", en: "Costed walk-forward with embargo; done when params and fold table written." } },
      { id: "ex3", text: { zh: "密封OOS+DSR(N=全部)及N=1对照；完成标准：同一PnL路径两数。", en: "Sealed OOS+DSR(N=all) and N=1 foil; done when both numbers share one PnL path." } },
      { id: "ex4", text: { zh: "仓位限制与TCA估计；完成标准：上限/maxDD与TCA bps为数值。", en: "Sizing limits and TCA estimate; done when caps/maxDD and TCA bps are numeric." } },
      { id: "ex5", text: { zh: "≥5日纸面+独立账本检出注入差错；完成标准：日期与abs_diff。", en: "≥5-day paper+independent ledger detects injected break; done when date+abs_diff printed." } },
      { id: "ex6", text: { zh: "量规自评（Must全过）；完成标准：每Must行Pass或Gap+修复计划。", en: "Rubric self-score (all Must pass); done when each Must is Pass or Gap+fix." } },
      { id: "ex7", text: { zh: "（可选）前沿失败对照附录；完成标准：不削弱Must行。", en: "(Optional) frontier failure appendix; done when Must rows stay intact." } },
      { id: "done1", text: { zh: "结业包通过自评量规全部Must行。", en: "Capstone pack meets all Must rubric rows." } },
      { id: "ex-us-contract", text: { zh: "改 fixture 一个字节后重跑合同检查；完成标准：contract_ok=False 后恢复。", en: "Change one fixture byte and rerun the contract check; done when contract_ok=False, then restore." } },
    ],
  },
];

export const phases: Phase[] = [
  {
    id: "P0",
    slug: "foundations",
    title: { zh: "零基础准备（可测验跳过）", en: "Zero-basis foundations (test-out OK)" },
    goal: { zh: "补齐 Python/pandas、统计概率、基础金融。", en: "Fill Python/pandas, stats/probability, basic finance." },
    cluster: "Foundational skills before market microstructure",
    lessons: phase_P0_lessons,
  },
  {
    id: "P1",
    slug: "markets-measurement",
    title: { zh: "市场语言与度量", en: "Market language & measurement" },
    goal: { zh: "用交易语言说话，并用收益/风险指标诚实评价玩具信号。", en: "Speak trading language; honestly evaluate toy signals with return/risk metrics." },
    cluster: "Market concepts + evaluation language",
    lessons: phase_P1_lessons,
  },
  {
    id: "P2",
    slug: "data-honest-backtests",
    title: { zh: "数据与诚实回测", en: "Data & honest backtests" },
    goal: { zh: "可版本化数据+陷阱审讯+成本+引擎假设。", en: "Versioned data + trap interrogation + costs + engine assumptions." },
    cluster: "Research infrastructure / scientific method for backtests",
    lessons: phase_P2_lessons,
  },
  {
    id: "P3",
    slug: "classic-strategies",
    title: { zh: "经典策略族", en: "Classic strategy families" },
    goal: { zh: "复现动量/回归/配对并做对照。", en: "Reproduce momentum/reversion/pairs and compare." },
    cluster: "Classic alpha templates before factors/ML",
    lessons: phase_P3_lessons,
  },
  {
    id: "P4",
    slug: "factor-research",
    title: { zh: "因子研究", en: "Factor research" },
    goal: { zh: "IC/分层/组合化的可重复因子工作流。", en: "Repeatable IC/quantile/portfolio factor workflow." },
    cluster: "Cross-sectional research methods",
    lessons: phase_P4_lessons,
  },
  {
    id: "P5",
    slug: "ml-pipelines",
    title: { zh: "机器学习与现代流水线", en: "ML & modern pipelines" },
    goal: { zh: "防泄漏ML + 可复现现代流水线基线。", en: "Leakage-safe ML + reproducible modern pipeline baseline." },
    cluster: "Supervised ML methodology for finance",
    lessons: phase_P5_lessons,
  },
  {
    id: "P6",
    slug: "risk-execution",
    title: { zh: "风险、仓位与执行", en: "Risk, sizing & execution" },
    goal: { zh: "仓位层、执行成本与硬约束工程化。", en: "Sizing layer, execution costs, engineered hard limits." },
    cluster: "Portfolio construction / execution / controls",
    lessons: phase_P6_lessons,
  },
  {
    id: "P7",
    slug: "paper-ethics",
    title: { zh: "纸面与伦理", en: "Paper trading & ethics" },
    goal: { zh: "纸面闭环与合规/研究伦理。", en: "Paper loop plus compliance/research ethics." },
    cluster: "Operationalization and professional norms",
    lessons: phase_P7_lessons,
  },
  {
    id: "P8",
    slug: "frontier-methods",
    title: { zh: "前沿与非主流方法", en: "Frontier & unconventional methods" },
    goal: { zh: "在经典纪律之上批判性接触LLM agent、TSFM、另类数据与Crypto/链上。", en: "Critically engage LLM agents, TSFMs, alt-data, crypto/on-chain atop classic discipline." },
    cluster: "Post-prerequisite frontier / niche methods",
    lessons: phase_P8_lessons,
  },
  {
    id: "P9",
    slug: "capstone",
    title: { zh: "结业项目", en: "Capstone" },
    goal: { zh: "端到端诚实交付。", en: "End-to-end honest delivery." },
    cluster: "Synthesis",
    lessons: phase_P9_lessons,
  },
];

/** @deprecated V1 name — prefer `phases`. */
export const months = phases;

export function phaseStats(phase: Phase) {
  const hours = phase.lessons.reduce((sum, l) => sum + l.hours, 0);
  return {
    lessons: phase.lessons.length,
    tasks: phase.lessons.reduce((sum, l) => sum + l.tasks.length, 0),
    hours,
    weeksAt6h: Math.round((hours / 6) * 10) / 10,
    weeksAt12h: Math.round((hours / 12) * 10) / 10,
  };
}

export function getPhase(slugOrId: string): Phase | undefined {
  return phases.find((p) => p.slug === slugOrId || p.id === slugOrId);
}

export function getLesson(phaseSlug: string, lessonSlug: string) {
  const phase = getPhase(phaseSlug);
  if (!phase) return undefined;
  const index = phase.lessons.findIndex((l) => l.slug === lessonSlug);
  if (index < 0) return undefined;
  return {
    phase,
    lesson: phase.lessons[index],
    index,
    prev: phase.lessons[index - 1],
    next: phase.lessons[index + 1],
  };
}

export function lessonKey(phaseId: string, lessonSlug: string) {
  return `${phaseId}/${lessonSlug}`;
}

export const OPTIONAL_TOOL_LINKS: Record<string, string> = {
  "qlib-docs": "https://qlib.readthedocs.io/en/stable/",
  "qlib-github": "https://github.com/microsoft/qlib",
  "rd-agent": "https://github.com/microsoft/RD-Agent",
  "rd-agent-quant-msr": "https://www.microsoft.com/en-us/research/articles/rd-agent-quant/",
  "rd-agent-quant-arxiv": "https://arxiv.org/abs/2505.15155",
  "vectorbt-docs": "https://vectorbt.dev/",
  "zipline-reloaded": "https://zipline.ml4trading.io/",
  "zipline-github": "https://github.com/stefan-jansen/zipline-reloaded",
  "backtrader": "https://www.backtrader.com/",
  "ml4t-repo": "https://github.com/stefan-jansen/machine-learning-for-trading",
  "quant-wiki": "https://github.com/LLMQuant/quant-wiki",
  "joinquant-zero": "https://www.joinquant.com/community/post/detailMobile?postId=13149",
  "nautilus": "https://github.com/nautechsystems/nautilus_trader",
  "nautilus-parity": "https://nautilustrader.io/blog/why-nautilustrader-exists/",
  "chain-of-alpha": "https://arxiv.org/abs/2508.06312",
  "quant-arena": "https://arxiv.org/abs/2610.30113",
  "tsfm-finance-eval": "https://arxiv.org/abs/2511.18578",
  "gmx-ccxt": "https://github.com/tradingstrategy-ai/gmx-ccxt-freqtrade/",
  "canvas-one-stop": "https://cursor.com/canvas/store-2382cb79-a91c-438a-bb75-0d38cd2e4b0d/e986247c-63a6-4a33-8d8e-97eb8be22290",
  "canvas-x-curated": "https://cursor.com/canvas/store-2382cb79-a91c-438a-bb75-0d38cd2e4b0d/1c5e6f58-9ce1-4602-b188-cb69366123db",
};

export const COURSE_SOURCE = {
  author: "Quant-trading-learn",
  authorUrl: "https://github.com/liudicsu/Quant-trading-learn",
  url: "https://github.com/liudicsu/Quant-trading-learn",
  title: "Quant trading curriculum V2",
};
