# Service for IADT (optional - for health checks and metrics)
resource "kubernetes_service_v1" "iadt_worker" {
  metadata {
    name      = "iadt-worker"
    namespace = kubernetes_namespace_v1.iadt.metadata[0].name
    labels = {
      app = "iadt-worker"
    }
  }

  spec {
    selector = {
      app = "iadt-worker"
    }

    port {
      name       = "metrics"
      port       = 8080
      target_port = 8080
      protocol   = "TCP"
    }

    type = "ClusterIP"
  }

  depends_on = [kubernetes_namespace_v1.iadt]
}
