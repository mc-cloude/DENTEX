variable "namespace" {
  type = string
}

variable "postgres_url" {
  type      = string
  sensitive = true
}

resource "helm_release" "marquez" {
  name       = "marquez"
  namespace  = var.namespace
  repository = "https://helm.datakin.com"
  chart      = "marquez"
  version    = "0.23.3"

  set {
    name  = "postgresql.auth.existingSecret"
    value = "marquez-postgres"
  }
}

resource "kubernetes_secret" "postgres" {
  metadata {
    name      = "marquez-postgres"
    namespace = var.namespace
  }
  data = {
    url = var.postgres_url
  }
}
