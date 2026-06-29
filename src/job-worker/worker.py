import os
import json
from confluent_kafka import Consumer, Producer, KafkaError
from elasticsearch import Elasticsearch
from prometheus_client import start_http_server, Counter

# Prometheus Metric
JOBS_INDEXED = Counter('jobs_indexed_total', 'Total number of jobs successfully indexed into Elasticsearch')

# Predefined list of target skills
TARGET_SKILLS = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#",
    "golang", "go", "rust", "php", "ruby", "kotlin", "swift",
    "scala", "r", "sql", "bash", "powershell",

    # Frontend
    "html", "css", "react", "reactjs", "next.js", "nextjs",
    "vue", "vue.js", "angular", "svelte", "tailwind",
    "bootstrap", "jquery", "redux",

    # Backend
    "node", "node.js", "nodejs", "express", "nestjs",
    "django", "flask", "fastapi", "spring", "spring boot",
    "asp.net", ".net", "laravel", "ruby on rails",

    # Mobile
    "android", "ios", "react native", "flutter", "xamarin",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes",
    "terraform", "ansible", "jenkins", "github actions",
    "gitlab ci", "circleci", "helm", "nginx",

    # Databases
    "mysql", "postgresql", "postgres", "sqlite",
    "mongodb", "redis", "oracle", "sql server",
    "firebase", "dynamodb", "cassandra",

    # Messaging & Streaming
    "kafka", "rabbitmq", "sqs", "pub/sub",

    # APIs
    "rest", "rest api", "graphql", "grpc",
    "soap", "openapi", "swagger",

    # Version Control
    "git", "github", "gitlab", "bitbucket",

    # Operating Systems
    "linux", "unix", "windows",

    # Testing
    "junit", "pytest", "jest", "cypress",
    "selenium", "playwright", "mocha",

    # Data Engineering
    "spark", "hadoop", "airflow", "etl",

    # AI / ML
    "machine learning", "deep learning", "tensorflow",
    "pytorch", "scikit-learn", "opencv", "pandas",
    "numpy", "langchain", "llm", "openai",

    # Security
    "oauth", "jwt", "saml", "owasp", "ssl", "tls",

    # Monitoring
    "prometheus", "grafana", "elk", "elastic",
    "logstash", "kibana", "datadog", "splunk",

    # Methodologies
    "agile", "scrum", "kanban", "waterfall",

    # Software Engineering Concepts
    "oop", "object oriented programming",
    "design patterns", "microservices",
    "distributed systems", "system design",
    "data structures", "algorithms",
    "multithreading", "concurrency",
    "debugging", "unit testing",
    "integration testing", "ci/cd",

    # Soft Skills
    "communication", "teamwork",
    "problem solving", "critical thinking",
    "time management", "leadership"
]

def extract_skills(text):
    """Simple keyword matching to extract skills from text."""
    if not text:
        return []
    text = text.lower()
    return [skill for skill in TARGET_SKILLS if skill in text]

def main():
    #Start the Prometheus metrics server on port 8081
    start_http_server(8081)
    print("Metrics server started on port 8081")

    # Kafka Configuration
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
    CONSUME_TOPIC = 'raw-job-postings'
    PRODUCE_TOPIC = 'live-skill-mentions'

    # Consumer
    consumer_conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'job-processor-group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe([CONSUME_TOPIC])
    
    # Producer
    producer_conf = {'bootstrap.servers': KAFKA_BROKER}
    producer = Producer(producer_conf)
    
    # Elasticsearch Configuration
    ES_HOST = os.getenv('ES_HOST', 'localhost')
    ES_PORT = os.getenv('ES_PORT', '9200')
    ES_PASSWORD = os.getenv('ES_PASSWORD')

    es = Elasticsearch(
        f"https://{ES_HOST}:{ES_PORT}",
        basic_auth=("elastic", ES_PASSWORD),
        verify_certs=False
    )
    
    print(f"Connecting to Kafka at {KAFKA_BROKER}...")
    print(f"Worker started. Listening to {CONSUME_TOPIC}...")

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

            # Parse the incoming job
            job_data = json.loads(msg.value().decode('utf-8'))
            job_id = job_data.get('id', 'unknown')
            job_title = job_data.get('title', 'Unknown Title')
            job_desc = job_data.get('description', '')
            
            print(f"\n Received Job: {job_title}")
            
            # Action 1: Index into Elasticsearch
            es.index(index='jobs', id=str(job_id), document=job_data)
            JOBS_INDEXED.inc()
            print(f"Indexed job {job_id}")
            
            # Action 2: Extract Skills & Stream to Kafka, combining title and description to maximize keyword hits
            found_skills = extract_skills(job_title + " " + job_desc)
            
            for skill in found_skills:
                # Stream each individual skill back into Kafka
                producer.produce(PRODUCE_TOPIC, key=str(job_id), value=skill)
                print(f"Streamed skill mention: {skill.upper()}")
            
            # Flush to ensure messages are delivered
            producer.flush()

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    main()