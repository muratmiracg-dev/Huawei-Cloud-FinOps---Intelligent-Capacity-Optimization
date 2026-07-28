variable "name" {
  type = string
}

variable "environment" {
  type = string
}

variable "enterprise_project_id" {
  type = string
}

variable "key_pair_name" {
  type = string
}

variable "node_flavor" {
  type = string
}

variable "node_pool_min" {
  type = number
}

variable "node_pool_max" {
  type = number
}

variable "tags" {
  type = map(string)
}
