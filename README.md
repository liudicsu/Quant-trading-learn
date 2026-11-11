# Quant Trading Learn · 量化交易学习

Self-contained bilingual site (中文 `/zh`, English `/en`) for quantitative **research methods**.

**Learning only — not investment advice.**

## Curriculum V2

Phases P0–P9 from knowledge dependencies (`src/lib/curriculum.ts`, `docs/CURRICULUM_V2.md`).

Routes: `/[locale]/phase/<phaseSlug>/<lessonSlug>`.

**Written so far:** full bodies for **P0–P9** (zh+en), 28 lessons.

**Hours:** 415.25h full / 395.25h skip-P0 (exact; per-lesson sub-items sum to each total).

**Default scope:** US-listed stocks / non-leveraged ETFs in USD (US-first). Chinese is a teaching language, not the default market; A-share / HK / EU material is labelled comparison reading. All labs run offline on synthetic or hand-made fixtures.

`shap` is optional everywhere (root and `examples/p5/requirements.txt`); `examples/p5/02` skips its SHAP block without it.

## Develop

```bash
npm ci && npm run dev
```

P0 labs: `examples/p0/`. P1/P2 labs: `examples/p1/`, `examples/p2/`.

Python labs need:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`matplotlib` is required for P2 charts (`public/p2/*.png`).

## Pages

```bash
PAGES_BASE_PATH=/Quant-trading-learn npm run build
```

https://liudicsu.github.io/Quant-trading-learn/
