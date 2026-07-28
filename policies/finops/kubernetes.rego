package finops.kubernetes

import rego.v1

required_finops_labels := {
    "finops.huaweicloud.com/cost-center",
    "finops.huaweicloud.com/owner",
    "finops.huaweicloud.com/environment",
}

workload if {
    input.kind == "Deployment"
}

workload if {
    input.kind == "StatefulSet"
}

deny contains msg if {
    workload
    some required in required_finops_labels
    not input.spec.template.metadata.labels[required]
    msg := sprintf("%s/%s is missing cost allocation label %s", [
        input.kind,
        input.metadata.name,
        required,
    ])
}

deny contains msg if {
    workload
    some container in input.spec.template.spec.containers
    not container.resources.requests.cpu
    msg := sprintf("container %s must define a CPU request", [container.name])
}

deny contains msg if {
    workload
    some container in input.spec.template.spec.containers
    not container.resources.requests.memory
    msg := sprintf("container %s must define a memory request", [container.name])
}

deny contains msg if {
    workload
    some container in input.spec.template.spec.containers
    not container.resources.limits.memory
    msg := sprintf("container %s must define a memory limit", [container.name])
}

deny contains msg if {
    workload
    input.spec.template.spec.securityContext.runAsNonRoot != true
    msg := sprintf("%s/%s must run as non-root", [
        input.kind,
        input.metadata.name,
    ])
}

deny contains msg if {
    input.kind == "HorizontalPodAutoscaler"
    input.spec.maxReplicas > 20
    msg := sprintf("HPA %s exceeds the approved capacity ceiling of 20 replicas", [
        input.metadata.name,
    ])
}
