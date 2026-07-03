# Master Cluster Automation Controller
NAMESPACE=data-pipeline
MONITORING_NS=monitoring

.PHONY: start stop status ports tail-worker tail-geo trigger-scraper clean-pvc

# Wakes up the stopped Kind cluster nodes
start:
	@echo "Waking up Docker Desktop Node Engines..."
	docker start job-board-cluster-control-plane
	@echo "Waiting for core Kubernetes services to stabilize..."
	kubectl wait --for=condition=Ready nodes --all --timeout=60s
	@echo "Cluster is awake. Run 'make ports' in background and 'make status' to check stateful sets."

# Puts the cluster to sleep to save laptop battery power
stop:
	@echo "Suspending Kind control plane to conserve system resources..."
	docker stop job-board-cluster-control-plane
	@echo "All operations safely frozen."

# Displays real-time cluster health summary
status:
	@echo "Active Pipeline Workloads:"
	kubectl get pods -n $(NAMESPACE)
	@echo "\nActive Observability Workloads:"
	kubectl get pods -n $(MONITORING_NS)

# Automated Port-Forward Orchestrator (Run this in a dedicated terminal window)
ports:
	@echo "Spinning up parallel network proxy bridges..."
	@echo "Grafana on http://localhost:8080"
	@echo "Elasticsearch on https://localhost:9200"
	@echo "Redis Cache on http://localhost:6379"
	@echo "MinIO Engine on http://localhost:9001"
	kubectl port-forward svc/kube-prometheus-stack-grafana 8080:80 -n $(MONITORING_NS) & \
	kubectl port-forward svc/elasticsearch-master 9200:9200 -n $(NAMESPACE) & \
	kubectl port-forward svc/redis 6379:6379 -n default & \
	kubectl port-forward svc/minio-service 9001:9001 -n $(NAMESPACE) & \
	kubectl port-forward svc/my-kafka-kafka-bootstrap 9092:9092 -n $(NAMESPACE)

# Runs the background backend web framework automatically with credentials attached
run-backend:
	@echo "Extracting secure keystore authorization codes..."
	$(eval ES_PASSWORD=$(shell kubectl get secret elasticsearch-master-credentials -n $(NAMESPACE) -o jsonpath='{.data.password}' | base64 --decode))
	@echo "Starting FastAPI App on http://localhost:8000"
	cd src/api && ES_PASSWORD=$(ES_PASSWORD) ./venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Triggers an on-demand scraper run immediately
trigger-scraper:
	@echo "Forcing scraper ingestion sequence..."
	kubectl create job --from=cronjob/job-scraper manual-run-`date +%s` -n $(NAMESPACE)

# Real-time log monitors
tail-worker:
	kubectl logs deployment/job-worker -n $(NAMESPACE) -f

tail-geo:
	kubectl logs deployment/geo-worker -n $(NAMESPACE) -f

# Nuclear reset option: Wipes old persistent disk claims if you want a complete reset
clean-pvc:
	@echo "Warning: Destroying underlying storage claims..."
	kubectl delete pvc --all -n $(NAMESPACE)