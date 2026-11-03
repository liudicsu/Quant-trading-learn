# P8 labs — Frontier & unconventional methods

Learning only — not investment advice. **Offline mocks only** (no paid LLM API, no network at runtime).

| Script | Lesson | What it demos |
|--------|--------|----------------|
| `01_llm_agents_offline.py` | `frontier-llm-agents` | Mock RD-Agent(Q) loop, Lopez-Lira sentiment foil, sealed OOS, Chain-of-Alpha withdrawn note |
| `02_tsfm_crypto_nautilus.py` | `frontier-tsfm-altdata-crypto` | Mock TSFM vs AR/naive/strong CS, funding carry, CCXT-shaped mock, GMX OI toy, Nautilus identical-code checklist |

```bash
cd examples/p8
python3 01_llm_agents_offline.py | tee 01_llm_agents_offline.out
python3 02_tsfm_crypto_nautilus.py | tee 02_tsfm_crypto_nautilus.out
```

Charts land in `public/p8/`. CSVs/JSON in `examples/p8/data/`.
