variable "region" {
  default = "us-east-1"
}

variable "vpc_id" {
  type = string
}

variable "public_subnets" {
  type = list(string)
}

variable "port" {
  type    = number
  default = 6379
}

variable "cpu" {
  default     = null
  description = "CPU to allocate to container"
  type        = number
}

variable "memory" {
  default     = 128
  description = "Amount (in MiB) of memory used by the task"
  type        = number
}

variable "image" {
  type        = string
  description = "Container image from ECS to run"
}

variable "name" {
  type        = string
  description = "Name to use for container"
}

variable "command" {
  type        = list(string)
  default     = null
  description = "command used to start the container"
}

variable "ecs_cluster_id" {
  description = "ECS Cluster ID"
  type        = string
}

variable "ecs_service_iam_role_arn" {
  description = "ECS Service IAM Role ARN"
  type        = string
}

variable "ecs_sg_id" {
  type        = string
  description = "ECS Security Group ID"
}

variable "log_group_name" {
  type        = string
  description = "Name of the CloudWatch Logs group"
}

variable "log_stream_prefix" {
  type        = string
  description = "Name of the CloudWatch Logs stream"
}

variable "service_discovery_namespace_id" {
  type = string
}

variable "task_role_arn" {
  description = "Task Role ARN"
  type        = string
}

variable "execution_role_arn" {
  description = "Execution Role ARN"
  type        = string
}