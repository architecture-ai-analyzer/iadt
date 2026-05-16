# Update variables.tf with API key variables

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
