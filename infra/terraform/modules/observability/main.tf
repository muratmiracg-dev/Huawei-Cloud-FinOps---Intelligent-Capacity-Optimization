resource "huaweicloud_obs_bucket" "cost_export" {
  bucket        = var.cost_export_bucket
  acl           = "private"
  storage_class = "STANDARD"
  versioning    = true
  force_destroy = false
  tags          = var.tags

  lifecycle_rule {
    name    = "cost-export-retention"
    enabled = true

    transition {
      days          = 90
      storage_class = "WARM"
    }

    expiration {
      days = 400
    }

    noncurrent_version_expiration {
      days = 30
    }
  }
}

resource "huaweicloud_smn_topic" "cost_alerts" {
  name                  = "${var.name}-cost-alerts"
  display_name          = "FinOps cost and capacity alerts"
  enterprise_project_id = var.enterprise_project_id
}
