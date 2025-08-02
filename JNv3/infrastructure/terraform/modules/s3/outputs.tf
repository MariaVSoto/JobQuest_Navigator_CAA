# S3 Module Outputs for JobQuest Navigator v2

output "bucket_id" {
  description = "ID of the S3 bucket"
  value       = aws_s3_bucket.main.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.main.arn
}

output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.main.bucket
}

output "bucket_domain_name" {
  description = "Bucket domain name"
  value       = aws_s3_bucket.main.bucket_domain_name
}

output "bucket_regional_domain_name" {
  description = "Bucket regional domain name"
  value       = aws_s3_bucket.main.bucket_regional_domain_name
}

output "bucket_hosted_zone_id" {
  description = "Route 53 hosted zone ID for the bucket"
  value       = aws_s3_bucket.main.hosted_zone_id
}

output "bucket_region" {
  description = "AWS region where the bucket was created"
  value       = aws_s3_bucket.main.region
}

output "website_endpoint" {
  description = "Website endpoint (if website hosting is enabled)"
  value       = var.enable_website ? aws_s3_bucket_website_configuration.main[0].website_endpoint : null
}

output "website_domain" {
  description = "Website domain (if website hosting is enabled)"
  value       = var.enable_website ? aws_s3_bucket_website_configuration.main[0].website_domain : null
}

output "backup_bucket_id" {
  description = "ID of the backup S3 bucket (if enabled)"
  value       = var.enable_backup_bucket ? aws_s3_bucket.backup[0].id : null
}

output "backup_bucket_arn" {
  description = "ARN of the backup S3 bucket (if enabled)"
  value       = var.enable_backup_bucket ? aws_s3_bucket.backup[0].arn : null
}

output "backup_bucket_name" {
  description = "Name of the backup S3 bucket (if enabled)"
  value       = var.enable_backup_bucket ? aws_s3_bucket.backup[0].bucket : null
}