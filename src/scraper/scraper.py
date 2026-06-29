import json
import os
import requests
from confluent_kafka import Producer

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = 'raw-job-postings'
API_URL = 'https://remotive.com/api/remote-jobs?limit=15'

def delivery_report(err, msg):
    """ Callback triggered by Kafka to check if the message arrived successfully """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Delivered to topic {msg.topic()} [Partition: {msg.partition()}]")

def fetch_jobs():
    print(f"Fetching jobs from {API_URL}...")
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json().get('jobs', [])

def main():
    # 1. Initialize Kafka Producer
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})

    # 2. Fetch data
    jobs = fetch_jobs()
    print(f"Found {len(jobs)} jobs. Producing to Kafka...")

    # 3. Push jobs to the broker
    for job in jobs:
        # Clean payload
        payload = {
            'id': job.get('id'),
            'title': job.get('title'),
            'company': job.get('company_name'),
            'url': job.get('url'),
            'category': job.get('category'),
            'publication_date': job.get('publication_date'),
            'description': job.get('description')
        }

        # Trigger any available delivery report callbacks from previous loops
        producer.poll(0)

        # Produce a message with Job ID as the 'key'.
        producer.produce(
            topic=KAFKA_TOPIC,
            key=str(payload['id']).encode('utf-8'),
            value=json.dumps(payload).encode('utf-8'),
            callback=delivery_report
        )

    # 4. Wait for all messages in the Producer queue to be delivered before exiting
    producer.flush()
    print("All messages flushed. Scraper complete.")

if __name__ == '__main__':
    main()