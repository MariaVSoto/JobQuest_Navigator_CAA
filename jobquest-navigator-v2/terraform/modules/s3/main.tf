# S3 Module for JobQuest Navigator v2
# Provides secure file storage with versioning, encryption, and lifecycle policies

# Primary S3 Bucket for application storage
resource "aws_s3_bucket" "main" {
  bucket        = var.bucket_name
  force_destroy = var.force_destroy

  tags = merge(var.tags, {
    Name        = var.bucket_name
    Purpose     = "Application Storage"
    Environment = var.environment
  })
}

# Bucket versioning
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = var.versioning_enabled ? "Enabled" : "Suspended"
  }
}

# Server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_key_id != null ? "aws:kms" : "AES256"
      kms_master_key_id = var.kms_key_id
    }
    bucket_key_enabled = var.kms_key_id != null ? true : false
  }
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    id     = "main_lifecycle"
    status = "Enabled"

    # Transition to Infrequent Access after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Transition to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Transition to Deep Archive after 365 days
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    # Delete noncurrent versions after specified days
    noncurrent_version_expiration {
      noncurrent_days = var.noncurrent_version_expiration_days
    }

    # Delete incomplete multipart uploads after 7 days
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  # Temporary files cleanup
  rule {
    id     = "temp_cleanup"
    status = "Enabled"

    filter {
      prefix = "temp/"
    }

    expiration {
      days = 7
    }
  }

  # Log files cleanup
  rule {
    id     = "logs_cleanup"
    status = "Enabled"

    filter {
      prefix = "logs/"
    }

    expiration {
      days = var.logs_retention_days
    }
  }
}

# Bucket notification configuration
resource "aws_s3_bucket_notification" "main" {
  count  = var.enable_notifications ? 1 : 0
  bucket = aws_s3_bucket.main.id

  dynamic "lambda_function" {
    for_each = var.lambda_notifications
    content {
      lambda_function_arn = lambda_function.value.function_arn
      events              = lambda_function.value.events
      filter_prefix       = lambda_function.value.filter_prefix
      filter_suffix       = lambda_function.value.filter_suffix
    }
  }

  dynamic "queue" {
    for_each = var.sqs_notifications
    content {
      queue_arn     = queue.value.queue_arn
      events        = queue.value.events
      filter_prefix = queue.value.filter_prefix
      filter_suffix = queue.value.filter_suffix
    }
  }

  depends_on = [aws_s3_bucket.main]
}

# Bucket logging (if enabled)
resource "aws_s3_bucket_logging" "main" {
  count  = var.access_logging_bucket != null ? 1 : 0
  bucket = aws_s3_bucket.main.id

  target_bucket = var.access_logging_bucket
  target_prefix = "access-logs/${var.bucket_name}/"
}

# CORS configuration
resource "aws_s3_bucket_cors_configuration" "main" {
  count  = var.enable_cors ? 1 : 0
  bucket = aws_s3_bucket.main.id

  cors_rule {
    allowed_headers = var.cors_allowed_headers
    allowed_methods = var.cors_allowed_methods
    allowed_origins = var.cors_allowed_origins
    expose_headers  = var.cors_expose_headers
    max_age_seconds = var.cors_max_age_seconds
  }
}

# Website configuration (if enabled)
resource "aws_s3_bucket_website_configuration" "main" {
  count  = var.enable_website ? 1 : 0
  bucket = aws_s3_bucket.main.id

  index_document {
    suffix = var.website_index_document
  }

  error_document {
    key = var.website_error_document
  }

  dynamic "routing_rule" {
    for_each = var.website_routing_rules
    content {
      condition {
        key_prefix_equals = routing_rule.value.condition.key_prefix_equals
        http_error_code_returned_equals = routing_rule.value.condition.http_error_code_returned_equals
      }
      redirect {
        host_name               = routing_rule.value.redirect.host_name
        http_redirect_code      = routing_rule.value.redirect.http_redirect_code
        protocol                = routing_rule.value.redirect.protocol
        replace_key_prefix_with = routing_rule.value.redirect.replace_key_prefix_with
        replace_key_with        = routing_rule.value.redirect.replace_key_with
      }
    }
  }
}

# Bucket policy for application access
resource "aws_s3_bucket_policy" "main" {
  bucket = aws_s3_bucket.main.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [
        {
          Sid    = "DenyInsecureConnections"
          Effect = "Deny"
          Principal = "*"
          Action = "s3:*"
          Resource = [
            aws_s3_bucket.main.arn,
            "${aws_s3_bucket.main.arn}/*"
          ]
          Condition = {
            Bool = {
              "aws:SecureTransport" = "false"
            }
          }
        }
      ],
      var.additional_bucket_policies
    )
  })
}

# CloudWatch Metrics for S3 (optional)
resource "aws_cloudwatch_metric_alarm" "bucket_size" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.name_prefix}-s3-bucket-size"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "BucketSizeBytes"
  namespace          = "AWS/S3"
  period             = "86400"
  statistic          = "Average"
  threshold          = var.bucket_size_alarm_threshold
  alarm_description  = "This metric monitors S3 bucket size"
  alarm_actions      = var.alarm_actions

  dimensions = {
    BucketName  = aws_s3_bucket.main.bucket
    StorageType = "StandardStorage"
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "object_count" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.name_prefix}-s3-object-count"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "NumberOfObjects"
  namespace          = "AWS/S3"
  period             = "86400"
  statistic          = "Average"
  threshold          = var.object_count_alarm_threshold
  alarm_description  = "This metric monitors S3 object count"
  alarm_actions      = var.alarm_actions

  dimensions = {
    BucketName  = aws_s3_bucket.main.bucket
    StorageType = "AllStorageTypes"
  }

  tags = var.tags
}

# CloudTrail for S3 API logging (optional)
resource "aws_cloudtrail" "s3_data_events" {
  count                         = var.enable_cloudtrail ? 1 : 0
  name                          = "${var.name_prefix}-s3-data-events"
  s3_bucket_name               = var.cloudtrail_bucket_name
  s3_key_prefix               = "s3-data-events/"
  include_global_service_events = false

  event_selector {
    read_write_type                 = "All"
    include_management_events       = false

    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.main.arn}/*"]
    }

    data_resource {
      type   = "AWS::S3::Bucket"
      values = [aws_s3_bucket.main.arn]
    }
  }

  tags = var.tags
}

# Backup bucket (if enabled)
resource "aws_s3_bucket" "backup" {
  count         = var.enable_backup_bucket ? 1 : 0
  bucket        = "${var.bucket_name}-backup"
  force_destroy = var.force_destroy

  tags = merge(var.tags, {
    Name    = "${var.bucket_name}-backup"
    Purpose = "Backup Storage"
  })
}

resource "aws_s3_bucket_versioning" "backup" {
  count  = var.enable_backup_bucket ? 1 : 0
  bucket = aws_s3_bucket.backup[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backup" {
  count  = var.enable_backup_bucket ? 1 : 0
  bucket = aws_s3_bucket.backup[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_key_id != null ? "aws:kms" : "AES256"
      kms_master_key_id = var.kms_key_id
    }
    bucket_key_enabled = var.kms_key_id != null ? true : false
  }
}

resource "aws_s3_bucket_public_access_block" "backup" {
  count  = var.enable_backup_bucket ? 1 : 0
  bucket = aws_s3_bucket.backup[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Cross-region replication (if backup bucket enabled)
resource "aws_s3_bucket_replication_configuration" "main" {
  count      = var.enable_backup_bucket && var.backup_bucket_region != null ? 1 : 0
  role       = aws_iam_role.replication[0].arn
  bucket     = aws_s3_bucket.main.id
  depends_on = [aws_s3_bucket_versioning.main]

  rule {
    id     = "ReplicateToBackup"
    status = "Enabled"

    destination {
      bucket        = aws_s3_bucket.backup[0].arn
      storage_class = "STANDARD_IA"

      dynamic "encryption_configuration" {
        for_each = var.kms_key_id != null ? [1] : []
        content {
          replica_kms_key_id = var.kms_key_id
        }
      }
    }
  }
}

# IAM role for replication
resource "aws_iam_role" "replication" {
  count = var.enable_backup_bucket && var.backup_bucket_region != null ? 1 : 0
  name  = "${var.name_prefix}-s3-replication-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_policy" "replication" {
  count = var.enable_backup_bucket && var.backup_bucket_region != null ? 1 : 0
  name  = "${var.name_prefix}-s3-replication-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl",
          "s3:GetObjectVersionTagging"
        ]
        Effect = "Allow"
        Resource = "${aws_s3_bucket.main.arn}/*"
      },
      {
        Action = [
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = aws_s3_bucket.main.arn
      },
      {
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete",
          "s3:ReplicateTags"
        ]
        Effect = "Allow"
        Resource = "${aws_s3_bucket.backup[0].arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "replication" {
  count      = var.enable_backup_bucket && var.backup_bucket_region != null ? 1 : 0
  role       = aws_iam_role.replication[0].name
  policy_arn = aws_iam_policy.replication[0].arn
}