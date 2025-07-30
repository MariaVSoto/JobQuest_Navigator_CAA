# S3 Module Variables for JobQuest Navigator v2

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
}

variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "versioning_enabled" {
  description = "Enable versioning on the S3 bucket"
  type        = bool
  default     = false
}

variable "force_destroy" {
  description = "Allow bucket to be deleted even if it contains objects"
  type        = bool
  default     = false
}

variable "kms_key_id" {
  description = "KMS key ID for encryption (optional)"
  type        = string
  default     = null
}

variable "noncurrent_version_expiration_days" {
  description = "Number of days after which noncurrent versions expire"
  type        = number
  default     = 90
}

variable "logs_retention_days" {
  description = "Number of days to retain log files"
  type        = number
  default     = 30
}

variable "enable_notifications" {
  description = "Enable S3 bucket notifications"
  type        = bool
  default     = false
}

variable "lambda_notifications" {
  description = "Lambda function notifications configuration"
  type = list(object({
    function_arn  = string
    events        = list(string)
    filter_prefix = optional(string)
    filter_suffix = optional(string)
  }))
  default = []
}

variable "sqs_notifications" {
  description = "SQS queue notifications configuration"
  type = list(object({
    queue_arn     = string
    events        = list(string)
    filter_prefix = optional(string)
    filter_suffix = optional(string)
  }))
  default = []
}

variable "access_logging_bucket" {
  description = "S3 bucket for access logging (optional)"
  type        = string
  default     = null
}

variable "enable_cors" {
  description = "Enable CORS configuration"
  type        = bool
  default     = true
}

variable "cors_allowed_headers" {
  description = "List of allowed headers for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "cors_allowed_methods" {
  description = "List of allowed methods for CORS"
  type        = list(string)
  default     = ["GET", "POST", "PUT", "DELETE", "HEAD"]
}

variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "cors_expose_headers" {
  description = "List of headers to expose for CORS"
  type        = list(string)
  default     = ["ETag"]
}

variable "cors_max_age_seconds" {
  description = "Maximum age in seconds for CORS preflight requests"
  type        = number
  default     = 3000
}

variable "enable_website" {
  description = "Enable static website hosting"
  type        = bool
  default     = false
}

variable "website_index_document" {
  description = "Index document for website hosting"
  type        = string
  default     = "index.html"
}

variable "website_error_document" {
  description = "Error document for website hosting"
  type        = string
  default     = "error.html"
}

variable "website_routing_rules" {
  description = "Website routing rules"
  type = list(object({
    condition = object({
      key_prefix_equals                = optional(string)
      http_error_code_returned_equals = optional(string)
    })
    redirect = object({
      host_name               = optional(string)
      http_redirect_code      = optional(string)
      protocol                = optional(string)
      replace_key_prefix_with = optional(string)
      replace_key_with        = optional(string)
    })
  }))
  default = []
}

variable "additional_bucket_policies" {
  description = "Additional bucket policy statements"
  type        = list(any)
  default     = []
}

variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = false
}

variable "bucket_size_alarm_threshold" {
  description = "Threshold for bucket size alarm (in bytes)"
  type        = number
  default     = 10737418240  # 10GB
}

variable "object_count_alarm_threshold" {
  description = "Threshold for object count alarm"
  type        = number
  default     = 10000
}

variable "alarm_actions" {
  description = "List of alarm actions (SNS topic ARNs)"
  type        = list(string)
  default     = []
}

variable "enable_cloudtrail" {
  description = "Enable CloudTrail for S3 data events"
  type        = bool
  default     = false
}

variable "cloudtrail_bucket_name" {
  description = "S3 bucket for CloudTrail logs"
  type        = string
  default     = null
}

variable "enable_backup_bucket" {
  description = "Enable backup bucket with cross-region replication"
  type        = bool
  default     = false
}

variable "backup_bucket_region" {
  description = "Region for backup bucket (for cross-region replication)"
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}