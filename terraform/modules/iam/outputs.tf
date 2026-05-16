output "role_arn" {
  description = "IAM role ARN for IRSA"
  value       = aws_iam_role.iadt_worker.arn
}

output "role_name" {
  description = "IAM role name"
  value       = aws_iam_role.iadt_worker.name
}

output "service_account_name" {
  description = "Kubernetes service account name"
  value       = kubernetes_service_account.iadt_worker.metadata[0].name
}
