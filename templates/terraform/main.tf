# Deploys the repo's Helm chart (deploy/helm) — one chart deploys all services.
resource "helm_release" "REPO" {
  name             = "REPO"
  namespace        = var.namespace
  create_namespace = true
  chart            = "${path.module}/../helm"
}
