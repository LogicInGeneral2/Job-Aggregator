import os
import json
import time
from confluent_kafka import Consumer, KafkaError
from redis import Redis
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

r = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
# User-agent
geolocator = Nominatim(user_agent="portfolio_job_heatmap_v1")

def geocode_location(location_str):
    # Skip these
    invalid_locs = ['anywhere', 'remote', 'worldwide', 'global', 'us remote']
    if not location_str or any(word in location_str.lower() for word in invalid_locs):
        return None
        
    try:
        time.sleep(1.1) # Nominatim 1 req/sec limit
        location = geolocator.geocode(location_str, timeout=5)
        if location:
            return location.longitude, location.latitude
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Geocoding error for '{location_str}': {e}")
    return None

def main():
    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'geo-mapping-group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe(['raw-job-postings'])
    print("Geo-Worker listening to raw-job-postings...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None: continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(msg.error())
                continue

            job = json.loads(msg.value().decode('utf-8'))
            job_id = job.get('id')
            
            # Remotive API store
            location_str = job.get('location') 

            print(f"Processing Job ID: {job_id}, Location: {location_str}")
            
            coords = geocode_location(location_str)
            if coords:
                lon, lat = coords
                r.execute_command('GEOADD', 'job_heatmap', lon, lat, location_str, str(job_id))
                print(f"Mapped Job {job_id} ({location_str}) -> [Lon: {lon}, Lat: {lat}]")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    main()