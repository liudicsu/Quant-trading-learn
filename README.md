# Quant Trading Learn · 量化交易学习

Self-contained bilingual site (中文 `/zh`, English `/en`) for quantitative **research methods**.

**Learning only — not investment advice.**

## Curriculum V2

Phases P0–P9 from knowledge dependencies (`src/lib/curriculum.ts`, `docs/CURRICULUM_V2.md`).

Routes: `/[locale]/phase/<phaseSlug>/<lessonSlug>`.

**This batch:** full bodies for all **P0** lessons (zh+en). Other phases are outline stubs.

## Develop

```bash
npm ci && npm run dev
```

P0 labs: `examples/p0/`.

## Pages

```bash
PAGES_BASE_PATH=/Quant-trading-learn npm run build
```

https://liudicsu.github.io/Quant-trading-learn/
