variable "region_default" {
  default = "us-east-2"
}

variable "environment" {
  default = "homologation"
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

variable "iadt_replicas" {
  default = 2
}

variable "iadt_cpu_request" {
  default = "1000m"
}

variable "iadt_cpu_limit" {
  default = "2000m"
}

variable "iadt_memory_request" {
  default = "1Gi"
}

variable "iadt_memory_limit" {
  default = "4Gi"
}

variable "hpa_min_replicas" {
  default = 2
}

variable "hpa_max_replicas" {
  default = 10
}

variable "hpa_target_cpu_utilization" {
  default = 70
}

variable "llm_provider" {
  default = "anthropic"
}

variable "anthropic_api_key_secret_name" {
  default = "iadt-anthropic-api-key"
}

variable "openai_api_key_secret_name" {
  default = "iadt-openai-api-key"
}

variable "log_level" {
  default = "INFO"
}

variable "anthropic_api_key" {
  description = "Anthropic API key for LLM"
  type        = string
  default     = ""
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key for LLM"
  type        = string
  default     = ""
  sensitive   = true
}
