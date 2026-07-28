# Runbook: allocation coverage gap

## Trigger

`AllocationCoverageBelowTarget` or coverage below 95%.

## Response

1. List resources in the `unallocated` group.
2. Resolve owner from Enterprise Project, creator, CMDB, or approved inventory.
3. Assign `owner`, `cost-center`, `environment`, and `product`.
4. Apply tags through Terraform or an approved tagging workflow.
5. Activate relevant tags in Cost Center when required.
6. Rerun allocation after data availability delay.

## Exceptions

An unresolved resource needs an interim owner, reason, and expiry. Do not leave
an unowned cost outside budget scope.

## Exit

Coverage is at least 95%, every exception has an owner/expiry, and the next cost
snapshot reflects the intended allocation.
