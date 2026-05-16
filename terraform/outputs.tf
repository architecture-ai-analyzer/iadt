output "input_queue_url" {
  description = "Input SQS queue URL"
  value       = module.input_queue.queue_url
}

output "input_queue_arn" {
  description = "Input SQS queue ARN"
  value       = module.input_queue.queue_arn
}

output "output_queue_url" {
  description = "Output SQS queue URL"
  value       = module.output_queue.queue_url
}

output "output_queue_arn" {
  description = "Output SQS queue ARN"
  value       = module.output_queue.queue_arn
}

output "irsa_role_arn" {
  description = "IAM role ARN for IRSA"
  value       = module.iam.role_arn
}

output "kubernetes_namespace" {
  description = "Kubernetes namespace for IADT"
  value       = var.kubernetes_namespace
}

output "kubernetes_service_account" {
  description = "Kubernetes service account"
  value       = module.iam.service_account_name
}
