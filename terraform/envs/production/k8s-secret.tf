# Secret for Anthropic API Key (if using Anthropic)
resource "kubernetes_secret" "anthropic_api_key" {
  metadata {
    name      = var.anthropic_api_key_secret_name
    namespace = kubernetes_namespace.iadt.metadata[0].name
  }

  type = "Opaque"

  data = {
    ANTHROPIC_API_KEY = base64encode(var.anthropic_api_key)
  }

  count = var.anthropic_api_key != "" ? 1 : 0
}

# Secret for OpenAI API Key (if using OpenAI)
resource "kubernetes_secret" "openai_api_key" {
  metadata {
    name      = var.openai_api_key_secret_name
    namespace = kubernetes_namespace.iadt.metadata[0].name
  }

  type = "Opaque"

  data = {
    OPENAI_API_KEY = base64encode(var.openai_api_key)
  }

  count = var.openai_api_key != "" ? 1 : 0
}
