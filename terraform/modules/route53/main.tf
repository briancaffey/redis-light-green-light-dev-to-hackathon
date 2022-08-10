variable "zone_name" {
  description = "The name of the Route 53 zone. Last character should be a period"
  type        = string
}

variable "record_name" {
  description = "value of the record name (e.g. app.example.com)"
  type        = string
}

variable "alb_dns_name" {
  description = "ALB DNS name"
  type        = string
}

data "aws_route53_zone" "this" {
  name         = var.zone_name
  private_zone = false
}

resource "aws_route53_record" "this" {
  zone_id = data.aws_route53_zone.this.id
  name    = var.record_name
  type    = "CNAME"
  ttl     = "60"
  records = [var.alb_dns_name]
}

output "record_name" {
  value = var.record_name
}
