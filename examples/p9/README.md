# P9 labs — Capstone

Learning only — not investment advice. Offline / synthetic only.

| Script | Lesson | What it demos |
|--------|--------|----------------|
| `01_capstone_e2e.py` | `capstone` | Hypothesis → PIT panel → walk-forward+costs → DSR(N=all) → sizing → TCA → paper recon (injected break) → compliance → report template |

```bash
cd examples/p9
source ../../.venv/bin/activate
python 01_capstone_e2e.py | tee 01_capstone_e2e.out
```

Charts in `public/p9/`. Artefacts in `examples/p9/data/`.

- US-first pack (2026-11-08): `02_us_research_contract.py + us_research_contract.json — offline research-contract checker (source_mode/fallback_reason).`
