resource "aws_security_group" "this" {
  name        = "${terraform.workspace}-ecs-sg"
  description = "Allows inbound access from the ALB only"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [var.alb_sg_id]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAM role for ECS

# assume role
resource "aws_iam_role" "ecs_host" {
  name = "${terraform.workspace}-host-role"
  assume_role_policy = jsonencode({
    Version = "2008-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = [
            "ecs.amazonaws.com",
            "ec2.amazonaws.com",
            "ecs-tasks.amazonaws.com"
          ]
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_instance" {
  name = "${terraform.workspace}-instance-role"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:*",
          "ec2:*",
          "elasticloadbalancing:*",
          "ecr:*",
          "cloudwatch:*",
          "s3:*",
          "rds:*",
          "logs:*",
          "elasticache:*",
          "secretsmanager:*"
        ]
        Resource = "*"
      }
    ]
  })
  role = aws_iam_role.ecs_host.id
}

resource "aws_iam_role" "ecs_task" {
  name = "${terraform.workspace}-task-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = ""
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task" {
  name = "${terraform.workspace}-role-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:*", "ssmmessages:*"]
        Resource = ["*"]
      }
    ]
  })
  role = aws_iam_role.ecs_task.id
}

resource "aws_iam_role" "ecs_service" {
  name = "${terraform.workspace}-service-role"
  assume_role_policy = jsonencode({
    Version = "2008-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = [
            "ecs.amazonaws.com",
            "ec2.amazonaws.com"
          ]
        }
        Effect = "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_service" {
  name = "${terraform.workspace}-service-role-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "elasticloadbalancing:Describe*",
          "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
          "elasticloadbalancing:RegisterInstancesWithLoadBalancer",
          "ec2:Describe*",
          "ec2:AuthorizeSecurityGroupIngress",
          "elasticloadbalancing:RegisterTargets",
          "elasticloadbalancing:DeregisterTargets"
        ]
        Resource = ["*"]
      }
    ]
  })
  role = aws_iam_role.ecs_service.id
}

resource "aws_iam_instance_profile" "this" {
  name = "${terraform.workspace}-instance-profile"
  path = "/"
  role = aws_iam_role.ecs_host.name
}


# ECS Cluster

resource "aws_ecs_cluster" "this" {
  name = "${terraform.workspace}-cluster"
}

## Launch Configuration

resource "aws_launch_configuration" "this" {
  name                 = "${terraform.workspace}-launch-config"
  image_id             = lookup(var.amis, var.region)
  instance_type        = var.instance_type
  security_groups      = [aws_security_group.this.id]
  iam_instance_profile = aws_iam_instance_profile.this.name
  # key_name                    = var.key_name
  associate_public_ip_address = true
  user_data                   = <<EOT
#!/bin/bash
echo ECS_CLUSTER='${terraform.workspace}-cluster' > /etc/ecs/ecs.config
echo ECS_CONTAINER_STOP_TIMEOUT=2 >> /etc/ecs/ecs.config
EOT
}


###############################################################################
# ASG
###############################################################################

resource "aws_autoscaling_group" "this" {
  name                 = "${terraform.workspace}_auto_scaling_group"
  min_size             = 1 # var.autoscale_min
  max_size             = 1 # var.autoscale_max
  desired_capacity     = 1 # var.autoscale_desired
  health_check_type    = "EC2"
  launch_configuration = aws_launch_configuration.this.name
  vpc_zone_identifier  = var.public_subnets
}

# Service Discovery

resource "aws_service_discovery_private_dns_namespace" "this" {
  name        = "${terraform.workspace}-sd-ns"
  description = "Service discovery namespace"
  vpc         = var.vpc_id
}
