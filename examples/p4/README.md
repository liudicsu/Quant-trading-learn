# P4 labs

Offline synthetic labs for Phase P4 (factor research). Learning only — not investment advice.

Panel: 200 assets × 750 days with planted `beta_true` + industry/size contamination + nuisance factor.
CSVs are generated on first run by `ensure_panel()` in `_common.py` (seed 42).

```bash
# from repo root
source .venv/bin/activate
cd examples/p4
python 01_factor_workflow.py
python 02_factor_portfolio_lab.py
```

Charts land in `public/p4/`.
