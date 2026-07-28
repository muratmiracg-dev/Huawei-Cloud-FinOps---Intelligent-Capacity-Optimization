# Runbook: recommendation review

## Inputs

- recommendation type and ID,
- current monthly cost,
- estimated saving and confidence,
- P95 evidence and observation days,
- environment, owner, product, criticality,
- proposed action and risk.

## Review

1. Confirm the resource is still required.
2. Check planned peaks, releases, seasonality, and disaster-recovery role.
3. Confirm the recommendation does not conflict with another approved action.
4. Select the smallest reversible test.
5. Define SLO checks and rollback.
6. Assign an execution owner and maintenance window.

## Approval rules

- Low risk: resource owner.
- Medium risk: owner plus platform/SRE; finance for commitments.
- High risk: immediate SRE/platform review.
- Destructive or commercial action: explicit accountable approval.

## Exit

Approved, rejected, or deferred with reason and expiry. Approval alone is not
realized savings; measure a complete post-change billing period.
