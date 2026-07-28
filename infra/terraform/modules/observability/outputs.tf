output "cost_export_bucket" {
  value = huaweicloud_obs_bucket.cost_export.bucket
}

output "alert_topic_urn" {
  value = huaweicloud_smn_topic.cost_alerts.topic_urn
}
