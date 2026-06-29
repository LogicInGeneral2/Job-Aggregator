import os
import json
import redis
import smtplib
from email.message import EmailMessage

SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_EMAIL = os.getenv('SMTP_EMAIL')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

def send_digest(to_email, jobs):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("SMTP credentials missing.")
        return

    msg = EmailMessage()
    msg['Subject'] = f"Daily Job Digest: {len(jobs)} New Matches"
    msg['From'] = SMTP_EMAIL
    msg['To'] = to_email
    
    body = "Here are your matching jobs for the last 24 hours:\n\n"
    for j in jobs:
        body += f"- {j['title']}\n  Apply: {j['url']}\n\n"
        
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Digest sent to {to_email} with {len(jobs)} jobs.")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")
        return False

def main():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    user_ids = r.smembers("alert_users")
    
    print("📬 Starting Daily Digest run...")
    
    for uid in user_ids:
        queue_key = f"user:{uid}:pending_alerts"
        user_email = r.hget(f"user:{uid}", "email")
        
        # Pull all buffered jobs from Redis
        raw_jobs = r.lrange(queue_key, 0, -1)
        
        if raw_jobs and user_email:
            parsed_jobs = [json.loads(j) for j in raw_jobs]
            success = send_digest(user_email, parsed_jobs)
            
            # If the email sent successfully, delete the queue
            if success:
                r.delete(queue_key)
        else:
            print(f"No new jobs pending for user:{uid}")

    print("Daily Digest run complete.")

if __name__ == '__main__':
    main()