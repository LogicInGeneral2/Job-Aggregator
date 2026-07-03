FROM python:3.11-slim

# Set system configurations
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY scraper.py .

# Run the script
CMD ["python", "scraper.py"]