output "cce_cluster_id" {
  description = "CCE cluster identifier."
  value       = module.cce.cluster_id
}

output "cce_node_pool_id" {
  description = "Autoscaled CCE node pool identifier."
  value       = module.cce.node_pool_id
}

output "cost_export_bucket" {
  description = "OBS bucket used by Huawei Cost Details Export."
  value       = module.observability.cost_export_bucket
}

output "cost_alert_topic_urn" {
  description = "SMN topic for budget and optimization alerts."
  value       = module.observability.alert_topic_urn
}
