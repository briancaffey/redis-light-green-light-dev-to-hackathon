variable "region" {
  default = "us-east-1"
}

# VPC

variable "cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs" {
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
  description = "AZs to use for VPC"
  type        = list(string)
}

variable "public_subnets" {
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  description = "Public subnets to use for VPC"
  type        = list(string)
}

# Load Balancer

variable "acm_certificate_arn" {
  type        = string
  description = "ACM certificate ARN for load balancer"
}

# EC2

variable "instance_type" {
  default = "t2.micro"
}

# Route 53

variable "zone_name" {
  description = "The name of the Route 53 zone. Last character should be a period"
  type        = string
}

variable "record_name" {
  description = "value of the record name (e.g. app.example.com)"
  type        = string
}

# ECR

variable "redis_image" {
  type = string
  description = "Copy of public redis image in private ECR"
}

variable "ecr_app_repo" {
  description = "URL of the ECR repository that contains the backend image"
}

variable "app_image_tag" {
  description = "Image tag to use in backend container definitions"
  default     = "latest"
}

# app

variable "app_cpu" {
  default     = null
  description = "CPU to allocate to container"
  type        = number
}

variable "app_memory" {
  default     = 128
  description = "Amount (in MiB) of memory used by the app task"
  type        = number
}