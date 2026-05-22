terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
  }

  backend "s3" {
    bucket         = "tf-state-ai-architecture-analyzer"
    key            = "v1/iadt/dev/terraform.tfstate"
    region         = "us-east-2"
  }
}

provider "aws" {
  region = var.region_default
}

# # Configure data sources from parent directory
# variable "region_default" {
#   default = "us-east-2"
# }

# variable "environment" {
#   default = "dev"
# }

data "terraform_remote_state" "eks" {
  backend = "s3"

  config = {
    bucket         = "tf-state-ai-architecture-analyzer"
    key            = "v1/eks/dev/terraform.tfstate"
    region         = "us-east-2"
  }
}

data "aws_eks_cluster_auth" "cluster" {
  name = data.terraform_remote_state.eks.outputs.cluster_name
}

# Buscar dados do cluster diretamente da AWS para validação
data "aws_eks_cluster" "cluster" {
  name = data.terraform_remote_state.eks.outputs.cluster_name
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}
