import os
import json
import warnings
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
from redis import Redis
from urllib3.exceptions import InsecureRequestWarning

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
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Initialize connections
es = Elasticsearch(
    ES_HOST,
    basic_auth=(ES_USER, ES_PASSWORD),
    verify_certs=False
)
cache = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

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

@app.get("/api/jobs/search")
def search_jobs(q: str):
    """Performs a full-text search across job titles and companies."""
    try:
        response = es.search(
            index="jobs",
            body={
                "query": {
                    "multi_match": {
                        "query": q,
                        "fields": ["title^2", "company", "category"],
                        "fuzziness": "AUTO" # Allows for minor typos
                    }
                },
                "size": 15
            }
        )
        jobs = [hit["_source"] for hit in response["hits"]["hits"]]
        return {"source": "elasticsearch", "data": jobs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))