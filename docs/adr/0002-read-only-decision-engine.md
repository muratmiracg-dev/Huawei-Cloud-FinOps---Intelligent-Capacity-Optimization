# ADR-002: Read-only decision engine

- Status: Accepted
- Date: 2026-07-28

## Context

Stopping, resizing, deleting, scheduling, or purchasing cloud resources can
affect availability, data retention, and commercial commitments. Utilization
signals do not contain complete business context.

## Decision

The public service produces evidence and recommendations only. It has no cloud
mutation endpoint and no execution credentials. Approved execution belongs to a
separate workflow with owner review and rollback.

## Consequences

- A compromised API cannot directly delete resources.
- Human context remains part of the decision.
- Recommendations need lifecycle state and an approval system for production use.
- End-to-end automation is slower but safer and auditable.
