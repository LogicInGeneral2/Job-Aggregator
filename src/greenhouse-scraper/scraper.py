import json
import os
import time
import requests
from confluent_kafka import Producer

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = 'raw-job-postings'
TARGET_COMPANIES = {
    "airbnb": "Airbnb",
    "atlassian": "Atlassian",
    "cloudflare": "Cloudflare",
    "coinbase": "Coinbase",
    "datadog": "Datadog",
    "discord": "Discord",
    "doordash": "DoorDash",
    "figma": "Figma",
    "gitlab": "GitLab",
    "mongodb": "MongoDB",
    "airbnb": "Airbnb",
    "atlassian": "Atlassian",
    "cloudflare": "Cloudflare",
    "coinbase": "Coinbase",
    "datadog": "Datadog",
    "discord": "Discord",
    "doordash": "DoorDash",
    "figma": "Figma",
    "gitlab": "GitLab",
    "mongodb": "MongoDB",
}

def category_filter(job_obj) -> str:
    """
    Maps company-specific departments/job titles into normalized job categories.
    """

    text = ""

    # Department(s)
    departments = job_obj.get("departments", [])
    if isinstance(departments, list):
        for dept in departments:
            if isinstance(dept, dict):
                text += " " + dept.get("name", "")

    # Team (some APIs use teams instead)
    teams = job_obj.get("teams", [])
    if isinstance(teams, list):
        for team in teams:
            if isinstance(team, dict):
                text += " " + team.get("name", "")

    # Title
    text += " " + job_obj.get("title", "")

    text = text.lower()

    CATEGORY_KEYWORDS = {
        "Software Development": [
            "software", "developer", "engineer", "programmer",
            "backend", "front end", "frontend", "back end",
            "full stack", "fullstack", "web", "mobile",
            "android", "ios", "react", "angular", "vue",
            "java", "python", "golang", "c++", ".net",
            "ruby", "php"
        ],

        "Data Science": [
            "data scientist", "data science", "machine learning",
            "ml", "ai", "artificial intelligence",
            "deep learning", "nlp", "computer vision",
            "research scientist"
        ],

        "Data Engineering": [
            "data engineer", "etl", "data platform",
            "data warehouse", "big data", "analytics engineer"
        ],

        "Data Analytics": [
            "data analyst", "business intelligence",
            "bi", "analytics", "reporting",
            "business analyst"
        ],

        "DevOps Engineering": [
            "devops", "site reliability", "sre",
            "cloud engineer", "platform engineer",
            "infrastructure", "kubernetes", "aws",
            "azure", "gcp", "terraform"
        ],

        "Cybersecurity": [
            "security", "cyber", "soc", "penetration",
            "pentest", "infosec", "application security",
            "security engineer"
        ],

        "Quality Assurance": [
            "qa", "quality assurance", "quality engineer",
            "test engineer", "tester", "automation test",
            "software test", "sdet"
        ],

        "UI/UX Design": [
            "ui", "ux", "product designer",
            "interaction designer", "visual designer",
            "graphic designer", "design"
        ],

        "Product Management": [
            "product manager", "product owner",
            "technical product", "product"
        ],

        "Project Management": [
            "project manager", "program manager",
            "scrum master", "delivery manager",
            "agile coach"
        ],

        "IT Support": [
            "it support", "technical support",
            "helpdesk", "desktop support",
            "service desk", "support engineer"
        ],

        "Network Engineering": [
            "network", "network engineer",
            "network administrator"
        ],

        "Systems Administration": [
            "system administrator", "sysadmin",
            "linux administrator", "windows administrator"
        ],

        "Database Administration": [
            "database administrator", "dba",
            "sql administrator"
        ],

        "Sales": [
            "sales", "account executive",
            "business development", "inside sales",
            "account manager"
        ],

        "Marketing": [
            "marketing", "digital marketing",
            "growth", "seo", "sem",
            "content marketing", "brand"
        ],

        "Customer Success": [
            "customer success", "customer support",
            "customer service", "client success"
        ],

        "Human Resources": [
            "human resources", "hr",
            "recruiter", "recruitment",
            "talent acquisition", "people operations"
        ],

        "Finance": [
            "finance", "financial", "accounting",
            "accountant", "controller",
            "bookkeeper", "auditor"
        ],

        "Legal": [
            "legal", "counsel",
            "attorney", "lawyer",
            "compliance"
        ],

        "Operations": [
            "operations", "business operations",
            "operational excellence"
        ],

        "Supply Chain": [
            "supply chain", "procurement",
            "purchasing", "buyer",
            "logistics"
        ],

        "Manufacturing": [
            "manufacturing", "production",
            "plant", "assembly"
        ],

        "Healthcare": [
            "medical", "clinical",
            "healthcare", "nurse",
            "doctor", "pharmacist"
        ],

        "Education": [
            "teacher", "lecturer",
            "professor", "education",
            "trainer", "instructor"
        ],

        "Research": [
            "research", "scientist",
            "researcher", "r&d"
        ],

        "Consulting": [
            "consultant", "consulting",
            "advisory"
        ],

        "Executive": [
            "chief", "ceo", "cto",
            "cio", "coo", "cfo",
            "vp", "vice president",
            "director", "head of"
        ],

        "Internship": [
            "intern", "internship",
            "graduate program", "graduate",
            "apprentice", "co-op"
        ]
    }

    # Match categories
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "Not Stated"

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Delivered to topic {msg.topic()} [Partition: {msg.partition()}]")

def fetch_company_jobs(company_token):
    """Fetches jobs for a specific company endpoint."""
    url = f'https://boards-api.greenhouse.io/v1/boards/{company_token}/jobs'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('jobs', [])
    except Exception as e:
        print(f"Failed to fetch {company_token}: {e}")
        return []

def main():
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})
    total_jobs_scraped = 0
    print("🚀 Starting Greenhouse Multi-Tenant Batch Scrape...")

    # LOOP THROUGH ALL COMPANIES IN ONE RUN
    for token, company_name in TARGET_COMPANIES.items():
        jobs = fetch_company_jobs(token)
        print(f"Found {len(jobs)} jobs at {company_name}.")

        for job in jobs:
            loc_obj = job.get('location', {})
            location_string = loc_obj.get('name', 'Remote') if loc_obj else 'Remote'
            filtered_category = category_filter(job)
            
            payload = {
                'id': f"gh_stripe_{job.get('id')}",
                'title': job.get('title'),
                'company': company_name,
                'url': job.get('absolute_url'),
                'category': filtered_category,
                'publication_date': job.get('updated_at'),
                'description': job.get('title', ''),
                'location': location_string 
            }
            
            producer.poll(0)
            producer.produce(
                topic=KAFKA_TOPIC,
                key=str(payload['id']).encode('utf-8'),
                value=json.dumps(payload).encode('utf-8'),
                callback=delivery_report
            )

        total_jobs_scraped += len(jobs)
        
        # Wait 15 seconds before hitting the next company's API 
        time.sleep(15) 

    producer.flush()
    print(f"Greenhouse batch aggregation complete. Total jobs pushed to Kafka: {total_jobs_scraped}")

if __name__ == '__main__':
    main()