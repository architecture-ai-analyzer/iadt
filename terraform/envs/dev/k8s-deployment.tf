# IADT Worker Deployment
resource "kubernetes_deployment_v1" "iadt_worker" {
  metadata {
    name      = "iadt-worker"
    namespace = kubernetes_namespace_v1.iadt.metadata[0].name
    labels = {
      app = "iadt-worker"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "iadt-worker"
      }
    }

    template {
      metadata {
        labels = {
          app = "iadt-worker"
        }
      }

      spec {
        service_account_name = kubernetes_service_account_v1.iadt_worker.metadata[0].name

        container {
          name  = "iadt-worker"
          image = var.iadt_image
          image_pull_policy = "Always"

          command = ["python", "-m", "worker"]

          resources {
            requests = {
              cpu    = var.iadt_cpu_request
              memory = var.iadt_memory_request
            }
            limits = {
              cpu    = var.iadt_cpu_limit
              memory = var.iadt_memory_limit
            }
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map_v1.iadt_config.metadata[0].name
            }
          }

          # LLM API Keys as environment variables
          dynamic "env" {
            for_each = var.llm_provider == "anthropic" && var.anthropic_api_key != "" ? [1] : []
            content {
              name = "ANTHROPIC_API_KEY"
              value_from {
                secret_key_ref {
                  name = "iadt-anthropic-api-key"
                  key  = "ANTHROPIC_API_KEY"
                }
              }
            }
          }

          dynamic "env" {
            for_each = var.llm_provider == "openai" && var.openai_api_key != "" ? [1] : []
            content {
              name = "OPENAI_API_KEY"
              value_from {
                secret_key_ref {
                  name = "iadt-openai-api-key"
                  key  = "OPENAI_API_KEY"
                }
              }
            }
          }

          # Health check
          liveness_probe {
            exec {
              command = ["python", "-c", "import sys; sys.exit(0)"]
            }
            initial_delay_seconds = 30
            period_seconds        = 30
            timeout_seconds       = 5
            failure_threshold     = 3
          }
        }

        # Graceful shutdown
        termination_grace_period_seconds = 30
      }
    }
  }

  depends_on = [kubernetes_namespace_v1.iadt]
}
