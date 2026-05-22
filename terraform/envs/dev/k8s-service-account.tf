# Kubernetes Service Account for IADT Worker
# Simple approach without IRSA for academic free tier
resource "kubernetes_service_account_v1" "iadt_worker" {
  metadata {
    name      = var.kubernetes_service_account
    namespace = kubernetes_namespace_v1.iadt.metadata[0].name
    labels = {
      app = "iadt-worker"
    }
  }

  depends_on = [kubernetes_namespace_v1.iadt]
}
