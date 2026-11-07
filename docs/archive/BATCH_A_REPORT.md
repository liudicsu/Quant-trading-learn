> **Historical V1 document (archived).** Superseded by `docs/CURRICULUM_V2.md`; numbers here are out of date.

# Batch A Report — Quant-trading-learn

**Date:** 2026-11-04 (Asia/Shanghai)  
**Project path:** `/workspace/Quant-trading-learn`

## Verified locally

| Check | Result |
| --- | --- |
| `npm run build` | OK |
| `PAGES_BASE_PATH=/Quant-trading-learn npm run build` | OK (`out/`) |
| Dev curl | 200 `/zh`, `/zh/curriculum`, `/zh/month/month-1/prep-python-pandas`, `/en/...` |

## Curriculum (placeholder)

- **Official site data:** `src/lib/curriculum.ts` — **PLACEHOLDER** outline (5 nav months / 14 lessons), clearly labeled; will be rearranged by content later.
- **Reference only (not imported):** `src/lib/curriculum.draft.ts`, `docs/CURRICULUM_RESEARCH.md`
- **Sample ready:** `prep-python-pandas` — `/zh/month/month-1/prep-python-pandas` (+ `/en`)
- Progress key: `quant-trading-learn-progress-v1`
- Routes: `/[locale]/month/[month]/[lesson]`

## Stack

Next.js 16 + MDX + next-intl (`zh`/`en`) + Tailwind v4; Quiz / TaskChecklist / LessonComplete / MonthProgress (Hardware-learning parity).

## Deploy

- Repo: https://github.com/liudicsu/Quant-trading-learn
- Expected Pages: https://liudicsu.github.io/Quant-trading-learn/
- Pages settings: already `build_type=workflow`
- Workflows mirrored at `docs/deploy/pages.yml` and `docs/deploy/ci.yml`
- **Note:** OAuth token lacked `workflow` scope at push time; if `.github/workflows/*` could not be pushed, copy from `docs/deploy/` into `.github/workflows/` with a token that has `workflow` scope, then re-run the Actions deploy.

## Gaps

- Formal outline rearrange (user-driven)
- Fill remaining lesson bodies in later batches


## Git push status (2026-11-04 Asia/Shanghai)

- **Pushed** `main` to https://github.com/liudicsu/Quant-trading-learn (`9666a7f`)
- Pages site setting already enabled: https://liudicsu.github.io/Quant-trading-learn/
- **Actions workflow not installed on remote yet**: OAuth token lacks `workflow` scope (API create of `.github/workflows/*` returned 404/forbidden). Templates are in `docs/deploy/pages.yml` and `docs/deploy/ci.yml`.
- **To finish Pages deploy:** re-auth with `workflow` scope, copy templates into `.github/workflows/`, push, confirm Actions run green.

