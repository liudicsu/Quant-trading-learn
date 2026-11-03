/**
 * REFERENCE ONLY — NOT USED BY THE SITE.
 * Do not import this file from app code. Official outline will be rearranged later.
 * Kept for research notes alongside docs/CURRICULUM_RESEARCH.md.
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
  minutes: number;
  resources: string[];
  tasks: Task[];
  objectives?: L10n[];
  prereqs?: string[];
  mustTeach?: L10n[];
  pitfalls?: L10n[];
}

export interface Month {
  id: number;
  slug: string;
  title: L10n;
  goal: L10n;
  topics: L10n[];
  milestones: L10n[];
  lessons: Lesson[];
}

export const COURSE_META = {
  disclaimer: {
    zh: "学习用途，非投资建议。不构成买卖推荐或收益承诺。",
    en: "Learning only -- not investment advice. No trade recommendations or profit promises.",
  },
  audience: {
    zh: "程序员 / 算法工程师，有少量投资经验",
    en: "Programmer / algorithm engineer with light investing experience",
  },
  estimatedHours: "100-130",
  estimatedWeeks: "20-22",
  lessonCount: 20,
  monthCount: 5,
};

const month1Lessons: Lesson[] = [
  {
    slug: "markets-language",
    title: { zh: "市场与交易语言", en: "Markets & trading vocabulary" },
    summary: { zh: "分清资产、交易所、多空与杠杆，用假设到归因描述策略。", en: "Separate assets, venues, long/short and leverage; describe strategies as hypothesis to attribution." },
    minutes: 120,
    resources: ["quantstart-sat", "joinquant-zero", "canvas-one-stop"],
    objectives: [
      { zh: "能解释多头、空头、杠杆与现金账户。", en: "Explain long, short, leverage and cash accounts." },
      { zh: "能用三句话写下可复现研究目标。", en: "Write a reproducible research goal in three sentences." },
      { zh: "能区分 Alpha 与 Beta 的朴素含义。", en: "State plain-language Alpha vs Beta." },
      { zh: "能说明程序员优势在工程化研究。", en: "Argue the programmer edge is research engineering." },
    ],
    mustTeach: [
      { zh: "策略必须可复现：数据版本、代码、参数、成本假设。", en: "Strategies must be reproducible: data version, code, params, costs." },
      { zh: "主目标通常是约束下的风险调整后表现。", en: "Primary goal is usually risk-adjusted performance under constraints." },
    ],
    pitfalls: [
      { zh: "把投资建议当成课程目标。", en: "Treating investment tips as the course goal." },
      { zh: "尚未理解摩擦就宣称可实盘。", en: "Claiming live-ready before understanding frictions." },
    ],
    prereqs: [],
    tasks: [
      {
        id: "ret-nav",
        text: { zh: "用 CSV 价格算简单收益并画净值", en: "Compute simple returns from CSV and plot NAV" },
      },
      {
        id: "goal-3",
        text: { zh: "写下研究目标三句话", en: "Write the three-sentence research goal" },
      },
      {
        id: "friction-list",
        text: { zh: "列出至少五种市场摩擦", en: "List at least five market frictions" },
      },
      {
        id: "quiz-m1",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "microstructure-orders",
    title: { zh: "微观结构与订单", en: "Microstructure & order types" },
    summary: { zh: "读懂买卖价、中间价、市价/限价，并把滑点写入成交模型。", en: "Read bid/ask/mid, contrast market vs limit, put slippage into the fill model." },
    minutes: 150,
    resources: ["nyu-mathga-2708", "quant-wiki", "canvas-one-stop"],
    objectives: [
      { zh: "能手算 mid 与市价买相对 mid 的 bps。", en: "Compute mid and market-buy bps vs mid by hand." },
      { zh: "能解释市价与限价差异。", en: "Explain market vs limit differences." },
      { zh: "能指出同 bar 零成本过乐观。", en: "Explain why same-bar zero-cost fills are optimistic." },
      { zh: "能写一页成交与成本假设。", en: "Write a one-page fill and cost sheet." },
    ],
    mustTeach: [
      { zh: "mid = (bid+ask)/2；价差是即时成本。", en: "mid=(bid+ask)/2; spread is immediate cost." },
      { zh: "市价买单更贴近 ask。", en: "Market buys tend toward the ask." },
      { zh: "冲击与延迟本课只建直觉，不做 HFT 配方。", en: "Impact/latency: intuition only, no HFT recipes." },
    ],
    pitfalls: [
      { zh: "默认以中间价成交。", en: "Assuming mid fills." },
      { zh: "把 HFT 故事当零售说明书。", en: "Treating HFT lore as a retail playbook." },
    ],
    prereqs: ["markets-language"],
    tasks: [
      {
        id: "bps-hand",
        text: { zh: "手算市价买相对 mid 的 bps", en: "Hand-compute market-buy vs mid in bps" },
      },
      {
        id: "cost-page",
        text: { zh: "写明佣金、滑点、成交时点", en: "Document commission, slippage, fill timing" },
      },
      {
        id: "open-vs-close",
        text: { zh: "对比收盘与次日开盘成交", en: "Compare close vs next-open fills" },
      },
      {
        id: "quiz-m2",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "returns-vol-corr",
    title: { zh: "收益、波动与相关", en: "Returns, volatility & correlation" },
    summary: { zh: "正确年化，实现夏普与最大回撤，观察压力期相关抬升。", en: "Annualize correctly; implement Sharpe and MDD; watch stress correlations." },
    minutes: 150,
    resources: ["quantstart-sat", "joinquant-8w", "canvas-one-stop"],
    objectives: [
      { zh: "能区分简单收益与对数收益用途。", en: "Distinguish simple vs log returns." },
      { zh: "能用 σ_day×√252 年化波动。", en: "Annualize daily vol with σ_day×√252." },
      { zh: "能实现最大回撤并解释路径依赖。", en: "Implement MDD and explain path dependence." },
      { zh: "能计算滚动波动与滚动相关。", en: "Compute rolling vol and correlation." },
    ],
    mustTeach: [
      { zh: "夏普需声明频率与 Rf 约定。", en: "Sharpe needs stated frequency and Rf." },
      { zh: "危机期相关常趋近 1。", en: "In crises correlations often approach 1." },
    ],
    pitfalls: [
      { zh: "对均值错误使用 √252 年化。", en: "Annualizing means with √252 by mistake." },
      { zh: "只用全样本相关做风控。", en: "Using only full-sample correlation for risk." },
    ],
    prereqs: ["markets-language"],
    tasks: [
      {
        id: "mdd-impl",
        text: { zh: "实现 max_drawdown(nav)", en: "Implement max_drawdown(nav)" },
      },
      {
        id: "roll-vol",
        text: { zh: "画 20 日滚动波动", en: "Plot 20-day rolling volatility" },
      },
      {
        id: "roll-corr",
        text: { zh: "画滚动相关并标压力期", en: "Plot rolling correlation; mark stress" },
      },
      {
        id: "quiz-m3",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "eval-lab",
    title: { zh: "评估实验：基准与诚实指标表", en: "Evaluation lab: benchmarks & honest metrics" },
    summary: { zh: "相同成本假设下对照玩具信号与买入持有。", en: "Compare a toy signal to buy-and-hold under identical costs." },
    minutes: 120,
    resources: ["joinquant-8w", "canvas-one-stop"],
    objectives: [
      { zh: "能选择匹配的可投资基准。", en: "Choose a matching investable benchmark." },
      { zh: "能报告成本后年化/波动/夏普/回撤/换手。", en: "Report net ann. return/vol/Sharpe/MDD/turnover." },
      { zh: "能解释胜率高不等于好策略。", en: "Explain why win rate is not enough." },
    ],
    mustTeach: [
      { zh: "只报毛收益不诚实。", en: "Gross-only reporting is dishonest." },
      { zh: "换手放大成本。", en: "Turnover amplifies costs." },
    ],
    pitfalls: [
      { zh: "挑选有利起始日。", en: "Cherry-picking start dates." },
    ],
    prereqs: ["returns-vol-corr", "microstructure-orders"],
    tasks: [
      {
        id: "metric-table",
        text: { zh: "做成本后指标对照表", en: "Build net-of-cost metric table" },
      },
      {
        id: "cost-bump",
        text: { zh: "提高一档滑点观察变化", en: "Bump slippage one step; observe" },
      },
      {
        id: "baseline",
        text: { zh: "相对买入持有写结论三句", en: "Three-sentence conclusion vs buy-and-hold" },
      },
      {
        id: "quiz-m4",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
];

const month2Lessons: Lesson[] = [
  {
    slug: "data-cleaning",
    title: { zh: "数据与清洗", en: "Data & cleaning" },
    summary: { zh: "可版本化管线：复权、停牌、缺失、幸存者偏差与时点对齐。", en: "Versioned pipeline: adjustments, halts, missingness, survivorship, PIT." },
    minutes: 180,
    resources: ["qlib-docs", "joinquant-zero", "pyquant-data"],
    objectives: [
      { zh: "能解释复权前后收益差异。", en: "Explain adjusted vs raw return differences." },
      { zh: "能对齐交易日历并断言缺失率。", en: "Align calendar and assert missingness." },
      { zh: "能举例幸存者偏差。", en: "Give a survivorship-bias example." },
      { zh: "能写数据说明书。", en: "Write a data sheet." },
    ],
    mustTeach: [
      { zh: "基本面需 PIT 对齐。", en: "Fundamentals need point-in-time alignment." },
      { zh: "今日成分股不等于历史宇宙。", en: "Today's members ≠ historical universe." },
    ],
    pitfalls: [
      { zh: "静默填充跨越长期停牌。", en: "Silent fill across long suspensions." },
      { zh: "混用时区造成前瞻。", en: "Timezone mix causing lookahead." },
    ],
    prereqs: ["eval-lab"],
    tasks: [
      {
        id: "reindex-assert",
        text: { zh: "按交易日 reindex 并断言缺失率", en: "Reindex to sessions; assert missingness" },
      },
      {
        id: "adj-compare",
        text: { zh: "对比复权与未复权收益", en: "Compare adjusted vs unadjusted returns" },
      },
      {
        id: "data-sheet",
        text: { zh: "写一页数据说明书", en: "Write a one-page data sheet" },
      },
      {
        id: "quiz-d1",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "backtest-traps",
    title: { zh: "回测陷阱", en: "Backtesting traps" },
    summary: { zh: "修复前瞻偏差，记录试验次数，坚持样本外。", en: "Fix lookahead, log trials, insist on OOS." },
    minutes: 180,
    resources: ["afml-notes", "joinquant-8w", "canvas-one-stop"],
    objectives: [
      { zh: "能构造作弊均线与诚实 shift 对照。", en: "Build cheating vs honest shifted MA controls." },
      { zh: "能解释过拟合与多重检验直觉。", en: "Explain overfitting and multiple-testing intuition." },
      { zh: "能跑通样本外或 walk-forward。", en: "Run hold-out or walk-forward." },
      { zh: "能记录失败实验。", en: "Log failed experiments." },
    ],
    mustTeach: [
      { zh: "回测越漂亮越要审讯。", en: "The prettier the backtest, the harder the interrogation." },
      { zh: "把回测当作交叉验证，警惕虚假发现。", en: "Treat backtests as CV; watch false discoveries." },
    ],
    pitfalls: [
      { zh: "全样本调参后声称样本外。", en: "Tuning full-sample then claiming OOS." },
      { zh: "只保留成功实验。", en: "Keeping only successes." },
    ],
    prereqs: ["data-cleaning"],
    tasks: [
      {
        id: "cheat-vs-honest",
        text: { zh: "均线未 shift vs shift(1)", en: "MA unshifted vs shift(1)" },
      },
      {
        id: "grid-overfit",
        text: { zh: "小参数网格观察过拟合", en: "Small grid; observe overfitting" },
      },
      {
        id: "holdout",
        text: { zh: "冻结规则后打开末段样本外", en: "Freeze rules; open final hold-out" },
      },
      {
        id: "quiz-d2",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "costs-in-backtest",
    title: { zh: "成本写入回测", en: "Putting costs into the backtest" },
    summary: { zh: "佣金与滑点写入净值，做成本敏感表。", en: "Write fees/slippage into NAV; cost sensitivity table." },
    minutes: 120,
    resources: ["quantstart-sat", "joinquant-8w"],
    objectives: [
      { zh: "能实现净收益公式含换手成本。", en: "Implement net returns with turnover costs." },
      { zh: "能区分显性与隐性成本。", en: "Separate explicit vs implicit costs." },
      { zh: "能做至少三档成本敏感。", en: "Run at least three cost tiers." },
    ],
    mustTeach: [
      { zh: "换手×单边成本是拖累项。", en: "Turnover × one-way cost is drag." },
      { zh: "零成本曲线不能当实盘论据。", en: "Zero-cost curves are not live evidence." },
    ],
    pitfalls: [
      { zh: "对低流动性用过小固定 bps。", en: "Tiny fixed bps on illiquids." },
    ],
    prereqs: ["backtest-traps"],
    tasks: [
      {
        id: "net-pnl",
        text: { zh: "把成本写入向量化回测", en: "Add costs into vectorized backtest" },
      },
      {
        id: "ladder",
        text: { zh: "成本阶梯对夏普/回撤", en: "Cost ladder vs Sharpe/MDD" },
      },
      {
        id: "quiz-d3",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "vectorized-vs-event",
    title: { zh: "向量化 vs 事件驱动直觉", en: "Vectorized vs event-driven intuition" },
    summary: { zh: "理解向量化何时在成交时点撒谎；建立事件驱动心智模型。", en: "Know when vectorized fills lie; build event-driven mental model." },
    minutes: 150,
    resources: ["vectorbt-docs", "zipline-reloaded", "backtrader"],
    objectives: [
      { zh: "能说出向量化常见默认假设。", en: "State common vectorized defaults." },
      { zh: "能对比收盘成交与次 bar 开盘。", en: "Compare close vs next-bar open fills." },
      { zh: "能用 initialize/handle_data 描述事件循环。", en: "Describe event loop via initialize/handle_data." },
    ],
    mustTeach: [
      { zh: "引擎选择即成交与日历假设。", en: "Engine choice is fill and calendar assumptions." },
      { zh: "先诚实向量化，再事件驱动验证。", en: "Honest vectorized first, then event-driven validation." },
    ],
    pitfalls: [
      { zh: "未读文档相信库默认。", en: "Trusting unread library defaults." },
    ],
    prereqs: ["costs-in-backtest"],
    tasks: [
      {
        id: "two-fills",
        text: { zh: "同一信号两种成交时点", en: "Same signal, two fill timings" },
      },
      {
        id: "assumptions-para",
        text: { zh: "写一段回测假设", en: "Write backtest assumptions paragraph" },
      },
      {
        id: "optional-zipline",
        text: { zh: "（可选）浏览 Zipline Reloaded 入门", en: "(Optional) Skim Zipline Reloaded quickstart" },
      },
      {
        id: "quiz-d4",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
];

const month3Lessons: Lesson[] = [
  {
    slug: "momentum-trend",
    title: { zh: "动量与趋势", en: "Momentum & trend" },
    summary: { zh: "时序与截面动量；报告换手回撤；波动目标。", en: "TS and CS momentum; turnover/drawdown; vol targeting." },
    minutes: 180,
    resources: ["chan-books", "canvas-one-stop", "quant-wiki"],
    objectives: [
      { zh: "能实现双均线与简化 12-1 对照。", en: "Implement dual MA vs simplified 12-1." },
      { zh: "能解释跳过近一月动机。", en: "Explain skip-month motive." },
      { zh: "能加入波动目标并比较回撤。", en: "Add vol targeting; compare drawdowns." },
    ],
    mustTeach: [
      { zh: "截面排序与时序信号是两类问题。", en: "CS ranking and TS signals differ." },
      { zh: "拥挤与换手侵蚀纸面优势。", en: "Crowding and turnover erode paper edges." },
    ],
    pitfalls: [
      { zh: "忽视容量与冲击。", en: "Ignoring capacity and impact." },
    ],
    prereqs: ["vectorized-vs-event"],
    tasks: [
      {
        id: "dual-vs-mom",
        text: { zh: "双均线 vs 动量对照", en: "Dual-MA vs momentum control" },
      },
      {
        id: "vol-target",
        text: { zh: "目标波动 10% 对比", en: "10% vol target comparison" },
      },
      {
        id: "by-year",
        text: { zh: "分年收益表", en: "Year-by-year return table" },
      },
      {
        id: "quiz-s1",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "mean-reversion",
    title: { zh: "均值回归", en: "Mean reversion" },
    summary: { zh: "滚动 z-score 开平仓；识别趋势市失效。", en: "Rolling z-score entries; recognise trend-regime failure." },
    minutes: 150,
    resources: ["chan-books", "canvas-one-stop"],
    objectives: [
      { zh: "能实现 z-score 开平仓。", en: "Implement z-score entry/exit." },
      { zh: "能对比有无止损。", en: "Compare with/without stop." },
      { zh: "能写失效条件清单。", en: "Write invalidation checklist." },
    ],
    mustTeach: [
      { zh: "强趋势中回归易反复止损。", en: "In strong trends reversion dies by repeated stops." },
      { zh: "阈值应再估计。", en: "Thresholds should be re-estimated." },
    ],
    pitfalls: [
      { zh: "在明显趋势市硬做回归。", en: "Forcing reversion in clear trends." },
    ],
    prereqs: ["momentum-trend"],
    tasks: [
      {
        id: "z-rules",
        text: { zh: "实现 z<-2 / z>2", en: "Implement z<-2 / z>2" },
      },
      {
        id: "stop-ab",
        text: { zh: "有无止损 A/B", en: "With/without stop A/B" },
      },
      {
        id: "fail-list",
        text: { zh: "写下失效与停用条件", en: "Write failure/shutdown conditions" },
      },
      {
        id: "quiz-s2",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "pairs-stat-arb",
    title: { zh: "配对与统计套利入门", en: "Pairs & intro to statistical arb" },
    summary: { zh: "交易价差；滚动估计对冲比。", en: "Trade the spread; rolling hedge ratio." },
    minutes: 180,
    resources: ["chan-books", "stern-syllabus", "canvas-one-stop"],
    objectives: [
      { zh: "能解释高相关不足够。", en: "Explain why high correlation is not enough." },
      { zh: "能构造滚动价差与残差 z。", en: "Build rolling spread and residual z." },
      { zh: "能讨论腿失效或流动性问题。", en: "Discuss broken leg or liquidity issues." },
    ],
    mustTeach: [
      { zh: "协整直觉：组合可能平稳。", en: "Cointegration intuition: combo may be stationary." },
      { zh: "对冲比必须再估计。", en: "Hedge ratios must be re-estimated." },
    ],
    pitfalls: [
      { zh: "全样本 beta 一劳永逸。", en: "Forever full-sample beta." },
    ],
    prereqs: ["mean-reversion"],
    tasks: [
      {
        id: "roll-beta",
        text: { zh: "滚动 beta 价差与 z", en: "Rolling-beta spread and z" },
      },
      {
        id: "static-vs-roll",
        text: { zh: "全样本 vs 滚动对冲", en: "Static vs rolling hedge" },
      },
      {
        id: "shock-note",
        text: { zh: "不对称冲击情景一段", en: "Asymmetric-shock scenario note" },
      },
      {
        id: "quiz-s3",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "factor-workflow",
    title: { zh: "因子研究工作流", en: "Factor research workflow" },
    summary: { zh: "IC 与分层；假设到因子到组合。", en: "IC and quantiles; hypothesis to factor to portfolio." },
    minutes: 180,
    resources: ["afml-notes", "qlib-docs", "lopez-factor-mirage"],
    objectives: [
      { zh: "能实现 Spearman IC。", en: "Implement Spearman IC." },
      { zh: "能做分层多空净值。", en: "Build quantile long-short NAVs." },
      { zh: "能对比真因子与打乱因子。", en: "Compare real vs scrambled factor." },
    ],
    mustTeach: [
      { zh: "IC 衡量截面排序一致性。", en: "IC measures cross-sectional rank agreement." },
      { zh: "警惕虚假发现与因子海市蜃楼。", en: "Watch false discoveries and factor mirages." },
    ],
    pitfalls: [
      { zh: "只展示漂亮显著因子。", en: "Showing only pretty significant factors." },
    ],
    prereqs: ["pairs-stat-arb"],
    tasks: [
      {
        id: "ic-impl",
        text: { zh: "实现 ic(factor, fwd)", en: "Implement ic(factor, fwd)" },
      },
      {
        id: "quantile-nav",
        text: { zh: "分层组合净值", en: "Quantile portfolio NAVs" },
      },
      {
        id: "null-factor",
        text: { zh: "打乱因子对照", en: "Scrambled factor control" },
      },
      {
        id: "quiz-s4",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "strategy-compare-lab",
    title: { zh: "策略对照实验", en: "Strategy comparison lab" },
    summary: { zh: "同一宇宙成本指标下对照；复杂须胜过简单基准。", en: "Same universe/costs/metrics; complexity must beat simple baseline." },
    minutes: 120,
    resources: ["canvas-one-stop"],
    objectives: [
      { zh: "能产出三策略并排报告。", en: "Produce three-strategy side-by-side report." },
      { zh: "能说明复杂规则未胜过基准的原因。", en: "Explain why complexity failed the baseline." },
    ],
    mustTeach: [
      { zh: "对照实验要控制隐藏假设。", en: "Pin hidden assumptions in comparisons." },
    ],
    pitfalls: [
      { zh: "每策略偷偷用不同成本。", en: "Different silent costs per strategy." },
    ],
    prereqs: ["factor-workflow", "momentum-trend", "mean-reversion"],
    tasks: [
      {
        id: "report3",
        text: { zh: "提交三策略对照报告", en: "Submit three-strategy comparison" },
      },
      {
        id: "baseline-win",
        text: { zh: "指定简单基准并判定", en: "Name baseline and call winner" },
      },
      {
        id: "quiz-s5",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
];

const month4Lessons: Lesson[] = [
  {
    slug: "ml-leakage",
    title: { zh: "机器学习进量化：防泄漏", en: "ML for quant: anti-leakage" },
    summary: { zh: "时间安全切分、特征移位、简单模型优先；purge/embargo 与元标签直觉。", en: "Time-safe splits, shifted features, simple models; purge/embargo and meta-label intuition." },
    minutes: 210,
    resources: ["afml-notes", "ml4t-repo", "qlib-docs"],
    objectives: [
      { zh: "能演示 shuffle 泄漏。", en: "Demonstrate shuffle leakage." },
      { zh: "能时间切分并 shift 特征。", en: "Chronological split with shifted features." },
      { zh: "能用 IC/分层而非仅准确率评价。", en: "Evaluate with IC/quantiles not accuracy alone." },
      { zh: "能陈述试验次数意义。", en: "State why trial count matters." },
    ],
    mustTeach: [
      { zh: "失败常在数据管线而非模型名。", en: "Failures are often pipelines not model names." },
      { zh: "标签构造决定可交易性。", en: "Label design drives tradeability." },
    ],
    pitfalls: [
      { zh: "默认 K-fold shuffle。", en: "Default K-fold shuffle." },
      { zh: "边看测试边调参。", en: "Tuning while peeking at test." },
    ],
    prereqs: ["strategy-compare-lab"],
    tasks: [
      {
        id: "shuffle-ab",
        text: { zh: "随机 vs 时间切分对照", en: "Random vs chronological split" },
      },
      {
        id: "planted-leaks",
        text: { zh: "修复三处人为泄漏", en: "Fix three planted leaks" },
      },
      {
        id: "ic-eval",
        text: { zh: "用 IC 评价模型输出", en: "Evaluate model output with IC" },
      },
      {
        id: "quiz-ml",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "portfolio-risk-sizing",
    title: { zh: "组合、风险与仓位", en: "Portfolio, risk & position sizing" },
    summary: { zh: "波动目标、回撤熔断、Kelly 上界直觉、历史 VaR。", en: "Vol targeting, DD brakes, Kelly upper-bound intuition, historical VaR." },
    minutes: 150,
    resources: ["quantstart-sat", "uchicago-finm", "canvas-one-stop"],
    objectives: [
      { zh: "能实现波动目标仓位。", en: "Implement vol-target sizing." },
      { zh: "能解释满 Kelly 危险。", en: "Explain full-Kelly danger under error." },
      { zh: "能计算历史 VaR 并述局限。", en: "Compute historical VaR and state limits." },
    ],
    mustTeach: [
      { zh: "仓位是策略一层。", en: "Sizing is a strategy layer." },
      { zh: "实务常用半 Kelly 或更保守。", en: "Practice often uses half-Kelly or less." },
    ],
    pitfalls: [
      { zh: "把 VaR 当不会亏更多的承诺。", en: "Treating VaR as a no-worse promise." },
    ],
    prereqs: ["ml-leakage"],
    tasks: [
      {
        id: "three-sizing",
        text: { zh: "固定 vs 波动目标 vs 回撤熔断", en: "Fixed vs vol target vs DD brake" },
      },
      {
        id: "var95",
        text: { zh: "计算并讨论 95% 历史 VaR", en: "Compute/discuss 95% historical VaR" },
      },
      {
        id: "risk-page",
        text: { zh: "写风险偏好一页纸", en: "Write risk-preference page" },
      },
      {
        id: "quiz-risk",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "execution-slippage",
    title: { zh: "执行与滑点", en: "Execution & slippage" },
    summary: { zh: "执行是策略一部分；参与率与冲击示意。", en: "Execution is part of strategy; participation vs impact sketch." },
    minutes: 120,
    resources: ["nyu-mathga-2708", "quantstart-sat"],
    objectives: [
      { zh: "能区分显性与隐性成本。", en: "Separate explicit vs implicit costs." },
      { zh: "能用参与率约束规模。", en: "Cap size by participation." },
      { zh: "能对比开盘/收盘成交假设。", en: "Compare open vs close fill assumptions." },
    ],
    mustTeach: [
      { zh: "TWAP/VWAP 是日程直觉非收益保证。", en: "TWAP/VWAP are scheduling intuitions not guarantees." },
      { zh: "研究与纸面共用成本模型。", en: "Research and paper share a cost model." },
    ],
    pitfalls: [
      { zh: "研究零冲击、实盘大额。", en: "Zero-impact research then large live size." },
    ],
    prereqs: ["portfolio-risk-sizing"],
    tasks: [
      {
        id: "part-cap",
        text: { zh: "实现最大参与率约束", en: "Implement max participation cap" },
      },
      {
        id: "exec-page",
        text: { zh: "写执行假设一页纸", en: "Write execution assumptions page" },
      },
      {
        id: "quiz-exec",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "risk-systems-lab",
    title: { zh: "风险系统小实验", en: "Mini risk-systems lab" },
    summary: { zh: "配置化硬约束：缺口暂停、回撤降仓、密钥隔离。", en: "Config hard limits: gap pause, DD de-risk, secret isolation." },
    minutes: 120,
    resources: ["canvas-one-stop", "ml4t-repo"],
    objectives: [
      { zh: "能在数据陈旧时拒绝下单。", en: "Refuse orders on stale data." },
      { zh: "能在回撤阈值减仓。", en: "De-risk at drawdown threshold." },
      { zh: "能确认仓库无密钥。", en: "Confirm repo has no secrets." },
    ],
    mustTeach: [
      { zh: "熔断是工程控制不是预测。", en: "Kill switches are engineering, not forecasts." },
    ],
    pitfalls: [
      { zh: "只靠我会盯盘。", en: "Relying only on watching the screen." },
    ],
    prereqs: ["execution-slippage"],
    tasks: [
      {
        id: "stale-pause",
        text: { zh: "模拟数据中断暂停", en: "Simulate data gap pause" },
      },
      {
        id: "dd-flatten",
        text: { zh: "模拟回撤降仓", en: "Simulate drawdown de-risk" },
      },
      {
        id: "secret-scan",
        text: { zh: "自查无密钥进 git", en: "Self-check no secrets in git" },
      },
      {
        id: "quiz-sys",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
];

const month5Lessons: Lesson[] = [
  {
    slug: "paper-trading-infra",
    title: { zh: "纸面交易与迷你基建", en: "Paper trading & mini infra" },
    summary: { zh: "信号到目标到日志闭环，至少数个交易日。", en: "Signal to target to log loop for several sessions." },
    minutes: 180,
    resources: ["joinquant-8w", "cookbook-repo", "canvas-one-stop"],
    objectives: [
      { zh: "能实现 CSV 纸面撮合与对账。", en: "Implement CSV paper match and reconcile." },
      { zh: "能输出含异常日报。", en: "Emit daily report with anomalies." },
      { zh: "能解释纸面验流程不验收益。", en: "Explain paper validates process not profits." },
    ],
    mustTeach: [
      { zh: "纸面期间冻结研究版本。", en: "Freeze research version during paper." },
    ],
    pitfalls: [
      { zh: "纸面亏损立刻大改信号。", en: "Rewriting signal after paper losses." },
    ],
    prereqs: ["risk-systems-lab"],
    tasks: [
      {
        id: "csv-paper",
        text: { zh: "CSV 纸面撮合跑通", en: "Get CSV paper matching running" },
      },
      {
        id: "five-days",
        text: { zh: "至少 5 个交易日日志", en: "At least 5 session logs" },
      },
      {
        id: "daily-template",
        text: { zh: "写日报模板", en: "Write daily report template" },
      },
      {
        id: "quiz-paper",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "compliance-ethics",
    title: { zh: "合规、风险心态与研究伦理", en: "Compliance, risk mindset & research ethics" },
    summary: { zh: "先生存；区分学习与受监管业务；拒绝选择性汇报。", en: "Survive first; separate learning from regulated advice; refuse selective reporting." },
    minutes: 90,
    resources: ["afml-notes", "canvas-one-stop"],
    objectives: [
      { zh: "能写出风险偏好与硬约束。", en: "Write risk preferences and hard constraints." },
      { zh: "能把三次失败写入日志。", en: "Log three failures." },
      { zh: "能识别误导性回测宣传。", en: "Spot misleading backtest marketing." },
    ],
    mustTeach: [
      { zh: "本站是学习材料不是投顾。", en: "Site is learning material not advisory." },
      { zh: "不懂的产品零仓位。", en: "Zero size in products you do not understand." },
    ],
    pitfalls: [
      { zh: "只展示样本内曲线对外宣传。", en: "Marketing in-sample curves only." },
    ],
    prereqs: ["paper-trading-infra"],
    tasks: [
      {
        id: "pref-sheet",
        text: { zh: "完成风险偏好一页", en: "Finish risk-preference page" },
      },
      {
        id: "fail-log3",
        text: { zh: "记录三次失败", en: "Record three failures" },
      },
      {
        id: "pitch-audit",
        text: { zh: "审计保证夏普话术", en: "Audit guaranteed-Sharpe pitch" },
      },
      {
        id: "quiz-ethics",
        text: { zh: "完成本课测验", en: "Finish this lesson quiz" },
      },
    ],
  },
  {
    slug: "capstone",
    title: { zh: "结业项目：诚实的小策略", en: "Capstone: an honest small strategy" },
    summary: { zh: "假设到数据到信号到含成本回测到样本外到仓位到纸面日志。", en: "Hypothesis to data to signal to costed backtest to OOS to sizing to paper log." },
    minutes: 360,
    resources: ["canvas-one-stop", "ml4t-repo", "qlib-docs"],
    objectives: [
      { zh: "能提交可复现研究包。", en: "Submit reproducible research pack." },
      { zh: "能包含成本敏感与样本外讨论。", en: "Include cost sensitivity and OOS discussion." },
      { zh: "能附纸面日志与限制条款。", en: "Attach paper logs and limitations." },
    ],
    mustTeach: [
      { zh: "评分看诚实与工程，不看是否赚钱。", en: "Grade honesty and engineering, not profits." },
    ],
    pitfalls: [
      { zh: "只交漂亮样本内图。", en: "Only a pretty in-sample chart." },
    ],
    prereqs: ["compliance-ethics"],
    tasks: [
      {
        id: "hypo-page",
        text: { zh: "一页假设", en: "One-page hypothesis" },
      },
      {
        id: "full-backtest",
        text: { zh: "含成本与 shift 的可运行回测", en: "Runnable backtest with costs and shifts" },
      },
      {
        id: "oos-report",
        text: { zh: "样本外或 walk-forward 报告", en: "OOS or walk-forward report" },
      },
      {
        id: "paper-attach",
        text: { zh: "附上至少 5 日纸面日志", en: "Attach at least 5 days paper logs" },
      },
      {
        id: "rubric-self",
        text: { zh: "按量规自评", en: "Self-score against rubric" },
      },
    ],
  },
];

export const months: Month[] = [
  {
    id: 1,
    slug: "month-1",
    title: { zh: "市场语言与度量", en: "Market language & measurement" },
    goal: { zh: "能读懂交易语言与微观结构基础，并用收益/波动/回撤/夏普诚实评价玩具信号。", en: "Speak trading language and basic microstructure; honestly evaluate a toy signal with return/vol/MDD/Sharpe." },
    topics: [
      { zh: "资产、多空、Alpha/Beta", en: "Assets, long/short, Alpha/Beta" },
      { zh: "订单簿、价差、订单类型", en: "LOB, spread, order types" },
      { zh: "收益、波动、相关、回撤", en: "Returns, vol, correlation, drawdown" },
      { zh: "基准与成本后指标表", en: "Benchmarks and net metric tables" },
    ],
    milestones: [
      { zh: "完成收益与回撤 notebook", en: "Finish returns & drawdown notebook" },
      { zh: "写明一页成交成本假设", en: "Write one-page fill/cost sheet" },
      { zh: "玩具信号 vs 买入持有对照表", en: "Toy signal vs buy-and-hold table" },
    ],
    lessons: month1Lessons,
  },
  {
    id: 2,
    slug: "month-2",
    title: { zh: "数据与诚实回测", en: "Data & honest backtesting" },
    goal: { zh: "建成可版本化数据管线，能演示并修复回测陷阱，并把成本写入向量化回测。", en: "Build a versioned data pipeline, demo/fix backtest traps, and put costs into vectorized backtests." },
    topics: [
      { zh: "复权、幸存者偏差、PIT", en: "Adjustments, survivorship, PIT" },
      { zh: "前瞻、过拟合、样本外", en: "Lookahead, overfitting, OOS" },
      { zh: "佣金与滑点敏感度", en: "Fee and slippage sensitivity" },
      { zh: "向量化 vs 事件驱动假设", en: "Vectorized vs event-driven assumptions" },
    ],
    milestones: [
      { zh: "数据说明书 + 断言齐备", en: "Data sheet + asserts ready" },
      { zh: "陷阱对照实验报告", en: "Trap control-experiment report" },
      { zh: "成本后主回测可运行", en: "Net-of-cost main backtest runnable" },
    ],
    lessons: month2Lessons,
  },
  {
    id: 3,
    slug: "month-3",
    title: { zh: "经典策略与因子", en: "Classic strategies & factors" },
    goal: { zh: "复现动量、均值回归、配对，并完成 IC/分层因子工作流与对照实验。", en: "Reproduce momentum, mean reversion and pairs; finish IC/quantile workflow and a comparison lab." },
    topics: [
      { zh: "动量与趋势", en: "Momentum and trend" },
      { zh: "均值回归", en: "Mean reversion" },
      { zh: "配对与价差", en: "Pairs and spreads" },
      { zh: "因子 IC 与分层", en: "Factor IC and quantiles" },
    ],
    milestones: [
      { zh: "三份策略 notebook", en: "Three strategy notebooks" },
      { zh: "IC + 分层图", en: "IC + quantile charts" },
      { zh: "三策略对照报告", en: "Three-strategy comparison report" },
    ],
    lessons: month3Lessons,
  },
  {
    id: 4,
    slug: "month-4",
    title: { zh: "ML 方法、组合与执行", en: "ML methods, portfolio & execution" },
    goal: { zh: "掌握防泄漏 ML 草图、仓位与风险硬约束，以及执行成本敏感分析。", en: "Master leakage-safe ML sketch, sizing/risk hard limits, and execution cost sensitivity." },
    topics: [
      { zh: "时序切分与泄漏", en: "Time splits and leakage" },
      { zh: "波动目标与 Kelly 直觉", en: "Vol targeting and Kelly intuition" },
      { zh: "执行与参与率", en: "Execution and participation" },
      { zh: "熔断与密钥隔离", en: "Kill switches and secret isolation" },
    ],
    milestones: [
      { zh: "泄漏对照 notebook", en: "Leakage-control notebook" },
      { zh: "三种仓位对照表", en: "Three sizing comparison table" },
      { zh: "执行假设一页纸 + 熔断演示", en: "Execution sheet + kill-switch demo" },
    ],
    lessons: month4Lessons,
  },
  {
    id: 5,
    slug: "month-5",
    title: { zh: "纸面、合规与结业", en: "Paper, compliance & capstone" },
    goal: { zh: "跑通纸面闭环，书面化风险与伦理，提交诚实结业项目。", en: "Run a paper loop, write risk/ethics commitments, submit an honest capstone." },
    topics: [
      { zh: "纸面撮合与日报", en: "Paper matching and daily reports" },
      { zh: "合规与研究伦理", en: "Compliance and research ethics" },
      { zh: "结业量规与交付", en: "Capstone rubric and delivery" },
    ],
    milestones: [
      { zh: "≥5 日纸面日志", en: "≥5 days paper logs" },
      { zh: "风险偏好与失败日志", en: "Risk preference and failure log" },
      { zh: "结业包通过自评量规", en: "Capstone pack passes self-rubric" },
    ],
    lessons: month5Lessons,
  },
];

export function monthStats(month: Month) {
  const minutes = month.lessons.reduce((sum, l) => sum + l.minutes, 0);
  return {
    lessons: month.lessons.length,
    tasks: month.lessons.reduce((sum, l) => sum + l.tasks.length, 0),
    hours: Math.round(minutes / 30) / 2,
  };
}

export function getMonth(slug: string): Month | undefined {
  return months.find((m) => m.slug === slug);
}

export function getLesson(monthSlug: string, lessonSlug: string) {
  const month = getMonth(monthSlug);
  if (!month) return undefined;
  const index = month.lessons.findIndex((l) => l.slug === lessonSlug);
  if (index < 0) return undefined;
  return {
    month,
    lesson: month.lessons[index],
    index,
    prev: month.lessons[index - 1],
    next: month.lessons[index + 1],
  };
}

export function lessonKey(monthId: number, lessonSlug: string) {
  return `m${monthId}/${lessonSlug}`;
}

/** Optional resource id -> URL (for site resource cards). */
export const OPTIONAL_TOOL_LINKS: Record<string, string> = {
  "quantstart-sat": "https://www.quantstart.com/successful-algorithmic-trading-ebook/",
  "quantstart-books": "https://www.quantstart.com/articles/Top-5-Essential-Beginner-Books-for-Algorithmic-Trading/",
  "qlib-docs": "https://qlib.readthedocs.io/en/stable/",
  "qlib-github": "https://github.com/microsoft/qlib",
  "vectorbt-docs": "https://vectorbt.dev/",
  "zipline-reloaded": "https://zipline.ml4trading.io/",
  "zipline-github": "https://github.com/stefan-jansen/zipline-reloaded",
  "backtrader": "https://www.backtrader.com/",
  "ml4t-repo": "https://github.com/stefan-jansen/machine-learning-for-trading",
  "quant-wiki": "https://github.com/LLMQuant/quant-wiki",
  "joinquant-zero": "https://www.joinquant.com/community/post/detailMobile?postId=13149",
  "joinquant-8w": "http://lookmori.cn/",
  "ricequant-docs": "https://www.ricequant.com/doc/",
  "nyu-mathga-2708": "https://math-finance.cims.nyu.edu/academics/",
  "uchicago-finm": "https://summer.uchicago.edu/courses/quantitative-portfolio-management-and-algorithmic-trading/",
  "stern-syllabus": "https://web-docs.stern.nyu.edu/ioms/SYLLABI/Dhar_MULT-UB.0035_Fall13.pdf",
  "afml-notes": "https://rzeng0812.github.io/quant-atlas/80-Books/Lopez-de-Prado-Advances-Financial-ML",
  "nautilus": "https://github.com/nautechsystems/nautilus_trader",
  "canvas-one-stop": "https://cursor.com/canvas/store-2382cb79-a91c-438a-bb75-0d38cd2e4b0d/e986247c-63a6-4a33-8d8e-97eb8be22290",
};
