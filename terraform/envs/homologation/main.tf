# Data sources from root
data "terraform_remote_state" "root" {
  backend = "s3"

  config = {
    bucket         = "tf-state-ia-arch-analyzer"
    key            = "v1/iadt/homologation/terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "tf-state-lock"
    encrypt        = true
  }
}

# Remote states for upload-service
data "terraform_remote_state" "upload_service" {
  backend = "s3"

  config = {
    bucket         = "tf-state-ia-arch-analyzer"
    key            = "v1/upload-service/homologation/terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "tf-state-lock"
    encrypt        = true
  }
}

# Include all K8s resources from dev
locals {
  include_dev_k8s = true
}
