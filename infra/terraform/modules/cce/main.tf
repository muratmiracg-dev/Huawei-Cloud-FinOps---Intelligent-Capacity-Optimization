data "huaweicloud_availability_zones" "available" {}

resource "huaweicloud_vpc" "this" {
  name                  = "${var.name}-vpc"
  cidr                  = "10.42.0.0/16"
  enterprise_project_id = var.enterprise_project_id
  tags                  = var.tags
}

resource "huaweicloud_vpc_subnet" "this" {
  name              = "${var.name}-subnet"
  cidr              = "10.42.10.0/24"
  gateway_ip        = "10.42.10.1"
  vpc_id            = huaweicloud_vpc.this.id
  availability_zone = data.huaweicloud_availability_zones.available.names[0]
  primary_dns       = "100.125.1.250"
  secondary_dns     = "100.125.21.250"
  tags              = var.tags
}

resource "huaweicloud_cce_cluster" "this" {
  name                   = "${var.name}-${var.environment}"
  flavor_id              = "cce.s2.small"
  vpc_id                 = huaweicloud_vpc.this.id
  subnet_id              = huaweicloud_vpc_subnet.this.id
  container_network_type = "eni"
  authentication_mode    = "rbac"
  enterprise_project_id  = var.enterprise_project_id
  tags                   = var.tags
}

resource "huaweicloud_cce_node_pool" "finops" {
  cluster_id         = huaweicloud_cce_cluster.this.id
  name               = "${var.name}-elastic"
  os                 = "EulerOS 2.9"
  flavor_id          = var.node_flavor
  initial_node_count = var.node_pool_min
  availability_zone  = data.huaweicloud_availability_zones.available.names[0]
  key_pair           = var.key_pair_name
  billing_mode       = 0

  scall_enable             = true
  min_node_count           = var.node_pool_min
  max_node_count           = var.node_pool_max
  scale_down_cooldown_time = 10
  priority                 = 1

  root_volume {
    size       = 40
    volumetype = "SAS"
  }

  data_volumes {
    size       = 100
    volumetype = "SAS"
  }

  tags = var.tags

  lifecycle {
    precondition {
      condition     = var.node_pool_max >= var.node_pool_min
      error_message = "The maximum CCE node count cannot be below the minimum."
    }
  }
}
