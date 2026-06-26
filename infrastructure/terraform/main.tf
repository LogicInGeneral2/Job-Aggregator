terraform {
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "~> 0.4.0"
    }
  }
}

provider "kind" {}

# Provision a local Kubernetes cluster
resource "kind_cluster" "job_board_cluster" {
  name           = "job-board-cluster"
  node_image     = "kindest/node:v1.30.0"
  wait_for_ready = true
}

output "kubeconfig" {
  value       = kind_cluster.job_board_cluster.kubeconfig
  description = "The kubeconfig for the local cluster"
}