output "cluster_id" {
  value = huaweicloud_cce_cluster.this.id
}

output "node_pool_id" {
  value = huaweicloud_cce_node_pool.finops.id
}
