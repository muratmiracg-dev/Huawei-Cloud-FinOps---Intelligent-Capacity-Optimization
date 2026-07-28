# Data contracts

## Canonical contract

The analytics engine depends on four stable datasets. Cloud-specific collection
is isolated in adapters so the decision logic can run offline and remain
testable.

## `resources.csv`

Grain: one row per billable or capacity-relevant resource.

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `resource_id` | string | Yes | Stable cloud resource identifier |
| `name` | string | Yes | Human-readable name |
| `service` | enum | Yes | ECS, CCE_NODE, EVS, EIP, RDS, OBS, ELB, OTHER |
| `region` | string | Yes | Huawei Cloud region |
| `enterprise_project` | string | Yes | Enterprise Project grouping |
| `environment` | string | Allocation | development, qa, staging, production |
| `owner` | string | Allocation | Accountable team |
| `cost_center` | string | Allocation | Finance code |
| `product` | string | Allocation | Product or shared platform |
| `monthly_cost` | decimal | Yes | Current monthly baseline |
| `pricing_mode` | enum | Yes | pay_per_use, yearly_monthly, savings_plan |
| `vcpu`, `memory_gb`, `storage_gb` | number | By service | Capacity |
| `status` | string | Yes | active, idle, available, unbound |
| `attached` | boolean | Yes | Dependency state |
| `schedule` | string | Yes | 24x7 or approved schedule |
| `criticality` | string | Yes | low, standard, high, mission-critical |
| `tags_json` | JSON object | Yes | Additional tag evidence |

## `costs.csv`

Grain: one resource/day.

| Field | Type | Meaning |
|---|---|---|
| `date` | ISO date | Usage/cost date |
| `resource_id` | string | Resource join key |
| `service` | enum | Service dimension |
| `actual_cost` | decimal | Original/net cost input |
| `amortized_cost` | decimal | Effective amortized cost |
| `usage_quantity` | decimal | Service usage quantity |
| `currency` | ISO currency | Reporting currency |

## `utilization.csv`

Grain: one resource/timestamp.

| Field | Unit | Meaning |
|---|---|---|
| `timestamp` | ISO timestamp | Observation time |
| `resource_id` | string | Resource join key |
| `cpu_pct` | percent | Observed CPU |
| `memory_pct` | percent | Observed memory |
| `network_pct` | percent | Normalized network utilization |
| `disk_pct` | percent | Observed disk utilization |
| `request_cpu_pct` | percent | Requested CPU / node capacity |
| `request_memory_pct` | percent | Requested memory / node capacity |

## `budgets.csv`

Grain: one approved budget scope.

| Field | Meaning |
|---|---|
| `name` | Unique budget name |
| `scope_type` | all, product, environment, service, project, etc. |
| `scope_value` | Matching dimension value |
| `monthly_limit` | Approved amount |
| `actual_alert_pct` | Actual warning threshold |
| `forecast_alert_pct` | Forecast breach threshold |
| `currency` | Budget currency |

## Huawei export mapping

`finops.adapters.huawei_billing.normalize_billing_records` maps common English
Cost Center/Billing Center export names:

| Huawei field | Canonical field |
|---|---|
| Usage Date | `record_date` |
| Resource ID | `resource_id` |
| Service Type | `service` |
| Net Amount | `actual_cost` |
| Amortized Net Amount | `amortized_cost` |
| Usage | `usage_quantity` |
| Currency | `currency` |

Production mappings should be versioned because export headers and API schemas
can evolve.

## Data quality checks

- Required files must exist before readiness succeeds.
- CSV headers are read by name, not position.
- Dates and timestamps must be ISO-compatible.
- Numeric values must parse without implicit locale conversion.
- Unknown services map to `OTHER` instead of being discarded.
- Cost records remain immutable after acceptance.
- Collection freshness must be tracked externally.
- Customer identifiers and credentials must never enter the demo dataset.

## Reproducibility

The sample generator uses a fixed seed and closed date range. CI regenerates the
dataset and fails when committed files drift.
