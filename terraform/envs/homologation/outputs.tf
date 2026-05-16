output "namespace" {
  description = "Kubernetes namespace"
  value       = kubernetes_namespace.iadt.metadata[0].name
}

output "deployment_name" {
  description = "IADT worker deployment name"
  value       = kubernetes_deployment.iadt_worker.metadata[0].name
}

output "service_name" {
  description = "IADT worker service name"
  value       = kubernetes_service.iadt_worker.metadata[0].name
}

output "hpa_name" {
  description = "IADT HPA name"
  value       = kubernetes_horizontal_pod_autoscaler_v2.iadt_worker.metadata[0].name
}
