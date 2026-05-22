# Outputs removed - all managed in envs/dev/

output "kubernetes_service_account" {
  description = "Kubernetes service account"
  value       = module.iam.service_account_name
}
