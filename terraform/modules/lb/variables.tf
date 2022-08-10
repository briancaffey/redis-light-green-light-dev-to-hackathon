variable "acm_certificate_arn" {
  type        = string
  description = "ACM certificate ARN for load balancer"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "public_subnets" {
  type        = list(string)
  description = "Public subnets to use for load balancer"
}

variable "health_check_path" {
  default     = "/api/status/"
  description = "Health check path for the default target group"
  type        = string
}