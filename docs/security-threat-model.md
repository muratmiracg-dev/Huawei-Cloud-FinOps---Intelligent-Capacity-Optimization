# Security and threat model

## Scope

The threat model covers billing and utilization ingestion, the analytics engine,
API exposure, container/Kubernetes deployment, dashboards, CI, Terraform, and
the boundary to approved execution.

## Protected assets

- cloud cost and usage details,
- resource names and identifiers,
- ownership and cost-center metadata,
- budget and forecast information,
- cloud credentials and Terraform state,
- recommendation approvals and audit evidence,
- service reliability and capacity.

## Trust zones

| Zone | Sensitivity | Control |
|---|---|---|
| Huawei Cloud APIs and OBS | High | IAM, scoped bucket/prefix, TLS |
| Collector runtime | High | Read-only identity, secret manager, isolated logs |
| Canonical data storage | High | Encryption, access control, retention |
| Analytics/API | Medium-high | No mutation, input validation, network boundary |
| Monitoring | Medium | Authenticated Grafana, limited labels, retention |
| CI/CD | High | protected branch, pinned/reviewed actions, secret isolation |
| Execution workflow | Critical | approval, plan review, separate credentials |

## Threats and controls

| Threat | Impact | Primary controls | Residual risk |
|---|---|---|---|
| AK/SK leakage | Account compromise | Runtime secret, no credentials in repo, Trivy/CodeQL | CI or operator mishandling |
| Billing-data disclosure | Commercial sensitivity loss | Private OBS, least privilege, no payload logging | Authorized insider access |
| Malformed export | Wrong recommendation | Strict parsing, readiness failure, deterministic contracts | Valid but semantically changed schema |
| Cost-data poisoning | Waste or capacity incident | Source provenance, immutable snapshots, anomaly checks | Compromised authorized source |
| Recommendation overreach | SLO regression | Read-only engine, risk score, owner approval, canary | Human approval error |
| Savings double counting | Misleading business case | Maximum compatible saving per resource | Cross-resource dependencies |
| API abuse | Data extraction or denial | Private ingress, auth/TLS in production, limits | Misconfigured ingress |
| Container escape | Host compromise | non-root, read-only FS, seccomp, dropped capabilities | Runtime vulnerability |
| Metadata-service access | Credential theft | egress policy excludes `169.254.169.254` | Network-policy bypass/misconfiguration |
| Supply-chain compromise | Build/runtime compromise | CodeQL, Trivy, Dependabot, reviewed actions | Upstream zero-day |
| Terraform state exposure | Credentials/resource data disclosure | encrypted restricted backend | Backend policy error |
| Destructive rollback | Evidence/data loss | no generic destroy, protected OBS/state, reviewed plan | Operator bypass |

## Security requirements

- No cloud resource mutation endpoint.
- No long-lived credentials in files or images.
- No customer cost payload in application logs.
- Default non-root and read-only containers.
- Explicit resource requests and memory limits.
- Restricted namespace Pod Security labels.
- NetworkPolicy denies unnecessary paths and metadata service.
- High/critical scan findings fail CI.
- Recommendation execution requires an accountable owner.
- Exceptions have an expiry.

## Logging guidance

Allowed:

- collection timestamp,
- record counts,
- schema version,
- hashed or approved resource reference,
- recommendation ID,
- status, latency, and error class.

Avoid:

- AK/SK, tokens, cookies, or authorization headers,
- full exported cost rows,
- personal email recipients,
- unredacted account/project identifiers,
- Terraform plan/state content in public logs.

## Incident response

For suspected credential or billing-data exposure:

1. Stop the affected collector or pipeline.
2. Revoke/rotate the identity.
3. Preserve audit evidence without copying sensitive payloads into public issues.
4. Restrict OBS/object and CI access.
5. Identify affected time range and consumers.
6. Rebuild from an approved clean snapshot.
7. Document root cause and preventive control.

See [cost anomaly](runbooks/cost-anomaly.md) and
[platform unavailable](runbooks/platform-unavailable.md) runbooks for
operational response.
