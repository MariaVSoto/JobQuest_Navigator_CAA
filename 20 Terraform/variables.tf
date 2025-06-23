variable "aws_region" {
  description = "AWS region to deploy resources."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "A name for the project, used to prefix resource names."
  type        = string
  default     = "jobquest"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets."
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "rds_mysql_instance_class" {
  description = "Instance class for RDS MySQL."
  type        = string
  default     = "db.t3.micro"
}

variable "docdb_instance_class" {
  description = "Instance class for DocumentDB."
  type        = string
  default     = "db.r5.large"
}

variable "lambda_runtime" {
  description = "Runtime for Lambda functions (e.g., nodejs18.x, python3.9)."
  type        = string
  default     = "nodejs18.x"
}

variable "availability_zones" {
  description = "List of availability zones to use."
  type        = list(string)
  # default = ["us-east-1a", "us-east-1b"]
}
