# Security Module Outputs

output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "backend_security_group_id" {
  description = "ID of the backend security group"
  value       = aws_security_group.backend.id
}

output "frontend_security_group_id" {
  description = "ID of the frontend security group"
  value       = aws_security_group.frontend.id
}

output "rds_security_group_id" {
  description = "ID of the RDS security group"
  value       = aws_security_group.rds.id
}

output "redis_security_group_id" {
  description = "ID of the Redis security group"
  value       = aws_security_group.redis.id
}

output "bastion_security_group_id" {
  description = "ID of the bastion security group"
  value       = var.enable_bastion_access ? aws_security_group.bastion[0].id : null
}

output "service_discovery_security_group_id" {
  description = "ID of the service discovery security group"
  value       = aws_security_group.service_discovery.id
}

output "vpc_endpoints_security_group_id" {
  description = "ID of the VPC endpoints security group"
  value       = var.enable_vpc_endpoints ? aws_security_group.vpc_endpoints[0].id : null
}

output "security_group_map" {
  description = "Map of all security group IDs"
  value = {
    alb               = aws_security_group.alb.id
    backend           = aws_security_group.backend.id
    frontend          = aws_security_group.frontend.id
    rds               = aws_security_group.rds.id
    redis             = aws_security_group.redis.id
    service_discovery = aws_security_group.service_discovery.id
    bastion           = var.enable_bastion_access ? aws_security_group.bastion[0].id : null
    vpc_endpoints     = var.enable_vpc_endpoints ? aws_security_group.vpc_endpoints[0].id : null
  }
}