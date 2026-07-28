"""Repository abstractions keep analytics independent from cloud collection."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from finops.models import Budget, CloudResource, CostRecord, UtilizationSample


class FinOpsRepository(Protocol):
    def resources(self) -> Sequence[CloudResource]: ...

    def costs(self) -> Sequence[CostRecord]: ...

    def utilization(self) -> Sequence[UtilizationSample]: ...

    def budgets(self) -> Sequence[Budget]: ...


@dataclass(slots=True)
class InMemoryRepository:
    resource_records: Sequence[CloudResource]
    cost_records: Sequence[CostRecord]
    utilization_records: Sequence[UtilizationSample]
    budget_records: Sequence[Budget]

    def resources(self) -> Sequence[CloudResource]:
        return self.resource_records

    def costs(self) -> Sequence[CostRecord]:
        return self.cost_records

    def utilization(self) -> Sequence[UtilizationSample]:
        return self.utilization_records

    def budgets(self) -> Sequence[Budget]:
        return self.budget_records
