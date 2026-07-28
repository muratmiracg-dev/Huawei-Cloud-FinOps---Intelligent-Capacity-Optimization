# Runbook: cost anomaly

## Trigger

`CostAnomalyDetected` or an anomaly returned by `/api/v1/anomalies`.

## Triage

1. Record recommendation/resource ID, date, expected cost, actual cost, and score.
2. Confirm export freshness and whether the value is original or amortized cost.
3. Check planned launches, data processing, traffic, and commitment events.
4. Compare service, region, enterprise project, owner, and product dimensions.
5. Verify no duplicate or late records entered the canonical snapshot.

## Decision

- **Expected business event:** annotate and update forecast.
- **Data issue:** quarantine the snapshot, correct adapter/schema, rerun.
- **Unexpected consumption:** assign owner and reduce/stop through approved action.
- **Potential compromise:** start security incident response and rotate credentials.

## Exit

Close only after cause, owner, financial impact, and preventive action are
recorded. Do not use current-month expenditure as final reconciliation.
