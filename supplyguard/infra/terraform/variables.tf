variable "aws_region" {
  description = "AWS region for the SupplyGuard stack."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment label."
  type        = string
  default     = "demo"
}

variable "name" {
  description = "Lowercase resource name prefix."
  type        = string
  default     = "supplyguard"
}

variable "container_image" {
  description = "Immutable ECR image URI including the pushed image tag."
  type        = string
}

variable "app_secret_arn" {
  description = "Secrets Manager ARN containing JSON key SECRET_KEY for the scanner API."
  type        = string
  sensitive   = true
}

variable "certificate_arn" {
  description = "Optional ACM certificate ARN. When set, the ALB redirects HTTP to HTTPS."
  type        = string
  default     = ""
}

variable "allowed_cidr" {
  description = "CIDR allowed to reach the public load balancer. Restrict this for non-demo deployments."
  type        = string
  default     = "0.0.0.0/0"
}

variable "desired_count" {
  description = "Number of Fargate tasks."
  type        = number
  default     = 1
}

variable "app_port" {
  description = "SupplyGuard HTTP port inside the container."
  type        = number
  default     = 5050
}
