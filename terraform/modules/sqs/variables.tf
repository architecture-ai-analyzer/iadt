variable "queue_name" {
  description = "Name of the SQS queue"
  type        = string
}

variable "message_retention_seconds" {
  description = "Message retention period in seconds"
  type        = number
  default     = 86400 # 1 day (Free tier friendly)
}

variable "visibility_timeout_seconds" {
  description = "Visibility timeout for messages"
  type        = number
  default     = 300 # 5 minutes
}

variable "receive_wait_time_seconds" {
  description = "Long polling wait time"
  type        = number
  default     = 20
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
