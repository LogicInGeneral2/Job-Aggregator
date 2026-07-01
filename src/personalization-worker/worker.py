import os
import json
import redis
from confluent_kafka import Consumer, KafkaError

def main():
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
    TOPIC_NAME = 'user-clickstream'
    
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")

    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'personalization-group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe([TOPIC_NAME])
    
    print(f"Personalization Worker listening to {TOPIC_NAME}...")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF: continue
                else: 
                    print(msg.error())
                    break

            # Parse the click event
            event = json.loads(msg.value().decode('utf-8'))
            session_id = event.get('session_id', 'unknown')
            category = event.get('category', 'unknown')
            
            if category and category != 'unknown':
                preference_key = f"user_prefs:{session_id}"
                
                # Increment the user's affinity for this specific job category
                new_score = r.zincrby(preference_key, 1, category)
                
                # Keep only top 5 favorite categories to save RAM
                r.zremrangebyrank(preference_key, 0, -6)
                
                # 7-day expiration
                r.expire(preference_key, 604800)
                
                print(f"Updated User [{session_id}] -> Loves {category.upper()} (Score: {new_score})")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    main()