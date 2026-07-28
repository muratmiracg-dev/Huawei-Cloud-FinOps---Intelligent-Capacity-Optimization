variable "region" {
  description = "Huawei Cloud region."
  type        = string
  default     = "eu-west-101"
}

variable "project_name" {
  description = "Stable prefix for project resources."
  type        = string
  default     = "finops-optimizer"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,30}$", var.project_name))
    error_message = "project_name must be lowercase and DNS-safe."
  }
}

variable "environment" {
  description = "Deployment environment used in allocation tags."
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "environment must be development, staging, or production."
  }
}

variable "enterprise_project_id" {
  description = "Huawei Cloud Enterprise Project ID used for governance."
  type        = string
  default     = "0"
}

variable "key_pair_name" {
  description = "Existing KPS key pair for CCE node administration."
  type        = string
  default     = "replace-with-existing-keypair"
}

variable "node_flavor" {
  description = "CCE node flavor; validate regional availability before apply."
  type        = string
  default     = "s6.large.2"
}

variable "node_pool_min" {
  description = "Minimum autoscaled CCE nodes."
  type        = number
  default     = 2
}

variable "node_pool_max" {
  description = "Maximum autoscaled CCE nodes."
  type        = number
  default     = 6

  validation {
    condition     = var.node_pool_max >= var.node_pool_min
    error_message = "node_pool_max must be greater than or equal to node_pool_min."
  }
}

variable "cost_export_bucket_name" {
  description = "Globally unique OBS bucket for Cost Details Export."
  type        = string
  default     = "replace-with-unique-finops-cost-export"
}

variable "tags" {
  description = "Mandatory cost allocation tags."
  type        = map(string)
  default = {
    "owner"       = "platform-team"
    "cost-center" = "CC-300"
    "product"     = "Shared"
    "managed-by"  = "terraform"
  }
}
