variable "project_name" {
  description = "Project name"
  type        = string
  default     = "iadt"
}

variable "region_default" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for file uploads (manually created)"
  type        = string
  default     = "upload-service-bucket-ai-analyzer"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "kubernetes_namespace" {
  description = "Kubernetes namespace"
  type        = string
  default     = "iadt"
}

variable "kubernetes_service_account" {
  default = "iadt-worker"
}

variable "iadt_image" {
  default = "luigigb/iadt-worker:latest"
}

variable "iadt_cpu_request" {
  default = "250m"
}

variable "iadt_cpu_limit" {
  default = "500m"
}

variable "iadt_memory_request" {
  default = "256Mi"
}

variable "iadt_memory_limit" {
  default = "1Gi"
}

variable "llm_provider" {
  default = "openai"
}

variable "openai_model_text" {
  default = "gpt-4o-mini"
}

variable "openai_model_vision" {
  default = "gpt-4o"
}

variable "claude_model_text" {
  default = "claude-haiku-4-5-20251001"
}

variable "claude_model_vision" {
  default = "claude-opus-4-5-20251101"
}

variable "log_level" {
  default = "INFO"
}

variable "log_format" {
  default = "json"
}

variable "aws_access_key_id" {
  description = "AWS Access Key ID for pod credentials"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key for pod credentials"
  type        = string
  sensitive   = true
}
