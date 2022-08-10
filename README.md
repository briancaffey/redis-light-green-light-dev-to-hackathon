# flask, redis ecs, terraform

## Overview

This repo is for testing ECS networking configurations using:
- a simple flask app
- ECS cluster (EC2 or Fargate?)
-  `awsvpc` networking mode
- CloudMap for service discovery
- redis server running as a service in our ECS cluster

## Setup

- [x] add a simple flask app
- [x] add a simple dockerfile
- [x] add a simple docker-compose file with flask app and redis (dev mode)
- [x] add a simple docker-compose file with flask app and redis (prod mode with gunicorn)
- [x] add a redis connection to flask app
- [x] add basic view to test redis connection
- [x] add a terraform config that can be used locally

## AWS Setup

- [x] Setup ECR repository for flask backend
- [x] Build and push flask backend to ECR
- [x] ACM certificate ARN stored in terraform.tfvars file locally
- [x] Hosted Zone and Domain name purchased through AWS Route 53

## Terraform Configuration Details

- [x] VPC with only public subnets and no NAT gateway
- [x] Launch Configuration with 1 EC2 instance
- [x] ASG for ECS
- [ ] Service Discovery Resources