# P0 labs

Offline synthetic examples for Batch P0. Learning only — not investment advice.

| Script | Writes |
| --- | --- |
| `01_pandas_timeseries.py` | reads `data/synthetic_ohlc.csv`; `public/p0/returns_ma.png`; stdout → `01_pandas_timeseries.out` |
| `02_stats_probability.py` | `public/p0/returns_hist.png`; stdout → `02_stats_probability.out` |
| `03_basic_finance.py` | stdout → `03_basic_finance.out` |

```bash
python examples/p0/01_pandas_timeseries.py | tee examples/p0/01_pandas_timeseries.out
python examples/p0/02_stats_probability.py | tee examples/p0/02_stats_probability.out
python examples/p0/03_basic_finance.py | tee examples/p0/03_basic_finance.out
```

Requires `pandas`, `numpy`, `matplotlib`.
