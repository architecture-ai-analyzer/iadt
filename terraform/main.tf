# Input Queue (receives tasks from upload-service)
module "input_queue" {
  source = "./modules/sqs"

  queue_name                 = local.input_queue_name
  message_retention_seconds  = var.input_queue_message_retention_seconds
  visibility_timeout_seconds = var.input_queue_visibility_timeout_seconds
  receive_wait_time_seconds  = 20
  environment                = var.environment
  project_name               = var.project_name
  tags                       = local.common_tags
}

# Output Queue (publishes results to upload-service)
module "output_queue" {
  source = "./modules/sqs"

  queue_name                 = local.output_queue_name
  message_retention_seconds  = var.output_queue_message_retention_seconds
  visibility_timeout_seconds = var.output_queue_visibility_timeout_seconds
  receive_wait_time_seconds  = 20
  environment                = var.environment
  project_name               = var.project_name
  tags                       = local.common_tags
}

# IAM Role for IRSA (K8s Service Account)
module "iam" {
  source = "./modules/iam"

  cluster_name               = local.eks_data.cluster_name
  oidc_provider_arn          = local.eks_data.oidc_provider_arn
  oidc_provider_url          = local.eks_data.oidc_provider_url
  kubernetes_namespace       = var.kubernetes_namespace
  kubernetes_service_account = var.kubernetes_service_account
  input_queue_arn            = module.input_queue.queue_arn
  input_queue_name           = local.input_queue_name
  output_queue_arn           = module.output_queue.queue_arn
  output_queue_name          = local.output_queue_name
  s3_bucket_arn              = local.upload_service_data.s3_bucket_arn
  environment                = var.environment
  project_name               = var.project_name

  providers = {
    kubernetes = kubernetes
  }
}
