# HPA for IADT Worker Deployment
# Scales based on CPU and Memory usage
# Min: 1, Max: 3 replicas (free tier friendly)

resource "kubernetes_horizontal_pod_autoscaler_v2" "iadt_worker" {
  metadata {
    name      = "iadt-worker-hpa"
    namespace = kubernetes_namespace_v1.iadt.metadata[0].name
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment_v1.iadt_worker.metadata[0].name
    }

    min_replicas = 1
    max_replicas = 3

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 70
        }
      }
    }

    metric {
      type = "Resource"
      resource {
        name = "memory"
        target {
          type                = "Utilization"
          average_utilization = 80
        }
      }
    }
  }

  depends_on = [kubernetes_deployment_v1.iadt_worker]
}

