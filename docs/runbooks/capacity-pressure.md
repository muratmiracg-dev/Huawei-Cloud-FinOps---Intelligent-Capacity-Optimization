# Runbook: capacity pressure

## Trigger

`CapacityRiskRecommendation` or P95 CPU >= 85% / memory >= 88%.

## Immediate actions

1. Confirm signal freshness and affected workload.
2. Review latency, error rate, saturation, queue depth, and pending pods.
3. Suspend rightsizing and node-pool reduction for the affected scope.
4. Verify HPA and CCE node-pool autoscaling bounds.
5. Increase capacity manually when SLO risk is active and autoscaling cannot react.

## CCE checks

```bash
kubectl top nodes
kubectl top pods -A
kubectl get hpa -A
kubectl get pods -A --field-selector=status.phase=Pending
kubectl describe node <node>
```

Review Kubernetes requests before concluding that physical capacity alone is
insufficient.

## Exit

- utilization returns below the safe threshold,
- pending pods are resolved,
- SLO evidence is stable,
- root cause and new capacity policy are documented.
