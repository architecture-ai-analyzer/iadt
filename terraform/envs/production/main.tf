# Data sources from root
data "terraform_remote_state" "root" {
  backend = "s3"

  config = {
    bucket         = "tf-state-ia-arch-analyzer"
    key            = "v1/iadt/production/terraform.tfstate"
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
    key            = "v1/upload-service/production/terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "tf-state-lock"
    encrypt        = true
  }
}
