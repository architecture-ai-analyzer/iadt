# IADT Worker Deployment
resource "kubernetes_deployment" "iadt_worker" {
  metadata {
    name      = "iadt-worker"
    namespace = kubernetes_namespace.iadt.metadata[0].name
    labels = {
      app = "iadt-worker"
    }
  }

  spec {
    replicas = var.iadt_replicas

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
        service_account_name = data.terraform_remote_state.root.outputs.kubernetes_service_account

        container {
          name  = "iadt-worker"
          image = var.iadt_image
          image_pull_policy = "IfNotPresent"

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
              name = kubernetes_config_map.iadt_config.metadata[0].name
            }
          }

          # LLM API Key as environment variable
          dynamic "env" {
            for_each = var.llm_provider == "anthropic" && var.anthropic_api_key != "" ? [1] : []
            content {
              name = "ANTHROPIC_API_KEY"
              value_from {
                secret_key_ref {
                  name = var.anthropic_api_key_secret_name
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
                  name = var.openai_api_key_secret_name
                  key  = "OPENAI_API_KEY"
                }
              }
            }
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 8080
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 3
          }

          readiness_probe {
            http_get {
              path = "/ready"
              port = 8080
            }
            initial_delay_seconds = 10
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 2
          }
        }

        termination_grace_period_seconds = 120

        affinity {
          pod_anti_affinity {
            preferred_during_scheduling_ignored_during_execution {
              weight = 100
              pod_affinity_term {
                label_selector {
                  match_expressions {
                    key      = "app"
                    operator = "In"
                    values   = ["iadt-worker"]
                  }
                }
                topology_key = "kubernetes.io/hostname"
              }
            }
          }
        }
      }
    }
  }

  depends_on = [kubernetes_namespace.iadt]
}
