import os
import json
from urllib import response
import warnings
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
import redis
from urllib3.exceptions import InsecureRequestWarning
from pydantic import BaseModel
from confluent_kafka import Producer
from typing import Optional

app = FastAPI(title="Global Job Board API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hide TLS warnings
warnings.simplefilter('ignore', InsecureRequestWarning)

ES_HOST = os.getenv("ES_HOST", "https://localhost:9200")
ES_USER = os.getenv("ES_USER", "elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD", "")

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

# Initialize connections
es = Elasticsearch(
    ES_HOST,
    basic_auth=(ES_USER, ES_PASSWORD),
    verify_certs=False
)

cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Initialize Kafka Producer for Clickstream
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
click_producer = Producer({'bootstrap.servers': KAFKA_BROKER})

class ClickEvent(BaseModel):
    session_id: str
    job_id: str
    category: str

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "Job Board API"}

@app.get("/api/jobs/recent")
def get_recent_jobs():
    """Fetches the most recent jobs, utilizing Redis for caching."""
    cache_key = "recent_jobs"
    
    # 1. Check Redis Cache
    cached_data = cache.get(cache_key)
    if cached_data:
        print("Served from Redis Cache")
        return {"source": "redis", "data": json.loads(cached_data)}
    
    # 2. If not in cache, query Elasticsearch
    print("Cache miss. Querying Elasticsearch...")
    try:
        response = es.search(
            index="jobs",
            body={
                "query": {"match_all": {}},
                "sort": [{"publication_date": {"order": "desc"}}],
                "size": 20
            }
        )
        
        # Extract the actual job documents from the ES response
        jobs = [hit["_source"] for hit in response["hits"]["hits"]]
        
        # 3. Store the result in Redis for 60 seconds (TTL)
        cache.setex(cache_key, 60, json.dumps(jobs))
        
        return {"source": "elasticsearch", "data": jobs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from typing import Optional

@app.get("/api/jobs/search")
def search_jobs(q: str, session_id: Optional[str] = None):
    """
    Performs a full-text search and dynamically boosts results 
    based on the user's live clickstream preferences using function_score.
    """
    try:
        # 1. The Base Query wrapped in a function_score
        es_query = {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": q,
                        "fields": ["title^2", "company", "category"],
                        "fuzziness": "AUTO"
                    }
                },
                "functions": [],
                "boost_mode": "multiply"  # Multiplies the base score by the weight
            }
        }
        
        # 2. Check Redis for user preferences
        if session_id:
            preference_key = f"user_prefs:{session_id}"
            favorite_categories = cache.zrevrange(preference_key, 0, 2)
            
            if favorite_categories:
                print(f"Boosting search for session [{session_id}] with categories: {favorite_categories}")
                # Build the absolute override functions
                for category in favorite_categories:
                    es_query["function_score"]["functions"].append({
                        # THE FIX: Use a 'term' query on '.keyword' for an absolute, exact string match.
                        "filter": {
                            "term": {
                                "category.keyword": category
                            }
                        },
                        "weight": 6.7
                    })

        # 3. Execute the Personalized Search
        response = es.search(
            index="jobs",
            body={
                "query": es_query,
                "size": 15
            }
        )
        
        # 4. Extract the job data
        jobs = [hit["_source"] for hit in response["hits"]["hits"]]
            
        return {"source": "elasticsearch", "data": jobs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/skills/trending")
def get_trending_skills(limit: int = 10):
    """
    Fetches the top trending skills directly from the Redis Sorted Set.
    Returns the top 'limit' skills sorted by their frequency count.
    """
    try:
        # ZREVRANGE gets the highest scores first. 
        # 0 is the start index, (limit - 1) is the end index.
        # withscores=True returns a list of tuples
        raw_data = cache.zrevrange("trending_skills", 0, limit - 1, withscores=True)
        
        # Format the output into dictionaries
        leaderboard = [{"skill": skill.upper(), "count": int(score)} for skill, score in raw_data]
        
        return {"trending": leaderboard}
        
    except Exception as e:
        return {"error": str(e), "message": "Failed to fetch trending skills from Redis"}

@app.post("/api/jobs/click")
def record_click(event: ClickEvent):
    """Records a user click and drops it into Kafka for real-time processing."""
    try:
        payload = event.model_dump()
        
        # Produce the click event to Kafka instantly
        click_producer.produce(
            topic="user-clickstream",
            key=event.session_id.encode('utf-8'),
            value=json.dumps(payload).encode('utf-8')
        )
        
        # Wait for Kafka's receipt!
        click_producer.flush() 
        
        return {"status": "Event logged to Kafka"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/jobs/heatmap")
def get_job_heatmap():
    """Fetches real-time coordinates of active jobs from Redis."""
    try:
        # 1. Grab job IDs from the Redis
        members = cache.zrange("job_heatmap", 0, 100)
        
        if not members:
            return {"source": "redis", "data": []}
            
        # 2. Extract coordinates
        coords = cache.geopos("job_heatmap", *members)
        
        results = []
        for member, pos in zip(members, coords):
            if pos: # Ensure coordinates exist
                results.append({
                    "label": member,
                    "lng": pos[0],
                    "lat": pos[1]
                })
                
        return {"source": "redis", "data": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))