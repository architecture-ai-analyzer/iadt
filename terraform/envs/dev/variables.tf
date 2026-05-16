variable "region_default" {
  default = "us-east-2"
}

variable "environment" {
  default = "dev"
}

variable "project_name" {
  default = "iadt"
}

variable "kubernetes_namespace" {
  default = "iadt"
}

variable "kubernetes_service_account" {
  default = "iadt-worker"
}

variable "iadt_image" {
  default = "your-registry/iadt-worker:latest"
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

variable "openai_api_key" {
  default = ""
}

variable "openai_model_text" {
  default = "gpt-4o-mini"
}

variable "openai_model_vision" {
  default = "gpt-4o"
}

variable "anthropic_api_key" {
  default = ""
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
