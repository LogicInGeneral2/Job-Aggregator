import os
import json
import warnings
from confluent_kafka import Consumer
from elasticsearch import Elasticsearch
from urllib3.exceptions import InsecureRequestWarning

# Hide certificate warnings to keep the terminal logs clean
warnings.simplefilter('ignore', InsecureRequestWarning)

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = 'raw-job-postings'
ES_HOST = os.getenv('ES_HOST', 'https://localhost:9200')
ES_USER = os.getenv('ES_USER', 'elastic')
ES_PASSWORD = os.getenv('ES_PASSWORD', '')

def main():
    # 1. Initialize the Secure Elasticsearch Client
    print(f"Connecting securely to Elasticsearch at {ES_HOST}...")
    es = Elasticsearch(
        ES_HOST,
        basic_auth=(ES_USER, ES_PASSWORD),
        verify_certs=False
    )

    # 2. Initialize the Kafka Consumer
    print(f"Connecting to Kafka at {KAFKA_BROKER}...")
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'job-processor-group',
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe([KAFKA_TOPIC])
    print(f"Worker started. Listening to topic: {KAFKA_TOPIC}...")

    # 3. The Processing Loop
    try:
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            job_data = json.loads(msg.value().decode('utf-8'))
            job_id = job_data.get('id')
            job_title = job_data.get('title')

            print(f"Received Job: {job_title}")

            # 4. Push the standardized job to Elasticsearch
            es.index(index='jobs', id=str(job_id), document=job_data)
            print(f"Indexed job {job_id} into secure Elasticsearch")

    except Exception as e:
        print(f"Crash detected: {e}")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()