# ADR-003: Conservative non-overlapping savings

- Status: Accepted
- Date: 2026-07-28

## Context

A resource can be simultaneously marked for rightsizing, scheduling, stopping,
or commitment review. Adding every estimate exaggerates the business case.

## Decision

The executive savings portfolio keeps only the largest estimated monthly saving
per resource. Individual recommendations remain visible for review.

## Consequences

- Executive opportunity is explainable and conservative.
- Potentially compatible actions are not automatically stacked.
- A future scenario optimizer can model combinations after dependencies and
  prices are available.
