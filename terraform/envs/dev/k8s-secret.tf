# Secret for Anthropic API Key (optional fallback)
resource "kubernetes_secret_v1" "anthropic_api_key" {
  metadata {
    name      = "iadt-anthropic-api-key"
    namespace = kubernetes_namespace_v1.iadt.metadata[0].name
  }

  type = "Opaque"

  data = {
    ANTHROPIC_API_KEY = base64encode(var.anthropic_api_key)
  }

  # Only create if key is provided
  count = var.anthropic_api_key != "" ? 1 : 0
}

# Secret for OpenAI API Key
resource "kubernetes_secret_v1" "openai_api_key" {
  metadata {
    name      = "iadt-openai-api-key"
    namespace = kubernetes_namespace_v1.iadt.metadata[0].name
  }

  type = "Opaque"

  data = {
    OPENAI_API_KEY = base64encode(var.openai_api_key)
  }

  # Only create if key is provided
  count = var.openai_api_key != "" ? 1 : 0
}
#   sensitive   = true
# }
