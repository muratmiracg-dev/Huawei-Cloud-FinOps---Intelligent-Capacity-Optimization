"""Explainable rightsizing and capacity optimization recommendations."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Sequence

from finops.models import (
    CloudResource,
    PricingMode,
    Recommendation,
    RecommendationType,
    RiskLevel,
    ServiceType,
    UtilizationSample,
)
from finops.services.allocation import tag_compliance
from finops.services.statistics import mean, percentile

COMPUTE_SERVICES = {
    ServiceType.ECS,
    ServiceType.CCE_NODE,
    ServiceType.RDS,
}


def _recommendation_id(
    resource_id: str, recommendation_type: RecommendationType
) -> str:
    digest = hashlib.sha1(
        f"{resource_id}:{recommendation_type.value}".encode(), usedforsecurity=False
    ).hexdigest()[:10]
    return f"rec-{digest}"


def _confidence(samples: Sequence[UtilizationSample]) -> float:
    days = len({sample.timestamp.date() for sample in samples})
    return round(min(0.98, 0.55 + min(days, 30) / 30 * 0.4), 2)


def _recommend(
    resource: CloudResource,
    recommendation_type: RecommendationType,
    action: str,
    rationale: str,
    savings_pct: float,
    risk: RiskLevel,
    confidence: float,
    evidence: dict[str, object],
) -> Recommendation:
    savings = max(0.0, resource.monthly_cost * savings_pct / 100)
    return Recommendation(
        recommendation_id=_recommendation_id(resource.resource_id, recommendation_type),
        resource_id=resource.resource_id,
        resource_name=resource.name,
        service=resource.service,
        recommendation_type=recommendation_type,
        action=action,
        rationale=rationale,
        current_monthly_cost=round(resource.monthly_cost, 2),
        estimated_monthly_savings=round(savings, 2),
        estimated_savings_pct=round(savings_pct, 2),
        risk=risk,
        confidence=confidence,
        evidence=evidence,
    )


def generate_recommendations(
    resources: Sequence[CloudResource],
    utilization: Sequence[UtilizationSample],
    *,
    minimum_savings: float = 5.0,
    headroom_pct: float = 25.0,
) -> list[Recommendation]:
    samples_by_resource: defaultdict[str, list[UtilizationSample]] = defaultdict(list)
    for sample in utilization:
        samples_by_resource[sample.resource_id].append(sample)

    recommendations: list[Recommendation] = []
    for resource in resources:
        samples = samples_by_resource[resource.resource_id]
        confidence = _confidence(samples)
        cpu_p95 = percentile([sample.cpu_pct for sample in samples], 0.95)
        memory_p95 = percentile([sample.memory_pct for sample in samples], 0.95)
        network_p95 = percentile([sample.network_pct for sample in samples], 0.95)
        request_cpu_avg = mean([sample.request_cpu_pct for sample in samples])
        request_memory_avg = mean([sample.request_memory_pct for sample in samples])
        evidence = {
            "observation_days": len({sample.timestamp.date() for sample in samples}),
            "cpu_p95_pct": round(cpu_p95, 2),
            "memory_p95_pct": round(memory_p95, 2),
            "network_p95_pct": round(network_p95, 2),
            "headroom_policy_pct": headroom_pct,
        }

        compliant, missing_tags = tag_compliance(resource)
        if not compliant:
            recommendations.append(
                _recommend(
                    resource,
                    RecommendationType.TAGGING,
                    f"Add required cost allocation tags: {', '.join(missing_tags)}.",
                    "Incomplete ownership metadata prevents reliable showback and budget attribution.",
                    0.0,
                    RiskLevel.LOW,
                    0.99,
                    {"missing_tags": missing_tags},
                )
            )

        if resource.service in {ServiceType.EVS, ServiceType.EIP, ServiceType.ELB} and (
            not resource.attached or resource.status in {"idle", "unbound", "available"}
        ):
            recommendations.append(
                _recommend(
                    resource,
                    RecommendationType.IDLE_RESOURCE,
                    "Snapshot if required, then release the unattached resource.",
                    "Inventory state indicates that the resource is not serving an active workload.",
                    90.0,
                    RiskLevel.LOW,
                    0.98,
                    {"attached": resource.attached, "status": resource.status},
                )
            )

        if resource.service == ServiceType.OBS and resource.storage_gb >= 500:
            recommendations.append(
                _recommend(
                    resource,
                    RecommendationType.STORAGE_LIFECYCLE,
                    "Apply age-based OBS lifecycle transitions and expiration rules.",
                    "Large object storage footprint is eligible for tiering after access-pattern validation.",
                    22.0,
                    RiskLevel.LOW,
                    0.82,
                    {"storage_gb": resource.storage_gb},
                )
            )

        if resource.service not in COMPUTE_SERVICES or not samples:
            continue

        if cpu_p95 >= 85 or memory_p95 >= 88:
            recommendations.append(
                _recommend(
                    resource,
                    RecommendationType.CAPACITY_RISK,
                    "Increase capacity or enable policy-based autoscaling before the next peak window.",
                    "P95 utilization exceeds the safe operating threshold after required headroom.",
                    0.0,
                    RiskLevel.HIGH,
                    confidence,
                    evidence,
                )
            )
        elif cpu_p95 < 8 and memory_p95 < 15 and network_p95 < 10:
            if resource.environment.lower() in {"development", "dev", "test", "qa"}:
                recommendations.append(
                    _recommend(
                        resource,
                        RecommendationType.IDLE_RESOURCE,
                        "Stop the workload after owner approval; retain a reversible recovery path.",
                        "Sustained P95 CPU, memory, and network activity indicate an idle non-production workload.",
                        78.0,
                        RiskLevel.MEDIUM,
                        confidence,
                        evidence,
                    )
                )
            else:
                recommendations.append(
                    _recommend(
                        resource,
                        RecommendationType.RIGHTSIZE,
                        "Move down at least one flavor after a canary performance test.",
                        "Production workload is materially over-provisioned but is not automatically stoppable.",
                        38.0,
                        RiskLevel.MEDIUM,
                        confidence,
                        evidence,
                    )
                )
        elif cpu_p95 < 35 and memory_p95 < 45:
            target_vcpu = max(1, resource.vcpu // 2) if resource.vcpu else 0
            recommendations.append(
                _recommend(
                    resource,
                    RecommendationType.RIGHTSIZE,
                    (
                        f"Evaluate a {target_vcpu}-vCPU target flavor with "
                        f"{headroom_pct:.0f}% capacity headroom."
                    ),
                    "P95 CPU and memory remain below rightsizing thresholds across the observation window.",
                    28.0,
                    RiskLevel.MEDIUM
                    if resource.environment == "production"
                    else RiskLevel.LOW,
                    confidence,
                    evidence,
                )
            )

        if (
            resource.service == ServiceType.CCE_NODE
            and request_cpu_avg > cpu_p95 + 20
            and request_memory_avg > memory_p95 + 15
        ):
            request_evidence = dict(evidence)
            request_evidence.update(
                {
                    "request_cpu_avg_pct": round(request_cpu_avg, 2),
                    "request_memory_avg_pct": round(request_memory_avg, 2),
                }
            )
            recommendations.append(
                _recommend(
                    resource,
                    RecommendationType.REQUEST_TUNING,
                    "Tune Kubernetes requests and rebalance workloads before shrinking the node pool.",
                    "Average requested capacity materially exceeds observed P95 demand.",
                    14.0,
                    RiskLevel.MEDIUM,
                    confidence,
                    request_evidence,
                )
            )

        if (
            resource.environment.lower() in {"development", "dev", "test", "qa"}
            and resource.schedule == "24x7"
        ):
            recommendations.append(
                _recommend(
                    resource,
                    RecommendationType.SCHEDULE,
                    "Apply an owner-approved weekday schedule with automatic morning start.",
                    "Non-production resource runs continuously despite a business-hours workload profile.",
                    48.0,
                    RiskLevel.LOW,
                    0.9,
                    {"current_schedule": resource.schedule},
                )
            )

        stable_band = max(cpu_p95, memory_p95)
        if (
            resource.pricing_mode == PricingMode.PAY_PER_USE
            and resource.environment == "production"
            and 35 <= stable_band < 80
        ):
            recommendations.append(
                _recommend(
                    resource,
                    RecommendationType.COMMITMENT,
                    "Compare a one-year commitment or savings plan against the validated baseline.",
                    "Stable production utilization makes the pay-per-use baseline a commitment candidate.",
                    18.0,
                    RiskLevel.MEDIUM,
                    confidence,
                    evidence,
                )
            )

    return sorted(
        (
            recommendation
            for recommendation in recommendations
            if recommendation.estimated_monthly_savings >= minimum_savings
            or recommendation.recommendation_type
            in {RecommendationType.CAPACITY_RISK, RecommendationType.TAGGING}
        ),
        key=lambda item: (
            item.risk in {RiskLevel.CRITICAL, RiskLevel.HIGH},
            item.estimated_monthly_savings,
        ),
        reverse=True,
    )


def non_overlapping_savings(recommendations: Sequence[Recommendation]) -> float:
    """Conservatively use only the largest saving per resource."""

    best_by_resource: dict[str, float] = {}
    for item in recommendations:
        best_by_resource[item.resource_id] = max(
            best_by_resource.get(item.resource_id, 0.0),
            item.estimated_monthly_savings,
        )
    return round(sum(best_by_resource.values()), 2)
