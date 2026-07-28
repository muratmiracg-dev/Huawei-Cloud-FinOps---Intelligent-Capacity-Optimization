package finops.kubernetes_test

import data.finops.kubernetes
import rego.v1

valid_deployment := {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {"name": "valid"},
    "spec": {
        "template": {
            "metadata": {
                "labels": {
                    "finops.huaweicloud.com/cost-center": "CC-100",
                    "finops.huaweicloud.com/owner": "platform",
                    "finops.huaweicloud.com/environment": "production",
                },
            },
            "spec": {
                "securityContext": {"runAsNonRoot": true},
                "containers": [{
                    "name": "api",
                    "resources": {
                        "requests": {"cpu": "100m", "memory": "128Mi"},
                        "limits": {"memory": "256Mi"},
                    },
                }],
            },
        },
    },
}

test_valid_deployment_has_no_denials if {
    count(kubernetes.deny with input as valid_deployment) == 0
}

test_missing_cost_center_is_denied if {
    invalid := json.patch(valid_deployment, [{
        "op": "remove",
        "path": "/spec/template/metadata/labels/finops.huaweicloud.com~1cost-center",
    }])
    count(kubernetes.deny with input as invalid) > 0
}

test_hpa_capacity_ceiling if {
    hpa := {
        "kind": "HorizontalPodAutoscaler",
        "metadata": {"name": "unbounded"},
        "spec": {"maxReplicas": 30},
    }
    count(kubernetes.deny with input as hpa) == 1
}
