# CloudWatch Module for JobQuest Navigator v2
# Provides comprehensive monitoring, alerting, and observability

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", var.alb_arn_suffix],
            [".", "TargetResponseTime", ".", "."],
            [".", "HTTPCode_ELB_5XX_Count", ".", "."],
            [".", "HTTPCode_ELB_4XX_Count", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Application Load Balancer Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", var.ecs_service_names[0], "ClusterName", var.ecs_cluster_name],
            [".", "MemoryUtilization", ".", ".", ".", "."],
            [".", "RunningTaskCount", ".", ".", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "ECS Service Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.rds_instance_id],
            [".", "DatabaseConnections", ".", "."],
            [".", "FreeStorageSpace", ".", "."],
            [".", "ReadLatency", ".", "."],
            [".", "WriteLatency", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "RDS Database Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ElastiCache", "CPUUtilization", "CacheClusterId", "${var.elasticache_cluster_id}-001"],
            [".", "DatabaseMemoryUsagePercentage", ".", "."],
            [".", "CurrConnections", ".", "."],
            [".", "Evictions", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "ElastiCache Redis Metrics"
          period  = 300
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6

        properties = {
          query   = "SOURCE '/ecs/${var.name_prefix}/backend'\n| fields @timestamp, @message\n| sort @timestamp desc\n| limit 100"
          region  = data.aws_region.current.name
          title   = "Recent Backend Logs"
          view    = "table"
        }
      }
    ]
  })

  tags = var.tags
}

# Data source
data "aws_region" "current" {}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.name_prefix}-alerts"

  tags = var.tags
}

resource "aws_sns_topic_policy" "alerts" {
  arn = aws_sns_topic.alerts.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudWatchAlarmsToPublish"
        Effect = "Allow"
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.alerts.arn
      }
    ]
  })
}

# Email subscription for alerts
resource "aws_sns_topic_subscription" "email_alerts" {
  count     = length(var.alert_email_addresses)
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email_addresses[count.index]
}

# Slack subscription for alerts (if webhook provided)
resource "aws_sns_topic_subscription" "slack_alerts" {
  count     = var.slack_webhook_url != null ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "https"
  endpoint  = var.slack_webhook_url
}

# CloudWatch Log Groups (if not created by other modules)
resource "aws_cloudwatch_log_group" "application_logs" {
  count             = var.create_log_groups ? 1 : 0
  name              = "/aws/application/${var.name_prefix}"
  retention_in_days = var.log_retention_in_days

  tags = var.tags
}

# Custom Metrics - Application Health
resource "aws_cloudwatch_metric_alarm" "application_health" {
  alarm_name          = "${var.name_prefix}-application-health"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "3"
  metric_name        = "RequestCount"
  namespace          = "AWS/ApplicationELB"
  period             = "300"
  statistic          = "Sum"
  threshold          = "1"
  alarm_description  = "Application appears to be down - no requests received"
  alarm_actions      = [aws_sns_topic.alerts.arn]
  ok_actions         = [aws_sns_topic.alerts.arn]
  treat_missing_data = "breaching"

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  tags = var.tags
}

# High Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${var.name_prefix}-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  
  metric_query {
    id = "error_rate"
    
    metric {
      metric_name = "HTTPCode_ELB_5XX_Count"
      namespace   = "AWS/ApplicationELB"
      period      = 300
      stat        = "Sum"
      
      dimensions = {
        LoadBalancer = var.alb_arn_suffix
      }
    }
    
    return_data = true
  }
  
  metric_query {
    id = "total_requests"
    
    metric {
      metric_name = "RequestCount"
      namespace   = "AWS/ApplicationELB"
      period      = 300
      stat        = "Sum"
      
      dimensions = {
        LoadBalancer = var.alb_arn_suffix
      }
    }
    
    return_data = false
  }
  
  metric_query {
    id          = "error_rate_percentage"
    expression  = "(error_rate / total_requests) * 100"
    label       = "Error Rate Percentage"
    return_data = true
  }

  threshold         = 5 # 5% error rate
  alarm_description = "High error rate detected"
  alarm_actions     = [aws_sns_topic.alerts.arn]

  tags = var.tags
}

# Database Connection Alarm
resource "aws_cloudwatch_metric_alarm" "database_connections_high" {
  alarm_name          = "${var.name_prefix}-database-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "DatabaseConnections"
  namespace          = "AWS/RDS"
  period             = "300"
  statistic          = "Average"
  threshold          = var.database_connection_threshold
  alarm_description  = "High number of database connections"
  alarm_actions      = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_id
  }

  tags = var.tags
}

# ECS Service Task Count Alarm
resource "aws_cloudwatch_metric_alarm" "ecs_running_tasks_low" {
  count               = length(var.ecs_service_names)
  alarm_name          = "${var.name_prefix}-${var.ecs_service_names[count.index]}-tasks-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "RunningTaskCount"
  namespace          = "AWS/ECS"
  period             = "60"
  statistic          = "Average"
  threshold          = 1
  alarm_description  = "ECS service has no running tasks"
  alarm_actions      = [aws_sns_topic.alerts.arn]

  dimensions = {
    ServiceName = var.ecs_service_names[count.index]
    ClusterName = var.ecs_cluster_name
  }

  tags = var.tags
}

# Custom Log Metric Filters
resource "aws_cloudwatch_log_metric_filter" "error_count" {
  name           = "${var.name_prefix}-error-count"
  log_group_name = "/ecs/${var.name_prefix}/backend"
  pattern        = "[timestamp, request_id, level=ERROR, ...]"

  metric_transformation {
    name      = "ErrorCount"
    namespace = "JobQuest/Application"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "critical_errors" {
  name           = "${var.name_prefix}-critical-errors"
  log_group_name = "/ecs/${var.name_prefix}/backend"
  pattern        = "[timestamp, request_id, level=CRITICAL, ...]"

  metric_transformation {
    name      = "CriticalErrorCount"
    namespace = "JobQuest/Application"
    value     = "1"
  }
}

# Alarm for application errors
resource "aws_cloudwatch_metric_alarm" "application_errors" {
  alarm_name          = "${var.name_prefix}-application-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "ErrorCount"
  namespace          = "JobQuest/Application"
  period             = "300"
  statistic          = "Sum"
  threshold          = "10"
  alarm_description  = "High number of application errors"
  alarm_actions      = [aws_sns_topic.alerts.arn]
  treat_missing_data = "notBreaching"

  tags = var.tags
}

# Alarm for critical errors
resource "aws_cloudwatch_metric_alarm" "critical_errors" {
  alarm_name          = "${var.name_prefix}-critical-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "CriticalErrorCount"
  namespace          = "JobQuest/Application"
  period             = "300"
  statistic          = "Sum"
  threshold          = "1"
  alarm_description  = "Critical application errors detected"
  alarm_actions      = [aws_sns_topic.alerts.arn]
  treat_missing_data = "notBreaching"

  tags = var.tags
}

# CloudWatch Insights Queries (saved for easy access)
resource "aws_cloudwatch_query_definition" "error_analysis" {
  name = "${var.name_prefix}-error-analysis"

  log_group_names = [
    "/ecs/${var.name_prefix}/backend",
    "/ecs/${var.name_prefix}/frontend"
  ]

  query_string = <<EOF
fields @timestamp, @message, @logStream
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
EOF
}

resource "aws_cloudwatch_query_definition" "performance_analysis" {
  name = "${var.name_prefix}-performance-analysis"

  log_group_names = [
    "/ecs/${var.name_prefix}/backend"
  ]

  query_string = <<EOF
fields @timestamp, @message, @duration
| filter @message like /GraphQL/
| stats avg(@duration), max(@duration), min(@duration) by bin(5m)
| sort @timestamp desc
EOF
}

resource "aws_cloudwatch_query_definition" "user_activity" {
  name = "${var.name_prefix}-user-activity"

  log_group_names = [
    "/ecs/${var.name_prefix}/backend"
  ]

  query_string = <<EOF
fields @timestamp, @message, user_id
| filter @message like /user_id/
| stats count() by user_id
| sort count desc
| limit 50
EOF
}

# CloudWatch Composite Alarms
resource "aws_cloudwatch_composite_alarm" "system_health" {
  alarm_name          = "${var.name_prefix}-system-health"
  alarm_description   = "Overall system health composite alarm"
  
  alarm_rule = join(" OR ", [
    "ALARM(${aws_cloudwatch_metric_alarm.application_health.alarm_name})",
    "ALARM(${aws_cloudwatch_metric_alarm.high_error_rate.alarm_name})",
    "ALARM(${aws_cloudwatch_metric_alarm.database_connections_high.alarm_name})",
    "ALARM(${aws_cloudwatch_metric_alarm.critical_errors.alarm_name})"
  ])

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = var.tags
}

# X-Ray Tracing (if enabled)
resource "aws_xray_sampling_rule" "main" {
  count       = var.enable_xray_tracing ? 1 : 0
  rule_name   = "${var.name_prefix}-sampling"
  priority    = 9000
  version     = 1
  reservoir_size = 1
  fixed_rate     = 0.1
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_type   = "*"
  service_name   = "*"
  resource_arn   = "*"

  tags = var.tags
}

# EventBridge Rules for System Events
resource "aws_cloudwatch_event_rule" "ecs_task_state_change" {
  name        = "${var.name_prefix}-ecs-task-state-change"
  description = "Capture ECS task state changes"

  event_pattern = jsonencode({
    source      = ["aws.ecs"]
    detail-type = ["ECS Task State Change"]
    detail = {
      clusterArn = [var.ecs_cluster_arn]
    }
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "ecs_task_state_sns" {
  rule      = aws_cloudwatch_event_rule.ecs_task_state_change.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.alerts.arn
}

# Cost Anomaly Detection
resource "aws_ce_anomaly_detector" "service_monitor" {
  count         = var.enable_cost_anomaly_detection ? 1 : 0
  name          = "${var.name_prefix}-cost-anomaly"
  monitor_type  = "DIMENSIONAL"

  specification = jsonencode({
    Dimension = "SERVICE"
    MatchOptions = ["EQUALS"]
    Values = ["Amazon Elastic Container Service", "Amazon Relational Database Service"]
  })

  tags = var.tags
}

resource "aws_ce_anomaly_subscription" "service_monitor" {
  count     = var.enable_cost_anomaly_detection ? 1 : 0
  name      = "${var.name_prefix}-cost-anomaly-subscription"
  frequency = "DAILY"
  
  monitor_arn_list = [
    aws_ce_anomaly_detector.service_monitor[0].arn
  ]
  
  subscriber {
    type    = "EMAIL"
    address = var.alert_email_addresses[0]
  }

  tags = var.tags
}