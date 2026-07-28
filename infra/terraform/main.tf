locals {
  common_tags = merge(var.tags, {
    environment = var.environment
    project     = var.project_name
  })
}

module "cce" {
  source = "./modules/cce"

  name                  = var.project_name
  environment           = var.environment
  enterprise_project_id = var.enterprise_project_id
  key_pair_name         = var.key_pair_name
  node_flavor           = var.node_flavor
  node_pool_min         = var.node_pool_min
  node_pool_max         = var.node_pool_max
  tags                  = local.common_tags
}

module "observability" {
  source = "./modules/observability"

  name                  = var.project_name
  enterprise_project_id = var.enterprise_project_id
  cost_export_bucket    = var.cost_export_bucket_name
  tags                  = local.common_tags
}
