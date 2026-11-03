# Quant Trading Learn · 量化交易学习

Self-contained, bilingual (中文 `/zh`, English `/en`) site for quantitative trading **research methods**.

**Learning only — not investment advice.**

Scaffold UX mirrors [Hardware-learning](https://github.com/liudicsu/Hardware-learning).

## Curriculum status (Batch A)

`src/lib/curriculum.ts` is a **placeholder** outline for navigation. It will be rearranged by content later.

Reference research files (not imported by the app):

- `docs/CURRICULUM_RESEARCH.md`
- `src/lib/curriculum.draft.ts`

Sample lesson with full zh/en body: **`prep-python-pandas`**.

## Develop

```bash
npm ci
npm run dev
```

## Pages export

```bash
PAGES_BASE_PATH=/Quant-trading-learn npm run build
```

Workflow template: `docs/deploy/pages.yml` (also `.github/workflows/pages.yml` when workflow scope allows).
