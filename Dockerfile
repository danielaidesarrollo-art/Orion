FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any needed (e.g. for pandas/numpy if they were being built)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-medgemma.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-medgemma.txt

COPY . .

# Cloud Run defaults to port 8080
EXPOSE 8080

CMD ["uvicorn", "api.triage_api:app", "--host", "0.0.0.0", "--port", "8080"]
