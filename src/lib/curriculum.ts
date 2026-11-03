/**
 * BATCH A PLACEHOLDER CURRICULUM
 * -----------------------------
 * Scaffold only. Titles/grouping will be rescheduled by content later.
 * `curriculum.draft.ts` and `docs/CURRICULUM_RESEARCH.md` are reference files —
 * they are NOT imported by the site.
 *
 * Learning only — not investment advice.
 */

import type { Lesson, Month } from "./types";

export type { Locale, L10n, Task, Lesson, Month } from "./types";

export const COURSE_META = {
  disclaimer: {
    zh: "学习用途，非投资建议。不构成买卖推荐或收益承诺。",
    en: "Learning only — not investment advice. No trade recommendations or profit promises.",
  },
  note: {
    zh: "本大纲为站点脚手架占位，正式课表稍后按内容重排。",
    en: "This outline is a site scaffold placeholder; the formal schedule will be rearranged by content later.",
  },
};

export const COURSE_SOURCE = {
  author: "Quant-trading-learn",
  authorUrl: "https://github.com/liudicsu/Quant-trading-learn",
  url: "https://github.com/liudicsu/Quant-trading-learn",
  title: "Quant trading self-contained learning site (Batch A scaffold)",
};

const stubTasks = (prefix: string): Lesson["tasks"] => [
  {
    id: `${prefix}-read`,
    text: {
      zh: "浏览本课占位说明（正文待正式大纲后填写）",
      en: "Skim this placeholder note (body after the formal outline)",
    },
  },
  {
    id: `${prefix}-quiz`,
    text: {
      zh: "完成本课测验（如有）",
      en: "Finish any quizzes on this page",
    },
  },
];

function stub(
  slug: string,
  title: { zh: string; en: string },
  summary: { zh: string; en: string },
  minutes = 60,
): Lesson {
  return {
    slug,
    title,
    summary,
    minutes,
    resources: [],
    status: "outline",
    tasks: stubTasks(slug),
    objectives: [
      {
        zh: "【占位】了解本主题在学习路径中的位置",
        en: "[Placeholder] Know where this topic sits in the path",
      },
    ],
  };
}

/** Placeholder months — not the researched 5×20 schedule. */
export const months: Month[] = [
  {
    id: 1,
    slug: "month-1",
    title: { zh: "预备与市场语言（占位）", en: "Prep & market language (placeholder)" },
    goal: {
      zh: "【占位】补齐 Python/pandas 与交易语言；正式顺序待重排。",
      en: "[Placeholder] Python/pandas and trading vocabulary; formal order TBD.",
    },
    topics: [
      { zh: "Python / pandas", en: "Python / pandas" },
      { zh: "市场语言", en: "Market language" },
      { zh: "收益直觉", en: "Return intuition" },
    ],
    milestones: [
      { zh: "跑通示例课净值片段", en: "Run the sample NAV snippet" },
      { zh: "理解示例≠投资建议", en: "Treat demos as non-advice" },
    ],
    lessons: [
      {
        slug: "prep-python-pandas",
        title: {
          zh: "预备：Python 与 pandas 量化入门",
          en: "Prep: Python & pandas for quant work",
        },
        summary: {
          zh: "读价、算收益、画净值；教学示例，非交易信号。",
          en: "Load prices, compute returns, plot NAV — teaching only, not a signal.",
        },
        minutes: 90,
        resources: [],
        status: "ready",
        objectives: [
          {
            zh: "能用 pandas 计算简单收益与累计净值。",
            en: "Compute simple returns and cumulative NAV with pandas.",
          },
          {
            zh: "能解释 shift(1) 与信息时点对齐。",
            en: "Explain shift(1) and information-timing alignment.",
          },
          {
            zh: "能区分教学示例与投资建议。",
            en: "Distinguish teaching demos from investment advice.",
          },
        ],
        tasks: [
          {
            id: "run-nav",
            text: {
              zh: "在本地 notebook 复现净值计算片段",
              en: "Reproduce the NAV snippet in a local notebook",
            },
          },
          {
            id: "shift-explain",
            text: {
              zh: "用自己的话说明为何常用 signal.shift(1)",
              en: "Explain in your own words why signal.shift(1) is common",
            },
          },
          {
            id: "quiz-all",
            text: {
              zh: "完成本课全部小测验",
              en: "Answer every quiz on this page",
            },
          },
        ],
      },
      stub(
        "markets-language",
        { zh: "市场与交易语言（占位）", en: "Markets & trading vocabulary (placeholder)" },
        { zh: "占位：资产、多空、可复现目标。", en: "Placeholder: assets, long/short, reproducible goals." },
      ),
      stub(
        "returns-vol-corr",
        { zh: "收益、波动与相关（占位）", en: "Returns, vol & correlation (placeholder)" },
        { zh: "占位：夏普、回撤等度量直觉。", en: "Placeholder: Sharpe, drawdown intuition." },
      ),
    ],
  },
  {
    id: 2,
    slug: "month-2",
    title: { zh: "数据与回测（占位）", en: "Data & backtests (placeholder)" },
    goal: {
      zh: "【占位】数据清洗与诚实回测意识。",
      en: "[Placeholder] Data cleaning and honest-backtest awareness.",
    },
    topics: [
      { zh: "数据", en: "Data" },
      { zh: "回测陷阱", en: "Backtest traps" },
    ],
    milestones: [{ zh: "能说出三类常见回测作弊", en: "Name three common backtest cheats" }],
    lessons: [
      stub(
        "data-cleaning",
        { zh: "数据与清洗（占位）", en: "Data & cleaning (placeholder)" },
        { zh: "占位：复权、缺失、幸存者偏差。", en: "Placeholder: adjustment, gaps, survivorship." },
      ),
      stub(
        "backtest-traps",
        { zh: "回测陷阱（占位）", en: "Backtest traps (placeholder)" },
        { zh: "占位：lookahead、成本、过拟合。", en: "Placeholder: lookahead, costs, overfitting." },
        90,
      ),
    ],
  },
  {
    id: 3,
    slug: "month-3",
    title: { zh: "策略与因子（占位）", en: "Strategies & factors (placeholder)" },
    goal: {
      zh: "【占位】经典策略族与因子工作流入口。",
      en: "[Placeholder] Classic strategy families and factor workflow entry.",
    },
    topics: [
      { zh: "动量 / 回归", en: "Momentum / reversion" },
      { zh: "因子", en: "Factors" },
    ],
    milestones: [{ zh: "能区分策略族与评估指标", en: "Tell strategy families from metrics" }],
    lessons: [
      stub(
        "momentum-trend",
        { zh: "动量与趋势（占位）", en: "Momentum & trend (placeholder)" },
        { zh: "占位：时序/截面动量直觉。", en: "Placeholder: TS/CS momentum intuition." },
      ),
      stub(
        "mean-reversion",
        { zh: "均值回归（占位）", en: "Mean reversion (placeholder)" },
        { zh: "占位：z-score 与失效。", en: "Placeholder: z-score and failure modes." },
      ),
      stub(
        "factor-workflow",
        { zh: "因子研究工作流（占位）", en: "Factor research workflow (placeholder)" },
        { zh: "占位：IC、分层。", en: "Placeholder: IC, deciles." },
      ),
    ],
  },
  {
    id: 4,
    slug: "month-4",
    title: { zh: "风险、ML 与执行（占位）", en: "Risk, ML & execution (placeholder)" },
    goal: {
      zh: "【占位】仓位/风险、ML 防泄漏、执行成本概念。",
      en: "[Placeholder] Sizing/risk, ML anti-leakage, execution-cost concepts.",
    },
    topics: [
      { zh: "风控", en: "Risk" },
      { zh: "ML", en: "ML" },
      { zh: "执行", en: "Execution" },
    ],
    milestones: [{ zh: "能写出成本与切分检查表", en: "Draft cost and split checklists" }],
    lessons: [
      stub(
        "portfolio-risk-sizing",
        { zh: "组合风险与仓位（占位）", en: "Portfolio risk & sizing (placeholder)" },
        { zh: "占位：波动目标、回撤熔断。", en: "Placeholder: vol targeting, DD breakers." },
      ),
      stub(
        "ml-leakage",
        { zh: "ML 防泄漏注意点（占位）", en: "ML anti-leakage notes (placeholder)" },
        { zh: "占位：时序切分、禁止 shuffle。", en: "Placeholder: time splits, no shuffle." },
      ),
      stub(
        "execution-slippage",
        { zh: "执行与滑点概念（占位）", en: "Execution & slippage concepts (placeholder)" },
        { zh: "占位：无券商开户教程。", en: "Placeholder: no broker-signup tutorial." },
      ),
    ],
  },
  {
    id: 5,
    slug: "month-5",
    title: { zh: "落地与结业（占位）", en: "Ops & capstone (placeholder)" },
    goal: {
      zh: "【占位】纸面心态、伦理与结业清单入口。",
      en: "[Placeholder] Paper mindset, ethics, capstone checklist entry.",
    },
    topics: [
      { zh: "纸面", en: "Paper" },
      { zh: "伦理", en: "Ethics" },
      { zh: "结业", en: "Capstone" },
    ],
    milestones: [{ zh: "知道结业要交什么（诚实过程）", en: "Know honest capstone deliverables" }],
    lessons: [
      stub(
        "paper-trading-infra",
        { zh: "纸面交易与迷你基建（占位）", en: "Paper trading & mini infra (placeholder)" },
        { zh: "占位：日志与密钥隔离（无实盘下单）。", en: "Placeholder: logs/secrets (no live orders)." },
      ),
      stub(
        "compliance-ethics",
        { zh: "合规与研究伦理（占位）", en: "Compliance & research ethics (placeholder)" },
        { zh: "占位：选择性汇报与风险心态。", en: "Placeholder: selective reporting & risk mindset." },
      ),
      stub(
        "capstone",
        { zh: "结业项目清单（占位）", en: "Capstone checklist (placeholder)" },
        { zh: "占位：诚实可复现小策略交付。", en: "Placeholder: honest reproducible mini-strategy." },
        120,
      ),
    ],
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

export function allLessonsFlat() {
  return months.flatMap((m) => m.lessons.map((l) => ({ month: m, lesson: l })));
}
