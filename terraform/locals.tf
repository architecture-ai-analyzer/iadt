locals {
  # Resource naming convention
  input_queue_name      = "${var.project_name}-input-queue-${var.environment}"
  output_queue_name     = "${var.project_name}-output-queue-${var.environment}"
  irsa_role_name        = "${var.project_name}-irsa-${var.environment}"
  
  # Common tags
  common_tags = {
    Name        = var.project_name
    Environment = var.environment
  }

  # Data sources for networking and EKS
  vpc_data            = data.terraform_remote_state.vpc.outputs
  eks_data            = data.terraform_remote_state.eks.outputs
  upload_service_data = data.terraform_remote_state.upload_service.outputs
}
