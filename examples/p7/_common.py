"""P7 shared helpers. Learning only — not investment advice. NO broker order APIs."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

PUBLIC = Path(__file__).resolve().parents[2] / "public" / "p7"
PUBLIC.mkdir(parents=True, exist_ok=True)
DATA = Path(__file__).resolve().parent / "data"
DATA.mkdir(parents=True, exist_ok=True)
ANN = np.sqrt(252)
SEED = 7
