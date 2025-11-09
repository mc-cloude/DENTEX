variable "name" {
  type = string
}

variable "namespace" {
  type = string
}

variable "secret_store" {
  type = string
}

resource "kubernetes_manifest" "external_secret" {
  manifest = {
    apiVersion = "external-secrets.io/v1beta1"
    kind       = "ExternalSecret"
    metadata = {
      name      = var.name
      namespace = var.namespace
    }
    spec = {
      refreshInterval = "1h"
      secretStoreRef = {
        name = var.secret_store
        kind = "ClusterSecretStore"
      }
      target = {
        name = var.name
      }
      data = [
        {
          secretKey = "value"
          remoteRef = {
            key = var.name
          }
        }
      ]
    }
  }
}
