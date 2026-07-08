# An Event-Driven Job Aggregator

A simple event-driven microservices architecture that aggregates, processes, and normalizes job postings from multiple sources. This project aims to put DevOps practices into practice by utilizing a GitOps workflow, containerized builds, and cluster observability.

## Architecture Overview

The system is built on **Kubernetes** and communicates asynchronously via **Kafka**, served through **React**:
1. **Producers:** Workers fetch raw data from various platforms, dump saves it into **MinIO**, and publish event streams to Kafka topics.
2. **Consumers:** Independent pods utilize Kafka Consumer Groups to process the same stream for different purposes:
   * *Aggregator/Loader:* Normalizes data and writes to the primary database.
   * *Alerts/Digest Worker:* Triggers emails for specific job conditions.
3. **MinIO Backups:**
   * *Landing Zone:* Python scrapers drop raw, unprocessed JSON payloads.
   * *Archive:* Kafka Connect sinks processed event streams into buckets.
   * *Disaster Recovery:* S3 snapshot backups of Elasticsearch.
3. **Redis:** Utilized beyond caching:
   * *Sets:* Deduplication of incoming job IDs.
   * *Sorted Sets (ZSET):* Real-time calculation of "Trending Skills" leaderboards.
   * *Geospatial (GEO):* Indexing and querying job locations for real-time market heatmaps.
   * *Redis Hashes (HSET):* Store user preferences of job categories.
4. **Frontend:** The normalized data is indexed into **Elasticsearch** for fast querying, that are used via **FastAPI**, **Node.js**, and **React**.


## DevOps Pipeline & Observability

* Infrastructures provisioned via **Terraform** and bootstrapped/hardened via **Ansible**.
* Orchestrator in **Jenkins** triggers modular pipelines. Images are built natively inside the Kubernetes cluster, using **Kaniko**.
* **Argo CD** serves as the GitOps engine, seamlessly syncing the live Kubernetes state to the manifests.
* Automatic detection and email alerts, via **Prometheus** for Crashes, High CPU usage, and Deployment replica mismatches.
* Dashboards are injected dynamically via Kubernetes `ConfigMaps` and displayed using **Grafana**.
