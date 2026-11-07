# P5 labs

ML anti-leakage + modern pipelines + AFML depth (fracdiff / uniqueness / meta-label) on the P4 **weak** panel (subsample). Learning only.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd examples/p5
python 01_ml_leakage_control.py
python 02_modern_ml_pipelines.py          # lightgbm needed; shap OPTIONAL (SHAP block skipped if missing; bit-identical .out needs shap)
python 03_afml_depth.py                   # needs statsmodels
```

`requirements.txt` lists: numpy, pandas, scipy, scikit-learn, matplotlib, statsmodels, lightgbm; shap is **optional** (same as the root `requirements.txt`).
Capture **stdout only** when refreshing `.out` files (SHAP may print stderr warnings).
Charts → `public/p5/`.
