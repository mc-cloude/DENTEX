terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.24"
    }
  }
}

module "marquez" {
  source       = "../../modules/marquez"
  namespace    = "pulse-staging"
  postgres_url = var.postgres_url
}

module "lineage_backup" {
  source      = "../../modules/lineage_backup"
  bucket_name = "pulse-staging-lineage"
}

module "redis_password" {
  source       = "../../modules/eso_secret"
  name         = "redis-password"
  namespace    = "pulse-staging"
  secret_store = "pulse-eso"
}

variable "postgres_url" {
  type      = string
  sensitive = true
}
