# P7 labs

Paper trading & compliance: a simulated paper-trading loop and an official-sources checklist. **No real broker order code.** Learning only — not investment or legal advice.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd examples/p7
python 01_paper_trading_loop.py   # logging, reconciliation, drift, kill switches, live-vs-backtest gap
python 02_compliance_sources.py   # official regulator sources checklist (rules change; verify current text)
```

Each script has a matching `.out` with its expected stdout; capture **stdout only** when refreshing them.
