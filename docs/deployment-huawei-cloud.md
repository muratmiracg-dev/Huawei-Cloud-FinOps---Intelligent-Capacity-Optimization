# Huawei Cloud deployment guide

## Deployment outcome

The reference deployment provides:

- a VPC and subnet,
- a CCE cluster and autoscaled node pool,
- an OBS bucket for Cost Details Export,
- an SMN topic for cost and capacity alerts,
- a hardened FinOps API deployment,
- Prometheus-compatible metrics and optional ServiceMonitor.

Infrastructure files are examples. Validate region-specific flavors, storage
types, CCE versions, IAM policies, domain requirements, and pricing before
applying them to an account.

## Prerequisites

- Huawei Cloud account and target project
- Enterprise Project ID
- existing KPS key pair
- globally unique OBS bucket name
- Terraform >= 1.8
- Docker or a compatible image builder
- kubectl and Helm
- SWR organization
- access to a CCE cluster endpoint

## Authentication

Use the Huawei Cloud provider's supported runtime environment variables or an
approved identity mechanism. Never write AK/SK values into `.tfvars`, shell
history, images, ConfigMaps, or the repository.

Example variable names:

```bash
export HW_ACCESS_KEY="<runtime-secret>"
export HW_SECRET_KEY="<runtime-secret>"
export HW_REGION_NAME="eu-west-101"
```

Use a short-lived CI secret or approved agency wherever possible. Rotate any
credential that has been exposed.

## Least-privilege evidence collection

Design a dedicated read-only collector identity. Its exact policies depend on
the account model and enabled integrations, but the required evidence typically
includes:

- bill and resource expenditure read access,
- read access to the configured OBS cost-export prefix,
- CCE inventory read access,
- AOM metric read access,
- Cloud Eye metric read access,
- Tag Management read access.

Huawei Cloud's CCE Cloud Native Cost Governance documentation identifies CCE,
AOM, OBS, billing, Cloud Eye, RMS, ECS, and related dependent permissions.
Review the current policy names and reduce resource scope before production.

The API deployment itself does not need cloud credentials when analysis input is
mounted from an approved export process.

## 1. Provision infrastructure

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
cp backend.hcl.example backend.hcl
```

Edit:

- `region`
- `enterprise_project_id`
- `key_pair_name`
- `node_flavor`
- `cost_export_bucket_name`
- cost allocation tags

Then:

```bash
terraform fmt -recursive
terraform init -backend-config=backend.hcl
terraform validate
terraform plan -out=finops.tfplan
terraform show finops.tfplan
terraform apply finops.tfplan
```

Do not apply an unreviewed plan. Verify projected resources, node bounds, bucket
retention, and deletion behavior.

## 2. Configure Cost Details Export

In Huawei Cloud Cost Center:

1. Activate required cost tags.
2. Configure Cost Details Export to the Terraform-created OBS bucket.
3. Select original/amortized cost and usage details required by the organization.
4. Restrict the collector to the designated bucket prefix.
5. Record export schedule and data freshness.

Cost tags affect future organization of cost data after activation. Preserve
historical exported details when retrospective tag analysis is required.

## 3. Build and publish to SWR

Replace placeholders with the target region and SWR organization:

```bash
docker build -t finops-optimizer:1.0.0 .
docker tag finops-optimizer:1.0.0 \
  swr.eu-west-101.myhuaweicloud.com/<organization>/finops-optimizer:1.0.0
docker push \
  swr.eu-west-101.myhuaweicloud.com/<organization>/finops-optimizer:1.0.0
```

Use the current SWR login command from the console. Do not paste its secret into
committed scripts.

## 4. Deploy to CCE

### Kustomize

Set the SWR image without editing the base:

```bash
cd deploy/kubernetes/overlays/production
kustomize edit set image \
  ghcr.io/muratmiracg-dev/huawei-finops-optimizer=\
swr.eu-west-101.myhuaweicloud.com/<organization>/finops-optimizer:1.0.0
kubectl apply -k .
```

### Helm

```bash
helm upgrade --install finops deploy/helm/finops-optimizer \
  --namespace finops-system \
  --create-namespace \
  --set image.repository=\
swr.eu-west-101.myhuaweicloud.com/<organization>/finops-optimizer \
  --set image.tag=1.0.0
```

## 5. Validate

```bash
kubectl -n finops-system rollout status deployment/finops-optimizer
kubectl -n finops-system get pods,svc,hpa,pdb
kubectl -n finops-system port-forward svc/finops-optimizer 8080:80
curl --fail http://127.0.0.1:8080/health/ready
curl --fail http://127.0.0.1:8080/api/v1/summary
```

Confirm:

- pods are spread and ready,
- containers run as non-root,
- resource requests and limits are present,
- NetworkPolicy allows required traffic only,
- HPA bounds match the capacity plan,
- metrics are collected,
- exported data freshness is visible,
- no customer data appears in logs.

## 6. Roll back

Application:

```bash
kubectl -n finops-system rollout undo deployment/finops-optimizer
kubectl -n finops-system rollout status deployment/finops-optimizer
```

Helm:

```bash
helm -n finops-system history finops
helm -n finops-system rollback finops <revision>
```

Infrastructure rollback requires a reviewed Terraform plan. Never destroy a
cost-export bucket or state backend as a generic rollback action.

## Production hardening

- Put API ingress behind approved authentication and TLS.
- Use an IAM agency or workload identity instead of long-lived keys.
- Encrypt Terraform state and restrict the state bucket.
- Enable OBS access logging and retention controls.
- Route alerts through SMN to approved recipients.
- Pin container images by digest.
- Store generated evidence under immutable retention where required.
- Keep recommendation execution in a separate approval workflow.

## Official references

- [Cost Center functions](https://support.huaweicloud.com/intl/en-us/usermanual-cost/costcenter_0000001.html)
- [CCE Cloud Native Cost Governance](https://support.huaweicloud.com/intl/en-us/usermanual-cce/cce_10_0877.html)
- [CCE node pools](https://support.huaweicloud.com/intl/en-us/usermanual-cce/cce_10_0081.html)
- [Billing Center API](https://support.huaweicloud.com/intl/en-us/api-billing/api-billing-0000001.html)
