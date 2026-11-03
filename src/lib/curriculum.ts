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
  /** Site body status: P0 written in this batch; others stubs. */
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
  hoursFull: 238,
  hoursSkipFoundations: 218,
  hoursRangeLabel: {
    zh: "精确 238h 全量 / 218h 跳过 P0（对外约 220–250h / 200–230h）",
    en: "Exact 238h full / 218h skip P0 (public range ~220–250h / 200–230h)",
  },
  lessonCount: 27,
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
      classic: ["JoinQuant W01 pandas", "QuantStart Python stack"],
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
      classic: ["QuantStart beginner books", "JoinQuant 初识量化"],
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
    hours: 5,
    difficulty: 2,
    skippable: false,
    hourBasis: "2h concepts + 2.5h exercises + 0.5h quiz",
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
    hours: 7,
    difficulty: 2,
    skippable: false,
    hourBasis: "3h concepts + 3h exercises + 1h quiz",
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
    ],
  },
  {
    slug: "returns-vol-corr",
    status: "ready",
    title: { zh: "收益、波动与相关", en: "Returns, volatility & correlation" },
    summary: { zh: "年化、夏普、MDD、滚动统计；压力期相关。", en: "Annualization, Sharpe, MDD, rolling stats; stress corr." },
    hours: 8,
    difficulty: 2,
    skippable: false,
    hourBasis: "3h formulas + 4h coding + 1h quiz",
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
      classic: ["Canvas m3", "JoinQuant W02", "QuantStart performance"],
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
    hours: 5,
    difficulty: 2,
    skippable: false,
    hourBasis: "1.5h concepts + 3h lab + 0.5h quiz",
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
      classic: ["JoinQuant 策略评价", "Canvas eval"],
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
    status: "outline",
    title: { zh: "数据与清洗", en: "Data & cleaning" },
    summary: { zh: "复权、停牌、缺失、幸存者、PIT；数据说明书。", en: "Adjustments,halts,missingness,survivorship,PIT; data sheet." },
    hours: 10,
    difficulty: 3,
    skippable: false,
    hourBasis: "4h concepts + 5h pipeline lab + 1h docs/quiz",
    prereqs: ["eval-lab"],
    goals: [
      { zh: "版本化下载与哈希。", en: "Version downloads and hashes." },
      { zh: "举例幸存者偏差。", en: "Survivorship examples." },
      { zh: "写数据说明书。", en: "Write data sheet." },
    ],
    mustTeach: [
      { zh: "今日成分≠历史宇宙。", en: "Today's constituents ≠ historical universe." },
      { zh: "基本面需PIT。", en: "Fundamentals need PIT." },
      { zh: "时区混乱可前瞻一天。", en: "Timezone mess can lookahead a day." },
    ],
    exercises: [
      { zh: "reindex+缺失断言。", en: "reindex+missingness assert." },
      { zh: "复权对照。", en: "Adj vs raw." },
      { zh: "数据说明书。", en: "Data sheet." },
    ],
    quizTopics: [
      { zh: "幸存者偏差", en: "Survivorship" },
      { zh: "PIT含义", en: "PIT meaning" },
    ],
    doneWhen: [
      { zh: "管线可复跑+说明书。", en: "Rerunnable pipeline + sheet." },
    ],
    methodTags: {
      classic: ["Canvas m4", "QuantStart securities master", "Qlib data layer", "JoinQuant data"],
      niche: ["@pyquantnews finance API notes", "OpenBB quantitative docs", "Binance Vision + crypto data notes (@sera00111)"],
      frontier: ["Alt-data awareness; deeper in P8"],
    },
    tasks: [
      { id: "ex1", text: { zh: "reindex+缺失断言。", en: "reindex+missingness assert." } },
      { id: "ex2", text: { zh: "复权对照。", en: "Adj vs raw." } },
      { id: "ex3", text: { zh: "数据说明书。", en: "Data sheet." } },
      { id: "done1", text: { zh: "管线可复跑+说明书。", en: "Rerunnable pipeline + sheet." } },
    ],
  },
  {
    slug: "backtest-traps",
    status: "outline",
    title: { zh: "回测陷阱与过拟合审讯", en: "Backtest traps & overfitting interrogation" },
    summary: { zh: "前瞻、幸存者、过拟合、walk-forward、试验次数。", en: "Lookahead,survivorship,overfitting,walk-forward,trial counts." },
    hours: 16,
    difficulty: 4,
    skippable: false,
    hourBasis: "5h concepts + 9h multi-labs + 2h write-up — HEAVY",
    prereqs: ["data-cleaning", "stats-probability-basics"],
    goals: [
      { zh: "作弊vs诚实对照。", en: "Cheat vs honest controls." },
      { zh: "样本外/walk-forward。", en: "OOS/walk-forward." },
      { zh: "记录失败与试验次数。", en: "Log failures and trials." },
    ],
    mustTeach: [
      { zh: "未shift用当日收益=前瞻。", en: "Same-bar return without shift=lookahead." },
      { zh: "多重试错制造虚假发现。", en: "Multiple trials → false discoveries." },
      { zh: "冻结规则后再看样本外。", en: "Freeze rules before OOS." },
    ],
    exercises: [
      { zh: "均线作弊/诚实。", en: "MA cheat/honest." },
      { zh: "参数网格过拟合。", en: "Grid overfitting." },
      { zh: "末段hold-out。", en: "Final hold-out." },
      { zh: "失败日志模板。", en: "Failure log template." },
    ],
    quizTopics: [
      { zh: "lookahead定义", en: "Lookahead def" },
      { zh: "为何记录试验次数", en: "Why log trials" },
      { zh: "walk-forward目的", en: "Walk-forward purpose" },
    ],
    doneWhen: [
      { zh: "陷阱报告含对照与OOS。", en: "Trap report with controls+OOS." },
    ],
    methodTags: {
      classic: ["Canvas m5", "JoinQuant审讯室", "AFML backtest-as-CV", "@AfuOnTheWay三坑", "@lopezdeprado虚假发现"],
      niche: ["XQuant AI-first strategies still need interrogation"],
      frontier: ["Quant-Arena sealed-holdout spirit (detail P8)"],
    },
    tasks: [
      { id: "ex1", text: { zh: "均线作弊/诚实。", en: "MA cheat/honest." } },
      { id: "ex2", text: { zh: "参数网格过拟合。", en: "Grid overfitting." } },
      { id: "ex3", text: { zh: "末段hold-out。", en: "Final hold-out." } },
      { id: "ex4", text: { zh: "失败日志模板。", en: "Failure log template." } },
      { id: "done1", text: { zh: "陷阱报告含对照与OOS。", en: "Trap report with controls+OOS." } },
    ],
  },
  {
    slug: "costs-in-backtest",
    status: "outline",
    title: { zh: "成本写入回测", en: "Costs in the backtest" },
    summary: { zh: "佣金+滑点净收益；成本阶梯。", en: "Commission+slippage net; cost ladder." },
    hours: 6,
    difficulty: 3,
    skippable: false,
    hourBasis: "2h concepts + 3.5h coding + 0.5h quiz",
    prereqs: ["backtest-traps"],
    goals: [
      { zh: "实现换手成本公式。", en: "Implement turnover cost formula." },
      { zh: "≥3档成本敏感。", en: "≥3 cost tiers." },
    ],
    mustTeach: [
      { zh: "零成本曲线≠实盘论据。", en: "Zero-cost ≠ live evidence." },
      { zh: "显性vs隐性成本。", en: "Explicit vs implicit costs." },
    ],
    exercises: [
      { zh: "写入净收益。", en: "Wire net returns." },
      { zh: "成本阶梯图。", en: "Cost ladder chart." },
    ],
    quizTopics: [
      { zh: "隐性成本例子", en: "Implicit cost example" },
      { zh: "换手如何进公式", en: "Turnover in formula" },
    ],
    doneWhen: [
      { zh: "成本后主回测可运行。", en: "Net-of-cost main backtest runs." },
    ],
    methodTags: {
      classic: ["Canvas costs", "QuantStart TCA", "NYU TCA themes"],
      niche: [],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "写入净收益。", en: "Wire net returns." } },
      { id: "ex2", text: { zh: "成本阶梯图。", en: "Cost ladder chart." } },
      { id: "done1", text: { zh: "成本后主回测可运行。", en: "Net-of-cost main backtest runs." } },
    ],
  },
  {
    slug: "engines-vectorized-event",
    status: "outline",
    title: { zh: "回测引擎：向量化与事件驱动", en: "Backtest engines: vectorized & event-driven" },
    summary: { zh: "VectorBT vs Zipline/Backtrader；同构引擎概念。", en: "VectorBT vs Zipline/Backtrader; isomorphic engines." },
    hours: 8,
    difficulty: 3,
    skippable: false,
    hourBasis: "3h concepts + 4h compare lab + 1h optional docs",
    prereqs: ["costs-in-backtest"],
    goals: [
      { zh: "陈述向量化默认风险。", en: "State vectorized default risks." },
      { zh: "对比两成交时点净值。", en: "Compare two fill-timing NAVs." },
      { zh: "用initialize/handle_data描述事件循环。", en: "Describe event loop via initialize/handle_data." },
    ],
    mustTeach: [
      { zh: "引擎选择=成交与日历假设。", en: "Engine choice = fill/calendar assumptions." },
      { zh: "先诚实向量化再事件验证。", en: "Honest vectorized then event validation." },
      { zh: "同构引擎降低研究≠实盘缝隙（概念）。", en: "Isomorphic engines reduce research≠live gap." },
    ],
    exercises: [
      { zh: "同信号两成交时点。", en: "Same signal two fills." },
      { zh: "写回测假设段。", en: "Assumptions paragraph." },
      { zh: "（可选）浏览VectorBT与Zipline示例。", en: "(Optional) skim VectorBT/Zipline." },
    ],
    quizTopics: [
      { zh: "向量化乐观默认", en: "Optimistic vectorized defaults" },
      { zh: "事件驱动解决什么", en: "What event-driven buys" },
    ],
    doneWhen: [
      { zh: "假设段+双成交对照。", en: "Assumptions + dual-fill control." },
    ],
    methodTags: {
      classic: ["VectorBT", "Zipline Reloaded", "Backtrader", "Canvas engines"],
      niche: ["@RoundtableSpace Nautilus/Hummingbot", "Qbot (@BTCqzy1)", "Packt Cookbook"],
      frontier: ["NautilusTrader research-to-live parity (2024-2026)"],
    },
    tasks: [
      { id: "ex1", text: { zh: "同信号两成交时点。", en: "Same signal two fills." } },
      { id: "ex2", text: { zh: "写回测假设段。", en: "Assumptions paragraph." } },
      { id: "ex3", text: { zh: "（可选）浏览VectorBT与Zipline示例。", en: "(Optional) skim VectorBT/Zipline." } },
      { id: "done1", text: { zh: "假设段+双成交对照。", en: "Assumptions + dual-fill control." } },
    ],
  },
];

const phase_P3_lessons: Lesson[] = [
  {
    slug: "momentum-trend",
    status: "outline",
    title: { zh: "动量与趋势", en: "Momentum & trend" },
    summary: { zh: "时序/截面动量、12-1、换手与波动目标。", en: "TS/CS momentum, 12-1, turnover and vol targeting." },
    hours: 8,
    difficulty: 3,
    skippable: false,
    hourBasis: "3h concepts + 4.5h labs + 0.5h quiz",
    prereqs: ["engines-vectorized-event"],
    goals: [
      { zh: "双均线与简化动量对照。", en: "Dual-MA vs simplified momentum." },
      { zh: "报告换手与分年。", en: "Report turnover and by-year." },
    ],
    mustTeach: [
      { zh: "跳过近一月减弱短期反转。", en: "Skip-month dampens short-term reversal." },
      { zh: "拥挤与换手侵蚀优势。", en: "Crowding/turnover erode edges." },
    ],
    exercises: [
      { zh: "双均线vs动量。", en: "Dual-MA vs momentum." },
      { zh: "波动目标10%。", en: "10% vol target." },
      { zh: "分年表。", en: "By-year table." },
    ],
    quizTopics: [
      { zh: "12-1动机", en: "12-1 motive" },
      { zh: "时序vs截面", en: "TS vs CS" },
    ],
    doneWhen: [
      { zh: "两套动量结果含成本。", en: "Two momentum results net of costs." },
    ],
    methodTags: {
      classic: ["Canvas m6", "Chan momentum", "Stern trend"],
      niche: ["Pine/quants.md trend samples as foils", "QuantJourney browse critically"],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "双均线vs动量。", en: "Dual-MA vs momentum." } },
      { id: "ex2", text: { zh: "波动目标10%。", en: "10% vol target." } },
      { id: "ex3", text: { zh: "分年表。", en: "By-year table." } },
      { id: "done1", text: { zh: "两套动量结果含成本。", en: "Two momentum results net of costs." } },
    ],
  },
  {
    slug: "mean-reversion",
    status: "outline",
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
    ],
    exercises: [
      { zh: "z<-2/z>2。", en: "z<-2/z>2." },
      { zh: "有无止损A/B。", en: "Stop A/B." },
      { zh: "失效清单。", en: "Invalidation list." },
    ],
    quizTopics: [
      { zh: "回归策略趋势市表现", en: "Reversion in trends" },
      { zh: "为何再估计阈值", en: "Why re-estimate" },
    ],
    doneWhen: [
      { zh: "回归notebook+失效讨论。", en: "MR notebook + failure discussion." },
    ],
    methodTags: {
      classic: ["Canvas m7", "Chan MR", "Stern counter-trend"],
      niche: ["Pine reversal samples as overfitting foils"],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "z<-2/z>2。", en: "z<-2/z>2." } },
      { id: "ex2", text: { zh: "有无止损A/B。", en: "Stop A/B." } },
      { id: "ex3", text: { zh: "失效清单。", en: "Invalidation list." } },
      { id: "done1", text: { zh: "回归notebook+失效讨论。", en: "MR notebook + failure discussion." } },
    ],
  },
  {
    slug: "pairs-stat-arb",
    status: "outline",
    title: { zh: "配对与统计套利入门", en: "Pairs & intro statistical arb" },
    summary: { zh: "价差、滚动对冲比、相关≠可交易。", en: "Spreads, rolling hedge, correlation≠tradeable." },
    hours: 10,
    difficulty: 3,
    skippable: false,
    hourBasis: "4h concepts + 5h lab + 1h write-up",
    prereqs: ["mean-reversion"],
    goals: [
      { zh: "滚动beta价差。", en: "Rolling-beta spread." },
      { zh: "讨论腿断裂。", en: "Discuss broken legs." },
    ],
    mustTeach: [
      { zh: "高相关不足够。", en: "High corr insufficient." },
      { zh: "协整直觉。", en: "Cointegration intuition." },
      { zh: "对冲比再估计。", en: "Re-estimate hedge ratios." },
    ],
    exercises: [
      { zh: "滚动价差与z。", en: "Rolling spread and z." },
      { zh: "静态vs滚动。", en: "Static vs rolling." },
      { zh: "冲击情景段。", en: "Shock scenario note." },
    ],
    quizTopics: [
      { zh: "相关vs协整", en: "Corr vs cointegration" },
      { zh: "为何滚动估计", en: "Why rolling" },
    ],
    doneWhen: [
      { zh: "含成本配对notebook。", en: "Costed pairs notebook." },
    ],
    methodTags: {
      classic: ["Canvas m8", "Chan pairs", "Stern spreads"],
      niche: [],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "滚动价差与z。", en: "Rolling spread and z." } },
      { id: "ex2", text: { zh: "静态vs滚动。", en: "Static vs rolling." } },
      { id: "ex3", text: { zh: "冲击情景段。", en: "Shock scenario note." } },
      { id: "done1", text: { zh: "含成本配对notebook。", en: "Costed pairs notebook." } },
    ],
  },
  {
    slug: "strategy-compare-lab",
    status: "outline",
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
      { zh: "控制隐藏假设。", en: "Control hidden assumptions." },
      { zh: "简单是基准线。", en: "Simple is the baseline." },
    ],
    exercises: [
      { zh: "三策略报告。", en: "Three-strategy report." },
      { zh: "指定基准并判定。", en: "Name baseline and call." },
    ],
    quizTopics: [
      { zh: "对照实验要素", en: "Controlled comparison elements" },
    ],
    doneWhen: [
      { zh: "对照报告入库。", en: "Comparison report filed." },
    ],
    methodTags: {
      classic: ["Canvas comparison spirit", "JoinQuant research rules"],
      niche: ["Critique open strategy dumps (quants.md/Pine) as hypothesis sources only"],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "三策略报告。", en: "Three-strategy report." } },
      { id: "ex2", text: { zh: "指定基准并判定。", en: "Name baseline and call." } },
      { id: "done1", text: { zh: "对照报告入库。", en: "Comparison report filed." } },
    ],
  },
];

const phase_P4_lessons: Lesson[] = [
  {
    slug: "factor-workflow",
    status: "outline",
    title: { zh: "因子研究工作流", en: "Factor research workflow" },
    summary: { zh: "IC、分层、衰减、中性化直觉；拒绝堆参数。", en: "IC, quantiles, decay, neutralization; reject parameter stacking." },
    hours: 14,
    difficulty: 4,
    skippable: false,
    hourBasis: "5h concepts + 7h labs + 2h write-up — HEAVY",
    prereqs: ["strategy-compare-lab", "backtest-traps"],
    goals: [
      { zh: "实现Spearman IC。", en: "Implement Spearman IC." },
      { zh: "分层多空。", en: "Quantile long-short." },
      { zh: "真/假因子对照。", en: "True vs null factor." },
    ],
    mustTeach: [
      { zh: "IC=截面排序一致性。", en: "IC=cross-sectional rank agreement." },
      { zh: "因子海市蜃楼与虚假发现。", en: "Factor mirage / false discoveries." },
      { zh: "从经济假设出发。", en: "Start from economic hypothesis." },
    ],
    exercises: [
      { zh: "ic(factor,fwd)。", en: "ic(factor,fwd)." },
      { zh: "分层净值。", en: "Quantile NAVs." },
      { zh: "打乱因子对照。", en: "Scrambled control." },
      { zh: "IC衰减图。", en: "IC decay chart." },
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
      frontier: ["LLM formulaic alpha mining after this; formalized in P8"],
    },
    tasks: [
      { id: "ex1", text: { zh: "ic(factor,fwd)。", en: "ic(factor,fwd)." } },
      { id: "ex2", text: { zh: "分层净值。", en: "Quantile NAVs." } },
      { id: "ex3", text: { zh: "打乱因子对照。", en: "Scrambled control." } },
      { id: "ex4", text: { zh: "IC衰减图。", en: "IC decay chart." } },
      { id: "done1", text: { zh: "IC+分层+空因子报告。", en: "IC+quantile+null report." } },
    ],
  },
  {
    slug: "factor-portfolio-lab",
    status: "outline",
    title: { zh: "因子到组合实验", en: "Factor-to-portfolio lab" },
    summary: { zh: "换手、简单中性化、多因子合成诚实评估。", en: "Turnover, simple neutralization, honest multi-factor combo." },
    hours: 7,
    difficulty: 4,
    skippable: false,
    hourBasis: "2h concepts + 4.5h lab + 0.5h quiz",
    prereqs: ["factor-workflow"],
    goals: [
      { zh: "估计因子组合换手。", en: "Estimate factor-portfolio turnover." },
      { zh: "简易市值中性化示意。", en: "Simple size neutralization sketch." },
      { zh: "单因子vs等权多因子。", en: "Single vs EW multi-factor." },
    ],
    mustTeach: [
      { zh: "合成不自动提高可交易性。", en: "Combining ≠ auto tradeability." },
      { zh: "换手与成本再决定净收益。", en: "Turnover/costs decide net returns." },
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
    status: "outline",
    title: { zh: "机器学习防泄漏", en: "ML anti-leakage" },
    summary: { zh: "时间切分、特征shift、标签直觉、purge/embargo、元标签、试验次数。", en: "Time splits, feature shifts, labels, purge/embargo, meta-labeling, trial counts." },
    hours: 14,
    difficulty: 5,
    skippable: false,
    hourBasis: "5h AFML concepts + 7h labs + 2h write-up — HEAVY",
    prereqs: ["factor-workflow", "backtest-traps"],
    goals: [
      { zh: "演示shuffle泄漏。", en: "Demo shuffle leakage." },
      { zh: "时间切分并shift特征。", en: "Chronological split + shifted features." },
      { zh: "用IC而非仅准确率评价。", en: "Evaluate with IC not accuracy alone." },
    ],
    mustTeach: [
      { zh: "失败常在管线。", en: "Failures often in pipelines." },
      { zh: "禁止时序shuffle。", en: "No shuffling time series." },
      { zh: "purge/embargo直觉。", en: "Purge/embargo intuition." },
      { zh: "元标签：先方向再是否交易。", en: "Meta-labeling: side then trade-or-not." },
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
    status: "outline",
    title: { zh: "现代ML量化流水线（Qlib等）", en: "Modern ML quant pipelines (Qlib et al.)" },
    summary: { zh: "简单模型打底的可复现流水线；可选Qlib；不神话深度学习。", en: "Reproducible pipelines with simple models; optional Qlib; no DL mythology." },
    hours: 8,
    difficulty: 4,
    skippable: false,
    hourBasis: "3h architecture + 4h mini-pipeline + 1h optional Qlib",
    prereqs: ["ml-leakage-control", "data-cleaning"],
    goals: [
      { zh: "特征→模型→预测→简单组合草图。", en: "Feature→model→pred→simple portfolio sketch." },
      { zh: "说明为何先树/线性再深度。", en: "Trees/linear before deep nets." },
      { zh: "（可选）跑通Qlib quickstart思路。", en: "(Optional) Qlib quickstart ideas." },
    ],
    mustTeach: [
      { zh: "流水线可版本化比花哨模型重要。", en: "Versioned pipelines > flashy models." },
      { zh: "Qlib：Data/Model/Portfolio/Analysis。", en: "Qlib: Data/Model/Portfolio/Analysis." },
      { zh: "公开数据≠可交易优势。", en: "Public data ≠ tradeable edge." },
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
    status: "outline",
    title: { zh: "组合、风险与仓位", en: "Portfolio, risk & position sizing" },
    summary: { zh: "波动目标、回撤熔断、Kelly上界直觉、历史VaR。", en: "Vol targeting, DD brakes, Kelly upper-bound, historical VaR." },
    hours: 14,
    difficulty: 4,
    skippable: false,
    hourBasis: "5h concepts + 7h labs + 2h writing — HEAVY",
    prereqs: ["returns-vol-corr", "strategy-compare-lab"],
    goals: [
      { zh: "三种仓位层对照。", en: "Compare three sizing layers." },
      { zh: "解释满Kelly危险。", en: "Explain full-Kelly danger." },
      { zh: "陈述VaR局限。", en: "State VaR limits." },
    ],
    mustTeach: [
      { zh: "仓位是策略层。", en: "Sizing is a strategy layer." },
      { zh: "半Kelly/更保守。", en: "Half-Kelly or more conservative." },
      { zh: "风险预算与硬约束。", en: "Risk budgets and hard constraints." },
    ],
    exercises: [
      { zh: "固定/波动目标/回撤熔断。", en: "Fixed/vol-target/DD brake." },
      { zh: "VaR95+局限段。", en: "VaR95 + limits." },
      { zh: "风险偏好一页。", en: "Risk-preference page." },
    ],
    quizTopics: [
      { zh: "满Kelly问题", en: "Full-Kelly problem" },
      { zh: "波动目标直觉", en: "Vol-target intuition" },
      { zh: "VaR不是承诺", en: "VaR not a promise" },
    ],
    doneWhen: [
      { zh: "仓位对照表+风险一页。", en: "Sizing table + risk page." },
    ],
    methodTags: {
      classic: ["Canvas m11", "QuantStart VaR/Kelly", "UChicago FINM risk"],
      niche: [],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "固定/波动目标/回撤熔断。", en: "Fixed/vol-target/DD brake." } },
      { id: "ex2", text: { zh: "VaR95+局限段。", en: "VaR95 + limits." } },
      { id: "ex3", text: { zh: "风险偏好一页。", en: "Risk-preference page." } },
      { id: "done1", text: { zh: "仓位对照表+风险一页。", en: "Sizing table + risk page." } },
    ],
  },
  {
    slug: "execution-slippage",
    status: "outline",
    title: { zh: "执行与滑点", en: "Execution & slippage" },
    summary: { zh: "参与率、冲击示意、TWAP/VWAP直觉。", en: "Participation, impact sketch, TWAP/VWAP intuition." },
    hours: 7,
    difficulty: 3,
    skippable: false,
    hourBasis: "2.5h concepts + 4h experiments + 0.5h quiz",
    prereqs: ["costs-in-backtest", "portfolio-risk-sizing"],
    goals: [
      { zh: "加参与率约束。", en: "Add participation caps." },
      { zh: "写执行假设一页。", en: "Write execution sheet." },
    ],
    mustTeach: [
      { zh: "执行是策略一部分。", en: "Execution is part of strategy." },
      { zh: "研究与纸面共用成本模型。", en: "Research and paper share cost models." },
    ],
    exercises: [
      { zh: "参与率约束。", en: "Participation constraint." },
      { zh: "开盘vs收盘。", en: "Open vs close." },
      { zh: "执行一页纸。", en: "Execution one-pager." },
    ],
    quizTopics: [
      { zh: "隐性成本", en: "Implicit costs" },
      { zh: "参与率含义", en: "Participation meaning" },
    ],
    doneWhen: [
      { zh: "执行假设纳入主配置。", en: "Execution assumptions in main config." },
    ],
    methodTags: {
      classic: ["Canvas m12", "NYU impact/TCA", "QuantStart execution"],
      niche: ["@sera00111 execution/venue notes"],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "参与率约束。", en: "Participation constraint." } },
      { id: "ex2", text: { zh: "开盘vs收盘。", en: "Open vs close." } },
      { id: "ex3", text: { zh: "执行一页纸。", en: "Execution one-pager." } },
      { id: "done1", text: { zh: "执行假设纳入主配置。", en: "Execution assumptions in main config." } },
    ],
  },
  {
    slug: "risk-systems-lab",
    status: "outline",
    title: { zh: "风险系统小实验", en: "Mini risk-systems lab" },
    summary: { zh: "数据缺口暂停、回撤降仓、密钥不进git。", en: "Pause on gaps, de-risk on DD, secrets out of git." },
    hours: 5,
    difficulty: 3,
    skippable: false,
    hourBasis: "1.5h concepts + 3h labs + 0.5h quiz",
    prereqs: ["portfolio-risk-sizing", "execution-slippage"],
    goals: [
      { zh: "陈旧数据拒单。", en: "Refuse orders on stale data." },
      { zh: "回撤熔断。", en: "DD kill switch." },
      { zh: "自查无密钥。", en: "Self-check no secrets." },
    ],
    mustTeach: [
      { zh: "熔断是工程不是预测。", en: "Kill switches are engineering, not forecasts." },
    ],
    exercises: [
      { zh: "缺口→暂停。", en: "Gap→pause." },
      { zh: "回撤→降仓。", en: "DD→de-risk." },
      { zh: "密钥扫描。", en: "Secret scan." },
    ],
    quizTopics: [
      { zh: "硬约束", en: "Hard constraints" },
    ],
    doneWhen: [
      { zh: "三道硬约束演示通过。", en: "Three hard-constraint demos pass." },
    ],
    methodTags: {
      classic: ["Canvas m13 bits", "ML4T ops"],
      niche: ["Cookbook/Qbot config ideas"],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "缺口→暂停。", en: "Gap→pause." } },
      { id: "ex2", text: { zh: "回撤→降仓。", en: "DD→de-risk." } },
      { id: "ex3", text: { zh: "密钥扫描。", en: "Secret scan." } },
      { id: "done1", text: { zh: "三道硬约束演示通过。", en: "Three hard-constraint demos pass." } },
    ],
  },
];

const phase_P7_lessons: Lesson[] = [
  {
    slug: "paper-trading-infra",
    status: "outline",
    title: { zh: "纸面交易与迷你基建", en: "Paper trading & mini infra" },
    summary: { zh: "信号→目标→日志；≥5日；冻结版本。", en: "Signal→target→log; ≥5 days; freeze version." },
    hours: 10,
    difficulty: 3,
    skippable: false,
    hourBasis: "3h design + 6h running/logging + 1h template",
    prereqs: ["risk-systems-lab"],
    goals: [
      { zh: "CSV纸面撮合。", en: "CSV paper matching." },
      { zh: "出日报。", en: "Emit daily reports." },
      { zh: "解释纸面验流程。", en: "Explain paper validates process." },
    ],
    mustTeach: [
      { zh: "纸面期间不按盈亏改规则。", en: "Don't edit rules for P&L during paper." },
      { zh: "对账与异常日志。", en: "Reconciliation and anomaly logs." },
    ],
    exercises: [
      { zh: "CSV撮合。", en: "CSV matching." },
      { zh: "5日日志。", en: "5-day logs." },
      { zh: "日报模板。", en: "Daily template." },
    ],
    quizTopics: [
      { zh: "纸面验证什么", en: "What paper validates" },
      { zh: "为何冻结版本", en: "Why freeze versions" },
    ],
    doneWhen: [
      { zh: "≥5日日志包。", en: "≥5-day log pack." },
    ],
    methodTags: {
      classic: ["Canvas m13", "JoinQuant W08", "QuantStart paper-before-live"],
      niche: ["Qbot/Atlas reference architecture", "Nautilus isomorphic paper/sim concept"],
      frontier: [],
    },
    tasks: [
      { id: "ex1", text: { zh: "CSV撮合。", en: "CSV matching." } },
      { id: "ex2", text: { zh: "5日日志。", en: "5-day logs." } },
      { id: "ex3", text: { zh: "日报模板。", en: "Daily template." } },
      { id: "done1", text: { zh: "≥5日日志包。", en: "≥5-day log pack." } },
    ],
  },
  {
    slug: "compliance-ethics",
    status: "outline",
    title: { zh: "合规、风险心态与研究伦理", en: "Compliance, risk mindset & research ethics" },
    summary: { zh: "先生存；学习≠投顾；拒绝选择性汇报。", en: "Survive first; learning≠advisory; refuse selective reporting." },
    hours: 4,
    difficulty: 2,
    skippable: false,
    hourBasis: "2h reading + 1.5h writing + 0.5h quiz",
    prereqs: ["paper-trading-infra"],
    goals: [
      { zh: "写风险偏好。", en: "Write risk preference." },
      { zh: "记录失败。", en: "Log failures." },
      { zh: "拆穿保证夏普话术。", en: "Debunk guaranteed-Sharpe pitches." },
    ],
    mustTeach: [
      { zh: "本站学习材料非投资建议。", en: "Site materials are not investment advice." },
      { zh: "不懂则零仓位。", en: "Zero size if you don't understand." },
    ],
    exercises: [
      { zh: "风险一页。", en: "Risk page." },
      { zh: "三次失败。", en: "Three failures." },
      { zh: "话术审计。", en: "Pitch audit." },
    ],
    quizTopics: [
      { zh: "选择性汇报危害", en: "Harm of selective reporting" },
      { zh: "学习与受监管业务边界", en: "Learning vs regulated advice" },
    ],
    doneWhen: [
      { zh: "伦理清单勾选完成。", en: "Ethics checklist complete." },
    ],
    methodTags: {
      classic: ["Canvas m14", "AFML scientific ethics"],
      niche: [],
      frontier: ["LLM/agent research must obey same ethics/hold-out (link P8)"],
    },
    tasks: [
      { id: "ex1", text: { zh: "风险一页。", en: "Risk page." } },
      { id: "ex2", text: { zh: "三次失败。", en: "Three failures." } },
      { id: "ex3", text: { zh: "话术审计。", en: "Pitch audit." } },
      { id: "done1", text: { zh: "伦理清单勾选完成。", en: "Ethics checklist complete." } },
    ],
  },
];

const phase_P8_lessons: Lesson[] = [
  {
    slug: "frontier-llm-agents",
    status: "outline",
    title: { zh: "前沿：LLM / 多智能体量化研发", en: "Frontier: LLM / multi-agent quant R&D" },
    summary: { zh: "RD-Agent(Q)、公式化alpha挖掘、Quant-Arena：批判性试用，不替代防泄漏。", en: "RD-Agent(Q), formulaic alpha mining, Quant-Arena: critical trials — never replace anti-leakage." },
    hours: 8,
    difficulty: 5,
    skippable: false,
    hourBasis: "4h guided reading + 3h critical exercises + 1h rules rewrite",
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
      frontier: ["microsoft/RD-Agent + R&D-Agent(Q) NeurIPS 2025 / arXiv:2505.15155", "Chain-of-Alpha arXiv:2508.06312", "LLM+MCTS arXiv:2505.11122", "Quant-Arena arXiv:2610.30113"],
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
    status: "outline",
    title: { zh: "前沿：时序基础模型 · 另类数据 · Crypto/链上", en: "Frontier: TSFMs · alt-data · crypto/on-chain" },
    summary: { zh: "Chronos/TimesFM金融评测的谨慎结论；另类数据；CCXT/资金费率/链上。", en: "Cautious Chronos/TimesFM finance results; alt-data; CCXT/funding/on-chain." },
    hours: 8,
    difficulty: 4,
    skippable: false,
    hourBasis: "4h paper/docs + 3h design exercises + 1h optional pull",
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
      frontier: ["Chronos/TimesFM finance evals e.g. arXiv:2511.18578", "Trading Strategy GMX CCXT adapters 2025", "OpenBB-style alt/market data aggregation"],
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
    status: "outline",
    title: { zh: "结业项目：诚实的小策略", en: "Capstone: an honest small strategy" },
    summary: { zh: "假设→数据→信号→含成本回测→样本外→仓位→纸面；可选前沿负结果附录。", en: "Hypothesis→data→signal→costed backtest→OOS→sizing→paper; optional frontier failure appendix." },
    hours: 24,
    difficulty: 5,
    skippable: false,
    hourBasis: "6h design/data + 10h backtest/OOS + 4h paper + 4h writing — project",
    prereqs: ["paper-trading-infra", "compliance-ethics", "factor-workflow", "portfolio-risk-sizing"],
    goals: [
      { zh: "交付可复现研究包。", en: "Deliver reproducible research pack." },
      { zh: "含成本敏感与样本外。", en: "Include cost sensitivity and OOS." },
      { zh: "附纸面日志与限制条款。", en: "Attach paper logs and limitations." },
    ],
    mustTeach: [
      { zh: "评分看诚实与工程不看是否赚钱。", en: "Grade honesty and engineering, not profits." },
      { zh: "可选前沿附录不得削弱核心纪律。", en: "Optional frontier appendix must not weaken core discipline." },
    ],
    exercises: [
      { zh: "一页假设。", en: "One-page hypothesis." },
      { zh: "含成本+shift回测。", en: "Costed+shifted backtest." },
      { zh: "OOS/walk-forward。", en: "OOS/walk-forward." },
      { zh: "≥5日纸面。", en: "≥5-day paper." },
      { zh: "量规自评。", en: "Rubric self-score." },
      { zh: "（可选）前沿失败对照附录。", en: "(Optional) frontier failure appendix." },
    ],
    quizTopics: [
    ],
    doneWhen: [
      { zh: "结业包通过自评量规全部达标。", en: "Capstone pack meets all pass rubric rows." },
    ],
    methodTags: {
      classic: ["Canvas capstone", "JoinQuant综合+模拟"],
      niche: ["Open strategy libs sparingly as hypothesis inspiration only"],
      frontier: ["Optional negative-result appendix on RD-Agent/TSFM/on-chain signal"],
    },
    tasks: [
      { id: "ex1", text: { zh: "一页假设。", en: "One-page hypothesis." } },
      { id: "ex2", text: { zh: "含成本+shift回测。", en: "Costed+shifted backtest." } },
      { id: "ex3", text: { zh: "OOS/walk-forward。", en: "OOS/walk-forward." } },
      { id: "ex4", text: { zh: "≥5日纸面。", en: "≥5-day paper." } },
      { id: "ex5", text: { zh: "量规自评。", en: "Rubric self-score." } },
      { id: "ex6", text: { zh: "（可选）前沿失败对照附录。", en: "(Optional) frontier failure appendix." } },
      { id: "done1", text: { zh: "结业包通过自评量规全部达标。", en: "Capstone pack meets all pass rubric rows." } },
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
  "quantstart-sat": "https://www.quantstart.com/successful-algorithmic-trading-ebook/",
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
  "joinquant-8w": "http://lookmori.cn/",
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
