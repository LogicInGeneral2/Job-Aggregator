import os
import json
from confluent_kafka import Consumer, KafkaError
from elasticsearch import Elasticsearch
from prometheus_client import start_http_server, Counter

# 1. Define our Custom Metric
JOBS_INDEXED = Counter('jobs_indexed_total', 'Total number of jobs successfully indexed into Elasticsearch')

def main():
    # 2. Start the Prometheus metrics server on port 8081
    start_http_server(8081)
    print("Metrics server started on port 8081")

    # Kafka Configuration
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
    TOPIC_NAME = 'raw-job-postings'

    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'job-processor-group',
        'auto.offset.reset': 'earliest'
    }
    
    # Elasticsearch Configuration
    ES_HOST = os.getenv('ES_HOST', 'localhost')
    ES_PORT = os.getenv('ES_PORT', '9200')
    ES_PASSWORD = os.getenv('ES_PASSWORD')

    es = Elasticsearch(
        f"https://{ES_HOST}:{ES_PORT}",
        basic_auth=("elastic", ES_PASSWORD),
        verify_certs=False
    )
    
    print(f"Connecting securely to Elasticsearch at https://{ES_HOST}:{ES_PORT}...")
    
    consumer = Consumer(conf)
    consumer.subscribe([TOPIC_NAME])
    
    print(f"Connecting to Kafka at {KAFKA_BROKER}...")
    print(f"Worker started. Listening to topic: {TOPIC_NAME}...")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            job_data = json.loads(msg.value().decode('utf-8'))
            job_id = job_data.get('id', 'unknown')
            job_title = job_data.get('title', 'Unknown Title')
            
            print(f"Received Job: {job_title}")
            
            # Index into Elasticsearch
            es.index(index='jobs', id=str(job_id), document=job_data)
            
            # 3. Increment on success
            JOBS_INDEXED.inc()
            
            print(f"Indexed job {job_id} into secure Elasticsearch")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    main()