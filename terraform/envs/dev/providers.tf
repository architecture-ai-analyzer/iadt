terraform {
  backend "s3" {
    bucket         = "tf-state-ia-arch-analyzer"
    key            = "v1/iadt/dev/terraform.tfstate"
    region         = "us-east-2"
  }
}

# Configure data sources from parent directory
variable "region_default" {
  default = "us-east-2"
}

variable "environment" {
  default = "dev"
}

data "terraform_remote_state" "eks" {
  backend = "s3"

  config = {
    bucket         = "tf-state-ia-arch-analyzer"
    key            = "v1/eks/dev/terraform.tfstate"
    region         = "us-east-2"
  }
}

data "aws_eks_cluster_auth" "cluster" {
  name = data.terraform_remote_state.eks.outputs.cluster_name
}

provider "kubernetes" {
  host                   = data.terraform_remote_state.eks.outputs.cluster_endpoint
  cluster_ca_certificate = base64decode(data.terraform_remote_state.eks.outputs.cluster_ca)
  token                  = data.aws_eks_cluster_auth.cluster.token
}
