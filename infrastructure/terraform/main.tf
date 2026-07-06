terraform {
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "~> 0.4.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12.1"
    }
  }
}

# 1. Create the Local Kind Cluster
resource "kind_cluster" "job_board_cluster" {
  name           = "job-board-cluster"
  node_image     = "kindest/node:v1.30.0"
  wait_for_ready = true
}

# 2. Configure the Helm Provider to talk to the new cluster
provider "helm" {
  kubernetes {
    host                   = kind_cluster.job_board_cluster.endpoint
    client_certificate     = kind_cluster.job_board_cluster.client_certificate
    client_key             = kind_cluster.job_board_cluster.client_key
    cluster_ca_certificate = kind_cluster.job_board_cluster.cluster_ca_certificate
  }
}

# 3. Deploy Strimzi Operator via Helm
resource "helm_release" "strimzi_operator" {
  name             = "my-strimzi"
  repository       = "https://strimzi.io/charts/"
  chart            = "strimzi-kafka-operator"
  namespace        = "data-pipeline"
  create_namespace = true

  depends_on = [kind_cluster.job_board_cluster]
}

# 4. Deploy Elasticsearch via Helm
resource "helm_release" "elasticsearch" {
  name             = "my-elastic"
  repository       = "https://helm.elastic.co"
  chart            = "elasticsearch"
  namespace        = "data-pipeline"
  create_namespace = true

  values = [
    file("../../YAML/elastic-values.yaml")
  ]

  depends_on = [kind_cluster.job_board_cluster]
}

# 5. Deploy Prometheus & Grafana via Helm
resource "helm_release" "kube_prometheus_stack" {
  name             = "kube-prometheus-stack"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  namespace        = "monitoring"
  create_namespace = true

  set {
    name  = "grafana.adminPassword"
    value = "admin"
  }

  depends_on = [kind_cluster.job_board_cluster]
}