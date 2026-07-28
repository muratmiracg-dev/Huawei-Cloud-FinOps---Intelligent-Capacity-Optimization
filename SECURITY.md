# Security policy

## Supported versions

Security fixes are maintained for the latest `1.x` release on `main`.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability, leaked credential,
customer identifier, or billing record. Use GitHub's private vulnerability
reporting for this repository.

Include:

- affected component and version,
- reproduction steps using non-sensitive data,
- expected impact,
- suggested mitigation when available.

## Security boundaries

- The committed demo contains no real account, customer, or billing data.
- Huawei Cloud credentials must be supplied at runtime through an approved
  secret manager or workload identity mechanism.
- The application is read-only by design; cloud resource mutation requires a
  separate approved automation path.
- Recommendations are advisory and require human approval.
- Containers run as UID/GID `10001`, with a read-only root filesystem, no
  privilege escalation, and all Linux capabilities dropped.

See [docs/security-threat-model.md](docs/security-threat-model.md) for trust
boundaries, threats, controls, and residual risk.
