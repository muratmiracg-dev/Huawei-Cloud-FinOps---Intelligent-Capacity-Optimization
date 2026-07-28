# Project governance

## Decision ownership

| Decision | Accountable role | Required evidence |
|---|---|---|
| Analytics rule | FinOps engineering | Test, method, safety constraint |
| Capacity threshold | SRE/platform | P95 evidence, headroom, SLO impact |
| Budget threshold | Finance + product | Approved budget and scope |
| Infrastructure change | Cloud platform | Terraform plan, security review, rollback |
| Recommendation execution | Resource owner | Approval, maintenance window, validation |

## Change classes

- **Low risk:** documentation, deterministic fixtures, display-only changes.
- **Medium risk:** analytics thresholds, API behavior, dashboard alerts.
- **High risk:** IAM, networking, cost-export retention, CCE scaling bounds, or
  any execution automation.

High-risk changes require explicit security, finance, and platform review.
