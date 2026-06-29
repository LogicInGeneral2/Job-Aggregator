FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY worker.py .

# Run the script. 
# The -u flag forces Python to unbuffer the standard output, to see the print() statements instantly in the kubectl logs.
CMD ["python", "-u", "worker.py"]