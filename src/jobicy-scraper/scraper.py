import json
import os
import requests
from confluent_kafka import Producer

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = 'raw-job-postings'
API_URL = 'https://jobicy.com/api/v2/remote-jobs?count=15'

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Delivered to topic {msg.topic()} [Partition: {msg.partition()}]")

def fetch_jobs():
    print(f"Fetching jobs from {API_URL}...")
    headers = {'User-Agent': 'Portfolio-Aggregator-v1'}
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()
    return response.json().get('jobs', [])

def main():
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})
    jobs = fetch_jobs()
    print(f"Found {len(jobs)} jobs. Normalizing and producing to Kafka...")

    for job in jobs:
        # Schema Normalization. 
        payload = {
            'id': f"jobicy_{job.get('id')}", 
            'title': job.get('jobTitle'),
            'company': job.get('companyName'),
            'url': job.get('url'),
            'category': job.get('jobCategory'),
            'publication_date': job.get('pubDate'),
            'description': job.get('jobDescription', ''),
            'location': job.get('jobGeo')
        }
        
        producer.poll(0)
        producer.produce(
            topic=KAFKA_TOPIC,
            key=str(payload['id']).encode('utf-8'),
            value=json.dumps(payload).encode('utf-8'),
            callback=delivery_report
        )

    producer.flush()
    print("All Jobicy messages flushed. Scraper complete.")

if __name__ == '__main__':
    main()