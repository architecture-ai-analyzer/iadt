# Kubernetes Namespace
resource "kubernetes_namespace_v1" "iadt" {
  metadata {
    name = var.kubernetes_namespace
    labels = {
      "app.kubernetes.io/name" = "iadt"
    }
  }
}

# ConfigMap with environment configuration
resource "kubernetes_config_map_v1" "iadt_config" {
  metadata {
    name      = "iadt-config"
    namespace = kubernetes_namespace_v1.iadt.metadata[0].name
  }

  data = {
    # AWS Configuration
    AWS_REGION                    = var.region_default
    CLOUD_AWS_REGION              = var.region_default
    AWS_ACCESS_KEY_ID             = var.aws_access_key_id
    AWS_SECRET_ACCESS_KEY         = var.aws_secret_access_key
    
    # SQS Configuration
    IADT_INPUT_QUEUE_URL          = data.aws_sqs_queue.input_queue.url
    IADT_OUTPUT_QUEUE_URL         = data.aws_sqs_queue.output_queue.url
    IADT_WORKER_VISIBILITY_TIMEOUT = "300"
    IADT_WORKER_OUTPUT_MAX_BYTES   = "262144" # 256KB
    
    # S3 Configuration
    S3_BUCKET                     = var.s3_bucket_name
    S3_REGION                     = var.region_default
    
    # LLM Provider Configuration
    LLM_PROVIDER                  = var.llm_provider
    OPENAI_MODEL_TEXT             = var.openai_model_text
    OPENAI_MODEL_VISION           = var.openai_model_vision
    CLAUDE_MODEL_TEXT             = var.claude_model_text
    CLAUDE_MODEL_VISION           = var.claude_model_vision
    
    # Logging Configuration
    LOG_LEVEL                     = var.log_level
    LOG_FORMAT                    = var.log_format
    PYTHONUNBUFFERED              = "1"
  }
}

# Secret for API keys (must be created manually or via external process)
# kubectl create secret generic iadt-anthropic-api-key --from-literal=ANTHROPIC_API_KEY=<your-key> -n iadt
# kubectl create secret generic iadt-openai-api-key --from-literal=OPENAI_API_KEY=<your-key> -n iadt
