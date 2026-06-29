import os
import json
import redis
from confluent_kafka import Consumer, KafkaError

def main():
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
    TOPIC_NAME = 'raw-job-postings'
    
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    print(f"🔌 Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")

    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'alerts-group', 
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe([TOPIC_NAME])
    
    print(f"Alerts Worker buffering matches into Redis...")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF: continue
                else: break

            job_data = json.loads(msg.value().decode('utf-8'))
            job_title = job_data.get('title', 'Unknown Title')
            job_desc = job_data.get('description', '')
            job_url = job_data.get('url', 'No link provided')
            full_text = (job_title + " " + job_desc).lower()
            
            # The Match Engine
            user_ids = r.smembers("alert_users")
            for uid in user_ids:
                user_keywords = r.smembers(f"user:{uid}:alerts")
                
                if user_keywords and all(kw.lower() in full_text for kw in user_keywords):
                    # NEW: Buffer the job into a Redis List instead of emailing
                    digest_payload = json.dumps({"title": job_title, "url": job_url})
                    r.rpush(f"user:{uid}:pending_alerts", digest_payload)
                    print(f"Buffered match for user:{uid} -> {job_title}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    main()