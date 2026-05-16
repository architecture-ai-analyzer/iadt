variable "environment" {
  description = "Environment name (dev, homologation, production)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "iadt"
}

variable "region_default" {
  description = "Default AWS region"
  type        = string
  default     = "us-east-2"
}

variable "vpc_remote_state_bucket" {
  description = "S3 bucket containing the networking remote state"
  type        = string
  default     = "tf-state-ia-arch-analyzer"
}

variable "vpc_remote_state_key" {
  description = "S3 key for the networking remote state"
  type        = string
  default     = "v1/networking"
}

variable "eks_remote_state_bucket" {
  description = "S3 bucket containing the EKS remote state"
  type        = string
  default     = "tf-state-ia-arch-analyzer"
}

variable "eks_remote_state_key" {
  description = "S3 key for the EKS remote state"
  type        = string
  default     = "v1/eks"
}

variable "upload_service_remote_state_bucket" {
  description = "S3 bucket containing the upload-service remote state"
  type        = string
  default     = "tf-state-ia-arch-analyzer"
}

variable "upload_service_remote_state_key" {
  description = "S3 key for the upload-service remote state"
  type        = string
  default     = "v1/upload-service"
}

# SQS Configuration
variable "input_queue_message_retention_seconds" {
  description = "Input queue message retention"
  type        = number
  default     = 86400 # 1 day (Free tier friendly)
}

variable "input_queue_visibility_timeout_seconds" {
  description = "Input queue visibility timeout for processing"
  type        = number
  default     = 300 # 5 minutes
}

variable "output_queue_message_retention_seconds" {
  description = "Output queue message retention"
  type        = number
  default     = 86400 # 1 day (Free tier friendly)
}

variable "output_queue_visibility_timeout_seconds" {
  description = "Output queue visibility timeout"
  type        = number
  default     = 300 # 5 minutes
}

# Kubernetes Configuration
variable "kubernetes_namespace" {
  description = "Kubernetes namespace for IADT"
  type        = string
  default     = "iadt"
}

variable "kubernetes_service_account" {
  description = "Kubernetes service account for IADT"
  type        = string
  default     = "iadt-worker"
}

# IADT Deployment Configuration
variable "iadt_image" {
  description = "Docker image for IADT worker"
  type        = string
  default     = "your-registry/iadt-worker:latest"
}

variable "iadt_cpu_request" {
  description = "CPU request for IADT worker"
  type        = string
  default     = "250m"
}

variable "iadt_cpu_limit" {
  description = "CPU limit for IADT worker"
  type        = string
  default     = "500m"
}

variable "iadt_memory_request" {
  description = "Memory request for IADT worker"
  type        = string
  default     = "256Mi"
}

variable "iadt_memory_limit" {
  description = "Memory limit for IADT worker"
  type        = string
  default     = "1Gi"
}

# LLM Provider Configuration
variable "llm_provider" {
  description = "LLM provider (anthropic or openai)"
  type        = string
  default     = "openai"
  validation {
    condition     = contains(["anthropic", "openai"], var.llm_provider)
    error_message = "llm_provider must be either 'anthropic' or 'openai'."
  }
}

# OpenAI Configuration
variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "openai_model_text" {
  description = "OpenAI model for text processing"
  type        = string
  default     = "gpt-4o-mini"
}

variable "openai_model_vision" {
  description = "OpenAI model for vision/image analysis"
  type        = string
  default     = "gpt-4o"
}

# Anthropic Configuration (fallback)
variable "anthropic_api_key" {
  description = "Anthropic API key (fallback)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "claude_model_text" {
  description = "Claude model for text processing"
  type        = string
  default     = "claude-haiku-4-5-20251001"
}

variable "claude_model_vision" {
  description = "Claude model for vision/image analysis"
  type        = string
  default     = "claude-opus-4-5-20251101"
}

# Logging Configuration
variable "log_level" {
  description = "Log level (DEBUG, INFO, WARNING, ERROR)"
  type        = string
  default     = "INFO"
}

variable "log_format" {
  description = "Log format (text or json)"
  type        = string
  default     = "json"
  validation {
    condition     = contains(["text", "json"], var.log_format)
    error_message = "log_format must be either 'text' or 'json'."
  }
}
