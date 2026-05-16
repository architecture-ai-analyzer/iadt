variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "oidc_provider_arn" {
  description = "OIDC provider ARN from EKS"
  type        = string
}

variable "oidc_provider_url" {
  description = "OIDC provider URL from EKS"
  type        = string
}

variable "kubernetes_namespace" {
  description = "Kubernetes namespace"
  type        = string
}

variable "kubernetes_service_account" {
  description = "Kubernetes service account name"
  type        = string
}

variable "input_queue_arn" {
  description = "ARN of input SQS queue"
  type        = string
}

variable "input_queue_name" {
  description = "Name of input SQS queue"
  type        = string
}

variable "output_queue_arn" {
  description = "ARN of output SQS queue"
  type        = string
}

variable "output_queue_name" {
  description = "Name of output SQS queue"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of S3 bucket for diagrams"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}
