import os
import redis
from confluent_kafka import Consumer, KafkaError

def main():
    # Configuration
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
    TOPIC_NAME = 'live-skill-mentions'
    
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = os.getenv('REDIS_PORT', '6379')

    # Connect to Redis, decode_responses=True is to get strings back instead of raw bytes
    r = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), decode_responses=True)
    print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")

    # Connect to Kafka
    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'leaderboard-group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe([TOPIC_NAME])
    
    print(f"Leaderboard Worker listening to {TOPIC_NAME}...")

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

            # Extract from the Kafka message
            skill = msg.value().decode('utf-8')
            
            # Update the Redis Sorted Set, zincrby(name_of_set, amount_to_increment, value)
            new_score = r.zincrby('trending_skills', 1, skill)
            
            print(f"Incremented [{skill.upper()}] - New Score: {new_score}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    main()