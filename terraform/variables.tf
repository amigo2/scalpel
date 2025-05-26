variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-2"
}

variable "aws_profile" {
  description = "AWS CLI profile to use"
  type        = string
  default     = "bistro_agent"
}

variable "vpc_name" {
  description = "Name tag of the VPC to use"
  type        = string
}

variable "subnet_tier_tag" {
  description = "Value of the Tier tag on private subnets"
  type        = string
  default     = "private"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "scalpel_db"
}

variable "db_username" {
  description = "Master username for the DB"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Master password for the DB"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 8
    error_message = "The database password must be at least 8 characters long."
  }
}

variable "db_port" {
  description = "PostgreSQL port"
  type        = number
  default     = 5432
}

variable "db_instance_class" {
  description = "Instance class for Aurora replicas"
  type        = string
  default     = "db.t3.medium"
}

variable "ecr_repo_name" {
  description = "Name for the ECR repo"
  type        = string
  default     = "scalpel"
}

variable "lambda_memory_size" {
  description = "Lambda memory (MB)"
  type        = number
  default     = 2048
}

variable "lambda_timeout" {
  description = "Lambda timeout (seconds)"
  type        = number
  default     = 30
}