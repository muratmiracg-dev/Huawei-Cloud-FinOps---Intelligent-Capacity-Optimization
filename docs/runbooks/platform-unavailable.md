# Runbook: FinOps platform unavailable

## Trigger

`FinOpsApiDown`, failed readiness, or missing dashboard data.

## Triage

```bash
kubectl -n finops-system get pods,svc,hpa,pdb
kubectl -n finops-system describe deployment finops-optimizer
kubectl -n finops-system logs deployment/finops-optimizer --tail=200
kubectl -n finops-system get events --sort-by=.lastTimestamp
```

Check:

- data files or mounted export availability,
- container image pull,
- resource pressure and HPA status,
- NetworkPolicy/DNS,
- malformed CSV schema,
- recent deployment.

## Recovery

Roll back the application when the new version is responsible:

```bash
kubectl -n finops-system rollout undo deployment/finops-optimizer
kubectl -n finops-system rollout status deployment/finops-optimizer
```

Do not delete OBS exports or Terraform state as a recovery shortcut.

## Exit

Readiness returns `200`, Prometheus resumes collection, data freshness is
confirmed, and missed analyses are replayed.
