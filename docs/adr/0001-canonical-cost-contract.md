# ADR-001: Canonical cost and utilization contract

- Status: Accepted
- Date: 2026-07-28

## Context

Huawei Cloud evidence can arrive through Cost Center exports, Billing Center
APIs, OBS, CCE, AOM, and Cloud Eye. Coupling analytics directly to each source
would make tests slow, credentials necessary, and schema changes risky.

## Decision

Use four canonical contracts: resources, daily costs, timestamped utilization,
and budgets. Cloud-specific adapters normalize evidence before analytics.

## Consequences

- Core analytics run offline and without cloud credentials.
- Demo and production use the same decision logic.
- Source schema changes are isolated to adapters.
- Collection freshness and lineage must be managed by the ingestion layer.
