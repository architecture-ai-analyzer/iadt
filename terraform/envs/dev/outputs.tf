output "namespace" {
  description = "Kubernetes namespace"
  value       = kubernetes_namespace_v1.iadt.metadata[0].name
}

output "deployment_name" {
  description = "IADT worker deployment name"
  value       = kubernetes_deployment_v1.iadt_worker.metadata[0].name
}

output "service_name" {
  description = "IADT worker service name"
  value       = kubernetes_service_v1.iadt_worker.metadata[0].name
}

# kubectl get pods -n iadt
