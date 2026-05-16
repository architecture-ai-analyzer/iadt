resource "aws_sqs_queue" "main" {
  name                       = var.queue_name
  message_retention_seconds  = var.message_retention_seconds
  visibility_timeout_seconds = var.visibility_timeout_seconds
  receive_wait_time_seconds  = var.receive_wait_time_seconds
  
  tags = merge(
    var.tags,
    {
      Name        = var.queue_name
      Environment = var.environment
      Project     = var.project_name
    }
  )
}
