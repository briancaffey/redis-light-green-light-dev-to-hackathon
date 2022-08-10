module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${terraform.workspace}-vpc"
  cidr = var.cidr

  azs            = var.azs
  public_subnets = var.public_subnets

  enable_nat_gateway = false
  enable_dns_hostnames = true
  enable_dns_support   = true

}

module "lb" {
  source              = "./modules/lb"
  vpc_id              = module.vpc.vpc_id
  acm_certificate_arn = var.acm_certificate_arn
  health_check_path   = "/"
  public_subnets      = module.vpc.public_subnets
}

module "ecs" {
  source         = "./modules/ecs"
  vpc_id         = module.vpc.vpc_id
  public_subnets = module.vpc.public_subnets
  instance_type  = var.instance_type
  alb_sg_id      = module.lb.alb_sg_id
  region         = var.region
}

module "route53" {
  source       = "./modules/route53"
  zone_name    = var.zone_name
  record_name  = var.record_name
  alb_dns_name = module.lb.dns_name
}

module "redis" {
  source                         = "./modules/redis"
  name                           = "redis"
  vpc_id                         = module.vpc.vpc_id
  ecs_cluster_id                 = module.ecs.cluster_id
  public_subnets                 = module.vpc.public_subnets
  ecs_sg_id                      = module.ecs.ecs_sg_id
  image                          = "${var.redis_image}:latest"
  region                         = var.region
  log_group_name                 = "/ecs/${terraform.workspace}/redis"
  log_stream_prefix              = "redis"
  service_discovery_namespace_id = module.ecs.service_discovery_namespace_id
  ecs_service_iam_role_arn       = module.ecs.service_iam_role_arn
  task_role_arn                  = module.ecs.task_role_arn
  execution_role_arn             = module.ecs.execution_role_arn
}

locals {
  be_image = "${var.ecr_app_repo}:${var.app_image_tag}"
  env_vars = [
    {
      name  = "REDIS_HOST"
      # value = "${terraform.workspace}-redis.${terraform.workspace}-sd-ns"
      value = "default-redis.default-sd-ns"
    }
  ]
}

module "app" {
  source                   = "./modules/app"
  name                     = "gunicorn"
  ecs_cluster_id           = module.ecs.cluster_id
  task_role_arn            = module.ecs.task_role_arn
  ecs_service_iam_role_arn = module.ecs.service_iam_role_arn
  command                  = ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
  env_vars                 = local.env_vars
  image                    = local.be_image
  alb_default_tg_arn       = module.lb.alb_default_tg_arn
  log_group_name           = "/ecs/${terraform.workspace}/app"
  log_stream_prefix        = "app"
  region                   = var.region
  cpu                      = var.app_cpu
  memory                   = var.app_memory
  port                     = 5000
  path_patterns            = ["/*"]
  health_check_path        = "/api/status/"
  listener_arn             = module.lb.listener_arn
  vpc_id                   = module.vpc.vpc_id
  priority                 = 1
  ecs_sg_id                = module.ecs.ecs_sg_id
  public_subnets           = module.vpc.public_subnets
  execution_role_arn       = module.ecs.execution_role_arn
}
