# Horizontal Pod Autoscaler
resource "kubernetes_horizontal_pod_autoscaler_v2" "iadt_worker" {
  metadata {
    name      = "iadt-worker-hpa"
    namespace = kubernetes_namespace.iadt.metadata[0].name
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.iadt_worker.metadata[0].name
    }

    min_replicas = var.hpa_min_replicas
    max_replicas = var.hpa_max_replicas

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = var.hpa_target_cpu_utilization
        }
      }
    }

    behavior {
      scale_up {
        stabilization_window_seconds = 60
        policies {
          type                  = "Percent"
          value                 = 100
          period_seconds        = 60
        }
        policies {
          type                  = "Pods"
          value                 = 2
          period_seconds        = 60
        }
        select_policy = "Max"
      }

      scale_down {
        stabilization_window_seconds = 300
        policies {
          type                  = "Percent"
          value                 = 50
          period_seconds        = 60
        }
        select_policy = "Min"
      }
    }
  }

  depends_on = [kubernetes_deployment.iadt_worker]
}
