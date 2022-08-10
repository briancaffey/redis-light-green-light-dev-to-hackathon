variable "region" {
  default = "us-east-1"
}

variable "vpc_id" {
  type = string
}

variable "alb_sg_id" {
  type        = string
  description = "Security group ID for ALB"
}

variable "public_subnets" {
  type = list(string)
}

variable "instance_type" {
  default = "t2.micro"
}

variable "amis" {
  description = "Which AMI to spawn."
  default = {
    us-east-1 = "ami-0fe19057e9cb4efd8"
  }
}