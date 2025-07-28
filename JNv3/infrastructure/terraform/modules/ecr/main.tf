# ECR Module for JobQuest Navigator v2
# Creates and manages Elastic Container Registry repositories

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ============================================================================
# ECR REPOSITORIES
# ============================================================================

resource "aws_ecr_repository" "repositories" {
  for_each = toset(var.repositories)

  name                 = "${var.name_prefix}-${each.value}"
  image_tag_mutability = var.image_tag_mutability

  # Enable image scanning for security
  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  # Encryption configuration
  encryption_configuration {
    encryption_type = var.encryption_type
    kms_key         = var.kms_key_id
  }

  tags = merge(var.tags, {
    Name       = "${var.name_prefix}-${each.value}"
    Type       = "ECR Repository"
    Component  = each.value
    Repository = each.value
  })
}

# ============================================================================
# ECR LIFECYCLE POLICIES
# ============================================================================

resource "aws_ecr_lifecycle_policy" "policy" {
  for_each = aws_ecr_repository.repositories

  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last ${var.max_image_count} images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v", "release"]
          countType     = "imageCountMoreThan"
          countNumber   = var.max_image_count
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Delete untagged images older than ${var.untagged_image_days} days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = var.untagged_image_days
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ============================================================================
# ECR REPOSITORY POLICIES (IAM-based access control)
# ============================================================================

resource "aws_ecr_repository_policy" "policy" {
  for_each = var.enable_cross_account_access ? aws_ecr_repository.repositories : {}

  repository = each.value.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCrossAccountAccess"
        Effect = "Allow"
        Principal = {
          AWS = var.cross_account_arns
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetRepositoryPolicy",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages",
          "ecr:BatchDeleteImage",
          "ecr:GetLifecyclePolicy",
          "ecr:GetLifecyclePolicyPreview",
          "ecr:ListTagsForResource",
          "ecr:DescribeImageScanFindings"
        ]
      },
      {
        Sid    = "AllowPushPull"
        Effect = "Allow"
        Principal = {
          AWS = var.allowed_principals
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
      }
    ]
  })
}

# ============================================================================
# ECR REPLICATION CONFIGURATION (Optional for multi-region)
# ============================================================================

resource "aws_ecr_replication_configuration" "replication" {
  count = var.enable_replication ? 1 : 0

  replication_configuration {
    rule {
      destination {
        region      = var.replication_region
        registry_id = data.aws_caller_identity.current.account_id
      }
      
      repository_filter {
        filter      = "${var.name_prefix}-*"
        filter_type = "PREFIX_MATCH"
      }
    }
  }
}

# ============================================================================
# ECR PUBLIC REPOSITORIES (Optional for public images)
# ============================================================================

resource "aws_ecrpublic_repository" "public_repositories" {
  for_each = var.enable_public_repositories ? toset(var.public_repositories) : toset([])

  repository_name = "${var.name_prefix}-${each.value}"

  catalog_data {
    about_text        = var.repository_descriptions[each.value]
    architectures     = ["x86-64", "ARM 64"]
    description       = var.repository_descriptions[each.value]
    operating_systems = ["Linux"]
    usage_text        = "Docker pull commands and usage instructions"
  }

  tags = merge(var.tags, {
    Name       = "${var.name_prefix}-${each.value}-public"
    Type       = "ECR Public Repository"
    Component  = each.value
    Repository = each.value
    Visibility = "Public"
  })
}

# ============================================================================
# DATA SOURCES
# ============================================================================

data "aws_caller_identity" "current" {}

# ============================================================================
# CLOUDWATCH LOG GROUPS FOR ECR SCANNING
# ============================================================================

resource "aws_cloudwatch_log_group" "ecr_scanning" {
  for_each = var.enable_scan_logging ? aws_ecr_repository.repositories : {}

  name              = "/aws/ecr/scanning/${each.value.name}"
  retention_in_days = var.scan_log_retention_days

  tags = merge(var.tags, {
    Name      = "${var.name_prefix}-ecr-scanning-${each.key}"
    Type      = "CloudWatch Log Group"
    Component = "ECR Scanning"
  })
}

# ============================================================================
# ECR SCAN RESULTS SNS NOTIFICATIONS (Optional)
# ============================================================================

resource "aws_sns_topic" "ecr_scan_results" {
  count = var.enable_scan_notifications ? 1 : 0

  name = "${var.name_prefix}-ecr-scan-results"

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-ecr-scan-results"
    Type = "SNS Topic"
  })
}

resource "aws_sns_topic_subscription" "ecr_scan_email" {
  count = var.enable_scan_notifications && length(var.notification_emails) > 0 ? length(var.notification_emails) : 0

  topic_arn = aws_sns_topic.ecr_scan_results[0].arn
  protocol  = "email"
  endpoint  = var.notification_emails[count.index]
}

# ============================================================================
# EVENTBRIDGE RULES FOR ECR SCANNING (Optional)
# ============================================================================

resource "aws_cloudwatch_event_rule" "ecr_scan_complete" {
  count = var.enable_scan_notifications ? 1 : 0

  name        = "${var.name_prefix}-ecr-scan-complete"
  description = "Trigger when ECR image scan completes"

  event_pattern = jsonencode({
    source      = ["aws.ecr"]
    detail-type = ["ECR Image Scan"]
    detail = {
      scan-status = ["COMPLETE"]
      finding-counts = {
        CRITICAL = [{ "numeric" = [">", 0] }]
      }
    }
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "sns" {
  count = var.enable_scan_notifications ? 1 : 0

  rule      = aws_cloudwatch_event_rule.ecr_scan_complete[0].name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.ecr_scan_results[0].arn

  input_transformer {
    input_paths = {
      repository = "$.detail.repository-name"
      region     = "$.detail.awsRegion"
      finding    = "$.detail.finding-counts"
    }
    input_template = "\"ECR Image Scan Alert: Repository <repository> in <region> has critical vulnerabilities. Finding counts: <finding>\""
  }
}