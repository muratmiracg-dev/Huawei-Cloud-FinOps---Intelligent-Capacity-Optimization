# Demo data contract

The committed dataset is deterministic, synthetic, and contains no customer or
Huawei Cloud account data.

| File | Grain | Purpose |
|---|---|---|
| `resources.csv` | One row per cloud resource | Inventory, ownership, tags, pricing, and monthly baseline |
| `costs.csv` | One row per resource per day | Original and amortized cost history |
| `utilization.csv` | Four samples per compute resource per day | CPU, memory, network, disk, and request efficiency |
| `budgets.csv` | One row per budget | Scope, limit, and alert thresholds |

Regenerate the exact dataset with:

```bash
python scripts/generate_demo_data.py
```

The fixed seed is intentionally versioned so recommendations, tests, screenshots,
and executive KPIs remain reproducible.
