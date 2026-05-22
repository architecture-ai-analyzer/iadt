# Variables removed - all managed in envs/dev/

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
